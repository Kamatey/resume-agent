# Resume/CV Analysis & Optimization Agent

An AI-powered resume analysis agent that uses LLM models to provide comprehensive CV evaluation, ATS scoring, keyword optimization, and intelligent rewriting.

## Features

### 1. **CV Parsing**
Automatically extracts and structures all information from resumes:
- Contact information (name, email, phone, LinkedIn)
- Professional summary/objective
- Work experience with achievements
- Education and certifications
- Skills (technical and soft)
- Projects and additional sections

### 2. **Keyword Generation**
Identifies critical keywords for ATS optimization:
- Technical skills and tools
- Industry-specific terminology
- Action verbs and accomplishments
- Domain expertise indicators
- Ranked by importance for job matching

### 3. **ATS Evaluation**
Scores resumes for Applicant Tracking System compatibility (0-100):
- Structure & Formatting (25 points)
- Contact Information (15 points)
- Keywords & Content (30 points)
- Completeness (20 points)
- Job Match (10 points)

Provides detailed breakdown and specific recommendations.

### 4. **Job Matching**
Compares CV against job descriptions:
- Keyword match analysis
- Skills alignment assessment
- Experience relevance scoring
- Qualification matching
- Overall fit score with recommendations

### 5. **Issue Analysis**
Deep dive into CV problems with categorization:
- **Critical Issues**: Must fix immediately
- **Major Issues**: Important improvements
- **Minor Issues**: Good to enhance
- **Suggestions**: Enhancement opportunities

### 6. **CV Rewriting**
AI-powered resume improvements:
- Strengthens action verbs
- Quantifies achievements
- Optimizes keywords for ATS
- Improves structure and formatting
- Tailors to specific job descriptions

### 7. **Improvement Plans**
Creates actionable roadmaps:
- Quick wins (0-30 minutes)
- Essential improvements (30 min - 2 hours)
- Advanced optimization (2-4 hours)
- Long-term enhancements (ongoing)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Run the agent:
```bash
python agent.py
```

The agent supports **two input modes**:
1. **Pasted Text** - Copy/paste CV or job description directly
2. **File Upload** - Upload PDF, DOCX, or TXT files

---

### Method 1: Pasted Text Input

Simply paste your CV or job description text directly into the chat:

**Example 1: Analyze a CV**
```
You: Analyze my CV:

[Paste your CV text here]
```

**Example 2: Get ATS Score**
```
You: Evaluate my resume for ATS compatibility

[Paste your CV]
```

**Example 3: Compare with Job Description**
```
You: Compare my CV against this job description:

CV: [Your CV text]

Job Description: [Job posting text]
```

**Example 4: Extract Keywords**
```
You: Extract the top 30 keywords from this job description:

[Paste job description]
```

---

### Method 2: File Upload

The agent **automatically detects file paths** in your input! You can:

**Option A: Just paste the file path**
```
You: C:\Users\Username\Downloads\Malik_Yussif_CV.pdf
```

**Option B: Include file path with your request**
```
You: C:\Users\Username\Downloads\resume.pdf compare with the job description: [paste JD]
```

**Supported file formats:** PDF, DOCX, DOC, TXT

---


### Example Workflows

**Workflow 1: Quick ATS Check**
```
You: file:my_resume.pdf
[Choose option 2: Evaluate ATS score]
```

**Workflow 2: Compare Against Job**
```
You: file:my_resume.pdf
[Choose option 5: Custom request]
Enter your request: Compare this CV against the following job description:
[Paste job description]
```

**Workflow 3: Full Analysis & Rewrite**
```
You: file:my_resume.pdf
[Choose option 3: Analyze for issues]

You: Based on the issues found, rewrite my CV to fix them and optimize for this job:
[Paste job description]
```


### Tools Available

- `parse_cv()` - Extract structured information from CV
- `extract_keywords()` - Identify important keywords
- `compare_cv_with_job()` - Match CV against job description
- `evaluate_ats_score()` - Score ATS compatibility
- `analyze_cv_issues()` - Deep issue analysis
- `generate_cv_rewrite()` - Rewrite and improve CV
- `generate_improvement_plan()` - Create action roadmap



## Project Structure

```
resume-agent/
├── agent.py              # Main agent application (CLI with file upload support)
├── tools.py              # LLM-powered analysis tools (7 tools)
├── requirements.txt      # Python dependencies
├── .env                  # API keys (create this)
└── README.md            # This file
```

