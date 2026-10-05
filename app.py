import streamlit as st
import os
import html

from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from PIL import Image
from groq import Groq
from streamlit_mic_recorder import mic_recorder

# =====================================================

# PAGE CONFIGURATION

# =====================================================

st.set_page_config(
page_title="IntervAI",
page_icon="🤖",
layout="wide"
)

# =====================================================

# GROQ API CONFIGURATION

# =====================================================

# =====================================================
# GROQ API CONFIGURATION
# =====================================================
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "Groq API key not found. "
        "Please check your .env file."
    )
    st.stop()

client = Groq(api_key=api_key)
st.write("API Key loaded:", bool(api_key))

try:
    models = client.models.list()
    st.success("Groq API connection working!")
    st.write("Available models:", len(models.data))
except Exception as e:
    st.error(f"Groq connection failed: {e}")
MODEL = "openai/gpt-oss-20b"


def generate_response(prompt):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content

# =====================================================

# HELPER FUNCTION

# =====================================================

# =====================================================
# HELPER FUNCTION
# =====================================================

def generate_response(prompt):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
# =====================================================

# APP TITLE

# =====================================================

st.title("🤖 IntervAI")

st.write(
"Practice interviews, improve your resume, "
"and get personalized feedback."
)

st.divider()

# =====================================================

# TWO COLUMNS

# =====================================================

col1, col2 = st.columns(2)

# =====================================================

# RESUME ASSISTANT

# =====================================================

with col1:

    st.subheader("📄 Resume Assistant")

    st.write(
        "Upload your resume and get personalized "
        "AI-powered improvement suggestions."
    )

    # -------------------------------------------------
    # RESUME UPLOAD
    # -------------------------------------------------

    resume = st.file_uploader(
        "Upload your Resume",
        type=[
            "pdf",
            "docx",
            "jpg",
            "jpeg",
            "png"
        ],
        key="resume"
    )

    # -------------------------------------------------
    # JOB DESCRIPTION
    # -------------------------------------------------

    st.subheader("💼 Job Description")

    job_description = st.text_area(
        "Paste Job Description",
        height=120,
        placeholder=(
            "Example: Python Developer with "
            "Python, SQL, Django..."
        ),
        key="job_description"
    )

    # -------------------------------------------------
    # RESUME PROCESSING
    # -------------------------------------------------

    if resume is not None:

        file_name = resume.name.lower()

        resume_text = ""

        try:

            # =========================================
            # DOCX
            # =========================================

            if file_name.endswith(".docx"):

                document = Document(resume)

                for paragraph in document.paragraphs:

                    if paragraph.text.strip():

                        resume_text += (
                            paragraph.text + "\n"
                        )

            # =========================================
            # PDF
            # =========================================

            elif file_name.endswith(".pdf"):

                resume.seek(0)

                reader = PdfReader(resume)

                for page in reader.pages:

                    text = page.extract_text()

                    if text:

                        resume_text += (
                            text + "\n"
                        )

            # =========================================
            # IMAGE
            # =========================================

            elif file_name.endswith(
                (".jpg", ".jpeg", ".png")
            ):

                st.warning(
                    "Image resume text extraction is "
                    "not enabled in this Groq version. "
                    "Please use PDF or DOCX for best results."
                )

                resume_text = ""

            # =========================================
            # CHECK PREVIOUS RESUME
            # =========================================

            has_previous_resume = (
                "previous_resume_text"
                in st.session_state
            )

            if has_previous_resume:

                st.info(
                    "🔄 Updated Resume detected. "
                    "Previous resume and feedback "
                    "will be used for comparison."
                )

            else:

                st.info(
                    "📄 First resume uploaded "
                    "in this session."
                )

            # =========================================
            # ANALYZE BUTTON
            # =========================================

            if st.button(
                "🤖 Analyze My Resume",
                key="analyze_resume"
            ):

                if not resume_text.strip():

                    st.warning(
                        "Could not read the uploaded resume. "
                        "Please use a PDF or DOCX file."
                    )

                else:

                    # =================================
                    # UPDATED RESUME
                    # =================================

                    if has_previous_resume:

                        prompt = f"""
You are an AI Resume Improvement Assistant.

The candidate previously uploaded a resume
and received AI feedback.

Now the candidate has uploaded an UPDATED RESUME.

Compare the previous resume with the updated resume.

PREVIOUS RESUME:

{st.session_state["previous_resume_text"]}

PREVIOUS AI FEEDBACK:

{st.session_state["previous_resume_analysis"]}

UPDATED RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}

Provide a clear comparison:

1. Job Match Percentage of Updated Resume
2. Improvements made compared with the previous resume
3. Previous suggestions successfully applied
4. Previous suggestions NOT applied
5. New missing skills
6. Updated resume strengths
7. Updated resume weaknesses
8. Updated suggestions for the candidate
9. Overall comparison

Clearly mention whether the updated resume
is better than the previous resume.

Keep the feedback simple and practical
for a student or fresher.
"""

                        analysis_title = (
                            "🔄 Updated Resume Analysis"
                        )

                    # =================================
                    # FIRST RESUME
                    # =================================

                    else:

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
9. Specific Suggestions to Improve the Resume

