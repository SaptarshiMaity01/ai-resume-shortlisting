import streamlit as st
from groq import Groq
import pdfplumber
import docx
import tempfile
import os
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# Configuration
GROQ_API_KEY = ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Improved PDF text extraction
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Try multiple extraction strategies
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if not page_text or len(page_text.strip()) < 50:  # If too little text
                    page_text = page.extract_text(
                        x_tolerance=3, 
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True
                    )
                text += (page_text or "") + "\n"
                
        # Fallback to OCR if text extraction fails
        if len(text.strip()) < 100:  # If we got very little text
            images = convert_from_path(file_path)
            ocr_text = " ".join([pytesseract.image_to_string(img) for img in images])
            if len(ocr_text) > len(text):
                text = ocr_text
                
    except Exception as e:
        st.error(f"PDF extraction error: {str(e)}")
        text = ""
    return text

# DOCX extraction
def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"DOCX extraction error: {str(e)}")
        return ""

# File processing with better temp file handling
def extract_resume_text(uploaded_file):
    _, extension = os.path.splitext(uploaded_file.name.lower())
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name
    
    try:
        if extension == ".pdf":
            text = extract_text_from_pdf(temp_path)
        elif extension == ".docx":
            text = extract_text_from_docx(temp_path)
        else:
            text = ""
    finally:
        os.unlink(temp_path)  # Clean up temp file
        
    return text

# More conservative text cleaning
def clean_text(text):
    if not text:
        return ""
    
    # Preserve common resume characters (®, ©, •, etc.)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'[^\w\s@\-.,•®©#&+\/\()]', '', text)  # Keep common special chars
    return text.strip()

# Enhanced resume analysis with better prompts
def analyze_resume(resume_text, technical_skills="", soft_skills=""):
    if not resume_text.strip():
        return "Error: Empty resume text"
        
    client = Groq(api_key=GROQ_API_KEY)

    criteria_parts = []
    if technical_skills.strip():
        criteria_parts.append(f"Required Technical Skills: {technical_skills}")
    if soft_skills.strip():
        criteria_parts.append(f"Required Soft Skills: {soft_skills}")
    
    criteria_string = "\n".join(criteria_parts) if criteria_parts else "General evaluation of qualifications"

    prompt = f"""
RESUME SCREENING TASK:
1. First, extract these details from the resume:
   - Full Name (from header/contact info)
   - All technical skills
   - All soft skills
   - Years of experience
   - Education

2. Then evaluate against these requirements:
{criteria_string}

RESPONSE FORMAT (STRICT):
1. Candidate Name: [full name]
2. Match Score: [0-100]
3. Key Skills Found: [comma-separated]
4. Missing Skills: [comma-separated]
5. Years of Experience: [number]
6. Education: [highest degree]
7. Verdict: [Strong/Moderate/Weak Match]

RESUME CONTENT:
{resume_text}
"""

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
            top_p=0.9,
            stream=False,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error in analysis: {str(e)}"

# More robust response parsing
def parse_analysis_response(response):
    result = {
        "name": "Not found",
        "score": 0,
        "found_skills": "Not found",
        "missing_skills": "Not found",
        "experience": "Not found",
        "education": "Not found",
        "verdict": "Not found",
        "raw_response": response
    }
    
    patterns = {
        "name": r"1\. Candidate Name:\s*(.+)",
        "score": r"2\. Match Score:\s*(\d+)",
        "found_skills": r"3\. Key Skills Found:\s*(.+)",
        "missing_skills": r"4\. Missing Skills:\s*(.+)",
        "experience": r"5\. Years of Experience:\s*(.+)",
        "education": r"6\. Education:\s*(.+)",
        "verdict": r"7\. Verdict:\s*(.+)"
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, response, re.IGNORECASE)
        if match:
            result[field] = match.group(1).strip()
    
    try:
        result["score"] = int(result["score"])
    except (ValueError, TypeError):
        result["score"] = 0
        
    return result

