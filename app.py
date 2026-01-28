import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv
import re
from datetime import datetime

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for beautiful centered UI
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Center content */
    .block-container {
        max-width: 900px;
        padding: 2rem 1rem;
        margin: 0 auto;
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: white;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: #667eea;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        color: #6b7280;
        font-size: 1.2rem;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
    }
    
    /* Metric card */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Progress bar */
    .progress-bar {
        background: #e5e7eb;
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 0.8rem;
        line-height: 20px;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f3f4f6;
        border-radius: 10px;
        font-weight: 600;
    }
    
    /* Success/Error boxes */
    .success-box {
        background: #d1fae5;
        color: #065f46;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: #fef3c7;
        color: #92400e;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    
    .error-box {
        background: #fee2e2;
        color: #991b1b;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide sidebar */
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = 0
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 AI Resume Analyzer</h1>
        <p>Get instant feedback, ATS scores, and actionable insights for your resume</p>
    </div>
""", unsafe_allow_html=True)

# Get API Key
api_key = os.getenv("GROQ_API_KEY")

# Main content area - centered
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📄 Upload Your Resume")
uploaded_file = st.file_uploader(
    "Choose a PDF or TXT file",
    type=["pdf", "txt"],
    help="Upload your resume in PDF or TXT format for analysis"
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🎯 Target Role (Optional)")
job_role = st.text_input(
    "Enter the job title or role",
    placeholder="e.g., Software Engineer, Data Analyst, Marketing Manager",
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# Analyze button (centered)
st.markdown('<div style="text-align: center; margin: 2rem 0;">', unsafe_allow_html=True)
analyze = st.button("🚀 Analyze Resume", use_container_width=False)
st.markdown('</div>', unsafe_allow_html=True)

# Helper functions
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + '\n'
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def calculate_ats_score(resume_text, job_role=""):
    """Calculate ATS score based on various criteria"""
    score = 0
    factors = {}
    
    # Check for contact information (20 points)
    contact_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        r'linkedin\.com/in/[\w-]+',  # LinkedIn
    ]
    contact_score = sum(10 if re.search(pattern, resume_text, re.IGNORECASE) else 0 
                       for pattern in contact_patterns[:2])
    contact_score += 5 if re.search(contact_patterns[2], resume_text, re.IGNORECASE) else 0
    score += min(contact_score, 20)
    factors['Contact Information'] = min(contact_score, 20)
    
    # Check for key sections (30 points)
    sections = ['experience', 'education', 'skills', 'projects', 'certifications']
    section_score = sum(6 for section in sections 
                       if re.search(rf'\b{section}\b', resume_text, re.IGNORECASE))
    score += min(section_score, 30)
    factors['Key Sections'] = min(section_score, 30)
    
    # Check for action verbs (20 points)
    action_verbs = ['developed', 'managed', 'created', 'designed', 'implemented', 
                   'achieved', 'improved', 'led', 'coordinated', 'analyzed']
    verb_count = sum(1 for verb in action_verbs 
                    if re.search(rf'\b{verb}', resume_text, re.IGNORECASE))
    verb_score = min(verb_count * 2, 20)
    score += verb_score
    factors['Action Verbs'] = verb_score
    
    # Check for metrics/numbers (15 points)
    numbers = re.findall(r'\d+%|\$\d+|\d+\+', resume_text)
    metric_score = min(len(numbers) * 3, 15)
    score += metric_score
    factors['Quantifiable Metrics'] = metric_score
    
    # Check for formatting (15 points)
    format_score = 0
    if len(resume_text) > 300:  # Adequate length
        format_score += 5
    if len(resume_text) < 4000:  # Not too long
        format_score += 5
    if resume_text.count('\n\n') > 3:  # Good spacing
        format_score += 5
    score += format_score
    factors['Formatting'] = format_score
    
    return min(score, 100), factors

def get_score_color(score):
    """Return color based on score"""
    if score >= 80:
        return "#10b981"  # Green
    elif score >= 60:
        return "#f59e0b"  # Orange
    else:
        return "#ef4444"  # Red

def get_score_label(score):
    """Return label based on score"""
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Needs Improvement"

# Analysis logic
if analyze and uploaded_file:
    if not api_key:
        st.error("❌ Please provide a Groq API key in the sidebar or environment variables.")
        st.stop()
    
    try:
        with st.spinner("🔍 Analyzing your resume..."):
            # Extract text
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("❌ The file appears to be empty. Please upload a valid resume.")
                st.stop()
            
            # Calculate ATS score
            ats_score, score_factors = calculate_ats_score(file_content, job_role)
            st.session_state.ats_score = ats_score
            
            # Prepare prompt for AI analysis
            prompt = f"""Analyze this resume and provide detailed, actionable feedback.

Target Role: {job_role if job_role else 'General job applications'}

Focus on:
1. **Overall Impression**: First impressions and key strengths
2. **Content Quality**: Clarity, impact, and relevance of experience
3. **Skills Presentation**: How well technical and soft skills are showcased
4. **Experience Description**: Effectiveness of achievement descriptions
5. **ATS Optimization**: Keywords and formatting for applicant tracking systems
6. **Specific Improvements**: Concrete recommendations for enhancement

Resume Content:
{file_content}

Provide your analysis in a clear, professional format with specific, actionable recommendations. Use markdown formatting for better readability."""
            
            # Get AI analysis
            client = Groq(api_key=api_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with 15+ years of experience in HR, recruitment, and career coaching. Provide detailed, constructive, and actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            st.session_state.analysis_result = response.choices[0].message.content
            st.session_state.analysis_done = True
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.stop()

# Display results
if st.session_state.analysis_done:
    st.markdown("---")
    st.markdown("## 📊 Analysis Dashboard")
    
    # ATS Score Dashboard
    score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
    
    with score_col2:
        score = st.session_state.ats_score
        score_color = get_score_color(score)
        score_label = get_score_label(score)
        
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">ATS COMPATIBILITY SCORE</div>
                <div class="metric-value">{score}/100</div>
                <div class="metric-label">{score_label}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.markdown(f"""
            <div class="progress-bar">
                <div class="progress-fill" style="width: {score}%; background: {score_color};">
                    {score}%
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Score breakdown
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📈 Score Breakdown")
    
    if 'score_factors' in locals():
        cols = st.columns(len(score_factors))
        for idx, (factor, factor_score) in enumerate(score_factors.items()):
            with cols[idx]:
                st.metric(
                    label=factor,
                    value=f"{factor_score}",
                    delta=None
                )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Analysis Results
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Analysis Results")
    st.markdown(st.session_state.analysis_result)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations based on score
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💡 Quick Recommendations")
    
    if score >= 80:
        st.markdown("""
            <div class="success-box">
                <strong>✅ Excellent!</strong> Your resume is well-optimized for ATS systems. 
                Focus on tailoring it for specific job descriptions.
            </div>
        """, unsafe_allow_html=True)
    elif score >= 60:
        st.markdown("""
            <div class="warning-box">
                <strong>⚠️ Good Progress!</strong> Your resume has a solid foundation. 
                Review the suggestions below to improve your ATS compatibility.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="error-box">
                <strong>🔧 Needs Work!</strong> Your resume may struggle with ATS systems. 
                Prioritize the improvements suggested in the analysis above.
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Download/Export options
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📥 Export Analysis")
    
    export_text = f"""
RESUME ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
ATS Score: {st.session_state.ats_score}/100
Target Role: {job_role if job_role else 'General'}

{st.session_state.analysis_result}
"""
    
    st.download_button(
        label="📄 Download Analysis Report",
        data=export_text,
        file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: white; padding: 2rem;">
        <p>Made with ❤️ using Streamlit and Groq AI</p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            Upload a new resume to start a fresh analysis
        </p>
    </div>
""", unsafe_allow_html=True)