Keep the feedback clear, practical,
and suitable for a student or fresher.

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

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

Keep the feedback clear, practical,
and suitable for a student or fresher.

RESUME:

{resume_text}
"""

                        analysis_title = (
                            "🤖 AI Resume Analysis"
                        )

                    # =================================
                    # GROQ ANALYSIS
                    # =================================

                    try:

                        with st.spinner(
                            "🤖 AI is analyzing your resume..."
                        ):

                            result = generate_response(
                                prompt
                            )

                        # -----------------------------
                        # DISPLAY RESULT
                        # -----------------------------

                        st.subheader(
                            analysis_title
                        )

                        st.markdown(result)

                        # -----------------------------
                        # SAVE CURRENT RESUME
                        # -----------------------------

                        st.session_state[
                            "previous_resume_text"
                        ] = resume_text

                        st.session_state[
                            "previous_resume_analysis"
                        ] = result

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
# COLUMN 2 - MOCK INTERVIEW
# =====================================================

with col2:

    st.subheader("🎤 Mock Interview")

    st.write(
        "Practice technical interview questions and "
        "get AI-powered feedback on your answers."
    )

    # -------------------------------------------------
    # INITIALIZE SESSION STATE
    # -------------------------------------------------

    if "interview_started" not in st.session_state:
        st.session_state["interview_started"] = False

    if "question_number" not in st.session_state:
        st.session_state["question_number"] = 1

    if "current_question" not in st.session_state:
        st.session_state["current_question"] = ""

    if "evaluation" not in st.session_state:
        st.session_state["evaluation"] = None

    # -------------------------------------------------
    # START INTERVIEW
    # -------------------------------------------------

    if st.button("🎤 Start Interview", key="start_interview"):

        st.session_state["interview_started"] = True
        st.session_state["question_number"] = 1
        st.session_state["evaluation"] = None

        question_prompt = """
        You are an AI interviewer conducting a software
        job interview for a college student or fresher.

        Start the interview by asking ONE simple technical
        interview question.

        The question should be suitable for a beginner
        or fresher.

        Do not give the answer.
        Do not ask multiple questions.

        Only return the interview question.
        """

        try:

            with st.spinner("🤖 Preparing interview question..."):

                result = generate_response(question_prompt)

            st.session_state["current_question"] = result

            st.rerun()

        except Exception as e:

            st.error(f"Could not generate question: {e}")

    # -------------------------------------------------
    # INTERVIEW SCREEN
    # -------------------------------------------------

    if st.session_state.get("interview_started", False):

        st.success("Interview started! 🚀")

        question_number = st.session_state.get(
            "question_number", 1
        )

        current_question = st.session_state.get(
            "current_question",
            "Preparing question..."
        )

        st.markdown(
            f"### Question {question_number}"
        )

        # -------------------------------------------------
        # DISPLAY QUESTION
        # -------------------------------------------------

        st.info(current_question)

        # -------------------------------------------------
        # READ QUESTION ALOUD
        # -------------------------------------------------

        import html

        safe_question = html.escape(current_question)

        speech_html = f"""
        <script>
        function speakQuestion() {{
            window.speechSynthesis.cancel();

            const text = `{safe_question}`;

            const speech = new SpeechSynthesisUtterance(text);

            speech.rate = 0.9;
            speech.pitch = 1;
            speech.volume = 1;

            window.speechSynthesis.speak(speech);
        }}

        // Automatically read the question
        window.onload = function() {{
            speakQuestion();
        }};
        </script>

        <button
            onclick="speakQuestion()"
            style="
                padding:8px 16px;
                border-radius:8px;
                border:1px solid #888;
                background:white;
                cursor:pointer;
            "
        >
            🔊 Replay Question
        </button>
        """

        st.components.v1.html(
            speech_html,
            height=50
        )

        st.markdown("### 🎙️ Your Answer")

        st.write(
            "Click the microphone button and answer "
            "the question."
        )

        # -------------------------------------------------
        # AUDIO RECORDER
        # -------------------------------------------------

        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop Recording",
            just_once=True,
            use_container_width=True,
            key=f"audio_{question_number}"
        )

        # -------------------------------------------------
        # PROCESS ANSWER
        # -------------------------------------------------

        if audio:

            st.success(
                "✅ Answer recorded successfully!"
            )

            try:

                # -----------------------------------------
                # SPEECH TO TEXT
                # -----------------------------------------

                with st.spinner(
                    "🎧 Converting your answer to text..."
                ):

                    transcription = client.audio.transcriptions.create(
                        file=(
                            "answer.wav",
                            audio["bytes"]
                        ),
                        model="whisper-large-v3-turbo",
                        response_format="text"
                    )

                answer_text = transcription

                st.markdown("### 📝 Your Answer")

                st.write(answer_text)

                # -----------------------------------------
                # AI EVALUATION
                # -----------------------------------------

                evaluation_prompt = f"""
                You are an AI interviewer evaluating
                a college student/fresher.

                Interview Question:
                {current_question}

                Candidate Answer:
                {answer_text}

                Evaluate the candidate's answer.

                Give the evaluation in this format:

                Score: X/10

                What was good:
                - Mention 1 or 2 positive points.

                What can be improved:
                - Mention important mistakes or missing points.

                Suggestions:
                - Give simple practical suggestions.

                Better Answer:
                Give a short and simple improved answer.

                Communication Feedback:
                Give one short sentence about the
                clarity and structure of the answer.

                Be supportive and suitable for a fresher.
                """

                with st.spinner(
                    "🤖 AI is evaluating your answer..."
                ):

                    evaluation = generate_response(
                        evaluation_prompt
                    )

                st.session_state["evaluation"] = evaluation

                st.markdown("### 📊 AI Evaluation")

                st.write(evaluation)

                # -----------------------------------------
                # NEXT QUESTION
                # -----------------------------------------

                if st.button(
                    "➡️ Next Question",
                    key=f"next_{question_number}"
                ):

                    old_question_number = question_number

                    next_question_prompt = f"""
                    You are an AI interviewer conducting
                    a software job interview for a college
                    student/fresher.

                    The candidate has completed question
                    {old_question_number}.

                    Generate ONE new simple technical
                    interview question.

                    Do not repeat the previous question.
                    Do not give the answer.
                    Do not ask multiple questions.

                    Only return the interview question.
                    """

                    try:

                        with st.spinner(
                            "🤖 Preparing next question..."
                        ):

                            result = generate_response(
                                next_question_prompt
                            )

                        st.session_state[
                            "question_number"
                        ] += 1

                        st.session_state[
                            "current_question"
                        ] = result

                        st.session_state[
                            "evaluation"
                        ] = None

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Could not generate next question: {e}"
                        )

            except Exception as e:

                st.error(
                    f"Could not process your answer: {e}"
                )

    # -------------------------------------------------
    # END INTERVIEW
    # -------------------------------------------------

    if st.session_state.get("interview_started", False):

        st.divider()

        if st.button(
            "🛑 End Interview",
            key="end_interview"
        ):

            st.session_state["interview_started"] = False
            st.session_state["current_question"] = ""
            st.session_state["question_number"] = 1
            st.session_state["evaluation"] = None

            st.success(
                "Interview ended. Great job! 🎉"
            )

            st.rerun()
# =====================================================
# AI CHATBOT
# =====================================================

st.divider()

st.header("💬 AI Career Chatbot")

st.write(
    "Ask questions about resumes, interviews, "
    "skills, careers, programming, or job preparation."
)

# -----------------------------------------------------
# CHAT HISTORY
# -----------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------------------------------
# DISPLAY PREVIOUS MESSAGES
# -----------------------------------------------------

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------------------------
# USER INPUT
# -----------------------------------------------------

user_question = st.chat_input(
    "Ask IntervAI anything..."
)

if user_question:

    # ---------------------------------------------
    # DISPLAY USER MESSAGE
    # ---------------------------------------------

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    # ---------------------------------------------
    # CHATBOT PROMPT
    # ---------------------------------------------

    chatbot_prompt = f"""