# Streamlit UI
st.set_page_config(page_title="AI Resume Screener Pro", layout="wide")
st.title("🚀 AI-Powered Resume Screening Tool")
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .upload-box { border: 2px dashed #ccc; padding: 20px; border-radius: 5px; }
    .match-score { font-weight: bold; font-size: 16px; }
    .strong-match { color: #2ecc71; }
    .moderate-match { color: #f39c12; }
    .weak-match { color: #e74c3c; }
    .resume-card { border-left: 5px solid #3498db; padding: 15px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📁 Upload Resumes")
    with st.container(border=True):
        uploaded_files = st.file_uploader(
            "Drag & drop resumes here (PDF/DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Supports multiple files",
            label_visibility="collapsed"
        )
    st.markdown(f"<p class='big-font'>📌 {len(uploaded_files) if uploaded_files else 'No'} files selected</p>", unsafe_allow_html=True)

with col2:
    st.subheader("🔍 Screening Criteria")
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        technical_skills = st.text_area(
            "Technical Skills (comma separated)",
            placeholder="Python, SQL, Machine Learning...",
            height=100
        )
    
    with col2_2:
        soft_skills = st.text_area(
            "Soft Skills (comma separated)",
            placeholder="Communication, Leadership...",
            height=100
        )
    
    st.markdown("---")
    
    if st.button("🚀 Screen Resumes", use_container_width=True, type="primary"):
        if not uploaded_files:
            st.warning("Please upload at least one resume")
        else:
            with st.spinner(f"Analyzing {len(uploaded_files)} resumes..."):
                results = []
                for uploaded_file in uploaded_files:
                    try:
                        # Debug: Show file being processed
                        st.toast(f"Processing: {uploaded_file.name}")
                        
                        # Extract and clean text
                        resume_text = extract_resume_text(uploaded_file)
                        cleaned_text = clean_text(resume_text)
                        
                        # Debug view (collapsible)
                        with st.expander(f"Raw text from {uploaded_file.name}", False):
                            st.text(cleaned_text[:2000] + "..." if len(cleaned_text) > 2000 else cleaned_text)
                        
                        if not cleaned_text.strip():
                            st.error(f"⚠️ No text extracted from {uploaded_file.name}")
                            continue
                            
                        # Analyze and parse
                        analysis = analyze_resume(cleaned_text, technical_skills, soft_skills)
                        parsed = parse_analysis_response(analysis)
                        
                        results.append({
                            "filename": uploaded_file.name,
                            **parsed
                        })
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                        results.append({
                            "filename": uploaded_file.name,
                            "error": str(e)
                        })
                
                # Display results
                successful = [r for r in results if "error" not in r]
                if successful:
                    st.success(f"✅ Analysis complete for {len(successful)}/{len(uploaded_files)} resumes")
                    
                    # Sort by score
                    successful.sort(key=lambda x: x["score"], reverse=True)
                    
                    for res in successful:
                        verdict_class = ""
                        if "Strong" in res["verdict"]:
                            verdict_class = "strong-match"
                        elif "Moderate" in res["verdict"]:
                            verdict_class = "moderate-match"
                        else:
                            verdict_class = "weak-match"
                        
                        with st.container(border=True):
                            st.markdown(f"""
                            <div class="resume-card">
                                <h3>{res['filename']}</h3>
                                <p><b>Candidate:</b> {res['name']}</p>
                                <p><b>Match Score:</b> <span class="match-score">{res['score']}/100</span></p>
                                <p><b>Verdict:</b> <span class="{verdict_class}">{res['verdict']}</span></p>
                                <p><b>Experience:</b> {res['experience']}</p>
                                <p><b>Education:</b> {res['education']}</p>
                                <p><b>Skills Found:</b> {res['found_skills']}</p>
                                <p><b>Missing Skills:</b> {res['missing_skills']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Show raw response in expander
                            with st.expander("Detailed Analysis", False):
                                st.text(res['raw_response'])
                
                # Show errors
                errors = [r for r in results if "error" in r]
                if errors:
                    st.warning(f"⚠️ Failed to process {len(errors)} files:")
                    for err in errors:
                        st.error(f"{err['filename']}: {err['error']}")