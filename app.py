import streamlit as st
import PyPDF2
import io
import os
import re
from groq import Groq
from dotenv import load_dotenv

# ================== CONFIG ==================
load_dotenv()

st.set_page_config(
    page_title="AI RESUME ANALYZER",
    page_icon="📃",
    layout="centered"
)

# ================== TITLE ==================
st.title("📄 AI Resume ANALYZER")
st.markdown("Upload your resume and get **AI-powered feedback, ATS score & recommendations** 🚀")

# ================== SIDEBAR ==================
st.sidebar.header("⚙️ Settings")
job_role = st.sidebar.text_input("Target Job Role (optional)")
analyze = st.sidebar.button("Analyze Resume")

# ================== FILE UPLOAD ==================
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])

# ================== API ==================
GROQ_API_KEY = "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"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ================== FUNCTIONS ==================
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

# -------- ATS SCORE FUNCTION --------
def calculate_ats_score(resume_text, job_role):
    common_skills = [
        "python","sql","java","machine learning","data analysis",
        "deep learning","excel","power bi","tableau",
        "communication","teamwork","problem solving",
        "html","css","javascript","react","flask","django"
    ]

    resume_text_lower = resume_text.lower()
    matched_skills = [skill for skill in common_skills if skill in resume_text_lower]

    skill_score = min(len(matched_skills) * 4, 40)  # max 40
    length_score = 20 if len(resume_text.split()) > 300 else 10
    role_score = 20 if job_role and job_role.lower() in resume_text_lower else 10

    ats_score = skill_score + length_score + role_score
    return min(ats_score, 100), matched_skills

# ================== MAIN LOGIC ==================
if analyze and uploaded_file:
    try:
        with st.spinner("🔍 Analyzing your resume..."):
            file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not have any content.")
            st.stop()

        # ================== ATS SCORE ==================
        ats_score, matched_skills = calculate_ats_score(file_content, job_role)

        st.subheader("📊 ATS Compatibility Score")
        st.progress(ats_score / 100)
        st.metric("ATS Score", f"{ats_score}/100")

        col1, col2 = st.columns(2)
        col1.metric("Resume Length (words)", len(file_content.split()))
        col2.metric("Matched Skills", len(matched_skills))

        # ================== SKILLS ==================
        st.subheader("✅ Detected Skills")
        if matched_skills:
            st.write(", ".join(matched_skills))
        else:
            st.warning("No common skills detected. Consider adding technical & soft skills.")

        # ================== AI ANALYSIS ==================
        prompt = f"""
        Please analyze this resume and provide constructive feedback.

        Focus on:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience description
        4. ATS optimization tips
        5. Improvements for {job_role if job_role else 'general job applications'}

        Resume:
        {file_content}

        Provide clear sections and bullet points.
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer and ATS specialist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )

        # ================== RESULTS ==================
        st.subheader("🧠 AI Resume Analysis")
        st.markdown(response.choices[0].message.content)

        # ================== RECOMMENDATIONS ==================
        st.subheader("🚀 Personalized Recommendations")

        recommendations = []
        if ats_score < 60:
            recommendations.append("Improve keyword optimization to increase ATS score.")
        if len(matched_skills) < 5:
            recommendations.append("Add more relevant technical and soft skills.")
        if len(file_content.split()) < 300:
            recommendations.append("Resume is too short. Add more experience details.")
        if job_role and job_role.lower() not in file_content.lower():
            recommendations.append("Mention your target job role explicitly.")

        for rec in recommendations:
            st.write("✔️", rec)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
