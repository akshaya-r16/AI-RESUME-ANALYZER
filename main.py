import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI RESUME ANALYZER", page_icon="📃", layout="centered")

# Custom CSS styling with better visibility and alignment
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Title styling - Better visibility */
    h1 {
        color: #ffffff !important;
        text-align: center;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 1rem;
    }
    
    /* Subtitle/markdown text - White and readable */
    [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-size: 18px;
        text-align: center;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* File uploader container */
    [data-testid="stFileUploader"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin: 20px 0;
    }
    
    /* File uploader label - Dark text for visibility */
    [data-testid="stFileUploader"] label {
        color: #2c3e50 !important;
        font-weight: 600;
        font-size: 16px;
    }
    
    /* Text input container */
    [data-testid="stTextInput"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin: 20px 0;
    }
    
    /* Text input label - Dark text */
    [data-testid="stTextInput"] label {
        color: #2c3e50 !important;
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 8px;
    }
    
    /* Input field styling */
    input {
        background-color: #ffffff !important;
        border: 2px solid #667eea !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
        color: #2c3e50 !important;
    }
    
    /* Button styling */
    .stButton {
        margin: 30px 0;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 15px 40px;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        width: 100%;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Results section styling */
    .element-container:has(h3) {
        background-color: rgba(255, 255, 255, 0.98);
        border-radius: 10px;
        padding: 25px;
        margin-top: 30px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Results heading */
    h3 {
        color: #667eea !important;
        font-weight: bold;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Results text content */
    .element-container:has(h3) ~ .element-container p,
    .element-container:has(h3) ~ .element-container li,
    .element-container:has(h3) ~ .element-container {
        color: #2c3e50 !important;
        background-color: rgba(255, 255, 255, 0.98);
        padding: 20px;
        border-radius: 8px;
        line-height: 1.6;
    }
    
    /* Error/Alert message styling */
    [data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
    }
    
    [data-testid="stAlert"] p {
        color: #e74c3c !important;
        font-weight: 600;
    }
    
    /* Block container spacing */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 800px;
    }
    
    /* Upload zone text */
    [data-testid="stFileUploader"] small {
        color: #555 !important;
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
   
