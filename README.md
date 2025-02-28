# Document Q&A System

A modular, scalable system for document management and intelligent question answering application.

## Architecture

1. **Flask API Layer** (`app.py`)
   * RESTful endpoints for document management and question answering
   * Handles file uploads, API requests, and responses

2. **Models Layer** (`models/`)
   * `DocumentModel`: Manages document metadata in PostgreSQL
   * `EmbeddingModel`: Handles vector embeddings and similarity search

3. **Services Layer** (`services/`)
   * `QuestionAnsweringService`: Coordinates PDF processing, embedding generation, and QA

4. **Database Layer** (`db/`)
   * Connection management
   * Schema initialization
   * PostgreSQL vector search

## API Endpoints

### Document Management
* `POST /api/documents` - Upload and process a PDF
* `GET /api/documents` - List all documents
* `GET /api/documents/<doc_id>` - Get document details
* `DELETE /api/documents/<doc_id>` - Delete a document

### Question Answering
* `POST /api/question` - Answer a question using the stored knowledge

## How to Use

1. **Setup the database:**
   ```bash
   python -m db.init_db
   ```

2. **Run the Flask application:**
   ```bash
   python app.py
   ```

3. **Upload a PDF document:**
   ```bash
   curl -X POST -F "file=@document.pdf" http://localhost:5000/api/documents
   ```

4. **Ask a question:**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"question":"What is the main topic?"}' http://localhost:5000/api/question
   ```

## BUILD
## using make
```
make pull-ollama   # Pulls Ollama Docker image
make run-ollama    # Starts Ollama server
make pull-model    # Pulls Llama3 model
make check-status  # Verifies Ollama is running
make docker-build
```