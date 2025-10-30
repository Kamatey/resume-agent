from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import os
import asyncio
import sys
import tempfile
import json
from agno.media import File as AgnoFile

# Set Windows-specific event loop policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from agent import create_agent

load_dotenv()

app = FastAPI(
    title="Resume Agent API",
    description="AI-powered Resume/CV Analysis and Optimization API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store agent instance
agent_instance = None


# Request/Response Models
class ChatRequest(BaseModel):
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent_instance
    agent_instance = await create_agent()
    print("✅ Resume Agent initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Resume Agent API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": agent_instance is not None
    }


async def process_file_input(file: UploadFile, input_name: str = "file"):
    """Helper function to process uploaded files"""
    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type for {input_name}. Allowed: {', '.join(allowed_extensions)}"
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        return tmp_file.name, file.filename


@app.post("/analyze")
async def analyze(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
    prompt: str = Form(default="Analyze this CV comprehensively and provide detailed insights.")
):
    """
    Analyze CV - FLEXIBLE INPUT:
    - CV: Provide either cv_file OR cv_text (required)
    - Job Description: Optionally provide jd_file OR jd_text (optional)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    # Validate CV input - check for actual file and non-empty text
    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided for the CV")

    # Validate JD input (optional) - check for actual file and non-empty text
    has_jd_file = jd_file is not None and hasattr(jd_file, 'filename')
    has_jd_text = jd_text is not None and isinstance(jd_text, str) and jd_text.strip() != ""

    cv_tmp_file = None
    jd_tmp_file = None

    try:
        files_to_process = []

        # Process CV
        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            files_to_process.append(AgnoFile(filepath=cv_tmp_file))
            cv_input_type = "file"
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            cv_input_type = "text"

        # Process Job Description if provided
        if has_jd_file:
            jd_tmp_file, jd_filename = await process_file_input(jd_file, "Job Description")
            files_to_process.append(AgnoFile(filepath=jd_tmp_file))
            prompt += f"\n\nJob Description is provided as a file."
            jd_input_type = "file"
        elif has_jd_text:
            prompt += f"\n\nJob Description:\n{jd_text}"
            jd_input_type = "text"
        else:
            jd_input_type = None

        # Run agent
        if files_to_process:
            response = agent_instance.run(prompt, files=files_to_process)
        else:
            response = agent_instance.run(prompt)

        # Clean up temp files
        if cv_tmp_file:
            os.unlink(cv_tmp_file)
        if jd_tmp_file:
            os.unlink(jd_tmp_file)

        result = {
            "success": True,
            "cv_input_type": cv_input_type,
            "analysis": response.content
        }

        if has_cv_file:
            result["cv_filename"] = cv_filename
        if jd_input_type:
            result["jd_input_type"] = jd_input_type
            if has_jd_file:
                result["jd_filename"] = jd_filename

        return result

    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp files on error
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        if jd_tmp_file:
            try:
                os.unlink(jd_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/chat")
async def chat(request: ChatRequest):
    """
    General chat endpoint for conversational interaction with the agent
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        response = agent_instance.run(request.message)

        return {
            "success": True,
            "response": response.content
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@app.post("/parse")
async def parse_cv(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None)
):
    """
    Parse CV and extract structured information
    - CV: Provide either cv_file OR cv_text (required)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None

    try:
        prompt = "Parse this CV and extract all structured information in detail using the parse_cv tool."

        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            response = agent_instance.run(prompt, files=[AgnoFile(filepath=cv_tmp_file)])
            os.unlink(cv_tmp_file)

            return {
                "success": True,
                "cv_input_type": "file",
                "cv_filename": cv_filename,
                "parsed_data": response.content
            }
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            response = agent_instance.run(prompt)

            return {
                "success": True,
                "cv_input_type": "text",
                "parsed_data": response.content
            }

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@app.post("/ats-score")
async def evaluate_ats(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None)
):
    """
    Evaluate ATS score for a CV - FLEXIBLE INPUT:
    - CV: Provide either cv_file OR cv_text (required)
    - Job Description: Optionally provide jd_file OR jd_text (optional)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""
    has_jd_file = jd_file is not None and hasattr(jd_file, 'filename')
    has_jd_text = jd_text is not None and isinstance(jd_text, str) and jd_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None
    jd_tmp_file = None

    try:
        prompt = "Evaluate this CV for ATS compatibility and provide a detailed score with recommendations using the evaluate_ats_score tool."
        files_to_process = []

        # Process CV
        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            files_to_process.append(AgnoFile(filepath=cv_tmp_file))
            cv_input_type = "file"
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            cv_input_type = "text"

        # Process Job Description if provided
        if has_jd_file:
            jd_tmp_file, jd_filename = await process_file_input(jd_file, "Job Description")
            files_to_process.append(AgnoFile(filepath=jd_tmp_file))
            prompt += f"\n\nJob Description is provided as a file."
            jd_input_type = "file"
        elif has_jd_text:
            prompt += f"\n\nJob Description:\n{jd_text}"
            jd_input_type = "text"
        else:
            jd_input_type = None

        # Run agent
        if files_to_process:
            response = agent_instance.run(prompt, files=files_to_process)
        else:
            response = agent_instance.run(prompt)

        # Clean up temp files
        if cv_tmp_file:
            os.unlink(cv_tmp_file)
        if jd_tmp_file:
            os.unlink(jd_tmp_file)

        result = {
            "success": True,
            "cv_input_type": cv_input_type,
            "ats_evaluation": response.content
        }

        if has_cv_file:
            result["cv_filename"] = cv_filename
        if jd_input_type:
            result["jd_input_type"] = jd_input_type
            if has_jd_file:
                result["jd_filename"] = jd_filename

        return result

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        if jd_tmp_file:
            try:
                os.unlink(jd_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"ATS evaluation failed: {str(e)}")


@app.post("/compare")
async def compare_cv_with_job(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None)
):
    """
    Compare CV with job description - FLEXIBLE INPUT:
    - CV: Provide either cv_file OR cv_text (required)
    - Job Description: Provide either jd_file OR jd_text (required)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""
    has_jd_file = jd_file is not None and hasattr(jd_file, 'filename')
    has_jd_text = jd_text is not None and isinstance(jd_text, str) and jd_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided for the CV")

    if not has_jd_file and not has_jd_text:
        raise HTTPException(status_code=400, detail="Either 'jd_file' or 'jd_text' must be provided for the Job Description")

    cv_tmp_file = None
    jd_tmp_file = None

    try:
        prompt = "Compare this CV with the job description using the compare_cv_with_job tool."
        files_to_process = []

        # Process CV
        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            files_to_process.append(AgnoFile(filepath=cv_tmp_file))
            cv_input_type = "file"
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            cv_input_type = "text"

        # Process Job Description
        if has_jd_file:
            jd_tmp_file, jd_filename = await process_file_input(jd_file, "Job Description")
            files_to_process.append(AgnoFile(filepath=jd_tmp_file))
            prompt += f"\n\nJob Description is provided as a file."
            jd_input_type = "file"
        else:
            prompt += f"\n\nJob Description:\n{jd_text}"
            jd_input_type = "text"

        # Run agent
        if files_to_process:
            response = agent_instance.run(prompt, files=files_to_process)
        else:
            response = agent_instance.run(prompt)

        # Clean up temp files
        if cv_tmp_file:
            os.unlink(cv_tmp_file)
        if jd_tmp_file:
            os.unlink(jd_tmp_file)

        result = {
            "success": True,
            "cv_input_type": cv_input_type,
            "jd_input_type": jd_input_type,
            "comparison": response.content
        }

        if has_cv_file:
            result["cv_filename"] = cv_filename
        if has_jd_file:
            result["jd_filename"] = jd_filename

        return result

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        if jd_tmp_file:
            try:
                os.unlink(jd_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@app.post("/keywords")
async def extract_keywords(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None),
    top_n: int = Form(default=25)
):
    """
    Extract keywords from CV
    - CV: Provide either cv_file OR cv_text (required)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None

    try:
        prompt = f"Extract the top {top_n} most important keywords from this document using the extract_keywords tool."

        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            response = agent_instance.run(prompt, files=[AgnoFile(filepath=cv_tmp_file)])
            os.unlink(cv_tmp_file)

            return {
                "success": True,
                "cv_input_type": "file",
                "cv_filename": cv_filename,
                "keywords": response.content
            }
        else:
            prompt += f"\n\nTEXT:\n{cv_text}"
            response = agent_instance.run(prompt)

            return {
                "success": True,
                "cv_input_type": "text",
                "keywords": response.content
            }

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")


