import streamlit as st
import PyPDF2
import json
import re
from io import BytesIO
from groq import Groq

# ⚠️ GROQ API KEY - HIDDEN FROM FRONTEND (PASTE YOUR KEY HERE)
GROQ_API_KEY = "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"  # ← PASTE YOUR KEY HERE

# Initialize client (fails silently if key invalid)
try:
   client = Groq(api_key="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")
   API_READY = True
except:
    client = None
    API_READY = False

# Custom CSS for beautiful UI
CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 3rem !important;
        font-weight: 700 !important;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    
    .metric-container {
        background: rgba(255,255,255,0.15) !important;
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem !important;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .stMetric > label {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1rem !important;
        font-weight: 500;
    }
    
    .stMetric > .stMetricValue {
        color: white !important;
        font-size: 2.8rem !important;
        font-weight: 700;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 15px 40px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 12px 35px rgba(0,0,0,0.3) !important;
    }
    
    .stTextArea > label, .stFileUploader > label {
        color: white !important;
        font-weight: 500;
    }
    
    .stTextArea textarea, .stTextArea div[style*="height"] {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 1rem !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(20px);
        padding: 5px;
        gap: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.05) !important;
        color: rgba(255,255,255,0.8) !important;
        border-radius: 15px !important;
        border: none !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: rgba(255,255,255,0.3) !important;
        color: white !important;
    }
</style>
"""

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file.read()))
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:8000]
    except Exception as e:
        st.error(f"PDF extraction failed: {str(e)}")
        return ""

def analyze_resume_groq(client, resume_text, job_desc):
    """Real Groq API analysis"""
    prompt = f"""
    You are an expert ATS analyzer. Analyze this resume against the job description.

    Return ONLY valid JSON with this EXACT structure:

    {{
        "ats_score": 85,
        "ai_score": 92,
        "strengths": ["3+ years Python experience matches requirement", "Strong AWS skills"],
        "gaps": ["Missing Docker experience"], 
        "suggestions": ["Add Docker to skills section", "Quantify achievements"],
        "summary": {{
            "missing_keywords": ["Docker", "Kubernetes"], 
            "recommended_sections": ["Technical Skills", "Projects"]
        }}
    }}

    RESUME:
    {resume_text[:4000]}

    JOB DESCRIPTION:
    {job_desc}

    Focus on ATS keywords, experience match, missing skills. Return ONLY JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        content = re.sub(r'```json|```', '', content).strip()
        result = json.loads(content)
        
        # Validate structure
        for field in ['ats_score', 'ai_score', 'strengths', 'gaps', 'suggestions', 'summary']:
            if field not in result:
                result[field] = 50 if 'score' in field else []
        
        return result
        
    except Exception as e:
        return fallback_analysis(resume_text, job_desc)

def fallback_analysis(resume_text, job_desc):
    """Smart fallback if API fails"""
    job_keywords = re.findall(r'\b[a-zA-Z]{3,}\b', job_desc.lower())
    resume_keywords = re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower())
    
    common = set(job_keywords) & set(resume_keywords)
    ats_score = min(95, max(30, len(common) * 5))
    
    return {
        "ats_score": ats_score,
        "ai_score": min(90, ats_score + 10),
        "strengths": [f"Found {len(common)} matching keywords", "Good resume structure"],
        "gaps": ["Real AI analysis unavailable"],
        "suggestions": ["Add more job-specific keywords", "Use standard section headers"],
        "summary": {
            "missing_keywords": list(set(job_keywords) - set(resume_keywords))[:5],
            "recommended_sections": ["Skills", "Experience", "Projects"]
        }
    }

# Page config
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject CSS
st.markdown(CSS, unsafe_allow_html=True)

def main():
    # Status indicator (top-right, subtle)
    status_col1, status_col2 = st.columns([3, 1])
    with status_col2:
        if API_READY:
            st.markdown('<span style="color: #10B981; font-size: 0.9rem;">✅ Groq AI Ready</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span style="color: #F59E0B; font-size: 0.9rem;">🔧 Demo Mode</span>', unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🚀 AI Resume Analyzer Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: rgba(255,255,255,0.9); font-size: 1.3rem;">Instant ATS scores • Skill gap analysis • AI-powered suggestions</p>', unsafe_allow_html=True)
    
    # Main content - NO SIDEBAR API INPUT
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Resume")
        uploaded_file = st.file_uploader("Choose PDF Resume", type="pdf")
        
        resume_text = ""
        if uploaded_file:
            with st.spinner("Extracting text..."):
                resume_text = extract_text_from_pdf(uploaded_file)
            
            if resume_text:
                st.success("✅ Resume ready for analysis!")
                with st.expander("📋 Preview"):
                    st.text_area("", resume_text[:800], height=200)
    
    with col2:
        st.header("💼 Job Description")
        job_desc = st.text_area(
            "Paste job description here",
            height=280,
            placeholder="""Senior Python Developer (5+ years)
• Python, Django/FastAPI, SQLAlchemy
• Docker, Kubernetes, AWS/GCP
• REST APIs, Microservices architecture
• Data Structures & Algorithms"""
        )
    
    # Analyze button
    if st.button("🔍 Analyze My Resume", use_container_width=True):
        if not resume_text:
            st.error("👆 Upload a resume PDF first")
            st.stop()
        if not job_desc.strip():
            st.error("👆 Add job description")
            st.stop()
        
        with st.spinner("🤖 AI analyzing your resume..."):
            if API_READY and client:
                analysis = analyze_resume_groq(client, resume_text, job_desc)
            else:
                analysis = fallback_analysis(resume_text, job_desc)
            
            analysis['overall_score'] = (analysis['ats_score'] + analysis['ai_score']) / 2
            st.session_state.analysis = analysis
        
        display_results(st.session_state.analysis)
    
    # Show previous analysis
    if 'analysis' in st.session_state:
        if st.button("📊 View Last Analysis", use_container_width=True):
            display_results(st.session_state.analysis)

def display_results(analysis):
    st.header("🎯 Analysis Results")
    
    # Scores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("ATS Score", f"{analysis['ats_score']:.0f}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("AI Score", f"{analysis['ai_score']:.0f}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Overall", f"{analysis['overall_score']:.0f}/100")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✅ Strengths", "❌ Gaps", "🎯 Suggestions", "📋 Summary"])
    
    with tab1:
        st.subheader("What You Did Well")
        for strength in analysis.get('strengths', []):
            st.success(f"✅ {strength}")
    
    with tab2:
        st.subheader("Areas to Improve")
        gaps = analysis.get('gaps', [])
        if gaps:
            for gap in gaps:
                st.warning(f"⚠️ {gap}")
        else:
            st.success("🎉 No major gaps detected!")
    
    with tab3:
        st.subheader("Actionable Recommendations")
        for i, suggestion in enumerate(analysis.get('suggestions', []), 1):
            st.info(f"{i}. {suggestion}")
    
    with tab4:
        st.subheader("ATS Optimization")
        summary = analysis.get('summary', {})
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Missing Keywords", len(summary.get('missing_keywords', [])))
        with col2:
            st.metric("Priority Sections", len(summary.get('recommended_sections', [])))
        st.json(summary)
    
    # Download report
    report = json.dumps(analysis, indent=2, ensure_ascii=False)
    st.download_button(
        "📥 Download Full Report",
        report,
        "resume-analysis.json",
        "application/json",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
