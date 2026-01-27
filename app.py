import streamlit as st
import PyPDF2
import io
import os
import re
from groq import Groq
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #4facfe, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}
.sub-text {
    text-align: center;
    color: #6c757d;
    font-size: 16px;
}
.card {
    background-color: #ffffff10;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.section-title {
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='main-title'>AI Resume Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>ATS Score • AI Feedback • Smart Recommendations</div>", unsafe_allow_html=True)
st.write("")

# ================= GROQ API =================
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ================= INPUT SECTION =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📂 Upload Resume</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF or TXT)",
    type=["pdf", "txt"]
)

st.markdown("<div class='section-title'>📄 Job Description</div>", unsafe_allow_html=True)
job_role = st.text_area(
    "Paste the Job Description or Target Role",
    height=120,
    placeholder="Example: Data Scientist with Python, SQL, ML experience..."
)

analyze = st.button("🚀 Analyze Resume")
st.markdown("</div>", unsafe_allow_html=True)

# ================= FUNCTIONS =================
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

def calculate_ats_score(resume_text, job_desc):
    keywords = [
        "python","sql","machine learning","data analysis","deep learning",
        "excel","power bi","tableau","communication","teamwork",
        "problem solving","flask","django","react","api"
    ]

    resume = resume_text.lower()
    matched = [k for k in keywords if k in resume]

    skill_score = min(len(matched) * 4, 40)
    length_score = 20 if len(resume_text.split()) > 300 else 10
    jd_score = 20 if job_desc and any(word in resume for word in job_desc.lower().split()) else 10

    total = skill_score + length_score + jd_score
    return min(total, 100), matched

# ================= MAIN LOGIC =================
if analyze and uploaded_file:
    try:
        with st.spinner("🔍 Analyzing your resume..."):
            resume_text = extract_text_from_file(uploaded_file)

        if not resume_text.strip():
            st.error("Resume content is empty.")
            st.stop()

        # ================= ATS DASHBOARD =================
        ats_score, matched_skills = calculate_ats_score(resume_text, job_role)

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📊 ATS Dashboard</div>", unsafe_allow_html=True)

        st.progress(ats_score / 100)
        col1, col2, col3 = st.columns(3)
        col1.metric("ATS Score", f"{ats_score}/100")
        col2.metric("Resume Words", len(resume_text.split()))
        col3.metric("Matched Skills", len(matched_skills))

        st.markdown("</div>", unsafe_allow_html=True)

        # ================= SKILLS =================
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>✅ Detected Skills</div>", unsafe_allow_html=True)
        if matched_skills:
            st.write(", ".join(matched_skills))
        else:
            st.warning("No major ATS keywords detected.")
        st.markdown("</div>", unsafe_allow_html=True)

        # ================= AI ANALYSIS =================
        prompt = f"""
        Analyze the resume and give:
        1. Strengths
        2. Weaknesses
        3. ATS optimization tips
        4. Skill gaps
        5. Improvements based on job description

        Job Description:
        {job_role}

        Resume:
        {resume_text}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert ATS resume reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1200
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🧠 AI Resume Feedback</div>", unsafe_allow_html=True)
        st.markdown(response.choices[0].message.content)
        st.markdown("</div>", unsafe_allow_html=True)

        # ================= RECOMMENDATIONS =================
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>🚀 Recommendations</div>", unsafe_allow_html=True)

        if ats_score < 60:
            st.write("✔️ Improve keyword matching with job description")
        if len(matched_skills) < 5:
            st.write("✔️ Add more technical and soft skills")
        if len(resume_text.split()) < 300:
            st.write("✔️ Resume is short, expand experience details")

        st.markdown("</div>", unsafe_allow_html=True)

        # ================= PREVIEW =================
        with st.expander("📄 View Extracted Resume Text"):
            st.text(resume_text[:4000])

    except Exception as e:
        st.error(f"Error: {str(e)}")
