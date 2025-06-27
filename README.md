# 🤖 KKH Nursing Chatbot

A web-based medical assistant chatbot designed for KK Women's and Children's Hospital. This AI-powered chatbot helps users retrieve reliable nursing knowledge, perform pediatric fluid calculations, and take interactive quizzes—all based on hospital-approved reference material.

![Chatbot UI Screenshot](preview.png) <!-- Optional: replace with your own image -->

---

## 🩺 Features

- 💬 **Chat Mode** — Ask nursing-related questions, get context-based answers
- 🧪 **Fluid Calculator** — Calculates pediatric fluid needs (maintenance, resuscitation, dehydration)
- 📚 **Quiz Mode** — Practice MCQs generated from the hospital handbook
- 🗂 **Session History** — Grouped chat/quiz sessions with renaming & deletion
- 🧠 **AI Models Used**
  - `Zephyr-7B` for response generation via LM Studio
  - `intfloat/multilingual-e5-large-instruct` for semantic search (embedding model)

---

## 🧱 Tech Stack

| Layer       | Tool/Framework                  |
|-------------|----------------------------------|
| Frontend    | HTML, CSS, JavaScript (GitHub Pages) |
| Backend     | FastAPI (Python)                |
| Deployment  | Fly.io or Cloudflare Tunnel     |
| Embeddings  | Sentence Transformers via LM Studio |
| LLM         | Zephyr 7B (hosted in LM Studio) |

---

## ⚙️ How It Works

1. Extract content from `nursing_guide_cleaned.txt` and split into chunks
2. Encode chunks using `intfloat/multilingual-e5-large-instruct` via LM Studio `/v1/embeddings`
3. Store top similar chunks based on cosine similarity with user's question
4. Send prompt to Zephyr-7B via LM Studio `/v1/chat/completions`
5. Return and display response in a friendly UI

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/zafirahhh/KKHChatbot.git
cd KKHChatbot
