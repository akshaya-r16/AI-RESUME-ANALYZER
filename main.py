import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI RESUME ANALYZER", page_icon="📃", layout="centered")

# Custom CSS for background color
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 8px;
    }
    
    .stFileUploader>div>div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }
    
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .stMarkdown {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("AI Resume Critiquer")
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
