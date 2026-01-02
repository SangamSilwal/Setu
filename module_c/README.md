# Module C: RAG-Based Letter Generation

This module generates professional, bias-free Nepali government letters by combining **Retrieval-Augmented Generation (RAG)** with **LLM-based adaptation**.

Instead of manually selecting templates, users simply describe their need (e.g., "I need a citizenship certificate for my child"), and the system:
1.  **Retrieves** the most relevant official template from the vector database.
2.  **Generates** a final letter by intelligently filling the template with user details.

## Features
-   **Intent-Based Retrieval**: Finds the right template even if the user doesn't know the official name.
-   **Smart Filling**: Extracts details (Name, Date, District) from natural language.
-   **Modular Design**: Separate Indexer, Retriever, and Generator components.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install chromadb sentence-transformers mistralai python-dotenv
    ```

2.  **Environment Variables**:
    Create a `.env` file in the project root:
    ```env
    MISTRAL_API_KEY=your_api_key_here
    ```

## Usage

### 1. Python API
```python
from module_c.interface import LetterGenerationAPI

api = LetterGenerationAPI()

# Describe your need in English or Nepali
description = "I need to apply for citizenship for my daughter Sita. I am Ram Sharma from Kathmandu."

result = api.generate_smart_letter(description)

if result['success']:
    print(f"Used Template: {result['template_used']}")
    print(result['letter'])
else:
    print(f"Error: {result['error']}")
```

### 2. Interactive Flow (Handling Missing Info)
```python
# 1. Analyze Requirements
analysis = api.analyze_requirements("I need a citizenship certificate")

if analysis['success'] and analysis['missing_fields']:
    print(f"Selected Template: {analysis['template_name']}")
    print(f"Missing Fields: {analysis['missing_fields']}")
    
    # 2. Provide Missing Info
    additional_data = {
        "Date": "2081-01-01",
        "District": "Kathmandu",
        "Applicant Name": "Ram Sharma"
    }
    
    result = api.generate_smart_letter(
        "I need a citizenship certificate", 
        additional_data=additional_data
    )
    print(result['letter'])
```

### 3. Adding New Templates
1.  Add your template text file (`.txt`) to `data/module-C/`.
2.  Run the indexer to update the vector database:
    ```bash
    python module_c/indexer.py
    ```

## Project Structure
-   `interface.py`: Main entry point.
-   `retriever.py`: Finds relevant templates using Vector DB.
-   `generator.py`: Uses LLM to fill retrieved templates.
-   `indexer.py`: Ingests templates into ChromaDB.
-   `vector_db.py`: Manages ChromaDB connection.
-   `config.py`: Configuration settings.
