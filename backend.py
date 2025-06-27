from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, requests, random
import numpy as np

# === FastAPI App ===
app = FastAPI()

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[" https://zafirahhh.github.io/KKHChatbot/"],  # Replace with your actual GitHub Pages link
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === File Paths ===
DATA_FILE = "data/nursing_guide_cleaned.txt"
EMBEDDING_FILE = "data/embedded_knowledge.json"
QUIZ_FILE = "data/quiz_questions.json"
CHUNK_SIZE = 300

# === Load Text Chunks ===
if not os.path.exists(DATA_FILE):
    raise FileNotFoundError(f"{DATA_FILE} not found.")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    text = f.read()

chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]

# === Get Embedding via LM Studio ===
def get_embedding(text: str):
    res = requests.post(
        "http://localhost:1234/v1/embeddings",
        json={
            "input": text,
            "model": "intfloat-multilingual-e5-large-instruct"
        }
    )
    res.raise_for_status()
    return res.json()["data"][0]["embedding"]

# === Load or Generate Embeddings ===
if os.path.exists(EMBEDDING_FILE):
    with open(EMBEDDING_FILE, "r", encoding="utf-8") as f:
        embedded_data = json.load(f)
        chunk_embeddings = np.array([item["embedding"] for item in embedded_data])
        chunks = [item["chunk"] for item in embedded_data]
else:
    embedded_data = []
    for chunk in chunks:
        embedding = get_embedding("passage: " + chunk)
        embedded_data.append({"chunk": chunk, "embedding": embedding})
    with open(EMBEDDING_FILE, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, indent=2)
    chunk_embeddings = np.array([item["embedding"] for item in embedded_data])

# === /ask Endpoint ===
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request: AskRequest):
    try:
        q_embed = get_embedding("query: " + request.question)
        sims = np.dot(chunk_embeddings, q_embed)
        top_idxs = np.argsort(sims)[-3:][::-1]
        context = "\n\n".join([chunks[i] for i in top_idxs])

        payload = {
            "model": "zephyr",
            "messages": [
                {"role": "system", "content": "You are a helpful nursing assistant. Answer based on the context only."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{request.question}"}
            ]
        }

        res = requests.post("https://child-trend-grocery-wagner.trycloudflare.com/v1/chat/completions", json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

# === /calculator Endpoint ===
class CalculatorRequest(BaseModel):
    weight: float
    age: int
    scenario: str

@app.post("/calculator")
async def calculator(request: CalculatorRequest):
    w, s = request.weight, request.scenario.lower()
    if s == "maintenance":
        fluid = w * 100 if w <= 10 else 1000 + (w - 10) * 50 if w <= 20 else 1500 + (w - 20) * 20
    elif s == "dehydration":
        fluid = w * 75
    elif s == "resuscitation":
        fluid = w * 20
    else:
        raise HTTPException(status_code=400, detail="Invalid scenario")
    return {"fluids_ml": fluid, "ml_per_hour": fluid / 24}

# === /quiz Endpoints ===
if not os.path.exists(QUIZ_FILE):
    raise FileNotFoundError("Quiz file not found.")

with open(QUIZ_FILE, "r", encoding="utf-8") as f:
    quiz_questions = json.load(f)

@app.get("/quiz")
async def get_quiz():
    return random.choice(quiz_questions)

class QuizEvaluateRequest(BaseModel):
    question_id: int
    answer: str

@app.post("/quiz/evaluate")
async def evaluate(request: QuizEvaluateRequest):
    q = next((q for q in quiz_questions if q["id"] == request.question_id), None)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    correct = request.answer.strip().lower() == q["correct_answer"].strip().lower()
    return {"correct": correct, "explanation": q["explanation"]}

# === /ping Endpoint ===
@app.get("/ping")
async def ping():
    return {"status": "online"}

# === Run Locally ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
