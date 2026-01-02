"""
Indexer Module for Module C
Ingests templates from the data directory into the Vector DB.
"""

import logging
import sys
from pathlib import Path

# Add project root to path to allow importing module_a
sys.path.append(str(Path(__file__).parent.parent))

from module_c.config import TEMPLATE_DIR
from module_c.template_loader import TemplateLoader
from module_c.vector_db import TemplateVectorDB
from module_a.embeddings import EmbeddingGenerator  # Reuse Module A's embedder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_index():
    logger.info("Starting Template Indexing...")
    
    # 1. Load Templates
    loader = TemplateLoader(TEMPLATE_DIR)
    template_files = loader.list_templates()
    
    if not template_files:
        logger.warning("No templates found to index.")
        return

    templates_data = []
    texts = []
    
    for filename in template_files:
        content = loader.load_template(filename)
        placeholders = list(loader.extract_placeholders(content))
        
        # Create a rich representation for embedding
        # We include the filename as it often contains the intent (e.g. "CitizenshipApplication")
        # and the content itself.
        text_for_embedding = f"Template Name: {filename}\nContent:\n{content}"
        
        templates_data.append({
            "id": filename,
            "text": content,
            "metadata": {
                "filename": filename,
                "placeholders": ", ".join(placeholders)
            }
        })
        texts.append(text_for_embedding)
        logger.info(f"Loaded: {filename}")

    # 2. Generate Embeddings
    logger.info("Generating embeddings...")
    embedder = EmbeddingGenerator()
    embeddings = embedder.generate_embeddings_batch(texts)
    
    # 3. Store in Vector DB
    logger.info("Storing in Vector DB...")
    db = TemplateVectorDB()
    
    # Optional: Reset collection to avoid duplicates on re-run
    # In a real app, we might check existence, but for hackathon, simple overwrite/add is fine.
    # Chroma's `add` will error on duplicate IDs, so let's use `upsert` if available or just `add`.
    # Since we use filename as ID, `add` might fail if already exists.
    # Let's try to delete and recreate for a clean slate or just catch error.
    try:
        db.client.delete_collection(db.collection_name)
        db.collection = db.client.create_collection(db.collection_name)
    except Exception:
        pass # Collection might not exist

    db.add_templates(templates_data, embeddings.tolist())
    
    logger.info("Indexing Complete!")

if __name__ == "__main__":
    build_index()
