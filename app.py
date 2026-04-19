import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# ------------------ 1. CONFIGURATION ------------------ #
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ Missing API Key! Add GEMINI_API_KEY in Secrets or .env")
    st.stop()

genai.configure(api_key=api_key)

# ------------------ 2. GET WORKING MODEL ------------------ #
def get_working_model():
    try:
        models = genai.list_models()
        valid_models = [
            m.name for m in models
            if "generateContent" in m.supported_generation_methods
        ]

        if not valid_models:
            return None

        # Prefer Gemini models if available
        for name in valid_models:
            if "gemini" in name.lower():
                return name

        return valid_models[0]

    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return None


model_name = get_working_model()

if not model_name:
    st.error("❌ No supported models available for your API key.")
    st.stop()

model = genai.GenerativeModel(model_name)

# ------------------ 3. PDF TEXT EXTRACTION ------------------ #
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

# ------------------ 4. UI ------------------ #
st.set_page_config(page_title="AI Student Analyzer", layout="wide")
st.title("📊 Student Performance Analysis System")
st.markdown("---")

with st.sidebar:
    st.header("📂 Upload Files")
    st.success(f"Using Model: {model_name}")

    marksheet_pdf = st.file_uploader("Upload Marksheet (PDF)", type="pdf")
    syllabus_pdf = st.file_uploader("Upload Syllabus (PDF)", type="pdf")

    if st.checkbox("Show Supported Models"):
        try:
            models = genai.list_models()
            for m in models:
                if "generateContent" in m.supported_generation_methods:
                    st.write(m.name)
        except Exception as e:
            st.write("Error:", e)

    st.info("PDF must be text-based (not scanned).")
    analyze_btn = st.button("Generate AI Analysis ✨", use_container_width=True)

# ------------------ 5. MAIN LOGIC ------------------ #
if analyze_btn:

    if not (marksheet_pdf and syllabus_pdf):
        st.warning("⚠️ Please upload both files.")
        st.stop()

    with st.spinner("🤖 AI is analyzing your data..."):

        marks_text = extract_text_from_pdf(marksheet_pdf)
        syllabus_text = extract_text_from_pdf(syllabus_pdf)

        if len(marks_text) < 20:
            st.error("❌ Could not extract text from marksheet.")
            st.stop()

        prompt = f"""
        Act as an expert Academic Counselor.

        Analyze the following data:

        [MARKSHEET DATA]
        {marks_text[:4000]}

        [SYLLABUS DATA]
        {syllabus_text[:4000]}

        Provide output in Markdown:

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
            st.info("Tip: Enable 'Show Supported Models' to debug.")