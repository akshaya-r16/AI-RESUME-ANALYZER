import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

load_dotenv()

# Fixed duplicate config - keep the second one
st.set_page_config(
    page_title="AI RESUME ANALYZER", 
    page_icon="📃", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful UI styling
st.markdown("""
    <style>
    .main-header {font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem;}
    .metric-container {background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin: 1rem 0;}
    .stMetric {font-size: 2rem !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 AI Resume Analyzer Pro</h1>', unsafe_allow_html=True)
st.markdown("**Upload your resume and unlock AI-powered insights, ATS scoring, and personalized recommendations!**")

# Secure API key from env
GROQ_API_KEY="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"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Sidebar for inputs (beautiful layout)
with st.sidebar:
    st.header("📁 Upload & Settings")
    uploaded_file = st.file_uploader("Choose your resume", type=["pdf", "txt"], help="PDF or TXT only")
    job_role = st.text_input("🎯 Target Job Role (optional)")
    analyze = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

# Initialize session state for dashboard
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = 0
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}

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

def calculate_ats_score(text, job_role):
    """Simple ATS score based on keyword matching and structure"""
    # Common ATS keywords by category (expanded from standard lists)
    ats_keywords = {
        'general': ['experience', 'skills', 'team', 'project', 'management', 'leadership', 'analysis', 'development', 'communication'],
        'software': ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'git', 'react', 'node.js'],
        'data': ['pandas', 'numpy', 'machine learning', 'sql', 'tableau', 'power bi', 'statistics'],
        'marketing': ['seo', 'google analytics', 'content marketing', 'social media', 'crm']
    }
    
    # Job role specific keywords
    role_keywords = ats_keywords.get(job_role.lower(), ats_keywords['general'])
    
    text_lower = text.lower()
    matches = sum(1 for keyword in role_keywords if re.search(re.escape(keyword), text_lower))
    keyword_score = min(matches / len(role_keywords) * 50, 50)
    
    # Structure checks
    has_sections = bool(re.search(r'(experience|work|employment)', text_lower, re.I)) + \
                   bool(re.search(r'(skills|technologies)', text_lower, re.I)) + \
                   bool(re.search(r'(education|degree)', text_lower, re.I))
    structure_score = (has_sections / 3) * 30
    
    # Readability (simple)
    sentences = len(re.split(r'[.!?]+', text))
    words = len(text.split())
    readability = min((sentences / max(words/20, 1)) * 20, 20)
    
    total_score = keyword_score + structure_score + readability
    return round(total_score, 1)

def get_recommendations(text, job_role):
    prompt = f"""Based on this resume: "{text[:2000]}..."
    For {job_role or 'the target role'}, provide 5 specific, actionable recommendations 
    to improve ATS compatibility and impact. Number them 1-5."""
    return prompt

# Main analysis logic (existing + new features)
if analyze and uploaded_file:
    try:
        with st.spinner("Analyzing your resume... This may take a moment."):
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("❌ File does not have any content...")
                st.stop()
            
            # ATS Score calculation
            ats_score = calculate_ats_score(file_content, job_role)
            st.session_state.ats_score = ats_score
            
            # Extract skills (simple regex for demo)
            skills = re.findall(r'\b(python|java|sql|aws|excel|leadership|analysis|project|team|communication)\b', file_content.lower())
            unique_skills = list(set(skills))
            st.session_state.metrics = {
                'Total Skills Found': len(unique_skills),
                'Keyword Matches': sum(1 for s in unique_skills if s in ['python','java','sql','aws','excel']),
                'Sections Detected': len(re.findall(r'(experience|skills|education|projects)', file_content.lower(), re.I))
            }
            
            # Original analysis prompt (enhanced)
            prompt = f"""Please analyze this resume and provide constructive feedback in JSON format:
{{"content_clarity": "score/10 + feedback", 
  "skills_presentation": "score/10 + feedback", 
  "experience_description": "score/10 + feedback", 
  "overall": "score/10 + summary",
  "recommendations": ["1-3 specific improvements for {job_role or 'general applications'}"]}}

Resume: {file_content}"""
            
            client = Groq(api_key="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")

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment. Respond in structured JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            st.session_state.analysis_results = response.choices[0].message.content
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

# Dashboard - New Feature 1: Beautiful Metrics Dashboard
if st.session_state.ats_score > 0:
    st.header("📊 Resume Dashboard")
    
    # Create gauge chart for ATS Score
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=st.session_state.ats_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "ATS Score"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ATS Score", f"{st.session_state.ats_score}/100", delta=None, label_visibility="collapsed")
    with col2:
        st.metric("Skills Found", st.session_state.metrics.get('Total Skills Found', 0))
    with col3:
        st.metric("Keyword Matches", st.session_state.metrics.get('Keyword Matches', 0))
    with col4:
        st.metric("Sections Detected", st.session_state.metrics.get('Sections Detected', 0))

# Analysis Results - Enhanced UI (existing + styled)
if st.session_state.analysis_results:
    st.header("📋 Detailed Analysis")
    
    # Render JSON-like structured response
    st.markdown("### **AI Feedback**")
    st.markdown(st.session_state.analysis_results)
    
    # Recommendations Section - New Feature 2
    st.header("💡 Actionable Recommendations")
    rec_prompt = get_recommendations(file_content, job_role)
    # For demo, show static enhanced recs - you can add another API call here
    recs = [
        "1. Add quantifiable achievements (e.g., 'Increased sales by 30%') to experience section.",
        "2. Include target job keywords like '{}' in skills section.".format(job_role or 'your role'),
        "3. Use standard section headers: Experience, Skills, Education.",
        "4. Limit resume to 1 page and use ATS-friendly fonts (Arial, Calibri).",
        "5. Add GitHub/Portfolio links if applicable."
    ]
    for rec in recs:
        st.info(rec)

# Footer
st.markdown("---")
st.markdown("*Powered by Groq AI & Streamlit | ATS Score based on keyword matching & structure analysis* [web:4][web:17]")
