# 🏠 HomeGuardian AI

HomeGuardian AI is an **AI-powered home appliance care assistant** that helps users understand, maintain, and troubleshoot their home appliances using their official appliance manuals.

The application combines **Retrieval-Augmented Generation (RAG), LangChain, Hugging Face models, FAISS, SQLite, and Streamlit** to provide appliance-specific AI assistance.

---

## 🎯 Project Idea

Home appliance manuals are often long, technical, and difficult for normal users to understand.

HomeGuardian AI simplifies this process by allowing the user to upload an appliance manual. The system processes the manual, automatically identifies appliance information, and allows the user to ask questions in natural language.

The application also helps users manage:

- Appliance information
- Maintenance reminders
- Repair history
- Repair costs
- AI troubleshooting

---

# ✨ Main Features

## 🏠 Smart Dashboard

The dashboard provides an overview of the user's appliances and their current care status.

It shows information such as:

- Number of appliances
- Upcoming maintenance
- Appliances needing attention
- Appliance status
- Quick access to AI assistance

Each appliance has an **Ask AI** button.

When the user clicks Ask AI for a specific appliance, HomeGuardian automatically opens the AI Assistant with that appliance selected.

---

## ➕ Automatic Appliance Setup

Users can add an appliance by uploading its **PDF manual**.

Instead of asking the user to manually enter many fields, HomeGuardian attempts to automatically detect:

- Appliance type
- Brand
- Model
- Appliance name

This makes appliance setup simple and user-friendly.

---

## 🤖 AI Assistant

The AI Assistant allows users to ask questions about a specific appliance.

Examples:

```text
Why is my refrigerator not cooling?

How should I clean the filter?

What does this error code mean?

How often should I maintain this appliance?

What should I check if the appliance does not start?
```

HomeGuardian searches the appliance manual and uses the relevant information to generate the answer.

---

# 🧠 Retrieval-Augmented Generation — RAG

HomeGuardian uses **Retrieval-Augmented Generation (RAG)**.

Instead of asking the language model to answer only from its general knowledge, the system first searches the uploaded appliance manual.

### RAG Workflow

```text
Appliance Manual PDF
        ↓
PDF Text Extraction
        ↓
Document Creation
        ↓
Text Splitting
        ↓
Text Embeddings
        ↓
FAISS Vector Database
        ↓
User Question
        ↓
Semantic Search
        ↓
Relevant Manual Sections
        ↓
Qwen Language Model
        ↓
Final Manual-Based Answer
```

This allows the AI Assistant to provide answers that are more relevant to the selected appliance.

---

# 🤖 AI Models Used

## Answer Generation Model

```text
Qwen/Qwen2.5-7B-Instruct
```

The Qwen model is used to generate the final response after HomeGuardian retrieves relevant information from the appliance manual.

---

## Embedding Model

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model converts manual text and user questions into numerical vectors.

These vectors allow HomeGuardian to perform **semantic search**, meaning it searches based on meaning rather than only exact words.

---

# 🔗 LangChain Usage

HomeGuardian uses several components from the LangChain ecosystem.

### LangChain Components

```text
langchain-core
langchain-community
langchain-text-splitters
langchain-huggingface
```

The project uses:

- LangChain `Document` objects
- `RecursiveCharacterTextSplitter`
- `HuggingFaceEmbeddings`
- FAISS integration
- Semantic similarity search

---

## Document Splitting

Large appliance manuals cannot efficiently be processed as one large piece of text.

HomeGuardian uses:

```python
RecursiveCharacterTextSplitter
```

to divide the manual into smaller chunks.

```text
Full Manual
    ↓
Chunk 1
Chunk 2
Chunk 3
Chunk 4
...
```

Each chunk can then be searched independently.

---

## Embeddings

HomeGuardian uses:

```python
HuggingFaceEmbeddings
```

with:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embeddings represent the meaning of each manual section numerically.

---

