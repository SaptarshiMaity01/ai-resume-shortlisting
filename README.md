# 🤖 ai-resume-shortlisting
 
![Python](https://img.shields.io/badge/python-3.8+-blue)  
![Streamlit](https://img.shields.io/badge/framework-streamlit-orange)  
![Groq](https://img.shields.io/badge/api-groq-purple)


---

## 📌 Overview

This is a **multi-resume upload and screening tool** powered by **AI (Large Language Model via Groq API)**. It helps recruiters and HR professionals quickly analyze resumes against technical and soft skills according to their requirements and gives:

- ✅ Match score out of 100  
- ✅ Final match verdict (Strong / Moderate / Weak)  
- ✅ Short reasoning summary  

Perfect for **ATS-like automation**, bulk candidate screening, and AI-powered recruitment tools.

---

## 🔧 Features

✅ Upload **multiple PDF or DOCX resumes**  
✅ Enter Technical And Sofkills As per Requirements 
✅ Get **structured AI analysis** for each resume  
✅ Clean, easy-to-understand output  
✅ Supports **bulk processing**  
✅ Powered by **Groq LLM API**

---

## 🧰 Technologies Used

- **Streamlit**: For building the web UI
- **Groq API**: To power the AI analysis
- **pdfplumber**: For extracting text from PDF resumes
- **python-docx**: For reading DOCX files
- **Regex**: For cleaning extracted text

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/AI-Powered Intelligent Resume Screening Tool.git
cd AI-Powered Intelligent Resume Screening Tool
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Groq API key

Create a `.env` file or replace this line in `app.py`:

```python
GROQ_API_KEY = "your_groq_api_key_here"
```

You can get your free Groq API key from [https://console.groq.com/keys](https://console.groq.com/keys)

### 4. Run the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

---

## 🧪 Sample Analysis Output

```
1. Candidate Name: John Doe
2. Match Score: 92
3. Final Verdict: Strong Match
4. Short Description: Extensive experience in Python and machine learning aligns perfectly with the role.
```
![Screenshot 2025-07-04 164129](https://github.com/user-attachments/assets/06782a4f-1d9d-4313-8c2d-a3d71a0574e0)

---


## 🙌 Acknowledgments

- Built with using [Streamlit](https://streamlit.io/)
- Powered by [Groq API](https://console.groq.com/docs)
- Inspired by modern recruitment tech and ATS systems

