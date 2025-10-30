
The API will be available at `http://localhost:8000`

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs


## API Endpoints Overview

**FLEXIBLE INPUT SYSTEM:**
- **CV Input**: All endpoints accept EITHER `cv_file` (file upload) OR `cv_text` (text input)
- **Job Description Input**: Some endpoints optionally accept EITHER `jd_file` (file upload) OR `jd_text` (text input)
- Supported file formats: PDF, DOCX, DOC, TXT

---

### 1. Health Check

**GET** `/health`

Check if the API and agent are running properly.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true
}
```

---

### 2. Analyze CV

**POST** `/analyze`

Comprehensive CV analysis with customizable prompts.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content
- `jd_file` (file, optional): Job description file
- `jd_text` (string, optional): Job description text
- `prompt` (string, optional): Custom analysis prompt

**Examples:**

**CV file only:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "cv_file=@resume.pdf"
```

**CV file + JD text:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "cv_file=@resume.pdf" \
  -F "jd_text=Looking for a senior Python developer with 5+ years experience"
```

**CV text + JD file:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "cv_text=John Doe, Software Engineer..." \
  -F "jd_file=@job_description.pdf"
```

**CV text + custom prompt:**
```bash
curl -X POST http://localhost:8000/analyze \
  -F "cv_text=John Doe, Software Engineer..." \
  -F "prompt=Focus on technical skills and quantifiable achievements"
```

---

### 3. Chat

**POST** `/chat`

General conversational interaction with the agent.

**Parameters:**
- `message` (string, required): Your question or message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What makes a good resume for a software engineer position?"}'
```

---

### 4. Parse CV

**POST** `/parse`

Extract structured information from a CV.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content

**Examples:**

```bash
# With file
curl -X POST http://localhost:8000/parse \
  -F "cv_file=@resume.pdf"

# With text
curl -X POST http://localhost:8000/parse \
  -F "cv_text=John Doe\nSoftware Engineer\n..."
```

---

### 5. ATS Score Evaluation

**POST** `/ats-score`

Evaluate ATS (Applicant Tracking System) compatibility score.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content
- `jd_file` (file, optional): Job description file
- `jd_text` (string, optional): Job description text

**Examples:**

```bash
# CV file only
curl -X POST http://localhost:8000/ats-score \
  -F "cv_file=@resume.pdf"

# CV file + JD text
curl -X POST http://localhost:8000/ats-score \
  -F "cv_file=@resume.pdf" \
  -F "jd_text=Senior Data Scientist with ML experience..."

# CV text + JD file
curl -X POST http://localhost:8000/ats-score \
  -F "cv_text=John Doe, Data Scientist..." \
  -F "jd_file=@job_posting.pdf"
```

---

### 6. Compare CV with Job Description

**POST** `/compare`

Compare CV against a job description to identify matches and gaps.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content
- `jd_file` (file, optional): Job description file
- `jd_text` (string, optional): Job description text

**Note:** At least one CV input AND one JD input are required.

**Examples:**

```bash
# CV file + JD text
curl -X POST http://localhost:8000/compare \
  -F "cv_file=@resume.pdf" \
  -F "jd_text=We need a senior developer with Python, AWS, and leadership skills"

# CV text + JD file
curl -X POST http://localhost:8000/compare \
  -F "cv_text=John Doe, Software Engineer..." \
  -F "jd_file=@job_description.pdf"

# Both files
curl -X POST http://localhost:8000/compare \
  -F "cv_file=@resume.pdf" \
  -F "jd_file=@job_description.pdf"
```

---

### 7. Extract Keywords

**POST** `/keywords`

Extract important keywords from a CV.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content
- `top_n` (integer, optional): Number of keywords to extract (default: 25)

**Examples:**

```bash
# Extract from file
curl -X POST http://localhost:8000/keywords \
  -F "cv_file=@resume.pdf" \
  -F "top_n=30"

