import streamlit as st
from pdfminer.high_level import extract_text
import pyttsx3
import speech_recognition as sr
import requests
import time

# 🔊 SPEECH FUNCTIONS
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening... Please answer now.")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "❌ Couldn't understand your answer."
        except sr.RequestError:
            return "❌ API error while recognizing speech."

# 📄 SKILL EXTRACTION
def extract_skills_from_resume(pdf_file):
    text = extract_text(pdf_file)
    skill_keywords = [
        "Python", "Java", "C++", "Machine Learning", "Deep Learning",
        "Data Analysis", "SQL", "NLP", "Communication", "Leadership",
        "Cloud", "HTML", "CSS", "JavaScript", "React", "Django",
        "Flask", "Git", "REST API", "Node.js"
    ]
    extracted_skills = [skill for skill in skill_keywords if skill.lower() in text.lower()]
    return text, extracted_skills or ["Basic Communication", "Team Work"]

# 🤖 AI QUESTION GENERATOR
def generate_question(skills, job_role):
    prompt = f"""
    You're a realistic interviewer. Generate a clear and relevant technical interview question for a final-year student applying for the role '{job_role}', based on common responsibilities and expected knowledge. Keep it practical, realistic, and focused.
    Provide only the question.
    """
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return "❌ Error getting question from AI."

# 📊 FINAL FEEDBACK
def generate_feedback(qa_pairs):
    feedback_prompt = "You're an expert interviewer. Here's a candidate's mock interview session:\n"
    for i, (q, a) in enumerate(qa_pairs, 1):
        feedback_prompt += f"Q{i}: {q}\nA{i}: {a}\n"
    feedback_prompt += """
Now, give a short, concise feedback report:
- Rate speaking skills and technical knowledge each out of 10.
- Mention 1–2 strengths and improvement areas for both.
- Format as a short professional paragraph.
"""
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-3-70b-instruct",
        "messages": [{"role": "user", "content": feedback_prompt}]
    }
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error(f"❌ Error getting feedback from AI: {response.status_code} - {response.text}")
        return None

# 🌟 STREAMLIT APP
st.set_page_config(page_title="FirstPunch", page_icon="🔥")
st.title("🔥 FirstPunch")
st.caption("Need not to be Perfect. 🧠💬")

st.markdown("Upload your resume, select your desired role, and begin your AI-powered mock interview!")

resume = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
job_roles = [
    "AI/ML Engineer", "Data Scientist", "Software Developer",
    "Frontend Developer", "Backend Developer", "Cybersecurity Analyst",
    "Cloud Engineer", "DevOps Engineer", "Product Manager", "UI/UX Designer"
]
role = st.selectbox("🎯 Select Desired Job Role", job_roles)

if resume:
    full_text, extracted_skills = extract_skills_from_resume(resume)
    st.success(f"✅ Skills Extracted: {', '.join(extracted_skills)}")
    if st.button("🚀 Start Interview"):
        speak("Welcome to the interview! Let’s begin with some questions.")
        st.markdown("### 💼 Interview in Progress...")

        qa_pairs = []
        question_count = 0

        questions = [
            "Tell me about yourself.",
            "What motivates you to pursue a career in this field?",
            generate_question(extracted_skills, role),
            generate_question(extracted_skills, role)
        ]

        for question in questions:
            st.markdown(f"**🧠 Question {question_count + 1}:** {question}")
            speak(question)

            answer = listen()
            st.markdown(f"**🗣️ Your Answer:** {answer}")
            qa_pairs.append((question, answer))
            question_count += 1

        speak("The interview is complete. Let me provide feedback.")
        st.subheader("📋 Final Feedback")
        feedback = generate_feedback(qa_pairs)
        if feedback:
            st.success(feedback)
