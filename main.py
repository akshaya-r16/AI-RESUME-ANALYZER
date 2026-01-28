import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI RESUME ANALYZER",
    page_icon="📃",
    layout="centered",
    initial_sidebar_state="auto"
)

# Custom CSS styling
st.markdown("""
    <style>
    /* Main app styling with gradient background */
    .main {
        background: linear-gradient(180deg, #e8f4f8 0%, #b8dce8 100%);
        padding: 3rem 2rem;
        min-height: 100vh;
    }
    
    /* Container for content */
    .stApp {
        background: linear-gradient(180deg, #e8f4f8 0%, #b8dce8 100%);
    }
    
    /* Title styling - Blue color like in screenshot */
    h1 {
        color: #1e88e5 !important;
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: none;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Subtitle/description styling - Gray text */
    [data-testid="stMarkdownContainer"] p {
        color: #6c757d !important;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 3rem;
        font-weight: 400;
    }
    
    /* File uploader styling - White card with icon */
    .stFileUploader {
        background-color: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border: 3px dashed #d0e8f2;
        text-align: center;
    }
    
    .stFileUploader label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.5rem;
    }
    
    .stFileUploader label::before {
        content: "📄";
        font-size: 1.5rem;
        background: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
    }
    
    /* Drag and drop area */
    [data-testid="stFileUploadDropzone"] {
        background-color: #f8fcff;
        border: 3px dashed #90caf9;
        border-radius: 15px;
        padding: 3rem 2rem;
        text-align: center;
    }
    
    [data-testid="stFileUploadDropzone"] button {
        background: #2196f3;
        color: white;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 1rem;
        border: none;
        font-size: 2rem;
    }
    
    /* Text area styling for job description */
    .stTextArea {
        background-color: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .stTextArea label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    
    .stTextArea label::before {
        content: "💼";
        font-size: 1.5rem;
        background: #e8f5e9;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        color: #495057;
        background-color: white;
        min-height: 200px;
    }
    
    .stTextArea textarea:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        outline: none;
    }
    
    /* Text input styling */
    .stTextInput {
        background-color: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .stTextInput label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
    }
    
    .stTextInput label::before {
        content: "💼";
        font-size: 1.5rem;
        background: #e8f5e9;
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTextInput input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem;
        font-size: 1rem;
        color: #495057 !important;
        background-color: white !important;
    }
    
    .stTextInput input:focus {
        border-color: #4caf50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
        outline: none;
    }
    
    /* Button styling - Bottom fixed button like in screenshot */
    .stButton {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 0;
        margin: 0;
        z-index: 999;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #90a4ae 0%, #78909c 100%);
        color: white !important;
        font-size: 1.1rem;
        font-weight: 700;
        padding: 1.2rem;
        border-radius: 0;
        border: none;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button::before {
        content: "✨ ";
        font-size: 1.2rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #78909c 0%, #607d8b 100%);
        box-shadow: 0 -6px 25px rgba(0,0,0,0.15);
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Results section styling */
    .analysis-results {
        background-color: white;
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-top: 2rem;
        margin-bottom: 6rem;
    }
    
    /* Headings in results */
    h3 {
        color: #1e88e5 !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.8rem !important;
    }
    
    /* Markdown content in results */
    div[data-testid="stMarkdownContainer"] {
        color: #333333;
    }
    
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #333333 !important;
        line-height: 1.8;
        font-size: 1rem;
    }
    
    div[data-testid="stMarkdownContainer"] strong {
        color: #1e88e5 !important;
        font-weight: 600;
    }
    
    /* Error messages */
    .stAlert {
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #1e88e5 !important;
    }
    
    /* Add padding to bottom of content for fixed button */
    .main .block-container {
        padding-bottom: 100px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        h1 {
            font-size: 2.5rem !important;
        }
        
        .stButton > button {
            font-size: 1rem;
            padding: 1rem;
        }
        
        .stFileUploader, .stTextInput {
            padding: 1.5rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

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
