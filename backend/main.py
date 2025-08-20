
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os


app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model once at startup
model = whisper.load_model("small")

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
    # Save uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Transcribe with Whisper
    result = model.transcribe(tmp_path)

    # Remove temp file
    os.remove(tmp_path)

    print(result["text"])
    return {"text": result["text"]}