# Extract from text
curl -X POST http://localhost:8000/keywords \
  -F "cv_text=John Doe, Software Engineer..." \
  -F "top_n=20"
```

---

### 8. Analyze Issues

**POST** `/analyze-issues`

Analyze CV for issues categorized by severity.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content

**Examples:**

```bash
# Analyze file
curl -X POST http://localhost:8000/analyze-issues \
  -F "cv_file=@resume.pdf"

# Analyze text
curl -X POST http://localhost:8000/analyze-issues \
  -F "cv_text=John Doe, Software Engineer..."
```

---

### 9. Rewrite CV

**POST** `/rewrite`

Generate an improved, ATS-optimized version of the CV.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content
- `jd_file` (file, optional): Job description file to tailor to
- `jd_text` (string, optional): Job description text to tailor to
- `focus_areas` (string, optional): Comma-separated focus areas (e.g., "achievements,keywords,formatting")

**Examples:**

```bash
# Rewrite CV file only
curl -X POST http://localhost:8000/rewrite \
  -F "cv_file=@resume.pdf"

# Rewrite with job description
curl -X POST http://localhost:8000/rewrite \
  -F "cv_file=@resume.pdf" \
  -F "jd_text=Senior Python Developer position..." \
  -F "focus_areas=achievements,keywords,impact"

# Rewrite text with JD file
curl -X POST http://localhost:8000/rewrite \
  -F "cv_text=John Doe, Software Engineer..." \
  -F "jd_file=@job_description.pdf"
```

---

### 10. Generate Improvement Plan

**POST** `/improvement-plan`

Create a prioritized, actionable improvement roadmap for a CV.

**Parameters:**
- `cv_file` (file, optional): CV file upload
- `cv_text` (string, optional): CV text content

**Examples:**

```bash
# Generate plan from file
curl -X POST http://localhost:8000/improvement-plan \
  -F "cv_file=@resume.pdf"

# Generate plan from text
curl -X POST http://localhost:8000/improvement-plan \
  -F "cv_text=John Doe, Software Engineer..."
```

---

## Python Client Examples

```python
import requests

BASE_URL = "http://localhost:8000"

# Example 1: Analyze CV file only
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/analyze",
        files={"cv_file": f}
    )
    print(response.json())

# Example 2: Analyze CV file with JD text
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/analyze",
        files={"cv_file": f},
        data={"jd_text": "Looking for a senior developer with Python and AWS experience"}
    )
    print(response.json())

# Example 3: Analyze CV text
response = requests.post(
    f"{BASE_URL}/analyze",
    data={"cv_text": "John Doe\nSoftware Engineer\n5 years experience..."}
)
print(response.json())

# Example 4: Compare CV file with JD text
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/compare",
        files={"cv_file": f},
        data={"jd_text": "Senior Backend Developer - Python, AWS, SQL"}
    )
    print(response.json())

# Example 5: Get ATS score with both files
with open("resume.pdf", "rb") as cv_f, open("job_description.pdf", "rb") as jd_f:
    response = requests.post(
        f"{BASE_URL}/ats-score",
        files={"cv_file": cv_f, "jd_file": jd_f}
    )
    print(response.json())

# Example 6: Parse CV text
response = requests.post(
    f"{BASE_URL}/parse",
    data={"cv_text": "John Doe\nSoftware Engineer\n..."}
)
print(response.json())

# Example 7: Extract keywords from file
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/keywords",
        files={"cv_file": f},
        data={"top_n": 30}
    )
    print(response.json())

# Example 8: Rewrite CV with job description
with open("resume.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/rewrite",
        files={"cv_file": f},
        data={
            "jd_text": "Senior ML Engineer position...",
            "focus_areas": "achievements,keywords,impact"
        }
    )
    print(response.json())

