from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.media import File
from dotenv import load_dotenv
import os
import asyncio
import sys
from tools import (
    parse_cv,
    extract_keywords,
    compare_cv_with_job,
    evaluate_ats_score,
    analyze_cv_issues,
    generate_cv_rewrite,
    generate_improvement_plan
)

# Set Windows-specific event loop policy to handle file descriptors better
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise RuntimeError("Missing OpenRouter API key. Set OPENROUTER_API_KEY in environment or .env file")


async def create_agent():
    return Agent(
        model=OpenRouter(id="google/gemini-2.5-flash", api_key=OPENROUTER_API_KEY, max_tokens=4000),
        add_history_to_context=True,
        markdown=True,
        tools=[
            parse_cv,
            extract_keywords,
            compare_cv_with_job,
            evaluate_ats_score,
            analyze_cv_issues,
            generate_cv_rewrite,
            generate_improvement_plan
        ],
        instructions=[
            """
            You are an expert Resume/CV Analysis and Optimization Agent powered by advanced AI models.

            **Your Core Capabilities:**

            1. **CV Parsing** - Extract and structure all information from resumes
               - Contact details, work experience, education, skills, certifications
               - Use parse_cv tool for comprehensive extraction

            2. **Keyword Generation** - Identify critical keywords for ATS optimization
               - Extract keywords from CVs and job descriptions
               - Use extract_keywords tool with appropriate top_n parameter

            3. **ATS Evaluation** - Score resumes for Applicant Tracking System compatibility
               - Evaluate structure, formatting, keywords, content quality
               - Provide scores out of 100 with detailed breakdowns
               - Use evaluate_ats_score tool (with or without job description)

            4. **Job Matching** - Compare CVs against job descriptions
               - Identify matching and missing keywords
               - Analyze skills, experience, and qualification alignment
               - Provide fit scores and specific recommendations
               - Use compare_cv_with_job tool

            5. **Issue Analysis** - Deep dive into CV problems
               - Categorize issues: Critical, Major, Minor, Suggestions
               - Provide specific fixes with examples
               - Use analyze_cv_issues tool

            6. **CV Rewriting** - Generate improved versions of CVs
               - Optimize for ATS while maintaining readability
               - Strengthen language and quantify achievements
               - Tailor to specific job descriptions
               - Use generate_cv_rewrite tool (optionally with job_description and focus_areas)

            7. **Improvement Planning** - Create actionable roadmaps
               - Prioritized steps from quick wins to long-term enhancements
               - Time estimates and impact assessment
               - Use generate_improvement_plan tool

            **How to Handle Files:**
            When users provide file paths (PDF, DOCX, TXT):
            - Files are automatically extracted by the system
            - You'll receive the text content to analyze
            - Use the appropriate tools on the extracted text

            **Best Practices:**
            - Always use the LLM-powered tools for analysis (they provide comprehensive AI-driven insights)
            - Combine multiple tools for thorough analysis when needed
            - Present results clearly with specific, actionable recommendations
            - When comparing with job descriptions, use compare_cv_with_job for best results
            - For rewriting requests, ask if there's a specific job description to tailor to
            - Provide both analysis AND actionable next steps

            **Response Format:**
            - Present tool outputs in a clear, organized manner
            - Highlight key findings and scores
            - Prioritize recommendations by impact
            - Use markdown formatting for readability
            - Be encouraging but honest about areas needing improvement

            Remember: All analysis is powered by advanced AI models, ensuring accurate,
            context-aware insights rather than simple rule-based matching.
            """
        ],
    )

if __name__ == "__main__":
    # Create the agent instance
    agent = asyncio.run(create_agent())

    
    while True:
        user_input = input("\n💼 You: ")

        # Check if user wants to exit
        if user_input.lower().strip() in ['quit', 'exit', 'bye', 'q']:
            print("\n✨ Thank you for using Resume Agent! Best of luck with your applications!")
            break

        # Skip empty inputs
        if not user_input.strip():
            continue

        # Auto-detect file paths in the input (look for .pdf, .docx, .doc, .txt extensions)
        import re
        file_path_pattern = r'([A-Za-z]:\\[^:\*\?"<>\|]+\.(pdf|docx|doc|txt)|[^\s]+\.(pdf|docx|doc|txt))'
        file_matches = re.findall(file_path_pattern, user_input, re.IGNORECASE)

        detected_file = None
        remaining_text = user_input

        if file_matches:
            # Extract the first valid file path
            for match in file_matches:
                potential_path = match[0]
                if os.path.exists(potential_path):
                    detected_file = potential_path
                    # Remove the file path from the input to get remaining text
                    remaining_text = user_input.replace(potential_path, '').strip()
                    break

        # Handle file detection
        if detected_file or user_input.strip().lower().startswith('file:'):
            # Get the file path
            if user_input.strip().lower().startswith('file:'):
                file_path = user_input[5:].strip()
                remaining_text = ""
            else:
                file_path = detected_file

            # Validate file exists
            if not os.path.exists(file_path):
                print(f"\n❌ Error: File not found at '{file_path}'")
                print("Please check the path and try again.")
                continue

            # Get file extension
            file_ext = os.path.splitext(file_path)[1].lower()
            supported_formats = ['.pdf', '.docx', '.doc', '.txt']

            if file_ext not in supported_formats:
                print(f"\n⚠️  Warning: File type '{file_ext}' may not be fully supported.")
                print(f"Supported formats: {', '.join(supported_formats)}")
                proceed = input("Continue anyway? (y/n): ")
                if proceed.lower() != 'y':
                    continue

            print(f"\n📄 Detected file: {os.path.basename(file_path)}")

            # If there's remaining text (like a job description), use it as the prompt
            if remaining_text:
                # Clean up the remaining text
                prompt = remaining_text.strip()
                print(f"📝 Request: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
            else:
                # Ask user what to do with the file
                print("What would you like me to do with this file?")
                print("  1. Parse CV and extract information")
                print("  2. Evaluate ATS score")
                print("  3. Analyze for issues")
                print("  4. Extract keywords")
                print("  5. Custom request (type your own)")

                action = input("\nYour choice (1-5): ").strip()

                # Map choices to prompts
                prompts = {
                    '1': "Parse this CV and extract all structured information in detail.",
                    '2': "Evaluate this CV for ATS compatibility and provide a detailed score with recommendations.",
                    '3': "Analyze this CV comprehensively and identify all issues categorized by severity.",
                    '4': "Extract the top 25 most important keywords from this document.",
                    '5': None  # Custom
                }

                if action == '5':
                    custom_prompt = input("Enter your request: ").strip()
                    if not custom_prompt:
                        print("No request provided. Skipping...")
                        continue
                    prompt = custom_prompt
                elif action in prompts:
                    prompt = prompts[action]
                else:
                    print("Invalid choice. Using default analysis.")
                    prompt = "Analyze this CV comprehensively."

            # Process file with agent
            print("\n🤖 Agent: ", end="")
            try:
                agent.print_response(
                    prompt,
                    files=[File(filepath=file_path)],
                    stream=True
                )
                print()
            except Exception as e:
                print(f"\n❌ Error processing file: {str(e)}")
                print("Please check the file format and try again.")

        else:
            # Regular text input - process normally
            print("\n🤖 Agent: ", end="")
            agent.print_response(user_input, stream=True)
            print()  # Add spacing between conversations
