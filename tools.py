from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenRouter client
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise RuntimeError("Missing OpenRouter API key")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)


def parse_cv(cv_content: str) -> str:
    """
    Parse CV/Resume using LLM to extract structured information.

    Args:
        cv_content: The CV text content to parse

    Returns:
        Structured parsing results from LLM
    """
    prompt = f"""
    Analyze the following CV/Resume and extract structured information in JSON format.

    Extract the following sections:
    - Contact Information (name, email, phone, LinkedIn, location)
    - Professional Summary/Objective
    - Work Experience (company, role, duration, responsibilities, achievements)
    - Education (institution, degree, year, GPA if mentioned)
    - Skills (technical skills, soft skills, tools, languages)
    - Certifications and Licenses
    - Projects (if any)
    - Additional sections (awards, publications, volunteer work, etc.)

    CV Content:
    {cv_content}

    Provide a comprehensive structured analysis in JSON format.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert CV parser. Extract information accurately and return valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def extract_keywords(text: str, top_n: int = 20) -> str:
    """
    Extract important keywords from text using LLM analysis.

    Args:
        text: Text to extract keywords from
        top_n: Number of top keywords to return

    Returns:
        List of keywords with relevance analysis
    """
    prompt = f"""
    Analyze the following text and extract the top {top_n} most important keywords and key phrases.

    Focus on:
    - Technical skills and tools
    - Industry-specific terminology
    - Action verbs and accomplishments
    - Certifications and qualifications
    - Domain expertise indicators

    Rank them by importance and relevance for job matching and ATS systems.

    Text:
    {text}

    Return a JSON array with keywords, their category (skill/tool/action/domain), and importance score.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert in keyword extraction for resumes and job descriptions. Focus on ATS-relevant terms."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def compare_cv_with_job(cv_content: str, job_description: str) -> str:
    """
    Compare CV against job description using LLM to identify matches and gaps.

    Args:
        cv_content: CV text content
        job_description: Job description text

    Returns:
        Detailed comparison analysis
    """
    prompt = f"""
    Compare the following CV with the Job Description and provide a comprehensive analysis.

    Analyze:
    1. Keyword Match - Which required keywords from the job description are present/missing in the CV
    2. Skills Match - Technical and soft skills alignment
    3. Experience Match - How well the experience aligns with job requirements
    4. Qualification Match - Education and certification requirements
    5. Overall Fit Score (0-100)
    6. Specific recommendations to improve match

    CV:
    {cv_content}

    Job Description:
    {job_description}

    Provide detailed analysis in JSON format with specific examples and actionable recommendations.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert recruiter and ATS specialist. Provide detailed, actionable matching analysis."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2000
    )

    return response.choices[0].message.content


def evaluate_ats_score(cv_content: str, job_description: str = None) -> str:
    """
    Evaluate ATS (Applicant Tracking System) compatibility using LLM.

    Args:
        cv_content: CV text content
        job_description: Optional job description for context

    Returns:
        Comprehensive ATS evaluation with score and recommendations
    """
    jd_context = f"\n\nJob Description for context:\n{job_description}" if job_description else ""

    prompt = f"""
    Evaluate the following CV for ATS (Applicant Tracking System) compatibility.

    Analyze these critical areas:

    1. **Structure & Formatting** (0-25 points)
       - Proper section headers
       - Logical organization
       - Clean formatting for parsing

    2. **Contact Information** (0-15 points)
       - Email, phone, location present
       - Professional profiles (LinkedIn)

    3. **Keywords & Content** (0-30 points)
       - Industry-relevant keywords
       - Action verbs and achievements
       - Quantifiable results

    4. **Completeness** (0-20 points)
       - All essential sections present
       - Sufficient detail in each section

    5. **Job Match** (0-10 points)
       - Alignment with job requirements (if job description provided)

    CV Content:
    {cv_content}
    {jd_context}

    Provide:
    - Overall ATS Score (0-100)
    - Score breakdown for each area
    - Specific issues found
    - Detailed recommendations for improvement
    - Priority ranking of fixes (Critical/High/Medium/Low)

    Return analysis in JSON format.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an ATS (Applicant Tracking System) expert. Evaluate resumes thoroughly and provide actionable feedback."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2500
    )

    return response.choices[0].message.content


