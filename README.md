🏠 HomeGuardian AI

HomeGuardian AI is an AI-powered home appliance care assistant built with Python, Streamlit, LangChain, Hugging Face, FAISS, and SQLite.

It helps users add appliances from their manuals, ask appliance-specific AI questions, manage maintenance reminders, and keep repair history in one place.

✨ Main Features

Automatic Appliance Setup

Upload a PDF appliance manual and HomeGuardian automatically detects:

appliance type

brand

model

appliance name

AI Appliance Assistant

Users can ask questions such as:

Why is my appliance not working?

How do I clean it?

What does an error code mean?

What safety steps should I follow?

The assistant answers using the appliance's official manual.

RAG-Based Question Answering

PDF Manual
   ↓
Text Extraction
   ↓
Text Splitting
   ↓
Embeddings
   ↓
FAISS Vector Store
   ↓
User Question
   ↓
Semantic Search
   ↓
Relevant Manual Chunks
   ↓
Qwen LLM
   ↓
Manual-Based Answer

Maintenance Reminders

Users can:

add maintenance tasks

set reminder dates

create recurring reminders

view upcoming, overdue, and completed tasks

mark maintenance as done

Repair History

Users can store:

appliance

what happened

repair date

cost

how it was fixed

technician/company

replaced parts

warranty information

notes

The page also summarizes total repairs, total spent, and latest repair date.

Smart Dashboard

The dashboard shows:

number of appliances

care reminders

appliances needing attention

appliance status

quick actions

Clicking Ask AI on an appliance card opens the AI Assistant with that same appliance already selected.

Light and Dark Mode

A custom animated sun/moon toggle switches between light and dark themes and remembers the user's choice in the browser.

🤖 AI Models Used

Text Generation

Qwen/Qwen2.5-7B-Instruct

Used to generate the final answer from retrieved manual context.

Embeddings

sentence-transformers/all-MiniLM-L6-v2

Used to convert manual chunks and questions into vectors for semantic search.

🧠 LangChain Components

HomeGuardian uses:

langchain-core

langchain-community

langchain-text-splitters

langchain-huggingface

LangChain Document

RecursiveCharacterTextSplitter

HuggingFaceEmbeddings

FAISS

The RAG workflow is controlled with custom Python logic rather than only a prebuilt chain.

🛠️ Technology Stack

Technology

Purpose

Python

Main language

Streamlit

Web UI

SQLite

Appliance, maintenance, and repair data

LangChain

RAG/document components

Hugging Face

Embeddings and LLM access

Qwen2.5-7B-Instruct

Answer generation

all-MiniLM-L6-v2

Embeddings

FAISS

Vector search

PyMuPDF

PDF text extraction

HTML/CSS/JavaScript

Custom UI and theme toggle

🗂️ Project Structure

HomeGuardian-AI/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── pages/
│   ├── 1_🏠_Dashboard.py
│   ├── 2_➕_Add_Appliance.py
│   ├── 3_🤖_AI_Assistant.py
│   ├── 4_📅_Maintenance.py
│   └── 5_🔧_Repair_History.py
│
├── core/
│   ├── database.py
│   ├── document_processor.py
│   ├── rag_engine.py
│   ├── appliance_detector.py
│   ├── manual_service.py
│   ├── ui.py
│   └── cosmic_theme_toggle.py
│
├── data/
│   └── homeguardian.db
│
└── .streamlit/
    └── config.toml

File names can differ slightly depending on the final local version.

⚙️ How It Works

Add Appliance

Upload manual
   ↓
Extract PDF text
   ↓
Detect appliance information
   ↓
Split manual into chunks
   ↓
Create embeddings
   ↓
Store vectors in FAISS
   ↓
Save appliance

Ask AI

Choose appliance
   ↓
Ask question
   ↓
Embed question
   ↓
FAISS finds relevant chunks
   ↓
Retrieved chunks go into prompt
   ↓
Qwen generates the answer

🚀 Installation

1. Clone

git clone https://github.com/YOUR_USERNAME/HomeGuardian-AI.git
cd HomeGuardian-AI

2. Create a virtual environment

python -m venv venv

Activate on Windows:

.\venv\Scripts\Activate.ps1

3. Install dependencies

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Important packages:

streamlit
langchain
langchain-core
langchain-community
langchain-text-splitters
langchain-huggingface
sentence-transformers
huggingface-hub
faiss-cpu
pymupdf
python-dotenv
pydantic
python-docx
pandas

🔐 Environment Variables

Create a .env file in the project root:

HF_TOKEN=your_huggingface_token_here
HOMEGUARDIAN_MODEL=Qwen/Qwen2.5-7B-Instruct

Never upload your real .env file or token to GitHub.

▶️ Run the App

python -m streamlit run app.py

If your project includes run_homeguardian.bat, you can also double-click it to start the app with the correct virtual environment.

🔒 Security Notes

Do not commit .env or API tokens.

Do not commit private uploaded manuals.

Local SQLite databases should normally stay out of a public repository.

The assistant displays safety guidance for dangerous appliance situations.

📚 Concepts Applied

Python

Streamlit

UI/UX

SQLite

CRUD

relational databases

PDF processing

NLP

information extraction

embeddings

semantic search

FAISS

RAG

LLMs

Hugging Face

LangChain

session state

context-aware navigation

error handling

logging

modular architecture

virtual environments

dependency management

🔮 Future Improvements

notifications

OCR for scanned manuals

authentication

cloud database

multiple households

voice questions

automatic maintenance suggestions

faster caching

cloud deployment

👩‍💻 Author

Developed as an AI application project combining RAG, LangChain, Hugging Face, Streamlit, SQLite, and user-centered UI/UX design.

⭐ HomeGuardian AI

Upload the manual. Understand the appliance. Maintain it smarter.