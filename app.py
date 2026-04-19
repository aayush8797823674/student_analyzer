import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import os
import pyotp
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from fpdf import FPDF 

# 1. Configuration & Setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')

# Initialize Session States
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'otp_sent' not in st.session_state:
    st.session_state.otp_sent = False

def send_otp(receiver_email):
    # Generate a secret key for this session
    if 'otp_secret' not in st.session_state:
        st.session_state.otp_secret = pyotp.random_base32()
    
    totp = pyotp.TOTP(st.session_state.otp_secret, interval=300) # Valid for 5 mins
    otp = totp.now()

    try:
        msg = EmailMessage()
        msg.set_content(f"Your One-Time Password for Student Analyzer is: {otp}")
        msg['Subject'] = 'Login Verification OTP'
        msg['From'] = st.secrets["EMAIL_USER"] # Your Gmail
        msg['To'] = receiver_email

        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(st.secrets["EMAIL_USER"], st.secrets["EMAIL_PASS"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# --- LOGIN UI ---
if not st.session_state.authenticated:
    st.header("🔐 Secure Access")
    email_input = st.text_input("Enter your Email:")
    
    if not st.session_state.otp_sent:
        if st.button("Get OTP"):
            if email_input:
                if send_otp(email_input):
                    st.session_state.otp_sent = True
                    st.rerun()
            else:
                st.warning("Please enter an email address.")
    else:
        otp_input = st.text_input("Enter the 6-digit OTP sent to your email")
        if st.button("Verify & Enter"):
            totp = pyotp.TOTP(st.session_state.otp_secret, interval=300)
            if totp.verify(otp_input):
                st.session_state.authenticated = True
                st.success("Identity Verified!")
                st.rerun()
            else:
                st.error("Invalid or Expired OTP. Try again.")
        
        if st.button("Resend OTP"):
            st.session_state.otp_sent = False
            st.rerun()
            
    st.stop() # This block stops the rest of the app until authenticated

# 2. Helper Function: Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Adding a title to the PDF
    pdf.cell(200, 10, txt="AI Student Performance Report", ln=True, align='C')
    pdf.ln(10)
    # Adding the analysis content
    # Multi_cell handles text wrapping for long AI responses
    pdf.multi_cell(0, 10, txt=text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

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
            result_text = response.text
            
            # Display Results
            st.success("Analysis Complete!")
            st.markdown("### 📝 AI Counselor Report")
            st.write(response.text)
            st.divider()
            pdf_data = create_pdf(result_text)
            st.download_button(
                label="📥 Download Analysis as PDF",
                data=pdf_data,
                file_name="student_analysis_report.pdf",
                mime="application/pdf"
            )
            
    else:
        st.error("Please upload both the Marksheet and the Syllabus first!")