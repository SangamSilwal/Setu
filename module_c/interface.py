"""
Public Interface for Module C (Letter Generation)
"""

import logging
from typing import List, Dict, Any
from .generator import LetterGenerator

logger = logging.getLogger(__name__)

class LetterGenerationAPI:
    """
    Main API for the Letter Generation module.
    """
    
    def __init__(self):
        self.generator = LetterGenerator()
        
    def get_available_templates(self) -> List[str]:
        """
        Get a list of all available letter templates.
        """
        return self.generator.loader.list_templates()
        
    def generate_letter(self, template_name: str, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Generate a letter using structured data.
        """
        try:
            letter = self.generator.generate_letter(template_name, user_data)
            return {
                "success": True,
                "letter": letter,
                "method": "template_fill"
            }
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_requirements(self, description: str) -> Dict[str, Any]:
        """
        Analyze description to find missing information.
        """
        try:
            return self.generator.analyze_requirements(description)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def search_template(self, query: str) -> Dict[str, Any]:
        """
        Search for a suitable template based on user query.
        """
        try:
            # Lazy import
            from .retriever import TemplateRetriever
            retriever = TemplateRetriever()
            results = retriever.retrieve_templates(query, k=1)
            
            if results:
                best = results[0]
                return {
                    "success": True,
                    "template_name": best['filename'],
                    "score": best['score'],
                    "content": best['content'] # Optional: return content preview
                }
            else:
                return {"success": False, "error": "No template found"}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"success": False, "error": str(e)}

    def get_template_details(self, template_name: str) -> Dict[str, Any]:
        """
        Get details (placeholders, content) for a specific template.
        """
        try:
            content = self.generator.loader.load_template(template_name)
            placeholders = self.generator.loader.extract_placeholders(content)
            return {
                "success": True,
                "template_name": template_name,
                "placeholders": list(placeholders),
                "content": content
            }
        except Exception as e:
            logger.error(f"Get details failed: {e}")
            return {"success": False, "error": str(e)}

    def fill_template(self, template_name: str, user_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Fill a specific template with provided data (Simple Substitution).
        """
        try:
            letter = self.generator.generate_letter(template_name, user_data)
            return {
                "success": True,
                "letter": letter,
                "method": "simple_fill"
            }
        except Exception as e:
            logger.error(f"Fill failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_smart_letter(self, description: str, template_name: str = None, additional_data: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Generate a letter using a natural language description (RAG-based).
        Optional: template_name to skip retrieval and use specific template.
        Optional: additional_data dict to fill specific missing fields.
        """
        try:
            # New signature: only description needed, template is retrieved automatically
            result = self.generator.generate_from_description(description, additional_data, template_name)
            if result['success']:
                result["method"] = "rag_generation"
            return result
        except Exception as e:
            logger.error(f"Smart generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