## FAISS Vector Search

The generated vectors are stored using **FAISS**.

FAISS allows HomeGuardian to quickly find the manual sections that are most similar to the user's question.

Example:

```text
User:
"My refrigerator is warm"

        ↓

Semantic Search

        ↓

Manual sections about:
- cooling problems
- blocked airflow
- temperature settings
- door problems
```

---

# 📅 Maintenance Reminders

HomeGuardian includes a maintenance management system.

Users can:

- Add maintenance tasks
- Select an appliance
- Choose a due date
- Create recurring maintenance
- View upcoming maintenance
- View overdue maintenance
- Mark maintenance as completed

Examples:

```text
Clean AC filter

Replace refrigerator water filter

Clean washing machine drum

Check water heater

Clean laptop cooling vents
```

---

# 🔧 Repair History

Users can also keep a history of appliance repairs.

A repair record can contain:

- Appliance
- Problem
- Repair date
- Repair cost
- How it was fixed
- Technician or company
- Replaced parts
- Warranty information
- Additional notes

The Repair History dashboard can also display:

- Total repairs
- Total amount spent
- Most recent repair

---

# 🗄️ Database

HomeGuardian uses **SQLite** for local data storage.

The database stores information related to:

```text
Appliances
Maintenance Tasks
Repair History
Reminders
Manual Information
```

Example relationships:

```text
Appliance
   │
   ├── Maintenance Tasks
   │
   ├── Repair History
   │
   └── Appliance Manual
```

---

# 📄 PDF Processing

HomeGuardian uses **PyMuPDF** to process uploaded PDF appliance manuals.

The general process is:

```text
Upload PDF
    ↓
Extract Text
    ↓
Detect Appliance Information
    ↓
Create Documents
    ↓
Split Documents
    ↓
Generate Embeddings
    ↓
Create FAISS Index
```

---

# 🎨 User Interface

The interface is built using **Streamlit**.

HomeGuardian contains five main pages:

```text
🏠 Dashboard

➕ Add Appliance

🤖 AI Assistant

📅 Maintenance

🔧 Repair History
```

The interface was designed to be simple for non-technical users.

The application minimizes unnecessary manual input and allows AI to perform as much of the setup as possible.

---

# 🌙 Light & Dark Mode

HomeGuardian includes a custom light/dark mode switch.

The interface contains:

- Dark theme
- Light theme
- Sun/Moon toggle
- Browser theme persistence
- Custom CSS
- Custom JavaScript

The selected theme is remembered while using the application.

---

# 🔄 Context-Aware Navigation

HomeGuardian uses Streamlit Session State to pass information between pages.

For example:

```text
Dashboard
   ↓
User clicks "Ask AI" on Toshiba appliance
   ↓
Toshiba appliance ID is saved
   ↓
AI Assistant opens
   ↓
Toshiba is automatically selected
```

This creates a smoother user experience.

---

# ⚠️ Error Handling

HomeGuardian includes custom error handling.

Instead of displaying large technical Python errors directly to the user, the application can display a friendly message such as:

```text
This page could not finish loading.
Your saved information is safe.
```

The interface provides options such as:

```text
Try Again

Return to Dashboard

Technical Details
```

Errors can also be stored in log files for debugging.

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application interface |
| SQLite | Local database |
| LangChain | RAG and document processing |
| Hugging Face | AI models |
| Qwen2.5-7B-Instruct | Answer generation |
| all-MiniLM-L6-v2 | Embeddings |
| FAISS | Vector database and semantic search |
| PyMuPDF | PDF text extraction |
| HTML | Custom interface elements |
| CSS | Application styling |
| JavaScript | Theme and UI behavior |

---

# 📂 Project Structure

