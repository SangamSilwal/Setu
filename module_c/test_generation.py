"""
Verification Script for Module C
Tests the Letter Generation functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from module_c.interface import LetterGenerationAPI

def test_module_c():
    print("=== Testing Module C: Letter Generation ===")
    
    api = LetterGenerationAPI()
    
    # 1. Test Listing Templates
    print("\n[1] Available Templates:")
    templates = api.get_available_templates()
    for t in templates:
        print(f" - {t}")
        
    if not templates:
        print("ERROR: No templates found!")
        return

    # 2. Test Simple Generation
    print("\n[2] Testing Simple Generation (CitizenshipbyDescentApplication.txt)")
    target_template = "CitizenshipbyDescentApplication.txt"
    if target_template in templates:
        user_data = {
            "Date": "2081-01-01",
            "CDO Name": "Ram Prasad",
            "District": "Kathmandu",
            "Applicant Name": "Sita Sharma",
            "Father's Name": "Hari Sharma",
            "Mother's Name": "Gita Sharma",
            "Age": "20",
            "Municipality": "Kathmandu",
            "Ward No": "10"
        }
        result = api.generate_letter(target_template, user_data)
        if result['success']:
            print("SUCCESS: Letter Generated")
            print("--- Preview (First 200 chars) ---")
            print(result['letter'][:200] + "...")
        else:
            print(f"FAILED: {result.get('error')}")
    else:
        print(f"SKIP: {target_template} not found")

    # 3. Test Smart Generation (LLM)
    print("\n[3] Testing Smart Generation (General Application to DAO.txt)")
    target_template = "General Application to DAO.txt"
    if target_template in templates:
        description = "I am Ramesh from Lalitpur. I want to complain about the noise pollution in my area (Ward 5). It happens every night."
        
        # Check if API key is present, otherwise warn
        if not os.getenv("MISTRAL_API_KEY"):
            print("WARNING: MISTRAL_API_KEY not set. Smart generation might fail or mock.")
            
        result = api.generate_smart_letter(target_template, description)
        if result['success']:
            print("SUCCESS: Smart Letter Generated")
            print("--- Preview (First 200 chars) ---")
            print(result['letter'][:200] + "...")
        else:
            print(f"FAILED: {result.get('error')}")
    else:
        print(f"SKIP: {target_template} not found")

if __name__ == "__main__":
    test_module_c()
