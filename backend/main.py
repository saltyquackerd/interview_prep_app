
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from whisper_utils import transcribe_audio_file
from llama3_utils import get_llama3_question
from rag_utils import process_resume, get_relevant_chunks
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")
app = FastAPI()



# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Static questions for roles
ROLE_QUESTIONS = {
    "software engineer": [
        "Describe a challenging software project you worked on.",
        "How do you ensure code quality?",
        "Explain the concept of RESTful APIs.",
        "What is your experience with version control systems?",
        "How do you approach debugging complex issues?"
    ],
    "data scientist": [
        "How do you handle missing data in a dataset?",
        "Explain the difference between supervised and unsupervised learning.",
        "Describe a machine learning project you've worked on.",
        "What is regularization in machine learning?",
        "How do you evaluate model performance?"
    ]
}

# Simple chat interview stateful endpoint (no resume)
from fastapi import Body
from typing import List, Dict, Optional

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    logger.info("[API] /upload_resume called with file: %s", file.filename)
    try:
        process_resume(await file.read(), file.filename)
        logger.info("[API] process_resume completed successfully.")
        return {"message": "Resume uploaded, processed, and indexed in ChromaDB."}
    except Exception as e:
        logger.exception("[API] Error in /upload_resume: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Resume processing failed: {str(e)}")

@app.post("/chat_interview")
def chat_interview(
    role: str = Body(...),
    history: Optional[List[Dict[str, str]]] = Body(default=[])
):
    role_key = role.strip().lower()
    # If no history, start with intro
    if not history:
        return {"reply": f"Let's begin your interview for the role of {role.title()}. Tell me about yourself."}

    # RAG: Retrieve relevant resume chunks for the last user answer
    last_user = next((turn["text"] for turn in reversed(history) if turn.get("role") == "user"), "")
    relevant_chunks = get_relevant_chunks(last_user)

    # Build chat history for Llama 3, with RAG context
    chat_messages = []
    rag_context = "\n".join(relevant_chunks)
    chat_messages.append({
        "role": "system",
        "content": f"You are an expert interviewer for a {role} position. Here are the most relevant parts of the candidate's resume:\n{rag_context}\n\nBased on the resume and the following conversation, ask the next most relevant interview question. Only reply with the next question."
    })
    for turn in history:
        if turn.get("role") == "bot":
            chat_messages.append({"role": "assistant", "content": turn.get("text", "")})
        else:
            chat_messages.append({"role": "user", "content": turn.get("text", "")})

    try:
        next_question = get_llama3_question(chat_messages)
        if not next_question:
            raise ValueError("Empty model output")
        return {"reply": next_question}
    except Exception as e:
        print(e)
        questions = ROLE_QUESTIONS.get(role_key, [])
        q_idx = len(history) - 1  # 1st answer is intro, then Q1, Q2, ...
        if q_idx < len(questions):
            return {"reply": questions[q_idx]}
        return {"reply": "Thank you for completing the interview!"}

from fastapi import Query

@app.get("/questions")
def get_questions(role: str = Query(..., description="Role to get questions for")):
    role_key = role.strip().lower()
    questions = ROLE_QUESTIONS.get(role_key)
    if not questions:
        return {"questions": [f"No questions found for role: {role}"]}
    return {"questions": questions}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    text = transcribe_audio_file(await file.read())
    print(text)
    return {"text": text}