def analyze_cv_issues(cv_content: str) -> str:
    """
    Deep analysis of CV to identify all issues and improvement areas using LLM.

    Args:
        cv_content: CV text content

    Returns:
        Comprehensive issue analysis with categorized problems
    """
    prompt = f"""
    Perform a comprehensive analysis of this CV to identify all issues and areas for improvement.

    Categorize issues into:

    1. **Critical Issues** (Must fix immediately)
       - Missing essential information
       - Major formatting problems
       - ATS-blocking issues

    2. **Major Issues** (Important to fix)
       - Weak content areas
       - Missing key sections
       - Poor keyword optimization

    3. **Minor Issues** (Good to improve)
       - Formatting inconsistencies
       - Wording improvements
       - Organization tweaks

    4. **Suggestions** (Enhancement opportunities)
       - Additional sections to add
       - Content enrichment ideas
       - Modern best practices

    CV Content:
    {cv_content}

    For each issue:
    - Clearly describe the problem
    - Explain why it matters
    - Provide specific fix recommendations
    - Show before/after examples where applicable

    Return comprehensive analysis in JSON format.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a professional resume writer and career coach. Identify issues comprehensively and provide actionable solutions."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=2500
    )

    return response.choices[0].message.content


def generate_cv_rewrite(cv_content: str, job_description: str = None, focus_areas: str = None) -> str:
    """
    Generate rewritten/improved version of CV using LLM.

    Args:
        cv_content: Original CV text content
        job_description: Optional job description to tailor CV
        focus_areas: Specific areas to focus improvement on

    Returns:
        Rewritten CV with improvements and explanation of changes
    """
    jd_context = f"\n\nTailor the CV for this job:\n{job_description}" if job_description else ""
    focus_context = f"\n\nFocus especially on: {focus_areas}" if focus_areas else ""

    prompt = f"""
    Rewrite and improve the following CV to make it more effective and ATS-friendly.

    Improvements to make:
    1. Strengthen action verbs and quantify achievements
    2. Optimize keywords for ATS
    3. Improve structure and formatting
    4. Enhance professional summary
    5. Refine experience descriptions
    6. Better showcase skills and accomplishments
    {jd_context}
    {focus_context}

    Original CV:
    {cv_content}

    Provide:
    1. Complete rewritten CV in professional format
    2. Summary of key changes made
    3. Explanation of improvements and why they matter
    4. Before/after comparison for major sections

    Return in JSON format with separate fields for the rewritten CV and change explanations.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are an expert resume writer with 15+ years experience. Create compelling, ATS-optimized resumes that get interviews."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=3500
    )

    return response.choices[0].message.content


def generate_improvement_plan(cv_content: str, job_description: str = None) -> str:
    """
    Generate comprehensive improvement plan for CV using LLM.

    Args:
        cv_content: CV text content
        job_description: Optional job description for context

    Returns:
        Detailed step-by-step improvement plan
    """
    jd_context = f"\n\nJob Description:\n{job_description}" if job_description else ""

    prompt = f"""
    Create a comprehensive, prioritized improvement plan for this CV.

    CV Content:
    {cv_content}
    {jd_context}

    Provide a step-by-step plan that includes:

    1. **Quick Wins** (0-30 minutes)
       - Immediate fixes that have high impact

    2. **Essential Improvements** (30 min - 2 hours)
       - Important changes to content and structure

    3. **Advanced Optimization** (2-4 hours)
       - Deep improvements and tailoring

    4. **Long-term Enhancements** (ongoing)
       - Skills to develop, experiences to gain

    For each improvement:
    - Specific action to take
    - Expected impact (High/Medium/Low)
    - Time required
    - Detailed instructions
    - Examples where helpful

    Also provide:
    - Current CV strength score (0-100)
    - Projected score after improvements
    - Priority ranking of all improvements

    Return detailed plan in JSON format.
    """

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "You are a career coach and resume expert. Create actionable, prioritized improvement plans."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=3000
    )

    return response.choices[0].message.content
