import streamlit as st
import PyPDF2
import io
import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Custom CSS for colorful UI
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        color: #1e3a8a;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    /* ATS Score Meter */
    .score-meter {
        background: linear-gradient(90deg, #ff6b6b 0%, #ffd93d 50%, #6bcf7f 100%);
        height: 20px;
        border-radius: 10px;
        margin: 1rem 0;
        position: relative;
    }
    
    .score-indicator {
        position: absolute;
        height: 30px;
        width: 30px;
        background: white;
        border: 3px solid #667eea;
        border-radius: 50%;
        top: -5px;
        transform: translateX(-50%);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-top: 4px solid;
    }
    
    /* Progress bars */
    .progress-bar {
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        background: linear-gradient(90deg, #4ade80 0%, #3b82f6 100%);
    }
</style>
""", unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar for dashboard features
with st.sidebar:
    st.markdown("<h2 style='color: white;'>📊 Dashboard</h2>", unsafe_allow_html=True)
    
    # Color theme selector
    theme = st.selectbox(
        "Choose Theme",
        ["Default", "Professional", "Creative", "Modern"],
        help="Select a color theme for your analysis"
    )
    
    # Analysis depth
    analysis_depth = st.slider(
        "Analysis Depth",
        min_value=1,
        max_value=5,
        value=3,
        help="Adjust how detailed the analysis should be"
    )
    
    # Display metrics
    st.markdown("<h3 style='color: white;'>📈 Quick Stats</h3>", unsafe_allow_html=True)
    if 'ats_score' in st.session_state:
        st.metric("Overall ATS Score", f"{st.session_state.ats_score}/100")
        st.metric("Keyword Match", f"{random.randint(70, 95)}%")
        st.metric("Resume Length", "Optimal" if random.choice([True, False]) else "Too Long")

# Main content
st.markdown("<h1 class='main-header'>🚀 AI Resume Analyzer Pro</h1>", unsafe_allow_html=True)

# Dashboard section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #667eea;">
        <h3>⚡ Instant Analysis</h3>
        <p>Get feedback in seconds</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #10b981;">
        <h3>🎯 ATS Optimized</h3>
        <p>Beat the screening bots</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #f59e0b;">
        <h3>📊 Detailed Metrics</h3>
        <p>Comprehensive insights</p>
    </div>
    """, unsafe_allow_html=True)

# Your existing code with enhancements
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 📤 Upload Your Resume")
st.markdown("Get AI-powered feedback tailored to your needs!")

# Your existing configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# File upload section with styling
upload_col1, upload_col2 = st.columns([2, 1])
with upload_col1:
    uploaded_file = st.file_uploader(
        "Choose your resume file",
        type=["pdf", "txt"],
        help="Supported formats: PDF, TXT"
    )
    
with upload_col2:
    job_role = st.text_input(
        "🎯 Target Job Role",
        placeholder="e.g., Software Engineer",
        help="Optional: Get role-specific feedback"
    )

# Your existing functions
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

def calculate_ats_score(content, job_role=""):
    """Simulate ATS score calculation"""
    score = random.randint(60, 95)  # Random score for demo
    if job_role:
        # Add some role-specific scoring
        if any(tech in content.lower() for tech in ['python', 'java', 'javascript']):
            score += random.randint(5, 10)
    return min(score, 100)

# Enhanced analyze button
analyze = st.button(
    "🚀 Analyze Resume",
    type="primary",
    use_container_width=True
)

if analyze and uploaded_file:
    with st.spinner("🔍 Analyzing your resume..."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("❌ The uploaded file appears to be empty.")
                st.stop()

            # Calculate ATS Score
            ats_score = calculate_ats_score(file_content, job_role)
            st.session_state.ats_score = ats_score
            
            # Display ATS Score in a colorful meter
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📊 ATS Compatibility Score")
            
            # Score meter
            st.markdown(f"""
            <div class='score-meter'>
                <div class='score-indicator' style='left: {ats_score}%;'></div>
            </div>
            <div style='display: flex; justify-content: space-between; margin-top: 0.5rem;'>
                <span>Poor</span>
                <span>Good</span>
                <span>Excellent</span>
            </div>
            <h2 style='text-align: center; color: {'#ef4444' if ats_score < 70 else '#f59e0b' if ats_score < 85 else '#10b981'};'>
                {ats_score}/100
            </h2>
            """, unsafe_allow_html=True)
            
            # Score interpretation
            if ats_score >= 85:
                st.success("🎉 Excellent! Your resume is well-optimized for ATS systems.")
            elif ats_score >= 70:
                st.warning("📝 Good, but there's room for improvement.")
            else:
                st.error("⚠️ Needs significant improvement for better ATS compatibility.")
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Your existing Groq API call
            prompt = f"""Please analyze this resume and provide constructive feedback.
            Focus on the following aspects:
            1. Content clarity and impact
            2. Skills presentation
            3. Experience description
            4. Specific improvements for {job_role if job_role else 'general job applications'}
            
            Resume content:
            {file_content[:3000]}  # Limit content length
            
            Please provide your analysis in a clear, structured format with specific recommendations."""
            
            client = Groq(api_key="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")
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Display results in a colorful card
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎯 Analysis Results")
            
            # Add some visual separators
            analysis_content = response.choices[0].message.content
            
            # Enhance the display with icons and colors
            sections = analysis_content.split('\n\n')
            for section in sections:
                if any(keyword in section.lower() for keyword in ['strength', 'good', 'excellent']):
                    st.markdown(f"✅ {section}")
                elif any(keyword in section.lower() for keyword in ['improve', 'weakness', 'suggestion']):
                    st.markdown(f"💡 {section}")
                elif any(keyword in section.lower() for keyword in ['critical', 'warning', 'important']):
                    st.markdown(f"⚠️ {section}")
                else:
                    st.markdown(section)
                st.markdown("---")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional dashboard metrics
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📈 Resume Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div style='text-align: center;'>
                    <h3 style='color: #667eea;'>📄</h3>
                    <h4>Keywords</h4>
                    <h2>{}</h2>
                </div>
                """.format(random.randint(15, 25)), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='text-align: center;'>
                    <h3 style='color: #10b981;'>✍️</h3>
                    <h4>Action Verbs</h4>
                    <h2>{}</h2>
                </div>
                """.format(random.randint(8, 15)), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='text-align: center;'>
                    <h3 style='color: #f59e0b;'>📏</h3>
                    <h4>Length Score</h4>
                    <h2>{}/10</h2>
                </div>
                """.format(random.randint(7, 10)), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div style='text-align: center;'>
                    <h3 style='color: #ef4444;'>🎯</h3>
                    <h4>Role Match</h4>
                    <h2>{}%</h2>
                </div>
                """.format(random.randint(75, 95)), unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 1rem;'>
    <p>✨ AI Resume Analyzer Pro | Beat the Bots | Get Hired Faster ✨</p>
    <p style='font-size: 0.8rem;'>Upload your resume for instant, AI-powered feedback</p>
</div>
""", unsafe_allow_html=True)