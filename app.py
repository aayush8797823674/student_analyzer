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

if api_key:
    genai.configure(api_key=api_key)
    # Using 'gemini-1.5-flash' which is the current stable industry standard
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
else:
    st.error("Missing API Key! Please add GEMINI_API_KEY to Secrets or .env file.")
    st.stop()

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

# Sidebar for uploads
with st.sidebar:
    st.header("📂 Document Upload")
    marksheet_pdf = st.file_uploader("Upload Marksheet (PDF)", type="pdf")
    syllabus_pdf = st.file_uploader("Upload Syllabus (PDF)", type="pdf")
    
    # DEBUG TOOL: This will show you what models your key can actually see
    if st.checkbox("Show Supported Models"):
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            st.write(models)
        except:
            st.write("Could not list models. Check API Key.")
            
    st.info("Ensure PDFs are digital text-based, not scanned images.")
    analyze_btn = st.button("Generate AI Analysis ✨", use_container_width=True)

# 4. Main Logic
if analyze_btn:
    if marksheet_pdf and syllabus_pdf:
        with st.spinner("🤖 Gemini is calculating your performance..."):
            # Extract text
            marks_text = extract_text_from_pdf(marksheet_pdf)
            syllabus_text = extract_text_from_pdf(syllabus_pdf)
            
            # Validation: Stop if extraction failed
            if not marks_text or len(marks_text) < 20:
                st.error("Could not extract enough text from the Marksheet. Is it a scanned image?")
                st.stop()
            
            # 5. The AI Prompt
            # Truncating to 5000 characters prevents 'InvalidArgument'/400 errors
            prompt = f"""
            Act as an expert Academic Counselor. 
            Analyze the following Marksheet data against the Syllabus provided.
            
            [MARKSHEET DATA]
            {marks_text[:5000]} 
            
            [SYLLABUS DATA]
            {syllabus_text[:5000]}
            
            Output your response in Markdown with these headings:
            1. **Performance Summary**: Overview of standing.
            2. **Gap Analysis**: Specific chapters/topics where marks were low.
            3. **4-Week Study Plan**: Personalized improvement roadmap.
            4. **Career Recommendations**: Based on strong subjects.
            """
            
            try:
                # Generate Content
                response = model.generate_content(prompt)
                
                # Display Results
                st.balloons()
                st.success("Analysis Complete!")
                st.markdown("### 📝 AI Counselor Report")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"AI API Error: {str(e)}")
                st.info("Tip: If you see a 404, check the 'Show Supported Models' box in the sidebar to find the correct model name.")
    else:
        st.warning("⚠️ Please upload both files to continue.")