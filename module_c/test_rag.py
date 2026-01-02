"""
Verification Script for Module C (RAG Architecture)
Tests the RAG-based Letter Generation functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from module_c.interface import LetterGenerationAPI
from module_c.retriever import TemplateRetriever

def test_module_c_rag():
    print("=== Testing Module C: RAG Letter Generation ===")
    
    # 1. Test Retrieval Directly
    print("\n[1] Testing Retrieval Logic")
    retriever = TemplateRetriever()
    
    queries = [
        ("I need a citizenship certificate for my child", "CitizenshipbyDescentApplication.txt"),
        ("I want to complain about noise in my ward", "General Application to DAO.txt"),
        ("I need a recommendation letter from ward office", "WardOfficeRecommendationRequest.txt")
    ]
    
    for query, expected in queries:
        print(f"\nQuery: '{query}'")
        results = retriever.retrieve_templates(query, k=1)
        if results:
            top_match = results[0]['filename']
            print(f" -> Retrieved: {top_match}")
            if top_match == expected:
                print(" -> [PASS] Correct template found.")
            else:
                print(f" -> [WARN] Expected {expected}, got {top_match}")
        else:
            print(" -> [FAIL] No templates retrieved.")

    # 2. Test End-to-End Generation
    print("\n[2] Testing End-to-End RAG Generation")
    api = LetterGenerationAPI()
    
    description = "I need a citizenship certificate for my daughter Sita. I am Ram Sharma from Kathmandu Ward 10. Date is 2081-01-01."
    
    if not os.getenv("MISTRAL_API_KEY"):
        print("WARNING: MISTRAL_API_KEY not set. Generation might fail.")
        
    result = api.generate_smart_letter(description)
    
    if result['success']:
        print("SUCCESS: Letter Generated")
        print(f"Template Used: {result.get('template_used')}")
        print("--- Preview (First 200 chars) ---")
        print(result['letter'][:200] + "...")
    else:
        print(f"FAILED: {result.get('error')}")

if __name__ == "__main__":
    test_module_c_rag()
