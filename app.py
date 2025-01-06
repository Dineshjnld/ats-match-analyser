import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import PyPDF2 as pdf
import plotly.express as px

# Load environment variables
load_dotenv()

# Configure the generative AI model
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
else:
    genai.configure(api_key=api_key)

# Helper function to extract text from PDF
def extract_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# Generate Gemini model response
def get_gemini_response(input_text):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return ""

# Updated Prompt Template
input_prompt = """
Hey, act like an experienced hiring manager and ATS (Applicant Tracking System) with a deep understanding of tech fields like software engineering, data science, and big data. Your task is to analyze the given resume based on hiring standards and provide the following:
1. Resume Score (out of 100) based on its quality, relevance, and completeness for general hiring purposes.
2. A detailed review highlighting strengths, weaknesses, and areas for improvement.
3. A concise summary of the candidate's profile.

resume: {text}
Expected Output: {{
    "Resume Score": "numeric",
    "Review": "detailed feedback on strengths and weaknesses",
    "Profile Summary": "concise summary"
}}
"""

# Streamlit UI
st.title("Resume Reviewer for Hiring Portal")
st.subheader("Evaluate and review resumes for better hiring decisions.")

# Input fields
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
submit = st.button("Analyze Resume")

if submit:
    if uploaded_file is None:
        st.error("Please upload a valid resume file.")
    else:
        # Extract text from the uploaded PDF
        resume_text = extract_pdf_text(uploaded_file)

        if resume_text.strip():
            st.subheader("Resume Content")
            st.text(resume_text)

            # Generate the API response
            prompt = input_prompt.format(text=resume_text)
            api_response = get_gemini_response(prompt)

            if api_response:
                try:
                    # Parse and process the API response
                    parsed_response = json.loads(api_response.strip())
                    
                    # Display Resume Score
                    st.subheader("Resume Score")
                    resume_score = parsed_response.get("Resume Score", "N/A")
                    st.metric(label="Resume Score", value=f"{resume_score}/100")

                    # Display Review
                    st.subheader("Detailed Review")
                    review = parsed_response.get("Review", "No review available.")
                    st.markdown(review)

                    # Display Profile Summary
                    st.subheader("Profile Summary")
                    profile_summary = parsed_response.get("Profile Summary", "No summary available.")
                    st.markdown(profile_summary)

                except json.JSONDecodeError as e:
                    st.error(f"Error decoding API response: {e}")
                    st.text("Raw API Response:")
                    st.text(api_response)
            else:
                st.error("No response received from the API. Please check your inputs and try again.")
        else:
            st.error("Failed to extract text from the uploaded resume. Please check the file and try again.")
