import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# 1. Configuration & Setup
load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')

# 2. Helper Function: Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# 3. Streamlit UI
st.set_page_config(page_title="AI Student Analyzer", layout="wide")
st.title("📊 Student Performance Analysis System")
st.markdown("Analyze marksheets against the syllabus using Gemini AI.")

# Sidebar for uploads
with st.sidebar:
    st.header("Upload Documents")
    marksheet_pdf = st.file_uploader("Upload Marksheet (PDF)", type="pdf")
    syllabus_pdf = st.file_uploader("Upload Syllabus (PDF)", type="pdf")
    analyze_btn = st.button("Generate AI Analysis ✨")

# 4. Main Logic
if analyze_btn:
    if marksheet_pdf and syllabus_pdf:
        with st.spinner("Analyzing data with Gemini..."):
            # Extract text
            marks_text = extract_text_from_pdf(marksheet_pdf)
            syllabus_text = extract_text_from_pdf(syllabus_pdf)
            
            # Construct the Prompt
            prompt = f"""
            You are an expert Academic Counselor. 
            I am providing a student's marksheet text and the corresponding syllabus.
            
            MARK SHEET DATA:
            {marks_text}
            
            SYLLABUS DATA:
            {syllabus_text}
            
            Please provide:
            1. **Performance Summary**: A brief overview of the student's standing.
            2. **Gap Analysis**: Identify specific chapters from the syllabus where the student scored low.
            3. **Personalized Study Plan**: A 4-week plan to improve in those specific weak areas.
            4. **Career Suggestion**: Based on their strongest subjects, suggest a potential career path.
            """
            
            # Get AI Response
            response = model.generate_content(prompt)
            
            # Display Results
            st.success("Analysis Complete!")
            st.markdown("### 📝 AI Counselor Report")
            st.write(response.text)
    else:
        st.error("Please upload both the Marksheet and the Syllabus first!")