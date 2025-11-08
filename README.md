# AI TA Platform

A complete AI-powered Teaching Assistant platform that allows instructors to create courses, upload materials, and provide students with intelligent Q&A support using RAG (Retrieval Augmented Generation) with Claude AI.

## Features

### For Instructors
- 📚 Create and manage courses
- 📄 Upload PDF course materials (syllabus, lectures, assignments, transcripts)
- ⚙️ Configure AI TA behavior and policies
- 🧪 Test AI responses with built-in simulator
- 📊 View analytics (question count, refusals, popular topics)
- 🔍 Monitor student Q&A logs

### For Students
- 📖 Browse published courses
- 💬 Ask questions about course content
- 📌 Get AI-generated answers with source citations
- 🔗 View source references from course materials

### Technical Highlights
- **RAG Pipeline**: PDF chunking, embeddings, vector search with ChromaDB
- **Claude Integration**: Intelligent responses with citation support
- **Policy Enforcement**: Configurable AI behavior (friendly, strict, Socratic)
- **Real-time Analytics**: Track usage and identify common topics
- **Modern UI**: Clean, responsive design with Tailwind CSS

## Architecture

```
ai-ta-platform/
├── backend/          # FastAPI REST API
│   ├── app/
│   │   ├── routes/   # API endpoints
│   │   ├── services/ # RAG pipeline, PDF processing
│   │   └── models.py # Database models
├── frontend/         # React + Vite
│   └── src/
│       ├── pages/    # Route components
│       └── components/ # Reusable UI
└── uploads/          # PDF storage (gitignored)
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Anthropic API Key** (for Claude)

That's it! SQLite is built into Python, so no database server installation required.

## Quick Start

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your credentials:
# - ANTHROPIC_API_KEY (your Claude API key)
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - DATABASE_URL is already set to SQLite (no changes needed)

# Run the backend
python -m uvicorn app.main:app --reload
```

Backend will run at **http://localhost:8000**

API Documentation: **http://localhost:8000/docs**

