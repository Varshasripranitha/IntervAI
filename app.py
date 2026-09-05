import streamlit as st
import os

from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from PIL import Image

from google import genai
from streamlit_mic_recorder import mic_recorder

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="IntervAI",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------
# Gemini API Configuration
# -----------------------------
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# -----------------------------
# App Title
# -----------------------------
st.title("🤖 IntervAI")

st.markdown(
    "### AI-Powered Mock Interview and Resume Assistant"
)

st.write(
    "Practice interviews, improve your resume, "
    "and get personalized feedback."
)

st.divider()


# -----------------------------
# Two Columns
# -----------------------------
col1, col2 = st.columns(2)


# =====================================================
# RESUME ASSISTANT
# =====================================================

# =====================================================
# RESUME ASSISTANT
# =====================================================

with col1:

    st.subheader("📄 Resume Assistant")

    st.write(
        "Upload your resume and get personalized "
        "AI-powered improvement suggestions."
    )

    # Resume Upload
    resume = st.file_uploader(
        "Upload your Resume",
        type=["pdf", "docx", "jpg", "jpeg", "png"],
        key="resume"
    )

    # Job Description
    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste Job Description",
        height=120,
        placeholder="Example: Python Developer with Python, SQL, Django...",
        key="job_description"
    )

    # Resume Processing
    if resume is not None:

        st.success(f"Resume uploaded: {resume.name}")

        file_name = resume.name.lower()
        resume_text = ""

        try:

            # Word Document
            if file_name.endswith(".docx"):

                document = Document(resume)

                for paragraph in document.paragraphs:

                    if paragraph.text.strip():
                        resume_text += paragraph.text + "\n"

            # PDF
            elif file_name.endswith(".pdf"):

                resume.seek(0)

                reader = PdfReader(resume)

                for page in reader.pages:

                    text = page.extract_text()

                    if text:
                        resume_text += text + "\n"

            # Image Resume
            elif file_name.endswith(
                (".jpg", ".jpeg", ".png")
            ):

                image = Image.open(resume)

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        "Extract all readable text from this resume image. "
                        "Return only the resume text.",
                        image
                    ]
                )

                resume_text = response.text

            # Store internally
            st.session_state["resume_text"] = resume_text

            # Analyze Resume
            if st.button(
                "🤖 Analyze My Resume",
                key="analyze_resume"
            ):

                if not resume_text.strip():

                    st.warning(
                        "Could not read the uploaded resume."
                    )

                else:

                    # If Job Description is provided
                    if job_description.strip():

                        prompt = f"""
You are an AI Resume Assistant.

Analyze the candidate's resume specifically
for the given Job Description.

Provide:

1. Job Match Percentage
2. Matching Skills
3. Missing Skills
4. Recommended Skills to Learn
5. Resume Strengths
6. Resume Improvements for This Job
7. Suitable Job Role
8. Overall Feedback

Keep the feedback clear, practical, and
suitable for a student or fresher.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

                    # If no Job Description
                    else:

                        prompt = f"""
You are an AI Resume Assistant.

Analyze the following resume.

Provide:

1. Resume Strengths
2. Areas for Improvement
3. Missing or Recommended Skills
4. Suggestions to Improve the Resume
5. Suitable Job Roles
6. Overall Resume Feedback

Keep the feedback clear, practical, and
suitable for a student or fresher.

RESUME:

{resume_text}
"""

                    try:

                        with st.spinner(
                            "🤖 Gemini is analyzing your resume..."
                        ):

                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=prompt
                            )

                        st.subheader(
                            "🤖 AI Resume Analysis"
                        )

                        st.markdown(response.text)

                    except Exception as e:

                        st.error(
                            f"Something went wrong: {e}"
                        )

        except Exception as e:

            st.error(
                f"❌ Could not read the resume: {e}"
            )
# =====================================================
# MOCK INTERVIEW
# =====================================================
# =====================================================
# MOCK INTERVIEW
# =====================================================
# =====================================================
# MOCK INTERVIEW
# =====================================================

with col2:

    st.subheader("🎤 Mock Interview")

    st.write(
        "Practice a real-time AI-powered mock interview."
    )

    if st.button(
        "🎤 Start Interview",
        key="start_interview"
    ):

        st.session_state["interview_started"] = True
        st.session_state["question_number"] = 1
        st.session_state["evaluation"] = None

        question_prompt = """
You are an AI interviewer conducting a software
job interview for a college student/fresher.

Start the interview by asking ONE simple technical
interview question.

Do not give the answer.
Do not ask multiple questions.
Only return the interview question.
"""

        try:

            with st.spinner(
                "🤖 Preparing your interview..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=question_prompt
                )

            st.session_state["current_question"] = response.text

        except Exception as e:

            st.error(
                f"Could not start interview: {e}"
            )


    # -------------------------------------------------
    # INTERVIEW SCREEN
    # -------------------------------------------------

    if st.session_state.get(
        "interview_started",
        False
    ):

        st.success("Interview started! 🚀")

        st.markdown(
            f"### Question {st.session_state.get('question_number', 1)}"
        )

        st.info(
            st.session_state.get(
                "current_question",
                "Preparing question..."
            )
        )

        st.markdown("### 🎙️ Your Answer")

        audio = mic_recorder(
            start_prompt="🎤 Start Answer",
            stop_prompt="⏹️ Stop Recording",
            key="voice_recorder"
        )

        if audio:

            st.audio(
                audio["bytes"],
                format="audio/wav"
            )

            st.success(
                "Answer recorded! ✅"
            )

            # -----------------------------------------
            # EVALUATE ANSWER
            # -----------------------------------------

            if st.button(
                "🤖 Evaluate My Answer",
                key="evaluate_answer"
            ):

                evaluation_prompt = f"""
You are an AI interviewer.

Interview Question:
{st.session_state.get("current_question", "")}

The candidate has submitted an answer.

Evaluate the candidate's answer.

Give the following:

1. Marks out of 10
2. What was done well
3. What could be improved
4. Suggestions
5. A better sample answer
6. Communication feedback

Keep the feedback simple and useful for a fresher.
"""

                try:

                    with st.spinner(
                        "🤖 Gemini is evaluating your answer..."
                    ):

                        response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=evaluation_prompt
                        )

                    st.session_state["evaluation"] = response.text

                except Exception as e:

                    st.error(
                        f"Could not evaluate answer: {e}"
                    )


            # -----------------------------------------
            # SHOW EVALUATION
            # -----------------------------------------

            if st.session_state.get(
                "evaluation"
            ):

                st.subheader(
                    "📊 Answer Evaluation"
                )

                st.markdown(
                    st.session_state["evaluation"]
                )

                # -------------------------------------
                # NEXT QUESTION
                # -------------------------------------

                if st.button(
                    "➡️ Next Question",
                    key="next_question"
                ):

                    old_question_number = (
                        st.session_state["question_number"]
                    )

                    next_question_prompt = f"""
You are an AI interviewer conducting a software
job interview for a college student/fresher.

The candidate has completed question
{old_question_number}.

Generate ONE new technical interview question.

Do not repeat the previous question.
Do not give the answer.
Do not ask multiple questions.

Only return the interview question.
"""

                    try:

                        with st.spinner(
                            "🤖 Preparing next question..."
                        ):

                            response = client.models.generate_content(
                                model="gemini-3.6-flash",
                                contents=next_question_prompt
                            )

                        st.session_state[
                            "question_number"
                        ] += 1

                        st.session_state[
                            "current_question"
                        ] = response.text

                        st.session_state[
                            "evaluation"
                        ] = None

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Could not generate next question: {e}"
                        )