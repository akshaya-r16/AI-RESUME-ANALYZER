import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv
import json
import re
from datetime import datetime

load_dotenv()

# Page config (keep only one)
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .ats-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    .score-excellent { color: #10b981; }
    .score-good { color: #3b82f6; }
    .score-average { color: #f59e0b; }
    .score-poor { color: #ef4444; }
    .recommendation-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .section-header {
        color: #667eea;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
    }
    .keyword-badge {
        display: inline-block;
        background: #e0e7ff;
        color: #4338ca;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    .missing-keyword {
        background: #fee2e2;
        color: #991b1b;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1rem;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📃 AI Resume Analyzer Pro</h1>
    <p>Upload your resume and get comprehensive AI-powered feedback with ATS scoring!</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'analysis_data' not in st.session_state:
    st.session_state.analysis_data = None

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/resume.png", width=80)
    st.markdown("### 🎯 Analysis Options")
    
    uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
    job_role = st.text_input("🎯 Target Job Role", placeholder="e.g., Software Engineer")
    job_description = st.text_area("📋 Job Description (Optional)", 
                                    placeholder="Paste the job description here for better ATS matching...",
                                    height=150)
    
    st.markdown("---")
    st.markdown("### ⚙️ Settings")
    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=["Quick", "Standard", "Detailed"],
        value="Standard"
    )
    
    analyze = st.button("🚀 Analyze Resume", use_container_width=True)
    
    if st.session_state.analysis_complete:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.analysis_complete = False
            st.session_state.analysis_data = None
            st.rerun()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    GROQ_API_KEY = "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"

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

def calculate_ats_score(file_content, job_description=""):
    """Calculate ATS score based on resume content and job description"""
    score = 0
    feedback = []
    
    # Check for contact information (20 points)
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', file_content):
        score += 10
    else:
        feedback.append("Add email address")
    
    if re.search(r'\b\d{10}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b', file_content):
        score += 10
    else:
        feedback.append("Add phone number")
    
    # Check for sections (30 points)
    sections = ['experience', 'education', 'skills', 'project']
    for section in sections:
        if section in file_content.lower():
            score += 7.5
        else:
            feedback.append(f"Add {section.title()} section")
    
    # Check for measurable achievements (20 points)
    if re.search(r'\b\d+%|\b\d+\+|\bincreased\b|\breduced\b|\bimproved\b', file_content.lower()):
        score += 20
    else:
        feedback.append("Add quantifiable achievements")
    
    # Check for keywords if job description provided (30 points)
    if job_description:
        job_keywords = set(re.findall(r'\b[a-z]{4,}\b', job_description.lower()))
        resume_keywords = set(re.findall(r'\b[a-z]{4,}\b', file_content.lower()))
        common_keywords = job_keywords.intersection(resume_keywords)
        keyword_score = min(30, len(common_keywords) * 2)
        score += keyword_score
        if keyword_score < 20:
            feedback.append("Include more keywords from job description")
    else:
        score += 15  # Base score if no job description
    
    return min(100, score), feedback

def get_ai_analysis(file_content, job_role, job_description, analysis_depth):
    """Get comprehensive AI analysis of the resume"""
    depth_tokens = {"Quick": 800, "Standard": 1500, "Detailed": 2500}
    
    prompt = f"""Analyze this resume comprehensively and provide structured feedback in JSON format.

Resume Content:
{file_content}

Target Job Role: {job_role if job_role else 'General'}
Job Description: {job_description if job_description else 'Not provided'}

Provide your analysis in the following JSON structure:
{{
    "overall_summary": "Brief overview of the resume (2-3 sentences)",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
    "content_analysis": {{
        "clarity": "Assessment of content clarity (1-2 sentences)",
        "impact": "Assessment of impact (1-2 sentences)",
        "score": 0-10
    }},
    "skills_analysis": {{
        "present": ["skill 1", "skill 2"],
        "missing": ["missing skill 1", "missing skill 2"],
        "recommendations": "Recommendations for skills section"
    }},
    "experience_analysis": {{
        "quality": "Quality assessment",
        "recommendations": "Specific recommendations"
    }},
    "recommendations": [
        {{
            "category": "Category name",
            "priority": "High/Medium/Low",
            "suggestion": "Detailed suggestion"
        }}
    ],
    "keywords": {{
        "found": ["keyword1", "keyword2"],
        "missing": ["missing1", "missing2"]
    }}
}}

Be specific, actionable, and professional."""

    client = Groq(api_key=GROQ_API_KEY)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an expert resume reviewer and ATS specialist. Provide structured, actionable feedback in valid JSON format only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=depth_tokens[analysis_depth]
    )
    
    return response.choices[0].message.content

def parse_ai_response(response_text):
    """Parse AI response and extract JSON data"""
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None
    except:
        return None

def display_dashboard(analysis_data, ats_score):
    """Display comprehensive dashboard with all metrics"""
    
    # ATS Score Section
    st.markdown('<div class="section-header">📊 ATS Compatibility Score</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        score_class = ("score-excellent" if ats_score >= 80 else 
                      "score-good" if ats_score >= 60 else 
                      "score-average" if ats_score >= 40 else "score-poor")
        
        st.markdown(f'<div class="ats-score {score_class}">{ats_score}%</div>', unsafe_allow_html=True)
        
        # Progress bar
        if ats_score >= 80:
            st.success("Excellent! Your resume is highly ATS-compatible")
        elif ats_score >= 60:
            st.info("Good! Some improvements will make it even better")
        elif ats_score >= 40:
            st.warning("Average. Significant improvements recommended")
        else:
            st.error("Needs work. Follow recommendations below")
    
    st.markdown("---")
    
    # Key Metrics
    st.markdown('<div class="section-header">📈 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Content Quality", f"{analysis_data.get('content_analysis', {}).get('score', 7)}/10", "")
    
    with col2:
        strengths_count = len(analysis_data.get('strengths', []))
        st.metric("Strengths Found", strengths_count, "")
    
    with col3:
        improvements_count = len(analysis_data.get('recommendations', []))
        st.metric("Improvements", improvements_count, "")
    
    with col4:
        keywords_found = len(analysis_data.get('keywords', {}).get('found', []))
        st.metric("Keywords Matched", keywords_found, "")

def display_analysis(analysis_data, ats_feedback):
    """Display detailed analysis results"""
    
    # Overall Summary
    st.markdown('<div class="section-header">📝 Overall Summary</div>', unsafe_allow_html=True)
    st.info(analysis_data.get('overall_summary', 'Analysis summary not available'))
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">✅ Strengths</div>', unsafe_allow_html=True)
        for strength in analysis_data.get('strengths', []):
            st.markdown(f"- {strength}")
    
    with col2:
        st.markdown('<div class="section-header">⚠️ Areas for Improvement</div>', unsafe_allow_html=True)
        for weakness in analysis_data.get('weaknesses', []):
            st.markdown(f"- {weakness}")
    
    # Content Analysis
    st.markdown('<div class="section-header">📄 Content Analysis</div>', unsafe_allow_html=True)
    content_analysis = analysis_data.get('content_analysis', {})
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Clarity:** {content_analysis.get('clarity', 'N/A')}")
    with col2:
        st.markdown(f"**Impact:** {content_analysis.get('impact', 'N/A')}")
    
    # Skills Analysis
    st.markdown('<div class="section-header">🛠️ Skills Analysis</div>', unsafe_allow_html=True)
    skills_analysis = analysis_data.get('skills_analysis', {})
    
    if skills_analysis.get('present'):
        st.markdown("**Present Skills:**")
        for skill in skills_analysis.get('present', []):
            st.markdown(f'<span class="keyword-badge">{skill}</span>', unsafe_allow_html=True)
    
    if skills_analysis.get('missing'):
        st.markdown("**Recommended Skills to Add:**")
        for skill in skills_analysis.get('missing', []):
            st.markdown(f'<span class="keyword-badge missing-keyword">{skill}</span>', unsafe_allow_html=True)
    
    # Keywords
    st.markdown('<div class="section-header">🔑 Keyword Analysis</div>', unsafe_allow_html=True)
    keywords = analysis_data.get('keywords', {})
    
    col1, col2 = st.columns(2)
    with col1:
        if keywords.get('found'):
            st.markdown("**Keywords Found:**")
            for kw in keywords.get('found', []):
                st.markdown(f'<span class="keyword-badge">{kw}</span>', unsafe_allow_html=True)
    
    with col2:
        if keywords.get('missing'):
            st.markdown("**Keywords Missing:**")
            for kw in keywords.get('missing', []):
                st.markdown(f'<span class="keyword-badge missing-keyword">{kw}</span>', unsafe_allow_html=True)

def display_recommendations(analysis_data, ats_feedback):
    """Display actionable recommendations"""
    
    st.markdown('<div class="section-header">💡 Actionable Recommendations</div>', unsafe_allow_html=True)
    
    recommendations = analysis_data.get('recommendations', [])
    
    # ATS-specific feedback
    if ats_feedback:
        st.markdown("**ATS Optimization:**")
        for feedback in ats_feedback:
            st.markdown(f'<div class="recommendation-box">🎯 {feedback}</div>', unsafe_allow_html=True)
    
    # AI recommendations by priority
    priorities = {"High": [], "Medium": [], "Low": []}
    for rec in recommendations:
        priority = rec.get('priority', 'Medium')
        priorities[priority].append(rec)
    
    for priority in ["High", "Medium", "Low"]:
        if priorities[priority]:
            st.markdown(f"**{priority} Priority:**")
            for rec in priorities[priority]:
                icon = "🔴" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                st.markdown(f'<div class="recommendation-box">{icon} <b>{rec.get("category", "General")}:</b> {rec.get("suggestion", "")}</div>', 
                           unsafe_allow_html=True)

# Main analysis logic
if analyze and uploaded_file:
    try:
        with st.spinner('🔍 Analyzing your resume...'):
            # Extract text
            file_content = extract_text_from_file(uploaded_file)
            
            if not file_content.strip():
                st.error("❌ File does not have any content...")
                st.stop()
            
            # Calculate ATS score
            ats_score, ats_feedback = calculate_ats_score(file_content, job_description)
            
            # Get AI analysis
            ai_response = get_ai_analysis(file_content, job_role, job_description, analysis_depth)
            analysis_data = parse_ai_response(ai_response)
            
            if not analysis_data:
                # Fallback: display raw AI response if parsing fails
                st.warning("⚠️ Could not parse structured analysis. Displaying detailed feedback:")
                st.markdown(ai_response)
                st.session_state.analysis_complete = True
                st.stop()
            
            # Store in session state
            st.session_state.analysis_complete = True
            st.session_state.analysis_data = {
                'ats_score': ats_score,
                'ats_feedback': ats_feedback,
                'ai_analysis': analysis_data,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        st.success("✅ Analysis complete!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("💡 Tip: Make sure your resume is properly formatted and readable.")

# Display results if analysis is complete
if st.session_state.analysis_complete and st.session_state.analysis_data:
    data = st.session_state.analysis_data
    
    # Dashboard
    display_dashboard(data['ai_analysis'], data['ats_score'])
    
    # Create tabs for organized display
    tab1, tab2, tab3 = st.tabs(["📊 Detailed Analysis", "💡 Recommendations", "📥 Export Report"])
    
    with tab1:
        display_analysis(data['ai_analysis'], data['ats_feedback'])
    
    with tab2:
        display_recommendations(data['ai_analysis'], data['ats_feedback'])
    
    with tab3:
        st.markdown('<div class="section-header">📥 Export Your Analysis</div>', unsafe_allow_html=True)
        st.markdown("Download your complete resume analysis report:")
        
        # Create report text
        report = f"""
AI RESUME ANALYSIS REPORT
Generated: {data['timestamp']}
========================

ATS SCORE: {data['ats_score']}/100

OVERALL SUMMARY:
{data['ai_analysis'].get('overall_summary', 'N/A')}

STRENGTHS:
{chr(10).join('- ' + s for s in data['ai_analysis'].get('strengths', []))}

AREAS FOR IMPROVEMENT:
{chr(10).join('- ' + w for w in data['ai_analysis'].get('weaknesses', []))}

RECOMMENDATIONS:
{chr(10).join(f"- [{r.get('priority', 'Medium')}] {r.get('category', 'General')}: {r.get('suggestion', '')}" for r in data['ai_analysis'].get('recommendations', []))}

ATS OPTIMIZATION TIPS:
{chr(10).join('- ' + f for f in data['ats_feedback'])}
        """
        
        st.download_button(
            label="📄 Download Report (TXT)",
            data=report,
            file_name=f"resume_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
        
        st.info("💡 Use this report to guide your resume improvements!")

# Welcome message when no analysis
if not st.session_state.analysis_complete:
    st.markdown("""
    <div style='text-align: center; padding: 3rem;'>
        <h2>👋 Welcome to AI Resume Analyzer Pro!</h2>
        <p style='font-size: 1.1rem; color: #666;'>
            Get comprehensive feedback on your resume including:
        </p>
        <div style='display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;'>
            <div style='background: #f0f9ff; padding: 1.5rem; border-radius: 10px; min-width: 200px;'>
                <h3>📊 ATS Score</h3>
                <p>See how well your resume passes Applicant Tracking Systems</p>
            </div>
            <div style='background: #f0fdf4; padding: 1.5rem; border-radius: 10px; min-width: 200px;'>
                <h3>💡 Recommendations</h3>
                <p>Get prioritized suggestions for improvement</p>
            </div>
            <div style='background: #fef3c7; padding: 1.5rem; border-radius: 10px; min-width: 200px;'>
                <h3>🎯 Keyword Analysis</h3>
                <p>Match your resume to job descriptions</p>
            </div>
        </div>
        <p style='margin-top: 2rem; font-size: 1.1rem;'>
            👈 Upload your resume in the sidebar to get started!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>💼 AI Resume Analyzer Pro | Powered by Groq AI | Made with ❤️ using Streamlit</p>
    <p style='font-size: 0.9rem;'>Tip: For best results, provide both your target job role and job description</p>
</div>
""", unsafe_allow_html=True)
