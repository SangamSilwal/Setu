"""
Retriever Module for Module C
Finds relevant templates based on user query/intent.
"""

import logging
from typing import List, Dict, Any
from .vector_db import TemplateVectorDB
from module_a.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class TemplateRetriever:
    """
    Retrieves the most relevant letter templates for a given user query.
    """
    
    def __init__(self):
        self.db = TemplateVectorDB()
        self.embedder = EmbeddingGenerator()
        
    def retrieve_templates(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        """
        Retrieve top-k templates matching the query.
        """
        logger.info(f"Retrieving templates for query: {query}")
        
        # 1. Embed Query
        query_embedding = self.embedder.generate_embedding(query)
        
        # 2. Query DB
        results = self.db.query_with_embedding(query_embedding.tolist(), n_results=k)
        
        # 3. Format Results
        retrieved = []
        if results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                
                retrieved.append({
                    "filename": results['ids'][0][i],
                    "content": doc,
                    "metadata": metadata,
                    "score": 1.0 - distance # Approximate similarity score
                })
                
        logger.info(f"Found {len(retrieved)} templates.")
        return retrieved
