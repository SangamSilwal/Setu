"""
Vector database module for Module C (Letter Templates)
Stores and retrieves letter templates with embeddings.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from .config import DATA_DIR

logger = logging.getLogger(__name__)

# Define Vector DB path for Module C
VECTOR_DB_DIR = DATA_DIR / "vector_db"

class TemplateVectorDB:
    """ChromaDB vector database for letter templates"""
    
    def __init__(self, persist_directory: Path = VECTOR_DB_DIR):
        """
        Initialize ChromaDB with persistent storage
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb not installed. "
                "Install with: pip install chromadb"
            )
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing Template Vector DB at {self.persist_directory}")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory)
        )
        
        # Create or get collection
        self.collection_name = "nepal_letter_templates"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Nepal letter templates for RAG generation"}
        )
        
        current_count = self.collection.count()
        logger.info(f"Collection '{self.collection_name}' ready. Count: {current_count}")
    
    def add_templates(
        self,
        templates: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ) -> None:
        """
        Add templates with embeddings to the database
        """
        if len(templates) != len(embeddings):
            raise ValueError("Number of templates must match number of embeddings")
        
        ids = [t['id'] for t in templates]
        documents = [t['text'] for t in templates]
        metadatas = [t['metadata'] for t in templates]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )
        logger.info(f"Added {len(templates)} templates to DB.")

    def query_with_embedding(
        self,
        query_embedding: List[float],
        n_results: int = 3
    ) -> Dict[str, Any]:
        """
        Query with pre-computed embedding
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
