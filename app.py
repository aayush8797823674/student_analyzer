import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# 1. Configuration & Setup
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Missing API Key! Add GEMINI_API_KEY in Secrets or .env")
    st.stop()

# Configure API
genai.configure(api_key=api_key)

# ✅ FIXED MODEL NAME (No '-latest')
model = genai.GenerativeModel("gemini-1.5-flash")

# 2. Helper Function: Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# 3. Streamlit UI
st.set_page_config(page_title="AI Student Analyzer", layout="wide")
st.title("📊 Student Performance Analysis System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📂 Document Upload")
    marksheet_pdf = st.file_uploader("Upload Marksheet (PDF)", type="pdf")
    syllabus_pdf = st.file_uploader("Upload Syllabus (PDF)", type="pdf")

    # Debug tool
    if st.checkbox("Show Supported Models"):
        try:
            models = [
                m.name for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]
            st.write(models)
        except Exception as e:
            st.write("Error fetching models:", e)

    st.info("Ensure PDFs are text-based (not scanned images).")
    analyze_btn = st.button("Generate AI Analysis ✨", use_container_width=True)

# 4. Main Logic
if analyze_btn:
    if not (marksheet_pdf and syllabus_pdf):
        st.warning("⚠️ Please upload both files.")
        st.stop()

    with st.spinner("🤖 AI is analyzing your data..."):
        marks_text = extract_text_from_pdf(marksheet_pdf)
        syllabus_text = extract_text_from_pdf(syllabus_pdf)

        if len(marks_text) < 20:
            st.error("❌ Marksheet text extraction failed (maybe scanned PDF).")
            st.stop()

        # Prompt
        prompt = f"""
        Act as an expert Academic Counselor.

        Analyze the following:

        [MARKSHEET DATA]
        {marks_text[:4000]}

        [SYLLABUS DATA]
        {syllabus_text[:4000]}

        Give response in Markdown:

        1. Performance Summary
        2. Gap Analysis
        3. 4-Week Study Plan
        4. Career Suggestions
        """

        try:
            response = model.generate_content(prompt)

            st.balloons()
            st.success("✅ Analysis Complete!")
            st.markdown("### 📝 AI Report")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"❌ API Error: {e}")
            st.info("Tip: Enable 'Show Supported Models' to verify model name.")