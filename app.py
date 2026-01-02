import streamlit as st
import re
from groq import Groq

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Dynamic AI Quiz Generator", layout="centered")
st.title("🧠 Dynamic AI Quiz Generator")
# ---------------- SESSION STATE ----------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# ---------------- GROQ CLIENT ----------------
client = Groq(api_key="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")

# ---------------- USER INPUT ----------------
name = st.text_input("Name")
topic = st.text_input("Topic (e.g. Node.js, DBMS, AI, OS)")
level = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

# ---------------- QUIZ GENERATION ----------------
def generate_quiz(topic, level):
    difficulty_map = {
        "Beginner": "basic definitions and fundamentals",
        "Intermediate": "working principles, use cases, comparisons",
        "Advanced": "internal architecture, performance, edge cases"
    }

    prompt = f"""
You are an expert question paper generator.

Generate exactly 5 multiple-choice questions on the topic "{topic}"
for {level} level students.

Rules:
- Each question must be strictly related to the topic
- Each question must have exactly 4 options (A, B, C, D)
- Only ONE option must be correct
- Options must be meaningful and not repetitive
- Clearly mention the correct answer
- Do NOT add explanations
- Do NOT ask questions back
- Follow the format exactly

Format:

Q1. Question text
A. Option text
B. Option text
C. Option text
D. Option text
Answer: A

Q2. Question text
A. Option text
B. Option text
C. Option text
D. Option text
Answer: B
"""


    response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.4
)

    return response.choices[0].message.content

# ---------------- PARSE QUIZ ----------------
import re

def parse_quiz(text):
    questions = []
    blocks = re.split(r"\nQ\d+\.", text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n")
        question = re.sub(r"^Q\d+\.\s*", "", lines[0]).strip()


        options = {}
        answer = None

        for line in lines:
            line = line.strip()

            if re.match(r"^[A-D]\.", line):
                key = line[0]
                options[key] = line[3:].strip()

            if line.startswith("Answer:"):
                answer = line.split(":")[1].strip()

        if len(options) == 4 and answer:
            questions.append({
                "question": question,
                "options": options,
                "answer": answer  # <-- A / B / C / D
            })

    return questions

# ---------------- UI FLOW ----------------
if st.button("Start Quiz"):
    if not name or not topic:
        st.warning("Please enter name and topic")
    else:
        with st.spinner("Generating quiz..."):
            quiz_text = generate_quiz(topic, level)
            st.session_state.questions = parse_quiz(quiz_text)

# ---------------- DISPLAY QUIZ ----------------
if "questions" in st.session_state:
    st.subheader("📘 Quiz")

    for i, q in enumerate(st.session_state.questions):
        st.markdown(f"**Q{i+1}. {q['question']}**")

        selected = st.radio(
            "Choose one:",
            options=list(q["options"].keys()),   # A, B, C, D
            format_func=lambda x: f"{x}. {q['options'][x]}",
            index=None,                           # 🔴 critical
            key=f"q_{i}"
        )

        # ✅ STORE ONLY OPTION KEY
        if selected:
            st.session_state.user_answers[i] = selected

if st.button("Submit Quiz"):
    score = 0

    for i, q in enumerate(st.session_state.questions):
        user_ans = st.session_state.user_answers.get(i)
        if user_ans == q["answer"]:
            score += 1

    st.subheader("📊 Result")
    st.write(f"**Name:** {name}")
    st.write(f"**Topic:** {topic}")
    st.write(f"**Score:** {score} / {len(st.session_state.questions)}")

    if score <= 2:
        st.error("Needs Improvement ❌")
    elif score <= 4:
        st.warning("Good 👍")
    else:
        st.success("Excellent 🎉")



