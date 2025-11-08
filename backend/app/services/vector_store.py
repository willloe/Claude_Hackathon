"""
ChromaDB vector store wrapper for document storage and retrieval.
"""
import chromadb
from typing import List, Dict
from .embeddings import generate_embeddings
from ..config import settings as app_settings


class VectorStore:
    """Wrapper for ChromaDB operations."""

    def __init__(self):
        """Initialize ChromaDB client."""
        # Use PersistentClient for ChromaDB 0.4.x
        self.client = chromadb.PersistentClient(
            path=app_settings.CHROMA_PERSIST_DIR
        )

    def _get_collection(self, course_id: str):
        """
        Get or create a collection for a course.

        Args:
            course_id: Course ID

        Returns:
            ChromaDB collection
        """
        collection_name = f"course_{course_id.replace('-', '_')}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"course_id": course_id}
        )

    def add_documents(self, chunks: List[Dict[str, any]], course_id: str):
        """
        Add document chunks to the vector store.

        Args:
            chunks: List of chunks with text and metadata
            course_id: Course ID
        """
        if not chunks:
            return

        collection = self._get_collection(course_id)

        # Extract texts and metadata
        texts = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]

        # Generate embeddings
        embeddings = generate_embeddings(texts)

        # Generate IDs
        ids = [f"{chunk['metadata']['material_id']}_{chunk['metadata']['chunk_index']}"
               for chunk in chunks]

        # Add to collection
        collection.add(
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
            ids=ids
        )

    def query(self, course_id: str, query_text: str, n_results: int = 5) -> List[Dict[str, any]]:
        """
        Query the vector store for relevant chunks.

        Args:
            course_id: Course ID
            query_text: Query text
            n_results: Number of results to return

        Returns:
            List of relevant chunks with metadata
        """
        collection = self._get_collection(course_id)

        # Check if collection has documents
        if collection.count() == 0:
            return []

        # Generate query embedding
        from .embeddings import generate_embedding
        query_embedding = generate_embedding(query_text)

        # Query collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count())
        )

        # Format results
        chunks = []
        if results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                chunks.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

        return chunks


# Global vector store instance
vector_store = VectorStore()
