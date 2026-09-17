# Production RAG Knowledge Assistant

This project is a beginner-friendly but production-minded Retrieval-Augmented Generation (RAG) application built from scratch in VS Code. It shows how to turn raw company or personal knowledge into a local AI assistant that can answer questions using documents, not just general memory.

This repo is also intentionally simple and stable for a real-world learning setup. The code avoids heavy framework complexity so you can understand every part of the flow: ingest files, chunk text, generate embeddings, search relevant context, and return an answer.

## Why this project matters for an AI/ML engineer

When recruiters or hiring managers look at AI/ML portfolios, they usually want to see more than toy demos. They want to see that you can:

- build a real end-to-end system from data to interface
- design a clean architecture
- use retrieval to ground answers in facts
- work with local documents and embeddings
- explain the system in simple terms
- use GitHub as a portfolio proof of work

This project demonstrates all of that in one app.

## Main idea

Imagine your company has an internal knowledge base: policies, onboarding docs, product notes, support FAQs, or project reports. A normal chatbot may answer based on generic training data, which can be wrong or vague. A RAG assistant instead does this:

1. Reads the documents you provide.
2. Breaks them into smaller chunks.
3. Turns each chunk into embeddings (numbers representing meaning).
4. Stores them in a vector database.
5. When you ask a question, it looks for the most similar chunks.
6. Uses those chunks to answer the question with context.

This reduces hallucination and keeps responses grounded in the docs you trust.

## What you will learn

This project helps you understand the main AI engineering flow in simple language:

- Problem definition: what do users want the system to answer?
- Data collection: what files or documents will the system use?
- Data cleaning: remove junk and keep knowledge useful
- Chunking: split long docs into smaller, searchable pieces
- Embeddings: convert text into vectors for semantic matching
- Vector database: store and retrieve relevant chunks quickly
- Prompting: feed retrieved context into the model with a clear instruction
- Evaluation: check whether the answer is helpful and grounded
- Deployment: make it run locally and push it to GitHub

## Project architecture

The app is built with a simple stack:

- Python
- Flask for the web app
- LangChain for document processing and retrieval
- Hugging Face sentence-transformers embeddings
- ChromaDB for vector storage
- Local text/PDF files as knowledge sources

### Flow

User question -> Flask app -> retrieval from Chroma -> relevant document chunks -> answer generation -> response shown in browser

## Folder structure

```text
rag-knowledge-assistant/
├── app/
│   ├── __init__.py
│   ├── rag_service.py
│   ├── routes.py
│   ├── static/
│   └── templates/
│       └── index.html
├── data/
│   ├── documents/
│   ├── uploads/
│   └── chroma-index/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── sample-knowledge.txt
```

## Step-by-step guide: how to build this project

### 1. Set up VS Code

- Install VS Code
- Install Python extension
- Open a new folder for your project
- Create a virtual environment named `.venv`

### 2. Create the project structure

Create a folder layout similar to the one above.

Keep your files organized by responsibility:

- `app/` for the Flask app
- `data/` for documents and the vector database
- `run.py` to start the app
- `requirements.txt` to install needed libraries

### 3. Add the dependencies

Use Python packages that help with retrieval and embeddings:

- Flask for the UI backend
- LangChain for document handling
- Chroma for vector search
- sentence-transformers for embeddings
- pypdf for PDF support

### 4. Add a sample knowledge base

Use small text files or PDF files containing product docs, customer FAQ, internal notes, or personal project knowledge.

This is the raw data your assistant will search through.

### 5. Chunk the documents

Large documents are too big to search directly. So the app splits them into smaller chunks such as 500-800 characters.

Why this helps:

- easier matching to user questions
- smaller context for retrieval
- better precision

### 6. Generate embeddings

Each chunk is converted into an embedding vector. These vectors capture the semantic meaning of the text.

This is the magic behind "similar meaning" search.

### 7. Store embeddings in a vector database

A vector database stores those embeddings and allows fast search for the most relevant chunk when a user asks a question.

### 8. Build the user interface

Use a basic HTML page with:

- input box for the question
- ask button
- response area
- upload area for new docs
- list of available files

### 9. Query flow

When the user enters a question:

- app receives the question
- queries the vector database
- finds the most relevant document pieces
- combines them into context
- sends answer to frontend

### 10. Improve quality

A basic RAG app is a start, not the end. To make it production-quality, you should later add:

- better chunking strategies
- metadata filters
- PDF and document ingestion
- better prompt templates
- conversation memory
- user feedback collection
- evals for answer quality
- logging and monitoring
- API security
- deployment to cloud

## Local setup instructions

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Activate it

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
python run.py
```

Then open:

```text
http://localhost:5000
```

## Free deployment with Render

This repository includes a `render.yaml` Blueprint for Render's free web service tier.

1. Open the Render dashboard and choose **New > Blueprint**.
2. Connect the `mano1310/Production-RAG-Knowledge-Assistant` repository.
3. Select the `main` branch and apply the Blueprint.

Render installs the dependencies and starts the app with Gunicorn. The free service may sleep after inactivity and uploaded files are not persistent across redeploys.

## Example questions

- What is the purpose of this knowledge assistant?
- How does RAG reduce hallucination?
- What are the best practices for AI/ML portfolios?
- What should an AI engineer focus on while building projects?

## GitHub portfolio tips

To make this project stand out to recruiters:

- put a strong README with architecture and setup steps
- show commit history for the build process
- explain trade-offs and design decisions
- include screenshots or a demo GIF
- add a short "what I learned" section
- keep your project reproducible with clear setup instructions

## Recommended next steps after this project

Once this project works, you can extend it to:

- multi-document PDF ingestion
- chatbot conversation memory
- user authentication
- vector DB with metadata filtering
- deployment on Render, Railway, or Azure
- LLM integration with OpenAI or Azure OpenAI
- evaluation framework and feedback loop

## Final note

This is a solid project for a portfolio because it shows your understanding of how actual AI systems work beyond simple prompt demos. It combines backend development, data engineering, embeddings, retrieval, UI, and product thinking in one real use case.

If you want to become an AI/ML engineer, build projects like this, explain them clearly, and keep improving them with real-world features.