### 2. Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Run the frontend
npm run dev
```

Frontend will run at **http://localhost:5173**

## Usage Workflow

### Demo Scenario: Complete End-to-End Flow

#### As an Instructor:

1. **Register Account**
   - Go to http://localhost:5173/register
   - Create account with role "Instructor"
   - You'll be redirected to `/instructor` dashboard

2. **Create Course**
   - Click "+ Create Course"
   - Enter course name (e.g., "CMSC 416")
   - Enter term (e.g., "Fall 2025")
   - Check "Publish immediately" if ready for students
   - Click "Create"

3. **Upload Materials**
   - Click "Manage" on your course
   - Go to "Materials" tab
   - Click "+ Upload PDF"
   - Select a PDF file
   - Choose material type (syllabus, lecture, assignment, transcript)
   - Wait for processing (PDF → chunks → embeddings → vector store)

4. **Configure AI Policies**
   - Go to "Policies" tab
   - Choose AI persona:
     - **Friendly**: Warm and encouraging
     - **Policy-First**: Strict rule enforcement
     - **Scaffolded**: Socratic questioning
   - Set allowed topics
   - Set disallowed actions (e.g., "Don't give complete assignment solutions")
   - Add custom instructions
   - Click "Save Policy"

5. **Test the AI TA**
   - Go to "Simulator" tab
   - Enter a test question
   - Click "Test Query"
   - Review AI response and citations
   - Check if refusals work as expected

6. **View Analytics**
   - Go to "Analytics" tab
   - See total questions, refusal rate
   - Review recent student questions
   - Identify common topics

#### As a Student:

1. **Register Account**
   - Go to http://localhost:5173/register
   - Create account with role "Student"
   - You'll be redirected to `/student` courses page

2. **Browse Courses**
   - View all published courses
   - See course details (term, location, office hours)

3. **Ask Questions**
   - Click "Ask Questions" on a course
   - Type your question in the chat
   - Get AI-generated answer with citations
   - Click on citation badges to see source snippets
   - Continue conversation or start new one

## Environment Variables

### Backend `.env`

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ai_ta_platform

# JWT
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Claude API
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# App
UPLOADS_DIR=./uploads
CHROMA_PERSIST_DIR=./chroma_db
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create user account
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Courses
- `POST /api/courses` - Create course (instructor)
- `GET /api/courses` - List courses
- `GET /api/courses/{id}` - Get course details
- `PUT /api/courses/{id}` - Update course (instructor)
- `DELETE /api/courses/{id}` - Delete course (instructor)

### Materials
- `POST /api/courses/{id}/materials` - Upload PDF (instructor)
- `GET /api/courses/{id}/materials` - List materials (instructor)
- `DELETE /api/materials/{id}` - Delete material (instructor)

### Policies
- `PUT /api/courses/{id}/policies` - Set/update policies (instructor)
- `GET /api/courses/{id}/policies` - Get policies (instructor)

### Q&A
- `POST /api/courses/{id}/ask` - Ask question (authenticated)
- `GET /api/courses/{id}/qa-logs` - Get Q&A history (instructor)

### Analytics
- `GET /api/courses/{id}/analytics` - Get analytics (instructor)

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for SQLite
- **Pydantic** - Data validation
- **ChromaDB** - Vector database
- **sentence-transformers** - Embedding generation
- **Anthropic Claude** - LLM for answers
- **PyPDF2** - PDF text extraction
- **tiktoken** - Token counting and chunking

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client

## Project Structure

```
ai-ta-platform/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── courses.py       # Course CRUD
│   │   │   ├── materials.py     # Material upload
│   │   │   ├── qa.py            # Q&A endpoint
│   │   │   └── analytics.py     # Analytics
│   │   ├── services/
│   │   │   ├── pdf_processor.py # PDF extraction & chunking
│   │   │   ├── embeddings.py    # Embedding generation
│   │   │   ├── vector_store.py  # ChromaDB wrapper
│   │   │   ├── claude_service.py # Claude API
│   │   │   └── rag_service.py   # RAG orchestration
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # JWT utilities
│   │   ├── dependencies.py      # Auth dependencies
│   │   ├── database.py          # DB connection
│   │   ├── config.py            # Settings
│   │   └── main.py              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── InstructorDashboard.jsx
│   │   │   ├── CourseDetail.jsx
│   │   │   ├── StudentCourses.jsx
│   │   │   └── ChatInterface.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   └── CitationBadge.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   └── package.json
└── README.md
```

## Troubleshooting

### Backend won't start
- Ensure ANTHROPIC_API_KEY is set in .env
- Check Python version (3.10+)
- Verify SECRET_KEY is set
- Delete ai_ta_platform.db and restart if database issues occur

### Frontend won't start
- Check Node.js version (18+)
- Clear node_modules: `rm -rf node_modules && npm install`
- Check backend is running on port 8000

### PDF upload fails
- Ensure file is actually a PDF
- Check UPLOADS_DIR exists and is writable
- Verify sentence-transformers model downloaded

### No answers from AI
- Check ANTHROPIC_API_KEY is valid
- Verify PDFs were processed (check `processed` field)
- Ensure ChromaDB directory exists
- Check backend logs for errors

### Citations not showing
- Verify PDFs chunked successfully
- Check vector store has documents
- Review RAG service logs

## Future Enhancements

- [ ] Multi-document question answering
- [ ] Support for more file types (DOCX, PPTX, etc.)
- [ ] Enhanced analytics with charts
- [ ] Real-time notifications
- [ ] Course templates
- [ ] Student feedback on answers
- [ ] Export Q&A logs to CSV
- [ ] Advanced search and filtering
- [ ] Dark mode

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.

## Support

For questions or issues, please create a GitHub issue.

---

Built with ❤️ for AI-powered education
