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

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += page.extract_text()
    return text

# Prompt template
input_prompt = """
Hey, act like a skilled or very experienced ATS (applicants tracking system) with a deep understanding of the tech field, software engineering, data science, data analyst, and big data engineer. Your task is to evaluate the resume based on the given job description. You must consider the job market is very competitive, and you should provide the best assistance for improving the resumes. Assign the percentage Matching based on the job description and the missing keyword with high accuracy.
resume:{text}
description: {jd}
I want the response in one single string having the structure {{"JD Match":"%", "Missing keywords":[], "profile summary":"" }}
"""

# Streamlit UI
st.title("ATS Match Analyzer")
st.text("Improve your resume")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload your Resume", type="pdf", help="Please upload a PDF")
submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        st.text("Input text from PDF:")
        st.text(text)

        response = get_gemini_response(input_prompt.format(text=text, jd=jd))

        # Print the raw response for debugging
        st.text("Raw API Response:")
        st.text(response)

        if response:
            try:
                # Strip any leading/trailing whitespace from the response
                response = response.strip()

                # Log the stripped response
                st.text("Stripped API Response:")
                st.text(response)

                # Parse the response
                parsed_response = json.loads(response)

                # Log the parsed response
                st.text("Parsed Response:")
                st.json(parsed_response)

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
            except json.JSONDecodeError as e:
                st.error(f"Failed to decode the response. The API response is not valid JSON. Error: {e}")
                st.text("Response received before JSON decoding error:")
                st.text(response)
        else:
            st.error("Received an empty response from the API. Please check the API call and try again.")
            

