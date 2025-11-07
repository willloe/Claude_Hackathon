# AI TA Platform - Backend

FastAPI-based REST API for the AI Teaching Assistant platform.

## Features

- **RESTful API** with automatic OpenAPI documentation
- **JWT Authentication** with role-based access control
- **RAG Pipeline** for intelligent question answering
- **Vector Search** with ChromaDB
- **PDF Processing** with chunking and embedding generation
- **Claude Integration** for high-quality AI responses
- **PostgreSQL** for relational data storage

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_ta_platform
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key
```

Generate SECRET_KEY:
```bash
openssl rand -hex 32
```

### 3. Set Up Database

```bash
# Create PostgreSQL database
createdb ai_ta_platform

# Or using psql:
psql -U postgres -c "CREATE DATABASE ai_ta_platform;"
```

The application will automatically create tables on first run.

### 4. Run the Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server will start at: **http://localhost:8000**

API Docs: **http://localhost:8000/docs**

## Project Structure

```
backend/
├── app/
│   ├── routes/              # API endpoints
│   │   ├── auth.py         # User authentication
│   │   ├── courses.py      # Course management
│   │   ├── materials.py    # Material upload/delete
│   │   ├── qa.py           # Question answering
│   │   └── analytics.py    # Usage analytics
│   ├── services/            # Business logic
│   │   ├── pdf_processor.py    # PDF text extraction
│   │   ├── embeddings.py       # Embedding generation
│   │   ├── vector_store.py     # ChromaDB wrapper
│   │   ├── claude_service.py   # Claude API calls
│   │   └── rag_service.py      # RAG orchestration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── auth.py             # JWT utilities
│   ├── dependencies.py     # FastAPI dependencies
│   ├── database.py         # DB connection
│   ├── config.py           # Settings
│   └── main.py             # App entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Database Models

### User
- **id**: UUID (PK)
- **email**: String (unique)
- **password_hash**: String
- **name**: String
- **role**: Enum (instructor, student)
- **created_at**: Timestamp

### Course
- **id**: UUID (PK)
- **name**: String
- **term**: String
- **owner_id**: UUID (FK → User)
- **is_published**: Boolean
- **office_hours**: String (optional)
- **instructor_email**: String (optional)
- **location**: String (optional)
- **late_policy**: Text (optional)
- **created_at**: Timestamp

### CourseMaterial
- **id**: UUID (PK)
- **course_id**: UUID (FK → Course)
- **filename**: String
- **file_type**: Enum (syllabus, lecture, assignment, transcript)
- **storage_path**: String
- **processed**: Boolean
- **chunk_count**: Integer
- **created_at**: Timestamp

### CoursePolicy
- **id**: UUID (PK)
- **course_id**: UUID (FK → Course, unique)
- **persona**: Enum (policy_first, friendly, scaffolded)
- **allowed_topics**: Text
- **disallowed_actions**: Text
- **custom_instructions**: Text
- **created_at**: Timestamp

### QALog
- **id**: UUID (PK)
- **course_id**: UUID (FK → Course)
- **user_id**: UUID (FK → User)
- **question_text**: Text
- **answer_text**: Text
- **sources**: JSONB (array of source objects)
- **was_refused**: Boolean
- **created_at**: Timestamp

## RAG Pipeline

### 1. PDF Ingestion
```python
# services/pdf_processor.py
- Extract text from PDF pages
- Chunk text into 600-800 token segments
- Preserve page numbers for citations
```

### 2. Embedding Generation
```python
# services/embeddings.py
- Use sentence-transformers (all-MiniLM-L6-v2)
- Generate 384-dimensional embeddings
- Batch processing for efficiency
```

### 3. Vector Storage
```python
# services/vector_store.py
- Store embeddings in ChromaDB
- One collection per course
- Metadata: course_id, material_id, filename, page, chunk_index
```

### 4. Retrieval
```python
# services/vector_store.py
- Query with student question
- Filter by course_id
- Return top 5 most relevant chunks
- Include source metadata
```

### 5. Generation
```python
# services/rag_service.py
- Build system prompt with policies
- Include retrieved chunks as context
- Call Claude API (claude-sonnet-4-20250514)
- Parse response for citations
- Detect policy violations
```

## API Endpoints

### Authentication

**POST /api/auth/register**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "instructor"
}
```

**POST /api/auth/login**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**GET /api/auth/me**
- Headers: `Authorization: Bearer <token>`

### Courses

**POST /api/courses** (Instructor only)
```json
{
  "name": "CMSC 416",
  "term": "Fall 2025",
  "is_published": true
}
```

**GET /api/courses**
- Returns user's courses (instructor) or published courses (student)

**PUT /api/courses/{id}** (Instructor only)
```json
{
  "is_published": true,
  "office_hours": "Mon 2-4pm"
}
```

### Materials

**POST /api/courses/{id}/materials** (Instructor only)
- Content-Type: multipart/form-data
- Fields: `file` (PDF), `file_type` (syllabus/lecture/assignment/transcript)

**GET /api/courses/{id}/materials** (Instructor only)

**DELETE /api/materials/{id}** (Instructor only)

### Policies

**PUT /api/courses/{id}/policies** (Instructor only)
```json
{
  "persona": "friendly",
  "allowed_topics": "Course concepts, assignments",
  "disallowed_actions": "No complete solutions",
  "custom_instructions": "Be encouraging"
}
```

### Q&A

**POST /api/courses/{id}/ask**
```json
{
  "question": "What is RAG?"
}
```

Response:
```json
{
  "answer": "RAG stands for...",
  "sources": [
    {
      "filename": "lecture1.pdf",
      "page": 5,
      "chunk_text": "..."
    }
  ],
  "was_refused": false
}
```

### Analytics

**GET /api/courses/{id}/analytics** (Instructor only)

Returns:
```json
{
  "total_questions": 42,
  "refusal_count": 3,
  "refusal_rate": 7.14,
  "recent_questions": [...],
  "top_topics": ["RAG", "embeddings", ...]
}
```

## Testing

```bash
# Run with test mode
pytest

# Or test manually with curl
curl http://localhost:8000/health
```

## Common Issues

### ChromaDB errors
- Delete `chroma_db/` directory and restart
- Ensure sufficient disk space

### PDF processing fails
- Check PDF is not encrypted/password protected
- Verify PyPDF2 can read the file
- Check file permissions

### Claude API errors
- Verify API key is valid
- Check account has credits
- Review rate limits

## Performance Tips

- Use ChromaDB persistent storage (set CHROMA_PERSIST_DIR)
- Cache embedding model in memory
- Index frequently queried fields in PostgreSQL
- Use connection pooling for database

## Security

- Always hash passwords (bcrypt)
- Validate all file uploads
- Use parameterized queries (SQLAlchemy handles this)
- Implement rate limiting in production
- Use HTTPS in production
- Rotate SECRET_KEY regularly

## Deployment

For production deployment:

```bash
# Use production WSGI server
pip install gunicorn

# Run with workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use Docker
docker build -t ai-ta-backend .
docker run -p 8000:8000 ai-ta-backend
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | Required |
| SECRET_KEY | JWT signing key | Required |
| ANTHROPIC_API_KEY | Claude API key | Required |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 1440 (24h) |
| UPLOADS_DIR | PDF storage directory | ./uploads |
| CHROMA_PERSIST_DIR | ChromaDB storage | ./chroma_db |

---

For frontend setup, see `frontend/README.md`
