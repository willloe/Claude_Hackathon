"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .config import settings
from .database import init_db
from .routes import auth, courses, materials, qa, analytics

# Create FastAPI app
app = FastAPI(
    title="AI TA Platform API",
    description="REST API for AI-powered Teaching Assistant platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(materials.router)
app.include_router(qa.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database and create necessary directories on startup."""
    # Create uploads directory
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)

    # Create ChromaDB directory
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

    # Initialize database
    init_db()
    print("Database initialized successfully!")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "AI TA Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
