"""
DictaPilot Snippet Library Module
Handles voice-activated text snippets with template support.

MIT License
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import platform
import re
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict, field

try:
    from jinja2 import Template, TemplateError
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    # Simple fallback template system


def get_snippets_path() -> Path:
    """Get platform-specific snippets file path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "snippets.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "snippets.json"


def get_snippets_dir() -> Path:
    """Create and return snippets directory"""
    snippets_path = get_snippets_path()
    snippets_path.parent.mkdir(parents=True, exist_ok=True)
    return snippets_path.parent


# Default categories
DEFAULT_CATEGORIES = [
    "General",
    "Email",
    "Code",
    "Personal",
    "Work"
]

# Default filler words to ignore in trigger matching
FILLER_WORDS = {"the", "a", "an", "um", "uh", "like", "you know"}


@dataclass
class Snippet:
    """Single snippet entry"""
    id: str
    trigger: str
    content: str
    category: str
    description: str
    is_template: bool
    variables: List[str] = field(default_factory=list)
    usage_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Snippet":
        return cls(**data)


class SnippetManager:
    """Manages snippet library with CRUD operations and template support"""
    
    def __init__(self, snippets_path: Optional[Path] = None):
        self.snippets_path = snippets_path or get_snippets_path()
        self._snippets: Dict[str, Snippet] = {}
        self._triggers: Dict[str, str] = {}  # trigger -> snippet_id
        self._load_snippets()
    
    def _load_snippets(self):
        """Load snippets from JSON file"""
        if self.snippets_path.exists():
            try:
                with open(self.snippets_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                snippets_list = data.get('snippets', [])
                for snippet_data in snippets_list:
                    snippet = Snippet.from_dict(snippet_data)
                    self._snippets[snippet.id] = snippet
                    self._triggers[snippet.trigger.lower()] = snippet.id
            except (json.JSONDecodeError, KeyError):
                self._snippets = {}
                self._triggers = {}
        else:
            self._snippets = {}
            self._triggers = {}
    
    def _save_snippets(self):
        """Save snippets to JSON file"""
        get_snippets_dir()
        
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "snippets": [s.to_dict() for s in self._snippets.values()]
        }
        
        with open(self.snippets_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_snippet(self, trigger: str, content: str, 
                   category: str = "General", description: str = "",
                   is_template: bool = False, 
                   variables: Optional[List[str]] = None,
                   tags: Optional[List[str]] = None) -> str:
        """Add a new snippet"""
        # Normalize trigger
        trigger_normalized = trigger.strip().lower()
        
        # Check for duplicate trigger
        if trigger_normalized in self._triggers:
            raise ValueError(f"Trigger '{trigger}' already exists")
        
        # Extract variables from template if not provided
        if is_template and not variables:
            variables = self._extract_variables(content)
        
        snippet = Snippet(
            id=str(uuid.uuid4()),
            trigger=trigger,
            content=content,
            category=category,
            description=description,
            is_template=is_template,
            variables=variables or [],
            tags=tags or []
        )
        
        self._snippets[snippet.id] = snippet
        self._triggers[trigger_normalized] = snippet.id
        self._save_snippets()
        
        return snippet.id
    
    def update_snippet(self, snippet_id: str, **kwargs) -> bool:
        """Update an existing snippet"""
        if snippet_id not in self._snippets:
            return False
        
        snippet = self._snippets[snippet_id]
        
        # Handle trigger change
        if 'trigger' in kwargs:
            new_trigger = kwargs['trigger'].strip().lower()
            if new_trigger != snippet.trigger.lower():
                # Remove old trigger
                del self._triggers[snippet.trigger.lower()]
                # Add new trigger
                self._triggers[new_trigger] = snippet.id
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(snippet, key):
                setattr(snippet, key, value)
        
        # Update template variables if content changed
        if 'content' in kwargs and snippet.is_template:
            snippet.variables = self._extract_variables(kwargs['content'])
        
        snippet.updated_at = datetime.now().isoformat()
        self._save_snippets()
        
        return True
    
    def delete_snippet(self, snippet_id: str) -> bool:
        """Delete a snippet"""
        if snippet_id not in self._snippets:
            return False
        
        snippet = self._snippets[snippet_id]
        del self._triggers[snippet.trigger.lower()]
        del self._snippets[snippet_id]
        self._save_snippets()
        
        return True
    
    def get_snippet(self, snippet_id: str) -> Optional[Snippet]:
        """Get a snippet by ID"""
        return self._snippets.get(snippet_id)
    
    def get_snippet_by_trigger(self, trigger: str) -> Optional[Snippet]:
        """Get a snippet by trigger phrase"""
        trigger_normalized = trigger.strip().lower()
        snippet_id = self._triggers.get(trigger_normalized)
        return self._snippets.get(snippet_id) if snippet_id else None
    
    def get_all_snippets(self, category: Optional[str] = None) -> List[Snippet]:
        """Get all snippets, optionally filtered by category"""
        snippets = list(self._snippets.values())
        
        if category:
            snippets = [s for s in snippets if s.category == category]
        
        return sorted(snippets, key=lambda s: s.usage_count, reverse=True)
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        categories = set(s.category for s in self._snippets.values())
        return sorted(categories) if categories else DEFAULT_CATEGORIES.copy()
    
    def search_snippets(self, query: str) -> List[Snippet]:
        """Search snippets by trigger or content"""
        query_lower = query.lower()
        results = []
        
        for snippet in self._snippets.values():
            if (query_lower in snippet.trigger.lower() or 
                query_lower in snippet.content.lower() or
                any(query_lower in tag.lower() for tag in snippet.tags)):
                results.append(snippet)
        
        return sorted(results, key=lambda s: s.usage_count, reverse=True)
    
    def match_trigger(self, spoken_text: str) -> Optional[Snippet]:
        """Match spoken text against triggers with fuzzy matching"""
        spoken_lower = spoken_text.lower().strip()
        
        # Direct match
        if spoken_lower in self._triggers:
            snippet_id = self._triggers[spoken_lower]
            snippet = self._snippets[snippet_id]
            self._increment_usage(snippet_id)
            return snippet
        
        # Try matching without fillers
        words = spoken_lower.split()
        filtered_words = [w for w in words if w not in FILLER_WORDS]
        filtered_text = ' '.join(filtered_words)
        
        if filtered_text != spoken_lower and filtered_text in self._triggers:
            snippet_id = self._triggers[filtered_text]
            snippet = self._snippets[snippet_id]
            self._increment_usage(snippet_id)
            return snippet
        
        # Try prefix match
        for trigger, snippet_id in self._triggers.items():
            if spoken_lower.startswith(trigger + ' ') or spoken_lower.startswith(trigger):
                snippet = self._snippets[snippet_id]
                self._increment_usage(snippet_id)
                return snippet
        
        return None
    
    def _increment_usage(self, snippet_id: str):
        """Increment usage count for a snippet"""
        if snippet_id in self._snippets:
            self._snippets[snippet_id].usage_count += 1
            self._save_snippets()
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract Jinja2 variables from content"""
        if not JINJA2_AVAILABLE:
            # Simple regex for {{ variable }} patterns
            pattern = r'\{\{\s*(\w+)\s*\}\}'
            matches = re.findall(pattern, content)
            return list(set(matches))
        
        try:
            template = Template(content)
            return list(template.module.__dict__.keys())
        except TemplateError:
            return []
    
    def render_template(self, content: str, variables: Optional[Dict[str, str]] = None) -> str:
        """Render a template with provided variables"""
        if not JINJA2_AVAILABLE:
            # Simple fallback: replace {{ var }} with provided value
            result = content
            if variables:
                for var_name, var_value in variables.items():
                    result = result.replace(f'{{{{ {var_name} }}}}', var_value)
                    result = result.replace(f'{{{{{var_name}}}}}', var_value)
            return result
        
        try:
            template = Template(content)
            return template.render(**(variables or {}))
        except TemplateError as e:
            return content
    
    def render_snippet(self, snippet_id: str, 
                      variables: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Render a snippet with variables"""
        snippet = self.get_snippet(snippet_id)
        if not snippet:
            return None
        
        if snippet.is_template:
            return self.render_template(snippet.content, variables)
        else:
            return snippet.content
    
    def increment_usage(self, snippet_id: str) -> bool:
        """Manually increment snippet usage"""
        if snippet_id not in self._snippets:
            return False
        
        self._snippets[snippet_id].usage_count += 1
        self._save_snippets()
        return True
    
    def export_to_json(self, filepath: Optional[Path] = None) -> Dict[str, Any]:
        """Export snippets to JSON"""
        export_data = {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "snippet_count": len(self._snippets),
            "snippets": [s.to_dict() for s in self._snippets.values()]
        }
        
        if filepath:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return export_data
    
    def import_from_json(self, filepath: Path) -> Dict[str, int]:
        """Import snippets from JSON"""
        filepath = Path(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        snippets = import_data.get('snippets', [])
        
        added = 0
        skipped = 0
        
        for snippet_data in snippets:
            trigger = snippet_data.get('trigger', '').strip().lower()
            
            if trigger in self._triggers:
                # Update existing if usage count is higher
                existing_id = self._triggers[trigger]
                existing = self._snippets[existing_id]
                
                if snippet_data.get('usage_count', 0) > existing.usage_count:
                    self.update_snippet(existing_id, **snippet_data)
                skipped += 1
            else:
                # Add new snippet
                self.add_snippet(
                    trigger=snippet_data.get('trigger', ''),
                    content=snippet_data.get('content', ''),
                    category=snippet_data.get('category', 'General'),
                    description=snippet_data.get('description', ''),
                    is_template=snippet_data.get('is_template', False),
                    variables=snippet_data.get('variables', []),
                    tags=snippet_data.get('tags', [])
                )
                added += 1
        
        return {"added": added, "skipped": skipped, "total": len(snippets)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get snippet library statistics"""
        categories = {}
        total_usage = 0
        
        for snippet in self._snippets.values():
            categories[snippet.category] = categories.get(snippet.category, 0) + 1
            total_usage += snippet.usage_count
        
        return {
            "total_snippets": len(self._snippets),
            "total_usage": total_usage,
            "categories": categories,
            "templates": sum(1 for s in self._snippets.values() if s.is_template)
        }
    
    def create_sample_snippets(self):
        """Create sample snippets for new users"""
        samples = [
            {
                "trigger": "email sig",
                "content": "Best regards,\n{{ name }}\n{{ title }}",
                "category": "Email",
                "description": "Email signature with variables",
                "is_template": True,
                "variables": ["name", "title"]
            },
            {
                "trigger": "meeting notes",
                "content": "Meeting Notes - {{ date }}\n\nAttendees: {{ attendees }}\n\nAgenda:\n1. \n2. \n3. \n\nAction Items:\n- ",
                "category": "Work",
                "description": "Meeting notes template",
                "is_template": True,
                "variables": ["date", "attendees"]
            },
            {
                "trigger": "code comment",
                "content": "# TODO: {{ task }} - {{ name }}",
                "category": "Code",
                "description": "Code comment template",
                "is_template": True,
                "variables": ["task", "name"]
            },
            {
                "trigger": "thanks",
                "content": "Thank you for your message. I will get back to you shortly.",
                "category": "General",
                "description": "Quick thank you response"
            }
        ]
        
        for sample in samples:
            try:
                self.add_snippet(**sample)
            except ValueError:
                pass  # Skip if trigger already exists


# Global instance for easy access
_snippet_manager_instance: Optional[SnippetManager] = None


def get_snippet_manager() -> SnippetManager:
    """Get or create the global snippet manager instance"""
    global _snippet_manager_instance
    if _snippet_manager_instance is None:
        _snippet_manager_instance = SnippetManager()
    return _snippet_manager_instance