```text
HomeGuardian-AI/
│
├── app.py
├── requirements.txt
├── README.md
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
├── pages/
│   ├── 1_🏠_Dashboard.py
│   ├── 2_➕_Add_Appliance.py
│   ├── 3_🤖_AI_Assistant.py
│   ├── 4_📅_Maintenance.py
│   └── 5_🔧_Repair_History.py
│
├── data/
│
└── .streamlit/
    └── config.toml
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/HomeGuardian-AI.git
```

Then:

```bash
cd HomeGuardian-AI
```

---

## 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 3. Install dependencies

```powershell
python -m pip install --upgrade pip
```

Then:

```powershell
python -m pip install -r requirements.txt
```

---

# 📦 Main Python Dependencies

The project uses packages such as:

```text
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
```

---

# 🔐 Environment Variables

Create a file named:

```text
.env
```

inside the project folder.

Example:

```env
HF_TOKEN=your_huggingface_token_here

HOMEGUARDIAN_MODEL=Qwen/Qwen2.5-7B-Instruct
```

> ⚠️ Never upload your real `.env` file or Hugging Face API token to GitHub.

---

# ▶️ Running HomeGuardian

After activating the virtual environment:

```powershell
python -m streamlit run app.py
```

The application will then open in the browser.

---

# 🚀 Windows Quick Launcher

The project can also use:

```text
run_homeguardian.bat
```

to automatically launch the application using the correct virtual environment.

This avoids manually activating the virtual environment every time.

---

# 🔒 Security

Sensitive information should not be uploaded to the public repository.

The following files should be included in `.gitignore`:

```text
.env
venv/
__pycache__/
*.log
data/*.db
uploaded_manuals/
vector_stores/
```

This protects:

- Hugging Face API tokens
- Local database information
- Uploaded manuals
- Generated vector indexes
- Local Python environments

---

# 🧩 Software Architecture

HomeGuardian separates different responsibilities into modules.

```text
UI Layer
    ↓
Streamlit Pages

Application Logic
    ↓
Manual Service
Appliance Detection
Maintenance Logic

AI Layer
    ↓
Document Processing
Embeddings
FAISS
RAG
Qwen

Data Layer
    ↓
SQLite Database
```

This modular structure improves:

- Maintainability
- Reusability
- Readability
- Scalability

---

# 📚 Concepts Learned and Applied

HomeGuardian demonstrates practical knowledge of:

### Software Development
- Python
- Modular programming
- Functions
- Exception handling
- Virtual environments
- Dependency management

### Web Development
- Streamlit
- HTML
- CSS
- JavaScript
- Session State
- Multipage applications

### Database
- SQLite
- CRUD operations
- Relational database concepts

### Artificial Intelligence
- Large Language Models
- Natural Language Processing
- Hugging Face
- Prompt construction
- Information extraction

### RAG
- Document loading
- Text splitting
- Embeddings
- Vector databases
- Semantic search
- Retrieval
- Context-based generation

### LangChain
- Documents
- Text splitters
- Hugging Face integrations
- FAISS integration

### User Experience
- Automatic appliance detection
- Context-aware navigation
- Simple forms
- Light/Dark mode
- Friendly error handling

---

# 🔮 Future Improvements

Possible future versions of HomeGuardian could include:

- User accounts
- Cloud database
- Email notifications
- Mobile notifications
- OCR for scanned manuals
- Voice AI Assistant
- Multiple households
- Cloud deployment
- Automatic maintenance recommendations
- More appliance categories
- Faster model caching
- Smart appliance integration
- Mobile application

---

# 💡 Project Goal

The main goal of HomeGuardian AI is to make appliance care easier for normal users.

Instead of reading a long technical manual, the user can simply:

```text
Upload Manual
      ↓
Add Appliance
      ↓
Ask AI
      ↓
Get Manual-Based Help
      ↓
Track Maintenance
      ↓
Track Repairs
```

---

# ⭐ HomeGuardian AI

### Upload the manual. Understand the appliance. Maintain it smarter.

Built using:

**Python • Streamlit • RAG • LangChain • Hugging Face • FAISS • SQLite**
