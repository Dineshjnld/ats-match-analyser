import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import PyPDF2 as pdf
import matplotlib.pyplot as plt
import plotly.express as px

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY="))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text    

# Prompt
input_prompt = """
Hey, act like a skilled or very experienced ATS (applicants tracking system) with a deep understanding of the tech field, software engineering, data science, data analyst, and big data engineer. Your task is to evaluate the resume based on the given job description. You must consider the job market is very competitive, and you should provide the best assistance for improving the resumes. Assign the percentage Matching based on the job description and the missing keyword with high accuracy.
resume:{text}
description: {jd}
I want the response in one single string having the structure {{"JD Match":"%", "Missing keywords":[], "profile summary":"" }}
"""

# Streamlit
st.title("ATS Match Analyzer")
st.text("Improve your resume")
jd = st.text_area("Paste the job Description")
uploaded_file = st.file_uploader("Upload your Resume", type="pdf", help="Please upload the PDF")
submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        response = get_gemini_response(input_prompt.format(text=text, jd=jd))

        # Parse the response
        parsed_response = json.loads(response)

        # Remove the percentage symbol and convert "JD Match" to a numeric type
        jd_match = float(parsed_response["JD Match"].strip('%'))

        # Create a Plotly figure for the pie chart
        fig = px.pie(
            values=[jd_match, 100 - jd_match],
            names=['Match', 'Mismatch'],
            title="Matching Percentage",
            color_discrete_sequence=['lightgreen', 'lightcoral'],
            labels={'Match': f'{jd_match:.1f}%', 'Mismatch': f'{100 - jd_match:.1f}%'}
        )

        # Display the pie chart using st.plotly_chart
        st.plotly_chart(fig)

        # Display missing keywords in red text
        st.subheader("Missing Keywords")
        missing_keywords = parsed_response["Missing keywords"]
        if missing_keywords:
            st.markdown(f"<p style='color:red'>{', '.join(missing_keywords)}</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p style='color:green'>No missing keywords!</p>", unsafe_allow_html=True)

        # Display profile summary
        st.subheader("Profile Summary")
        st.markdown(parsed_response["profile summary"])
