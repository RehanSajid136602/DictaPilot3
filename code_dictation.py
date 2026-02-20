"""
DictaPilot Code Dictation Module
Handles natural language to code conversion with IDE integration.

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
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


def get_code_dictation_config_path() -> Path:
    """Get platform-specific code dictation config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "code_dictation.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "code_dictation.json"


def get_code_dictation_config_dir() -> Path:
    """Create and return code dictation config directory"""
    config_path = get_code_dictation_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


# Programming language enum
class ProgrammingLanguage(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    BASH = "bash"
    POWERSHELL = "powershell"
    YAML = "yaml"
    JSON = "json"
    MARKDOWN = "markdown"


# Common programming terms mapping
PROGRAMMING_TERMS = {
    # Functions/methods
    "function": "def ",
    "method": "def ",
    "procedure": "def ",
    "routine": "def ",
    
    # Variables
    "variable": "",
    "var": "",
    "constant": "const ",
    "let": "let ",
    
    # Control flow
    "if statement": "if ",
    "for loop": "for ",
    "while loop": "while ",
    "switch": "switch ",
    "case": "case ",
    "default": "default:",
    
    # Classes
    "class": "class ",
    "object": "object ",
    "interface": "interface ",
    "trait": "trait ",
    
    # Import/require
    "import": "import ",
    "require": "require(",
    "include": "#include ",
    
    # Common patterns
    "print": "print(",
    "log": "console.log(",
    "return": "return ",
    "throw": "throw ",
    "try": "try {",
    "catch": "} catch (error) {",
    "finally": "} finally {",
    
    # Comments
    "comment": "# ",
    "document": "/**\n * ",
}


# Code snippet templates
CODE_TEMPLATES = {
    "python_function": "def {name}({params}):\n    {body}\n",
    "python_class": "class {name}({inheritance}):\n    def __init__(self{init_params}):\n        {init_body}\n",
    "python_loop": "for {item} in {collection}:\n    {body}\n",
    "python_if": "if {condition}:\n    {body}\n",
    
    "javascript_function": "function {name}({params}) {{\n    {body}\n}}\n",
    "javascript_arrow": "const {name} = ({params}) => {{\n    {body}\n}};\n",
    "javascript_class": "class {name} {{\n    constructor({params}) {{\n        {init_body}\n    }}\n}}\n",
    
    "java_method": "public {return_type} {name}({params}) {{\n    {body}\n}}\n",
    "java_class": "public class {name} {{\n    {members}\n}}\n",
    
    "sql_select": "SELECT {columns}\nFROM {table}\nWHERE {conditions}\nORDER BY {order};\n",
    "sql_insert": "INSERT INTO {table} ({columns})\nVALUES ({values});\n",
    "sql_update": "UPDATE {table}\nSET {assignments}\nWHERE {conditions};\n",
    
    "html_element": "<{tag}{attributes}>\n    {content}\n</{tag}>\n",
    "html_div": "<div{attributes}>\n    {content}\n</div>\n",
}


@dataclass
class CodeDictationConfig:
    """Configuration for code dictation"""
    enabled: bool = True
    auto_detect_language: bool = True
    current_language: str = "python"
    format_on_insert: bool = True
    add_semicolons: bool = True
    indent_size: int = 4
    use_tabs: bool = False
    templates_enabled: bool = True


class CodeDictationParser:
    """Parses natural language into code"""
    
    def __init__(self):
        self.current_language = ProgrammingLanguage.PYTHON
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        config_path = get_code_dictation_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_language = ProgrammingLanguage(
                        data.get('language', 'python')
                    )
            except (json.JSONDecodeError, IOError):
                pass
    
    def set_language(self, language: str):
        """Set current programming language"""
        try:
            self.current_language = ProgrammingLanguage(language)
        except ValueError:
            self.current_language = ProgrammingLanguage.PYTHON
    
    def parse_to_code(self, text: str) -> str:
        """Convert natural language to code"""
        result = text.strip()
        
        # Replace common terms with code
        for term, code in PROGRAMMING_TERMS.items():
            result = re.sub(r'\b' + term + r'\b', code, result, flags=re.IGNORECASE)
        
        # Apply language-specific transformations
        if self.current_language == ProgrammingLanguage.PYTHON:
            result = self._transform_python(result)
        elif self.current_language == ProgrammingLanguage.JAVASCRIPT:
            result = self._transform_javascript(result)
        elif self.current_language == ProgrammingLanguage.SQL:
            result = self._transform_sql(result)
        
        return result
    
    def _transform_python(self, text: str) -> str:
        """Transform text to Python code"""
        result = text
        
        # Convert camelCase to snake_case
        result = re.sub(r'([a-z])([A-Z])', r'\1_\2', result).lower()
        
        # Add Python-style method calls
        result = re.sub(r'(\w+)\s+method', r'\1()', result)
        
        # Add self. prefix for class methods
        if 'method' in text.lower():
            result = re.sub(r'(\w+)\s*\(\)', r'self.\1()', result)
        
        # Fix indentation markers
        result = result.replace('indent', '    ')
        result = result.replace('tab', '\t')
        
        return result
    
    def _transform_javascript(self, text: str) -> str:
        """Transform text to JavaScript code"""
        result = text
        
        # Convert to camelCase
        words = re.findall(r'[A-Z][a-z]*|[a-z]+', result)
        if len(words) > 1:
            camel = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
            result = result.replace(' '.join(words), camel)
        
        # Add semicolons
        result = re.sub(r'([^{}=])$', r'\1;', result)
        
        return result
    
    def _transform_sql(self, text: str) -> str:
        """Transform text to SQL"""
        result = text.upper()
        
        # Common SQL keyword replacements
        replacements = {
            r'\bfind\b': 'SELECT',
            r'\bget\b': 'SELECT',
            r'\bsearch\b': 'SELECT',
            r'\bfetch\b': 'SELECT',
            r'\bcreate\b': 'INSERT INTO',
            r'\badd\b': 'INSERT INTO',
            r'\bupdate\b': 'UPDATE',
            r'\bchange\b': 'UPDATE',
            r'\bremove\b': 'DELETE FROM',
            r'\bdelete\b': 'DELETE FROM',
        }
        
        for pattern, sql in replacements.items():
            result = re.sub(pattern, sql, result)
        
        return result
    
    def generate_template(self, template_name: str, **kwargs) -> str:
        """Generate code from template"""
        template = CODE_TEMPLATES.get(template_name)
        if not template:
            return ""
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    def format_code(self, code: str) -> str:
        """Format code according to settings"""
        config = self._load_config()
        
        result = code
        
        # Add semicolons (JS)
        if config.add_semicolons and self.current_language == ProgrammingLanguage.JAVASCRIPT:
            result = re.sub(r'([^{}()=\[\]:])$', r'\1;', result)
        
        # Fix indentation
        indent = '\t' if config.use_tabs else ' ' * config.indent_size
        
        return result


class IDELSPClient:
    """Client for IDE Language Server Protocol integration"""
    
    def __init__(self):
        self.ide_type = self._detect_ide()
        self.lsp_port = None
    
    def _detect_ide(self) -> str:
        """Detect running IDE"""
        # Check for common IDE processes
        ide_processes = {
            'code': 'vscode',
            'vscodium': 'vscode',
            'pycharm': 'pycharm',
            'idea': 'intellij',
            'goland': 'goland',
            'rider': 'rider',
            'webstorm': 'webstorm',
            'clion': 'clion',
            'androidstudio': 'android',
            'xcode': 'xcode'
        }
        
        # This would need actual process detection
        # For now, return unknown
        return "unknown"
    
    def connect_lsp(self, port: int = 5007) -> bool:
        """Connect to LSP server"""
        self.lsp_port = port
        # LSP connection logic would go here
        return True
    
    def get_completions(self, code: str, cursor_pos: int) -> List[Dict[str, Any]]:
        """Get code completions from LSP"""
        # This would query the LSP server
        return []
    
    def get_diagnostics(self, code: str) -> List[Dict[str, Any]]:
        """Get code diagnostics from LSP"""
        # This would query the LSP server
        return []
    
    def format_document(self, code: str) -> str:
        """Format document via LSP"""
        # This would call LSP document formatting
        return code


class CodeDictationManager:
    """Main manager for code dictation"""
    
    def __init__(self):
        self.parser = CodeDictationParser()
        self.lsp_client = IDELSPClient()
        self.config = CodeDictationConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration"""
        config_path = get_code_dictation_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.config.enabled = data.get('enabled', True)
                    self.config.auto_detect_language = data.get('auto_detect_language', True)
                    self.config.format_on_insert = data.get('format_on_insert', True)
                    self.config.add_semicolons = data.get('add_semicolons', True)
                    self.config.indent_size = data.get('indent_size', 4)
                    self.config.use_tabs = data.get('use_tabs', False)
                    self.config.templates_enabled = data.get('templates_enabled', True)
                    
                    if 'language' in data:
                        self.parser.set_language(data['language'])
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save configuration"""
        get_code_dictation_config_dir()
        config_path = get_code_dictation_config_path()
        
        data = {
            'enabled': self.config.enabled,
            'auto_detect_language': self.config.auto_detect_language,
            'language': self.parser.current_language.value,
            'format_on_insert': self.config.format_on_insert,
            'add_semicolons': self.config.add_semicolons,
            'indent_size': self.config.indent_size,
            'use_tabs': self.config.use_tabs,
            'templates_enabled': self.config.templates_enabled
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_enabled(self, enabled: bool):
        """Enable or disable code dictation"""
        self.config.enabled = enabled
        self._save_config()
    
    def set_language(self, language: str):
        """Set programming language"""
        self.parser.set_language(language)
        self._save_config()
    
    def process_text(self, text: str) -> str:
        """Process text and convert to code"""
        if not self.config.enabled:
            return text
        
        # Check if this looks like code
        if self._is_code_phrase(text):
            return self.parser.parse_to_code(text)
        
        return text
    
    def _is_code_phrase(self, text: str) -> bool:
        """Check if text contains code-related phrases"""
        code_indicators = [
            'function', 'method', 'class', 'loop', 'if', 'else',
            'variable', 'constant', 'import', 'return', 'print',
            'define', 'create', 'add', 'remove', 'update',
            'select', 'insert', 'delete', 'update',
            'for each', 'iterate', 'loop through',
            'equals', 'greater than', 'less than',
            'true', 'false', 'null', 'undefined'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in code_indicators)
    
    def insert_code(self, code: str, target: str = "clipboard") -> bool:
        """Insert code into target (clipboard or IDE)"""
        if target == "clipboard":
            # Use clipboard
            try:
                import pyperclip
                pyperclip.copy(code)
                return True
            except ImportError:
                # Fallback - would need platform-specific implementation
                return False
        
        elif target == "ide":
            # Try to insert via IDE integration
            return self.lsp_client.connect_lsp()
        
        return False
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported programming languages"""
        return [
            {"id": lang.value, "name": lang.value.capitalize()}
            for lang in ProgrammingLanguage
        ]
    
    def get_templates(self) -> List[str]:
        """Get available code templates"""
        return list(CODE_TEMPLATES.keys())


# Global instance
_code_dictation_instance: Optional[CodeDictationManager] = None


def get_code_dictation_manager() -> CodeDictationManager:
    """Get or create the global code dictation manager instance"""
    global _code_dictation_instance
    if _code_dictation_instance is None:
        _code_dictation_instance = CodeDictationManager()
    return _code_dictation_instance
