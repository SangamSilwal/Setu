"""
Template Loader Module
Handles loading and parsing of letter templates.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Set
from .config import TEMPLATE_DIR

logger = logging.getLogger(__name__)

class TemplateLoader:
    """
    Responsible for discovering, loading, and parsing letter templates.
    """

    def __init__(self, template_dir: Path = TEMPLATE_DIR):
        self.template_dir = template_dir

    def list_templates(self) -> List[str]:
        """
        List all available template files in the template directory.
        Returns a list of filenames.
        """
        if not self.template_dir.exists():
            logger.warning(f"Template directory not found: {self.template_dir}")
            return []
        
        # List text files
        templates = [f.name for f in self.template_dir.glob("*.txt")]
        return sorted(templates)

    def load_template(self, template_name: str) -> str:
        """
        Load the content of a specific template.
        """
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
            
        try:
            return template_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {e}")
            raise

    def extract_placeholders(self, template_text: str) -> Set[str]:
        """
        Extract placeholders from the template text.
        Supports formats:
        - [Placeholder Name]
        - {{Placeholder Name}}
        - <Placeholder Name>
        """
        placeholders = set()
        
        # Regex for [Placeholder]
        bracket_matches = re.findall(r'\[(.*?)\]', template_text)
        placeholders.update(bracket_matches)
        
        # Regex for {{Placeholder}}
        curly_matches = re.findall(r'\{\{(.*?)\}\}', template_text)
        placeholders.update(curly_matches)
        
        # Regex for <Placeholder>
        angle_matches = re.findall(r'<(.*?)>', template_text)
        placeholders.update(angle_matches)

        # Regex for {Placeholder} - careful to avoid double braces if possible, 
        # but for now we just want to catch {Key}
        # We use a negative lookahead/lookbehind or just simple matching for {Key} 
        # where Key doesn't contain { or }
        single_curly_matches = re.findall(r'(?<!\{)\{([^{}]+)\}(?!\})', template_text)
        placeholders.update(single_curly_matches)
        
        # Filter out empty strings or purely structural tags if any
        return {p.strip() for p in placeholders if p.strip()}
