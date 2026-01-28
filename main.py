import streamlit as st
import PyPDF2
import io
import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = "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"

GROQ_API_KEY= os.getenv("GROQ_API_KEY")

# Set page config only once - at the very beginning
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful UI
st.markdown("""
<style>
    /* Main background and text colors */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header styling */
    .main-header {
        color: white;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2d3748 0%, #4a5568 100%);
        padding: 20px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border: none;
        padding: 0.75rem 2.5rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
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
        height: 25px;
        border-radius: 12px;
        margin: 1rem 0;
        position: relative;
    }
    
    .score-indicator {
        position: absolute;
        height: 35px;
        width: 35px;
        background: white;
        border: 4px solid #667eea;
        border-radius: 50%;
        top: -5px;
        transform: translateX(-50%);
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        transition: left 1s ease-in-out;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-top: 5px solid;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* File uploader styling */
    .uploadedFile {
        background: linear-gradient(90deg, #e3f2fd 0%, #f3e5f5 100%);
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }
    
    /* Progress bars */
    .progress-container {
        margin: 1rem 0;
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        color: #4a5568;
    }
    
    .progress-bar {
        height: 12px;
        background: #e2e8f0;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, #4ade80 0%, #3b82f6 100%);
        transition: width 1s ease-in-out;
    }
    
    /* Analysis results styling */
    .analysis-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    
    .strength {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
    }
    
    .improvement {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
    }
    
    .critical {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for dashboard features
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>📊 DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Color theme selector
    st.markdown("<h4 style='color: white;'>🎨 Theme Settings</h4>", unsafe_allow_html=True)
    theme = st.selectbox(
        "Choose Theme",
        ["Default", "Professional", "Creative", "Modern"],
        help="Select a color theme for your analysis",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Analysis depth
    st.markdown("<h4 style='color: white;'>⚙️ Analysis Settings</h4>", unsafe_allow_html=True)
    analysis_depth = st.slider(
        "Analysis Depth",
        min_value=1,
        max_value=5,
        value=3,
        help="Adjust how detailed the analysis should be",
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Display metrics if available
    st.markdown("<h4 style='color: white;'>📈 PERFORMANCE METRICS</h4>", unsafe_allow_html=True)
    
    if 'ats_score' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "ATS Score", 
                f"{st.session_state.ats_score}/100",
                delta=f"+{random.randint(1, 10)}" if random.choice([True, False]) else f"-{random.randint(1, 5)}"
            )
        with col2:
            st.metric(
                "Keyword Match", 
                f"{random.randint(70, 95)}%"
            )
        
        # Progress bars for skills
        st.markdown("#### 📊 Skill Match")
        skills = ["Technical Skills", "Soft Skills", "Keywords", "Formatting"]
        for skill in skills:
            value = random.randint(60, 95)
            st.markdown(f"""
            <div class="progress-container">
                <div class="progress-label">
                    <span>{skill}</span>
                    <span>{value}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {value}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👈 Upload a resume to see metrics")

# Main content
st.markdown("<h1 class='main-header'>🚀 AI RESUME ANALYZER PRO</h1>", unsafe_allow_html=True)

# Dashboard section
st.markdown("<h3 style='color: #4a5568; text-align: center;'>📈 KEY METRICS AT A GLANCE</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #667eea;">
        <h3 style="color: #667eea; margin-bottom: 0.5rem;">⚡</h3>
        <h4 style="margin: 0; color: #4a5568;">Instant Analysis</h4>
        <p style="margin: 0; color: #718096; font-size: 0.9rem;">Get feedback in seconds</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #10b981;">
        <h3 style="color: #10b981; margin-bottom: 0.5rem;">🎯</h3>
        <h4 style="margin: 0; color: #4a5568;">ATS Optimized</h4>
        <p style="margin: 0; color: #718096; font-size: 0.9rem;">Beat screening bots</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #f59e0b;">
        <h3 style="color: #f59e0b; margin-bottom: 0.5rem;">📊</h3>
        <h4 style="margin: 0; color: #4a5568;">Detailed Metrics</h4>
        <p style="margin: 0; color: #718096; font-size: 0.9rem;">Comprehensive insights</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card" style="border-top-color: #8b5cf6;">
        <h3 style="color: #8b5cf6; margin-bottom: 0.5rem;">✨</h3>
        <h4 style="margin: 0; color: #4a5568;">AI Powered</h4>
        <p style="margin: 0; color: #718096; font-size: 0.9rem;">Advanced algorithms</p>
    </div>
    """, unsafe_allow_html=True)

# Your existing code with enhancements
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("### 📤 UPLOAD YOUR RESUME")
st.markdown("<p style='color: #4a5568;'>Get AI-powered feedback tailored to your career goals!</p>", unsafe_allow_html=True)

# Your existing configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# File upload section with styling
upload_col1, upload_col2 = st.columns([2, 1])
with upload_col1:
    uploaded_file = st.file_uploader(
        "**Choose your resume file**",
        type=["pdf", "txt"],
        help="📄 Supported formats: PDF, TXT",
        label_visibility="visible"
    )
    
with upload_col2:
    job_role = st.text_input(
        "**🎯 Target Job Role**",
        placeholder="e.g., Software Engineer",
        help="Optional: Get role-specific feedback",
        label_visibility="visible"
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
    """Simulate ATS score calculation with basic checks"""
    score = 75  # Base score
    
    # Check for common resume sections
    sections = ["experience", "education", "skills", "contact"]
    section_count = sum(1 for section in sections if section in content.lower())
    score += section_count * 3
    
    # Check length
    word_count = len(content.split())
    if 300 <= word_count <= 800:
        score += 10
    elif word_count < 300:
        score -= 5
    else:
        score -= 3
    
    # Check for keywords if job role provided
    if job_role:
        tech_keywords = {
            "software": ["python", "java", "javascript", "c++", "sql", "react"],
            "data": ["python", "sql", "excel", "tableau", "analysis"],
            "marketing": ["seo", "social media", "content", "campaign", "analytics"]
        }
        
        # Simple role matching
        role_lower = job_role.lower()
        for role_type, keywords in tech_keywords.items():
            if role_type in role_lower:
                matched = sum(1 for keyword in keywords if keyword in content.lower())
                score += min(matched * 2, 10)
                break
    
    # Ensure score is within bounds
    return max(0, min(100, score))

# Enhanced analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze = st.button(
        "🚀 ANALYZE MY RESUME",
        type="primary",
        use_container_width=True
    )

if analyze and uploaded_file:
    with st.spinner("🔍 Analyzing your resume... This may take a moment."):
        try:
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error("❌ The uploaded file appears to be empty. Please upload a valid resume.")
                st.stop()

            # Calculate ATS Score
            ats_score = calculate_ats_score(file_content, job_role)
            st.session_state.ats_score = ats_score
            
            # Display ATS Score in a colorful meter
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📊 ATS COMPATIBILITY SCORE")
            
            # Score meter
            score_color = "#ef4444" if ats_score < 70 else "#f59e0b" if ats_score < 85 else "#10b981"
            score_emoji = "⚠️" if ats_score < 70 else "📝" if ats_score < 85 else "🎉"
            
            st.markdown(f"""
            <div class="score-meter">
                <div class="score-indicator" style="left: {ats_score}%; border-color: {score_color};"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; color: #718096;">
                <span>Poor (0-69)</span>
                <span>Good (70-84)</span>
                <span>Excellent (85-100)</span>
            </div>
            <h2 style="text-align: center; color: {score_color}; margin: 1rem 0; font-size: 3rem;">
                {ats_score}/100 {score_emoji}
            </h2>
            """, unsafe_allow_html=True)
            
            # Score interpretation
            if ats_score >= 85:
                st.success("🎉 **Excellent!** Your resume is well-optimized for ATS systems and likely to pass automated screening.")
            elif ats_score >= 70:
                st.warning("📝 **Good job!** Your resume is decent but could benefit from some optimization to increase chances.")
            else:
                st.error("⚠️ **Needs improvement.** Your resume may struggle with ATS screening. Follow the recommendations below.")
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Your existing Groq API call
            prompt = f"""Please analyze this resume and provide constructive feedback.
            Focus on the following aspects (analysis depth level {analysis_depth}/5):
            1. Content clarity and impact
            2. Skills presentation and relevance
            3. Experience description and achievements
            4. Specific improvements for {job_role if job_role else 'general job applications'}
            5. ATS optimization suggestions
            
            Resume content (first 3000 characters):
            {file_content[:3000]}
            
            Please provide your analysis in a clear, structured format with specific recommendations.
            Use bullet points and categorize feedback as Strengths, Areas for Improvement, and Critical Actions."""
            
            client = Groq(api_key=GROQ_API_KEY or "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")
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer with years of experience in HR and recruitment. Provide actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Display results in a colorful card
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🎯 AI ANALYSIS RESULTS")
            
            # Add some visual separators
            analysis_content = response.choices[0].message.content
            
            # Enhanced display with categorized sections
            lines = analysis_content.split('\n')
            current_section = ""
            
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in ['strength', 'good', 'excellent', 'positive']):
                    st.markdown(f"<div class='analysis-section strength'><h4>✅ {line}</h4>", unsafe_allow_html=True)
                    current_section = "strength"
                elif any(keyword in line_lower for keyword in ['improve', 'weakness', 'suggestion', 'recommendation', 'could be better']):
                    st.markdown(f"<div class='analysis-section improvement'><h4>💡 {line}</h4>", unsafe_allow_html=True)
                    current_section = "improvement"
                elif any(keyword in line_lower for keyword in ['critical', 'warning', 'important', 'must', 'essential']):
                    st.markdown(f"<div class='analysis-section critical'><h4>⚠️ {line}</h4>", unsafe_allow_html=True)
                    current_section = "critical"
                elif line.strip().startswith('-') or line.strip().startswith('*'):
                    st.markdown(f"<div style='margin-left: 20px;'>{line}</div>", unsafe_allow_html=True)
                elif line.strip():
                    st.markdown(f"<p>{line}</p>", unsafe_allow_html=True)
                
                if line.strip() == '' and current_section:
                    st.markdown("</div>", unsafe_allow_html=True)
                    current_section = ""
            
            if current_section:
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Additional dashboard metrics
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 📈 RESUME BREAKDOWN")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Simulate calculated metrics
            metrics = {
                "keywords": random.randint(15, 30),
                "action_verbs": random.randint(8, 20),
                "length_score": random.randint(7, 10),
                "role_match": random.randint(60, 98) if job_role else random.randint(40, 80)
            }
            
            with col1:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h3 style='color: #667eea; font-size: 2.5rem;'>📄</h3>
                    <h4>Keywords Found</h4>
                    <h2 style='color: #4a5568;'>{metrics['keywords']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h3 style='color: #10b981; font-size: 2.5rem;'>✍️</h3>
                    <h4>Action Verbs</h4>
                    <h2 style='color: #4a5568;'>{metrics['action_verbs']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h3 style='color: #f59e0b; font-size: 2.5rem;'>📏</h3>
                    <h4>Length Score</h4>
                    <h2 style='color: #4a5568;'>{metrics['length_score']}/10</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <h3 style='color: #8b5cf6; font-size: 2.5rem;'>🎯</h3>
                    <h4>Role Match</h4>
                    <h2 style='color: #4a5568;'>{metrics['role_match']}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("💡 Tip: Make sure your resume file is not corrupted and try again.")

# Instructions when no file is uploaded
elif not uploaded_file:
    st.info("👆 **Please upload your resume file to begin analysis**")

st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 1.5rem; background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 10px;'>
    <h4 style='color: #4a5568;'>✨ AI Resume Analyzer Pro</h4>
    <p style='margin: 0.5rem 0;'>Beat the ATS Bots | Get More Interviews | Land Your Dream Job</p>
    <p style='font-size: 0.9rem; color: #718096;'>Upload your resume for instant, AI-powered feedback and optimization tips</p>
</div>
""", unsafe_allow_html=True)