@app.post("/analyze-issues")
async def analyze_issues(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None)
):
    """
    Analyze CV for issues and categorize by severity
    - CV: Provide either cv_file OR cv_text (required)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None

    try:
        prompt = "Analyze this CV comprehensively and identify all issues categorized by severity using the analyze_cv_issues tool."

        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            response = agent_instance.run(prompt, files=[AgnoFile(filepath=cv_tmp_file)])
            os.unlink(cv_tmp_file)

            return {
                "success": True,
                "cv_input_type": "file",
                "cv_filename": cv_filename,
                "issues": response.content
            }
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            response = agent_instance.run(prompt)

            return {
                "success": True,
                "cv_input_type": "text",
                "issues": response.content
            }

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Issue analysis failed: {str(e)}")


@app.post("/rewrite")
async def rewrite_cv(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None),
    jd_file: Optional[UploadFile] = File(default=None),
    jd_text: Optional[str] = Form(default=None),
    focus_areas: Optional[str] = Form(default=None)  # Comma-separated string
):
    """
    Generate an improved version of the CV - FLEXIBLE INPUT:
    - CV: Provide either cv_file OR cv_text (required)
    - Job Description: Optionally provide jd_file OR jd_text (optional)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""
    has_jd_file = jd_file is not None and hasattr(jd_file, 'filename')
    has_jd_text = jd_text is not None and isinstance(jd_text, str) and jd_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None
    jd_tmp_file = None

    try:
        prompt = "Rewrite this CV to optimize for ATS while maintaining readability using the generate_cv_rewrite tool."
        files_to_process = []

        if focus_areas:
            areas_list = [area.strip() for area in focus_areas.split(',')]
            prompt += f"\n\nFocus on these areas: {', '.join(areas_list)}"

        # Process CV
        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            files_to_process.append(AgnoFile(filepath=cv_tmp_file))
            cv_input_type = "file"
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            cv_input_type = "text"

        # Process Job Description if provided
        if has_jd_file:
            jd_tmp_file, jd_filename = await process_file_input(jd_file, "Job Description")
            files_to_process.append(AgnoFile(filepath=jd_tmp_file))
            prompt += f"\n\nJob Description is provided as a file."
            jd_input_type = "file"
        elif has_jd_text:
            prompt += f"\n\nJob Description to tailor to:\n{jd_text}"
            jd_input_type = "text"
        else:
            jd_input_type = None

        # Run agent
        if files_to_process:
            response = agent_instance.run(prompt, files=files_to_process)
        else:
            response = agent_instance.run(prompt)

        # Clean up temp files
        if cv_tmp_file:
            os.unlink(cv_tmp_file)
        if jd_tmp_file:
            os.unlink(jd_tmp_file)

        result = {
            "success": True,
            "cv_input_type": cv_input_type,
            "rewritten_cv": response.content
        }

        if has_cv_file:
            result["cv_filename"] = cv_filename
        if jd_input_type:
            result["jd_input_type"] = jd_input_type
            if has_jd_file:
                result["jd_filename"] = jd_filename

        return result

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        if jd_tmp_file:
            try:
                os.unlink(jd_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"CV rewrite failed: {str(e)}")


