import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(page_title="AI RESUME ANALYZER", page_icon="📃", layout="centered")
st.set_page_config(
    page_title="My App",
    layout="centered",
    initial_sidebar_state="auto"
)
st.markdown(
    """
    <style>
    /* Main app background */
    .stApp {
        background-color: #0f172a; /* dark slate */
        color: #e5e7eb;
        font-family: 'Segoe UI', sans-serif;
    }

    /* Title */
    h1 {
        text-align: center;
        color: #38bdf8;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Subtitle / description */
    .stMarkdown p {
        text-align: center;
        font-size: 16px;
        color: #cbd5f5;
        margin-bottom: 30px;
    }

    /* File uploader box */
    section[data-testid="stFileUploader"] {
        background-color: #020617;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }

    /* Text input */
    input {
        background-color: #020617 !important;
        color: #e5e7eb !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        padding: 10px !important;
    }

    /* Buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #38bdf8, #6366f1);
        color: white;
        font-size: 16px;
        font-weight: 600;
        padding: 10px 25px;
        border-radius: 10px;
        border: none;
        margin-top: 10px;
        width: 100%;
        transition: all 0.3s ease-in-out;
    }

    div.stButton > button:hover {
        transform: scale(1.02);
        background: linear-gradient(135deg, #6366f1, #38bdf8);
    }

    /* Analysis results card */
    .analysis-box {
        background-color: #020617;
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #1e293b;
        margin-top: 30px;
    }

    /* Headers inside result */
    h3 {
        color: #22d3ee;
    }

    /* Scrollbar (optional) */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Resume Analyzer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")
GROQ_API_KEY = "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"
GROQ_API_KEY= os.getenv("GROQ_API_KEY")
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role that you are targeting (optional).")
analyze = st.button("Analyze Resume")
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text=""
    for page in pdf_reader.pages:
        text+= page.extract_text() + '\n'
    return text
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")
if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()
        prompt = f"""Please analyze this resume and provide constructive feedback.
        Focus on the following aspects:
        1. Content clarity and impact
        2. Skills presentation
        3. Experience description
        4. Specific improvements for {job_role if job_role else 'general job applications'}
        Resume content:
        {file_content}
        Please provide your analysis in a clear, structured format with specific recommendations."""

        client = Groq(api_key="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")

        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": " You are an expert resume reviewer with years of experience in HR and recruitment"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        st.markdown("### Analysis Results")
        st.markdown(response.choices[0].message.content)
    except Exception as e:
        st.error(f"An error occured: {str(e)}")