You are IntervAI, an AI career and interview
assistant for college students and freshers.

Your role is to help users with:

- Resume improvement
- Job descriptions
- Interview preparation
- Technical interview questions
- Programming concepts
- Skills required for jobs
- Career guidance
- Communication and interview tips
- Project-related questions
- General doubts related to software careers

Give simple, accurate, practical answers.

If the user asks a technical question,
explain it in an easy-to-understand way.

If the user asks for code, provide a clear
working example and explain it briefly.

Do not make up information.

USER QUESTION:
{user_question}
"""

    # ---------------------------------------------
    # GENERATE RESPONSE
    # ---------------------------------------------

    try:

        with st.chat_message("assistant"):

            with st.spinner("🤖 Thinking..."):

                chatbot_response = generate_response(
                    chatbot_prompt
                )

            st.markdown(chatbot_response)

        # -----------------------------------------
        # SAVE AI RESPONSE
        # -----------------------------------------

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": chatbot_response
            }
        )

    except Exception as e:

        st.error(
            f"Could not generate response: {e}"
        )

# -----------------------------------------------------
# CLEAR CHAT
# -----------------------------------------------------

if st.session_state.chat_history:

    if st.button(
        "🗑️ Clear Chat",
        key="clear_chat"
    ):

        st.session_state.chat_history = []

        st.rerun()

