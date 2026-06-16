🧠AI Resume Analyzer

An intelligent resume analysis tool powered by Groq API, built with Python and Streamlit. Upload your resume and a job description to get instant AI-driven feedback, skill gap analysis, and ATS compatibility scores.
 
 
 How It Works

Upload Resume — User uploads a PDF or pastes resume text
Enter Job Description — User pastes the target job description
Parse & Extract — parser.py extracts clean text from the resume
Prompt Engineering — A structured prompt is built combining resume + JD
Groq Inference — The prompt is sent to Groq's LLaMA 3 model via REST API
Display Results — Streamlit renders the analysis in a clean, readable format
