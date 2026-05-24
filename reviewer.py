import os
import PyPDF2
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

# ── Extract text from PDF ─────────────────────────────────────────────────────
def extract_text_from_pdf(pdf_file) -> str:
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# ── Review the resume ─────────────────────────────────────────────────────────
def review_resume(pdf_file, job_role: str = "Software Engineer") -> dict:
    try:
        # Step 1: Extract text
        resume_text = extract_text_from_pdf(pdf_file)

        if not resume_text or len(resume_text) < 50:
            return {
                "success": False,
                "error": "Could not extract text from PDF. Make sure it's not a scanned image."
            }

        # Step 2: Setup LLM
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Step 3: Build prompt
        prompt = PromptTemplate.from_template("""
You are an expert HR professional and resume coach with 15 years of experience.
Analyze the following resume for a {job_role} position.

RESUME:
{resume_text}

Provide a detailed review in the following EXACT format:

OVERALL_SCORE: [give a score out of 10]

SUMMARY: [2-3 sentence overall impression]

STRENGTHS:
- [strength 1]
- [strength 2]
- [strength 3]

WEAKNESSES:
- [weakness 1]
- [weakness 2]
- [weakness 3]

MISSING_SECTIONS:
- [missing section 1]
- [missing section 2]

ATS_SCORE: [score out of 10 for ATS compatibility]
ATS_FEEDBACK: [one paragraph about ATS optimization]

IMPROVEMENTS:
- [specific improvement 1]
- [specific improvement 2]
- [specific improvement 3]
- [specific improvement 4]
- [specific improvement 5]

VERDICT: [one final motivating sentence]
""")

        # Step 4: Call LLM
        chain = prompt | llm
        response = chain.invoke({
            "job_role": job_role,
            "resume_text": resume_text[:4000]  # limit tokens
        })

        raw_output = response.content

        # Step 5: Parse the response
        result = parse_review(raw_output)
        result["success"] = True
        result["raw"] = raw_output
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ── Parse the structured response ────────────────────────────────────────────
def parse_review(text: str) -> dict:
    def extract_section(label, text):
        try:
            start = text.find(label + ":")
            if start == -1:
                return ""
            start += len(label) + 1
            end = text.find("\n\n", start)
            if end == -1:
                end = len(text)
            return text[start:end].strip()
        except:
            return ""

    def extract_list(label, text):
        section = extract_section(label, text)
        items = [line.strip("- ").strip()
                 for line in section.split("\n")
                 if line.strip().startswith("-")]
        return items

    return {
        "overall_score": extract_section("OVERALL_SCORE", text),
        "summary": extract_section("SUMMARY", text),
        "strengths": extract_list("STRENGTHS", text),
        "weaknesses": extract_list("WEAKNESSES", text),
        "missing_sections": extract_list("MISSING_SECTIONS", text),
        "ats_score": extract_section("ATS_SCORE", text),
        "ats_feedback": extract_section("ATS_FEEDBACK", text),
        "improvements": extract_list("IMPROVEMENTS", text),
        "verdict": extract_section("VERDICT", text),
    }


# ── Quick test ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("reviewer.py loaded successfully!")
    print("Run: streamlit run app.py")