# Example 9: Chat with agent
response = requests.post(
    f"{BASE_URL}/chat",
    json={"message": "What are the best practices for technical resumes?"}
)
print(response.json())
```

---

## JavaScript/Fetch Examples

```javascript
const BASE_URL = 'http://localhost:8000';

// Example 1: Analyze CV file
const analyzeFile = async (file) => {
  const formData = new FormData();
  formData.append('cv_file', file);

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};

// Example 2: Analyze CV file with JD text
const analyzeWithJD = async (cvFile, jdText) => {
  const formData = new FormData();
  formData.append('cv_file', cvFile);
  formData.append('jd_text', jdText);

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};

// Example 3: Analyze CV text
const analyzeText = async (cvText) => {
  const formData = new FormData();
  formData.append('cv_text', cvText);

  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};

// Example 4: Get ATS score with CV file and JD text
const getATSScore = async (cvFile, jdText) => {
  const formData = new FormData();
  formData.append('cv_file', cvFile);
  if (jdText) {
    formData.append('jd_text', jdText);
  }

  const response = await fetch(`${BASE_URL}/ats-score`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};

// Example 5: Compare with both files
const compareFiles = async (cvFile, jdFile) => {
  const formData = new FormData();
  formData.append('cv_file', cvFile);
  formData.append('jd_file', jdFile);

  const response = await fetch(`${BASE_URL}/compare`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};

// Example 6: Rewrite CV with options
const rewriteCV = async (cvFile, jdText, focusAreas) => {
  const formData = new FormData();
  formData.append('cv_file', cvFile);
  if (jdText) {
    formData.append('jd_text', jdText);
  }
  if (focusAreas) {
    formData.append('focus_areas', focusAreas);
  }

  const response = await fetch(`${BASE_URL}/rewrite`, {
    method: 'POST',
    body: formData
  });
  const data = await response.json();
  console.log(data);
};
```

---

## Response Format

All endpoints return JSON responses with the following structure:

**Success Response:**
```json
{
  "success": true,
  "cv_input_type": "file",
  "cv_filename": "resume.pdf",
  "jd_input_type": "text",
  "analysis": "AI-generated analysis..."
}
```

**Fields:**
- `success` (boolean): Whether the request was successful
- `cv_input_type` (string): "file" or "text" - indicates CV input type
- `cv_filename` (string): Filename (only present when cv_input_type is "file")
- `jd_input_type` (string): "file", "text", or null - indicates JD input type
- `jd_filename` (string): JD filename (only present when jd_input_type is "file")
- Response content fields vary by endpoint: `analysis`, `parsed_data`, `ats_evaluation`, `comparison`, `keywords`, `issues`, `rewritten_cv`, `improvement_plan`

**Error Response:**
```json
{
  "detail": "Error message description"
}
```

---

## Common HTTP Status Codes

- `200`: Success
- `400`: Bad Request (missing required parameters, invalid file type)
- `422`: Unprocessable Content (validation error)
- `500`: Internal Server Error (processing failed)
- `503`: Service Unavailable (agent not initialized)

---

## Environment Variables

Make sure your `.env` file contains:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

## Tips for Using Swagger UI

When using the interactive docs at http://localhost:8000/docs:

1. **Only fill in the fields you want to use** - leave others completely empty
2. **For file uploads**: Click "Choose File" and select your file
3. **For text inputs**: Type or paste your content
4. **Optional fields**: Can be left empty without issues
5. **Don't send both file and text** for the same input (CV or JD)

---

## Production Deployment

For production deployment, consider:

1. **Security**: Configure CORS properly (update `allow_origins` in [api.py](api.py))
2. **HTTPS**: Use a reverse proxy like Nginx with SSL certificates
3. **Rate Limiting**: Add rate limiting middleware
4. **Authentication**: Add API key authentication
5. **Monitoring**: Add logging and error tracking
6. **Scalability**: Use multiple workers with gunicorn:

```bash
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t resume-agent-api .
docker run -p 8000:8000 --env-file .env resume-agent-api
```
