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
