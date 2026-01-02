from module_c.interface import LetterGenerationAPI

api = LetterGenerationAPI()

# Describe your need in English or Nepali
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