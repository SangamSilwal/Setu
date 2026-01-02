"""
Verification Script for Module C (Interactive Flow)
Tests the analyze_requirements functionality.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from module_c.interface import LetterGenerationAPI

def test_interactive_flow():
    print("=== Testing Module C: Interactive Flow ===")
    
    api = LetterGenerationAPI()
    
    # 1. Analyze Requirements
    description = "I need a citizenship certificate for my child"
    print(f"\n[1] Analyzing Description: '{description}'")
    
    if not os.getenv("MISTRAL_API_KEY"):
        print("WARNING: MISTRAL_API_KEY not set. Analysis might fail.")

    analysis = api.analyze_requirements(description)
    
    if analysis['success']:
        print(f" -> Template Found: {analysis['template_name']}")
        print(f" -> Detected Placeholders: {analysis['detected_placeholders']}")
        print(f" -> Missing Fields: {analysis['missing_fields']}")
        
        if analysis['missing_fields']:
            print("\n[2] Providing Missing Info and Generating")
            # Simulate user providing data
            additional_data = {
                "Date": "2081-01-01",
                "District": "Kathmandu",
                "Applicant Name": "Ram Sharma",
                "Applicant Address": "Kathmandu-10",
                "Ward No": "10",
                "Municipality": "Kathmandu",
                "Father's Name": "Hari Sharma",
                "Mother's Name": "Gita Sharma",
                "Age": "20",
                "CDO Name": "Chief District Officer"
            }
            
            result = api.generate_smart_letter(description, additional_data)
            if result['success']:
                print("SUCCESS: Letter Generated with Additional Data")
                print("--- Preview ---")
                print(result['letter'][:200] + "...")
            else:
                print(f"FAILED: {result.get('error')}")
        else:
            print("No missing fields detected (unexpected for this short description).")
            
    else:
        print(f"Analysis Failed: {analysis.get('error')}")

if __name__ == "__main__":
    test_interactive_flow()
