from fastapi import APIRouter, HTTPException
from api.schemas import LetterGenerationRequest, LetterGenerationResponse
from module_c.interface import LetterGenerationAPI

router = APIRouter()
letter_api = LetterGenerationAPI()

@router.post("/generate-letter", response_model=LetterGenerationResponse)
async def generate_letter(request: LetterGenerationRequest):
    try:
        # Check if we need to analyze or generate
        # For simplicity, we assume the user might want to generate directly
        # If additional_data is provided, we use it.
        
        result = letter_api.generate_smart_letter(
            description=request.description,
            additional_data=request.additional_data
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-requirements", response_model=LetterGenerationResponse)
async def analyze_requirements(request: LetterGenerationRequest):
    try:
        result = letter_api.analyze_requirements(request.description)
        # Map result to response schema
        return {
            "success": result.get("success", False),
            "template_used": result.get("template_name"),
            "missing_fields": result.get("missing_fields"),
            "error": result.get("error")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
