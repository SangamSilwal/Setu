"""
Letter Generator Module
Combines templates with user data to produce final letters.
"""

import logging
from typing import Dict, Any, Optional
from .template_loader import TemplateLoader
from .llm_client import MistralClient

logger = logging.getLogger(__name__)

class LetterGenerator:
    """
    Handles the generation of letters from templates and user data.
    """
    
    def __init__(self):
        self.loader = TemplateLoader()
        try:
            self.llm = MistralClient()
        except Exception as e:
            logger.warning(f"LLM Client could not be initialized: {e}. LLM features will be disabled.")
            self.llm = None

    def generate_letter(self, template_name: str, user_data: Dict[str, str]) -> str:
        """
        Generate a letter by filling in a template with user data.
        Performs simple substitution.
        """
        template_text = self.loader.load_template(template_name)
        
        # 1. Simple Substitution
        # We iterate through keys in user_data and replace corresponding placeholders
        # We try to match [Key], {{Key}}, <Key>
        
        generated_text = template_text
        
        for key, value in user_data.items():
            # Replace [Key]
            generated_text = generated_text.replace(f"[{key}]", str(value))
            # Replace {{Key}}
            generated_text = generated_text.replace(f"{{{{{key}}}}}", str(value))
            # Replace <Key>
            generated_text = generated_text.replace(f"<{key}>", str(value))
            # Replace {Key}
            generated_text = generated_text.replace(f"{{{key}}}", str(value))
            
        return generated_text

    def refine_with_llm(self, draft_letter: str, instructions: str = "") -> str:
        """
        Use LLM to polish or refine the letter.
        """
        if not self.llm:
            logger.warning("LLM not available for refinement.")
            return draft_letter
            
        prompt = f"""
You are a helpful legal assistant for Nepal.
Please refine the following letter to be more professional and grammatically correct.
Ensure it remains factual to the original content.
Do not add any fake information.

Instructions: {instructions}

Draft Letter:
{draft_letter}

Refined Letter:
"""
        return self.llm.generate_response(prompt)

    def analyze_requirements(self, description: str) -> Dict[str, Any]:
        """
        Analyzes the user description against the best matching template
        to identify missing information.
        """
        if not self.llm:
            raise RuntimeError("LLM required for analysis.")
            
        from .retriever import TemplateRetriever
        
        retriever = TemplateRetriever()
        retrieved_templates = retriever.retrieve_templates(description, k=1)
        
        if not retrieved_templates:
            return {"success": False, "error": "No relevant template found."}
            
        best_template = retrieved_templates[0]
        template_content = best_template['content']
        template_name = best_template['filename']
        
        # Extract placeholders from the template
        placeholders = self.loader.extract_placeholders(template_content)
        
        if not placeholders:
            return {
                "success": True,
                "template_name": template_name,
                "detected_placeholders": [],
                "missing_fields": []
            }

        # Ask LLM which fields are missing from the description
        prompt = f"""
You are an intelligent assistant.
I have a letter template with the following required placeholders: {list(placeholders)}

The user provided this description: "{description}"

Identify which placeholders are MISSING or cannot be inferred from the description.
Return ONLY a comma-separated list of missing placeholders. If none are missing, return "None".

Missing Placeholders:
"""
        response = self.llm.generate_response(prompt, temperature=0.0)
        
        missing_fields = []
        if "None" not in response:
            # Clean up response
            cleaned = response.replace("\n", "").strip()
            if cleaned:
                missing_fields = [f.strip() for f in cleaned.split(",") if f.strip()]
        
        return {
            "success": True,
            "template_name": template_name,
            "detected_placeholders": list(placeholders),
            "missing_fields": missing_fields
        }

    def generate_from_description(self, description: str, additional_data: Dict[str, str] = None, template_name: str = None) -> Dict[str, Any]:
        """
        RAG-Based Generation:
        1. Retrieve relevant template based on description (OR use provided template_name).
        2. Use LLM to fill/adapt the retrieved template, incorporating additional data.
        """
        if not self.llm:
            raise RuntimeError("LLM required for smart generation.")
            
        best_template = None
        retrieval_score = 1.0 # Default if manual selection
        
        if template_name:
            # Direct template usage
            try:
                content = self.loader.load_template(template_name)
                best_template = {
                    "filename": template_name,
                    "content": content,
                    "score": 1.0
                }
                logger.info(f"Using specified template: {template_name}")
            except Exception as e:
                return {"success": False, "error": f"Template '{template_name}' not found: {e}"}
        else:
            # RAG Retrieval
            from .retriever import TemplateRetriever
            retriever = TemplateRetriever()
            retrieved_templates = retriever.retrieve_templates(description, k=1)
            
            if not retrieved_templates:
                return {
                    "success": False,
                    "error": "No relevant template found."
                }
            best_template = retrieved_templates[0]
            retrieval_score = best_template['score']
            
        template_content = best_template['content']
        template_name = best_template['filename']
        
        logger.info(f"Selected template: {template_name}")
        
        # Format additional data for the prompt
        additional_info_str = ""
        if additional_data:
            additional_info_str = "\nAdditional User Details:\n" + "\n".join(f"- {k}: {v}" for k, v in additional_data.items())
        
        # Prompt LLM to fill the retrieved template
        prompt = f"""
You are a helpful legal assistant for Nepal.
Your task is to write a formal letter based on the user's description, using the provided template as a strict guide.

User Description: "{description}"
{additional_info_str}

Selected Template ({template_name}):
{template_content}

Instructions:
1. Use the structure and formal language of the Selected Template.
2. Fill in the placeholders (like [Name], {{Date}}) with information from the User Description and Additional Details.
3. If information is still missing, use a generic placeholder like "[Insert Name]".
4. Output ONLY the final letter in Nepali (or English if the template is English). Do not add conversational text.

Final Letter:
"""
        generated_letter = self.llm.generate_response(prompt, temperature=0.3)
        
        return {
            "success": True,
            "letter": generated_letter,
            "template_used": template_name,
            "retrieval_score": retrieval_score
        }