@app.post("/improvement-plan")
async def generate_improvement_plan(
    cv_file: Optional[UploadFile] = File(default=None),
    cv_text: Optional[str] = Form(default=None)
):
    """
    Generate a prioritized improvement plan for the CV
    - CV: Provide either cv_file OR cv_text (required)
    """
    if not agent_instance:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    has_cv_file = cv_file is not None and hasattr(cv_file, 'filename')
    has_cv_text = cv_text is not None and isinstance(cv_text, str) and cv_text.strip() != ""

    if not has_cv_file and not has_cv_text:
        raise HTTPException(status_code=400, detail="Either 'cv_file' or 'cv_text' must be provided")

    cv_tmp_file = None

    try:
        prompt = "Create a prioritized improvement plan for this CV with actionable steps using the generate_improvement_plan tool."

        if has_cv_file:
            cv_tmp_file, cv_filename = await process_file_input(cv_file, "CV")
            response = agent_instance.run(prompt, files=[AgnoFile(filepath=cv_tmp_file)])
            os.unlink(cv_tmp_file)

            return {
                "success": True,
                "cv_input_type": "file",
                "cv_filename": cv_filename,
                "improvement_plan": response.content
            }
        else:
            prompt += f"\n\nCV TEXT:\n{cv_text}"
            response = agent_instance.run(prompt)

            return {
                "success": True,
                "cv_input_type": "text",
                "improvement_plan": response.content
            }

    except HTTPException:
        raise
    except Exception as e:
        if cv_tmp_file:
            try:
                os.unlink(cv_tmp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
