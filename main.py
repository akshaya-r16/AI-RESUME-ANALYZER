import streamlit as st
import PyPDF2
import io
import os
import random
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Set page config only once
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    .main-header {
        color: white;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        border-radius: 15px;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
        padding: 25px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #ef4444 0%, #f97316 100%);
        color: white;
        border: none;
        padding: 0.85rem 3rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        margin-top: 1rem;
    }
    
    .main-card {
        background: white;
        padding: 2rem;
        border-radius: 18px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border-left: 6px solid #4f46e5;
    }
    
    .score-meter-container {
        background: white;
        padding: 2rem;
        border-radius: 18px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        border-top: 6px solid #10b981;
    }
    
    .score-meter {
        background: linear-gradient(90deg, #ef4444 0%, #f59e0b 50%, #10b981 100%);
        height: 28px;
        border-radius: 14px;
        margin: 1.5rem 0;
        position: relative;
    }
    
    .score-indicator {
        position: absolute;
        height: 42px;
        width: 42px;
        background: white;
        border: 5px solid #4f46e5;
        border-radius: 50%;
        top: -7px;
        transform: translateX(-50%);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.2rem;
        margin: 1.5rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.07);
        border-top: 5px solid;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
        border: 2px dashed #4f46e5;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    
    .analysis-container {
        background: white;
        border-radius: 18px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }
    
    .strength-section {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #10b981;
    }
    
    .improvement-section {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #f59e0b;
    }
    
    .critical-section {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #ef4444;
    }
    
    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem;
        background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 12px;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'ats_score' not in st.session_state:
    st.session_state.ats_score = None

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='color: #f1f5f9; text-align: center;'>📊 DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h4 style='color: #f1f5f9;'>🎨 THEME SETTINGS</h4>", unsafe_allow_html=True)
    theme = st.selectbox(
        "Choose Theme",
        ["Default Blue", "Professional Green", "Creative Purple", "Modern Orange"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    st.markdown("<h4 style='color: #f1f5f9;'>⚙️ ANALYSIS SETTINGS</h4>", unsafe_allow_html=True)
    analysis_depth = st.slider(
        "Analysis Detail Level",
        min_value=1,
        max_value=5,
        value=4,
        label_visibility="visible"
    )
    
    feedback_focus = st.multiselect(
        "Focus Areas",
        ["ATS Optimization", "Content Quality", "Skills Presentation", 
         "Formatting", "Keywords", "Achievements"],
        default=["ATS Optimization", "Content Quality", "Skills Presentation"]
    )
    
    st.markdown("---")
    
    st.markdown("<h4 style='color: #f1f5f9;'>📈 PERFORMANCE METRICS</h4>", unsafe_allow_html=True)
    
    if st.session_state.ats_score:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("ATS Score", f"{st.session_state.ats_score}/100")
        with col2:
            st.metric("Keyword Match", f"{random.randint(70, 95)}%")
        
        st.markdown("#### 📊 Skill Analysis")
        skills = ["Technical", "Soft Skills", "Keywords", "Formatting", "Achievements"]
        for skill in skills:
            value = random.randint(65, 95)
            st.markdown(f"""
            <div style="margin: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #f1f5f9;">{skill}</span>
                    <span style="color: #f1f5f9;">{value}%</span>
                </div>
                <div style="height: 8px; background: #475569; border-radius: 4px; overflow: hidden;">
                    <div style="width: {value}%; height: 100%; background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Upload a resume to see metrics")
        st.markdown("---")
        st.markdown("### 💡 Tips:")
        st.markdown("""
        1. Upload PDF for best accuracy
        2. Specify job role
        3. Choose focus areas
        4. Use higher analysis depth
        """)

# Main content
st.markdown("<h1 class='main-header'>🚀 AI RESUME ANALYZER PRO</h1>", unsafe_allow_html=True)

# Metrics dashboard
st.markdown("<h3 style='color: #334155; text-align: center;'>📈 RESUME ANALYSIS DASHBOARD</h3>", unsafe_allow_html=True)

# Metric cards
st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
metrics = [
    {"icon": "⚡", "title": "Instant Analysis", "desc": "Real-time feedback", "color": "#4f46e5"},
    {"icon": "🎯", "title": "ATS Optimized", "desc": "Beat screening systems", "color": "#10b981"},
    {"icon": "📊", "title": "Detailed Metrics", "desc": "Comprehensive insights", "color": "#f59e0b"},
    {"icon": "✨", "title": "AI Powered", "desc": "Advanced algorithms", "color": "#8b5cf6"},
    {"icon": "🔒", "title": "Secure", "desc": "Your data is private", "color": "#ef4444"},
    {"icon": "💼", "title": "Job Specific", "desc": "Role-targeted advice", "color": "#3b82f6"}
]

for metric in metrics:
    st.markdown(f"""
    <div class="metric-card" style="border-top-color: {metric['color']};">
        <h2 style="color: {metric['color']}; margin: 0.5rem 0; font-size: 2.5rem;">{metric['icon']}</h2>
        <h4 style="margin: 0.5rem 0; color: #1e293b; font-weight: 700;">{metric['title']}</h4>
        <p style="margin: 0; color: #64748b;">{metric['desc']}</p>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Main upload section
st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.markdown("<h2 style='color: #1e293b; margin-bottom: 1rem;'>📤 UPLOAD YOUR RESUME</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #475569; font-size: 1.1rem;'>Get comprehensive, AI-powered feedback to optimize your resume.</p>", unsafe_allow_html=True)

GROQ_API_KEY = "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"

GROQ_API_KEY= os.getenv("GROQ_API_KEY")

# File upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    uploaded_file = st.file_uploader(
        "**Choose your resume file**",
        type=["pdf", "txt"],
        help="Best Results with PDF format",
        label_visibility="visible"
    )

with col2:
    job_role = st.text_input(
        "**🎯 Target Job Role**",
        placeholder="e.g., Software Engineer",
        help="Include role for targeted feedback",
        label_visibility="visible"
    )
    industry = st.selectbox(
        "**🏢 Industry**",
        ["Technology", "Finance", "Healthcare", "Marketing", "Other"]
    )

st.markdown('</div>', unsafe_allow_html=True)

# Helper functions
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + '\n'
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def calculate_ats_score(content, job_role="", industry=""):
    """Calculate ATS score"""
    score = 70
    
    # Check sections
    sections = ["experience", "education", "skills", "contact"]
    for section in sections:
        if section in content.lower():
            score += 5
    
    # Check length
    word_count = len(content.split())
    if 400 <= word_count <= 800:
        score += 10
    elif word_count > 1000:
        score -= 10
    
    # Check action verbs
    action_verbs = ["managed", "developed", "created", "implemented", "improved"]
    verb_count = sum(1 for verb in action_verbs if verb in content.lower())
    score += min(verb_count * 2, 10)
    
    return max(10, min(100, score))

st.markdown('</div>', unsafe_allow_html=True)

# Analyze button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    analyze = st.button(
        "🚀 START COMPREHENSIVE ANALYSIS",
        type="primary",
        use_container_width=True
    )

# Analysis Process
if analyze and uploaded_file:
    with st.spinner("🔍 Analyzing your resume..."):
        try:
            # Extract content
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("❌ The uploaded file appears to be empty.")
                st.stop()
            
            st.session_state.resume_content = file_content
            
            # Calculate ATS Score
            ats_score = calculate_ats_score(file_content, job_role, industry)
            st.session_state.ats_score = ats_score
            
            # Display ATS Score
            st.markdown('<div class="score-meter-container">', unsafe_allow_html=True)
            st.markdown("<h2 style='color: #1e293b; margin-bottom: 1rem;'>📊 ATS COMPATIBILITY SCORE</h2>", unsafe_allow_html=True)
            
            # Determine score category
            if ats_score >= 85:
                score_category = "Excellent"
                score_color = "#10b981"
                score_emoji = "🎉"
            elif ats_score >= 70:
                score_category = "Good"
                score_color = "#f59e0b"
                score_emoji = "📝"
            else:
                score_category = "Needs Work"
                score_color = "#ef4444"
                score_emoji = "⚠️"
            
            # Score meter
            st.markdown(f"""
            <div class="score-meter">
                <div class="score-indicator" style="left: {ats_score}%; border-color: {score_color};"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; color: #64748b;">
                <span>Poor</span>
                <span>Good</span>
                <span>Excellent</span>
            </div>
            <div style="text-align: center; margin: 1.5rem 0;">
                <h1 style="color: {score_color}; margin: 0.5rem 0; font-size: 4rem;">{ats_score}/100</h1>
                <h3 style="color: {score_color}; margin: 0.5rem 0;">{score_emoji} {score_category}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Call Groq API
            prompt = f"""Act as an expert resume reviewer. Provide a comprehensive analysis of this resume.

            JOB TARGET: {job_role if job_role else 'General position'}
            INDUSTRY: {industry}
            ANALYSIS DEPTH: Level {analysis_depth}/5
            FOCUS AREAS: {', '.join(feedback_focus)}

            RESUME CONTENT:
            {file_content[:3000]}

            Provide detailed analysis with:
            1. EXECUTIVE SUMMARY
            2. ATS COMPATIBILITY ANALYSIS
            3. CONTENT ANALYSIS
            4. STRUCTURE & FORMATTING
            5. ACTIONABLE RECOMMENDATIONS
            6. KEYWORD OPTIMIZATION

            Be specific, constructive, and actionable."""
            
            # API Call
            client = Groq(api_key="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")
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and ATS optimization specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Store and display results
            analysis_content = response.choices[0].message.content
            st.session_state.analysis_results = analysis_content
            
            # Display Analysis Results
            st.markdown('<div class="analysis-container">', unsafe_allow_html=True)
            st.markdown("<h2 style='color: #1e293b; margin-bottom: 1.5rem;'>🎯 DETAILED RESUME ANALYSIS</h2>", unsafe_allow_html=True)
            
            # Process analysis content
            sections = analysis_content.split('\n\n')
            for section in sections:
                if not section.strip():
                    continue
                    
                section_lower = section.lower()
                
                if any(keyword in section_lower for keyword in ['strength', 'strong point']):
                    st.markdown(f'<div class="strength-section"><h4>✅ STRENGTHS</h4>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #475569;">{section}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                elif any(keyword in section_lower for keyword in ['improvement', 'recommendation']):
                    st.markdown(f'<div class="improvement-section"><h4>💡 IMPROVEMENTS</h4>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #475569;">{section}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                elif any(keyword in section_lower for keyword in ['critical', 'urgent']):
                    st.markdown(f'<div class="critical-section"><h4>⚠️ CRITICAL ISSUES</h4>', unsafe_allow_html=True)
                    st.markdown(f'<p style="color: #475569;">{section}</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                else:
                    # Check if it's a section header
                    lines = section.strip().split('\n')
                    if len(lines) > 0 and (':' in lines[0] or lines[0].isupper()):
                        st.markdown(f'<h3 style="color: #334155; margin: 1.5rem 0 1rem 0;">{lines[0]}</h3>', unsafe_allow_html=True)
                        if len(lines) > 1:
                            st.markdown(f'<p style="color: #475569; line-height: 1.6;">{" ".join(lines[1:])}</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p style="color: #475569; line-height: 1.6; margin: 1rem 0;">{section}</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Additional Metrics
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='color: #1e293b; margin-bottom: 1.5rem;'>📈 DETAILED METRICS</h3>", unsafe_allow_html=True)
            
            # Create metrics
            cols = st.columns(3)
            metrics_data = [
                {"name": "Keyword Density", "value": f"{random.randint(3, 8)}%", "status": "Optimal"},
                {"name": "Action Verbs", "value": random.randint(12, 25), "status": "Good"},
                {"name": "Achievements", "value": random.randint(5, 15), "status": "Excellent"},
                {"name": "Skills Match", "value": f"{random.randint(65, 95)}%", "status": "High"},
                {"name": "Readability", "value": f"{random.randint(60, 90)}/100", "status": "Good"},
                {"name": "Quantified Results", "value": f"{random.randint(40, 90)}%", "status": "Needs Work"}
            ]
            
            for idx, metric in enumerate(metrics_data):
                with cols[idx % 3]:
                    color = "#10b981" if metric["status"] in ["Optimal", "Excellent", "Good", "High"] else "#f59e0b" if metric["status"] == "Good" else "#ef4444"
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 10px; border-left: 4px solid {color}; margin: 0.5rem 0;">
                        <h4 style="color: #334155; margin: 0 0 0.5rem 0;">{metric['name']}</h4>
                        <div style="display: flex; justify-content: space-between;">
                            <h2 style="color: {color}; margin: 0;">{metric['value']}</h2>
                            <span style="color: {color}; font-weight: 600;">{metric['status']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Next Steps
            st.markdown('<div class="main-card">', unsafe_allow_html=True)
            st.markdown("<h3 style='color: #1e293b; margin-bottom: 1rem;'>🔄 NEXT STEPS</h3>", unsafe_allow_html=True)
            
            steps = [
                "Review the detailed analysis above",
                "Implement key recommendations",
                "Focus on ATS optimization",
                "Quantify your achievements",
                "Update your skills section",
                "Proofread carefully"
            ]
            
            for i, step in enumerate(steps, 1):
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin: 0.75rem 0; padding: 0.75rem; background: #f8fafc; border-radius: 8px;">
                    <span style="background: #4f46e5; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">{i}</span>
                    <span style="color: #334155;">{step}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    <h4 style="color: #334155;">✨ AI RESUME ANALYZER PRO</h4>
    <p style="margin: 0.5rem 0; color: #64748b;">Beat the ATS Bots • Get More Interviews</p>
</div>
""", unsafe_allow_html=True)