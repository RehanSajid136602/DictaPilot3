"""
DictaPilot App Formatting Presets Module
Handles application-specific formatting and code syntax awareness.

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
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


def get_formatting_config_path() -> Path:
    """Get platform-specific formatting config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "formatting.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "formatting.json"


def get_formatting_config_dir() -> Path:
    """Create and return formatting config directory"""
    config_path = get_formatting_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class CodeLanguage(Enum):
    """Programming languages"""
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
    UNKNOWN = "unknown"


@dataclass
class FormattingPreset:
    """Formatting preset for an application"""
    name: str
    capitalize_sentences: bool = True
    add_periods: bool = True
    add_commas: bool = True
    preserve_newlines: bool = True
    auto_capitalize_first: bool = True
    format_lists: bool = True
    bullet_style: str = "-"  # -, *, numbers, letters
    code_aware: bool = False
    indent_size: int = 4
    use_tabs: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormattingPreset":
        return cls(**data)


# Default presets for application types
DEFAULT_PRESETS: Dict[str, FormattingPreset] = {
    "general": FormattingPreset(
        name="General",
        capitalize_sentences=True,
        add_periods=True,
        add_commas=True,
        preserve_newlines=True,
        auto_capitalize_first=True,
        format_lists=True,
        bullet_style="-"
    ),
    "email": FormattingPreset(
        name="Email",
        capitalize_sentences=True,
        add_periods=True,
        add_commas=True,
        preserve_newlines=True,
        auto_capitalize_first=True,
        format_lists=True,
        bullet_style="-"
    ),
    "code": FormattingPreset(
        name="Code",
        capitalize_sentences=False,
        add_periods=False,
        add_commas=True,
        preserve_newlines=True,
        auto_capitalize_first=False,
        format_lists=False,
        code_aware=True,
        indent_size=4,
        use_tabs=False
    ),
    "chat": FormattingPreset(
        name="Chat",
        capitalize_sentences=False,
        add_periods=False,
        add_commas=False,
        preserve_newlines=True,
        auto_capitalize_first=False,
        format_lists=False,
        bullet_style="-"
    ),
    "document": FormattingPreset(
        name="Document",
        capitalize_sentences=True,
        add_periods=True,
        add_commas=True,
        preserve_newlines=True,
        auto_capitalize_first=True,
        format_lists=True,
        bullet_style="1."
    ),
    "terminal": FormattingPreset(
        name="Terminal",
        capitalize_sentences=False,
        add_periods=False,
        add_commas=False,
        preserve_newlines=False,
        auto_capitalize_first=False,
        format_lists=False,
        code_aware=True,
        indent_size=4,
        use_tabs=True
    )
}

# Programming language patterns
LANGUAGE_PATTERNS: Dict[CodeLanguage, List[str]] = {
    CodeLanguage.PYTHON: [
        r'def\s+\w+\s*\(',
        r'class\s+\w+\s*:',
        r'import\s+\w+',
        r'from\s+\w+\s+import',
        r'if\s+__name__\s*==',
        r'print\s*\(',
        r'self\.',
        r'lambda\s+',
        r'yield\s+',
        r'async\s+def',
        r'@staticmethod',
        r'@classmethod'
    ],
    CodeLanguage.JAVASCRIPT: [
        r'function\s+\w+\s*\(',
        r'const\s+\w+\s*=',
        r'let\s+\w+\s*=',
        r'var\s+\w+\s*=',
        r'=>\s*{',
        r'require\s*\(',
        r'export\s+',
        r'import\s+.*from',
        r'console\.log',
        r'document\.',
        r'window\.',
        r'async\s+function',
        r'await\s+',
        r'Promise\.',
        r'\.then\s*\('
    ],
    CodeLanguage.TYPESCRIPT: [
        r'interface\s+\w+',
        r'type\s+\w+\s*=',
        r':\s*(string|number|boolean|any|void|never)',
        r'<\w+>',
        r'as\s+\w+',
        r'export\s+(interface|type|class|const)',
        r'React\.',
        r'useState\s*<',
        r'useEffect\s*\('
    ],
    CodeLanguage.JAVA: [
        r'public\s+class',
        r'private\s+(static\s+)?(final\s+)?\w+',
        r'protected\s+',
        r'void\s+\w+\s*\(',
        r'System\.out\.print',
        r'@Override',
        r'new\s+\w+\s*\(',
        r'import\s+java\.',
        r'package\s+\w+;',
        r'throws\s+\w+'
    ],
    CodeLanguage.CPP: [
        r'#include\s*<',
        r'std::',
        r'cout\s*<<',
        r'cin\s*>>',
        r'class\s+\w+\s*{',
        r'template\s*<',
        r'namespace\s+\w+',
        r'virtual\s+',
        r'nullptr',
        r'auto\s+\w+\s*='
    ],
    CodeLanguage.GO: [
        r'func\s+\w+\s*\(',
        r'func\s+\(\w+\s+\*?\w+\)',
        r'package\s+\w+',
        r'import\s+\(',
        r'fmt\.',
        r'go\s+func',
        r'defer\s+',
        r'chan\s+\w+',
        r'interface\s*{',
        r'struct\s*{'
    ],
    CodeLanguage.RUST: [
        r'fn\s+\w+\s*\(',
        r'let\s+mut\s+',
        r'let\s+\w+\s*:',
        r'impl\s+\w+',
        r'use\s+\w+::',
        r'match\s+\w+\s*{',
        r'pub\s+(fn|struct|enum)',
        r'println!',
        r'Vec<',
        r'Option<',
        r'Result<'
    ],
    CodeLanguage.SQL: [
        r'SELECT\s+',
        r'FROM\s+\w+',
        r'WHERE\s+',
        r'INSERT\s+INTO',
        r'UPDATE\s+\w+\s+SET',
        r'DELETE\s+FROM',
        r'CREATE\s+(TABLE|INDEX|VIEW)',
        r'ALTER\s+TABLE',
        r'JOIN\s+\w+',
        r'GROUP\s+BY',
        r'ORDER\s+BY'
    ],
    CodeLanguage.BASH: [
        r'^#!/bin/(bash|sh)',
        r'\$\{?\w+\}?',
        r'if\s+\[\[',
        r'if\s+\[',
        r'for\s+\w+\s+in',
        r'while\s+read',
        r'echo\s+',
        r'grep\s+',
        r'|\s*awk',
        r'sudo\s+',
        r'chmod\s+',
        r'\$\('
    ],
    CodeLanguage.YAML: [
        r'^\w+:\s*$',
        r'^\s+-\s+\w+:',
        r'^\s+\w+:\s+\|',
        r'^\s+\w+:\s+>',
        r'^\s+-\s+',
        r':\s+(true|false|null)',
        r':\s+\d+(\.\d+)?'
    ],
    CodeLanguage.HTML: [
        r'<!DOCTYPE\s+html',
        r'<html',
        r'<head>',
        r'<body>',
        r'<div',
        r'<span',
        r'<script',
        r'<style',
        r'class="',
        r'id="',
        r'</\w+>'
    ],
    CodeLanguage.CSS: [
        r'\{\s*[\w-]+\s*:',
        r'@media\s+',
        r'@import\s+',
        r'@keyframes\s+',
        r'\.\w+\s*\{',
        r'#\w+\s*\{',
        r'\w+\s*,\s*\w+\s*\{',
        r':hover\s*\{',
        r':focus\s*\{',
        r'margin:\s*',
        r'padding:\s*',
        r'color:\s*',
        r'background:'
    ]
}


class CodeSyntaxFormatter:
    """Formats code based on programming language"""
    
    def __init__(self):
        self.current_language = CodeLanguage.UNKNOWN
    
    def detect_language(self, text: str) -> CodeLanguage:
        """Detect programming language from text"""
        scores: Dict[CodeLanguage, int] = {}
        
        for lang, patterns in LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[lang] = scores.get(lang, 0) + 1
        
        if not scores:
            return CodeLanguage.UNKNOWN
        
        return max(scores, key=scores.get)
    
    def set_language(self, language: CodeLanguage):
        """Set current programming language"""
        self.current_language = language
    
    def format_code(self, text: str) -> str:
        """Format code text"""
        if self.current_language == CodeLanguage.UNKNOWN:
            # Try to detect
            self.current_language = self.detect_language(text)
        
        result = text
        
        # Apply language-specific formatting
        if self.current_language == CodeLanguage.PYTHON:
            result = self._format_python(result)
        elif self.current_language == CodeLanguage.JAVASCRIPT:
            result = self._format_javascript(result)
        elif self.current_language == CodeLanguage.SQL:
            result = self._format_sql(result)
        
        return result
    
    def _format_python(self, text: str) -> str:
        """Format Python code"""
        # Ensure proper indentation
        lines = text.split('\n')
        formatted = []
        
        indent_level = 0
        indent_size = 4
        
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent for closing blocks
            if stripped in [')', ']', '}', 'else:', 'elif:', 'finally:', 'except:', 'break', 'continue', 'pass']:
                indent_level = max(0, indent_level - 1)
            
            # Apply indentation
            if stripped:
                formatted.append(' ' * (indent_level * indent_size) + stripped)
            else:
                formatted.append('')
            
            # Increase indent for blocks
            if stripped and stripped[-1] in [':', '{', '(', '[']:
                indent_level += 1
        
        return '\n'.join(formatted)
    
    def _format_javascript(self, text: str) -> str:
        """Format JavaScript code"""
        # Basic formatting
        lines = text.split('\n')
        formatted = []
        
        indent_level = 0
        indent_size = 2
        
        for line in lines:
            stripped = line.strip()
            
            # Decrease indent for closing
            if stripped in ['}', ']', ')', ';']:
                indent_level = max(0, indent_level - 1)
            
            if stripped:
                formatted.append(' ' * (indent_level * indent_size) + stripped)
            else:
                formatted.append('')
            
            # Increase indent for blocks
            if stripped and stripped[-1] in ['{', '(', '[']:
                indent_level += 1
        
        return '\n'.join(formatted)
    
    def _format_sql(self, text: str) -> str:
        """Format SQL queries"""
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'JOIN', 
                   'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP BY',
                   'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT INTO',
                   'VALUES', 'UPDATE', 'SET', 'DELETE FROM', 'CREATE TABLE',
                   'ALTER TABLE', 'DROP TABLE', 'INDEX', 'VIEW']
        
        result = text.upper()
        for keyword in keywords:
            result = re.sub(r'\b' + keyword + r'\b', keyword, result)
        
        return result
    
    def get_syntax_keywords(self) -> List[str]:
        """Get syntax keywords for current language"""
        keywords = {
            CodeLanguage.PYTHON: ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with', 'as', 'lambda', 'yield', 'async', 'await', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is', 'pass', 'break', 'continue', 'raise', 'global', 'nonlocal'],
            CodeLanguage.JAVASCRIPT: ['function', 'const', 'let', 'var', 'return', 'if', 'else', 'for', 'while', 'try', 'catch', 'finally', 'class', 'new', 'this', 'async', 'await', 'import', 'export', 'default', 'true', 'false', 'null', 'undefined', 'typeof', 'instanceof'],
            CodeLanguage.SQL: ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN', 'IS', 'NULL', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER', 'ON', 'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'TABLE', 'INDEX', 'VIEW', 'AS', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
        }
        
        return keywords.get(self.current_language, [])


class AppFormattingManager:
    """Manages application-specific formatting"""
    
    def __init__(self):
        self.presets: Dict[str, FormattingPreset] = DEFAULT_PRESETS.copy()
        self.app_presets: Dict[str, str] = {}  # app_name -> preset_name
        self.code_formatter = CodeSyntaxFormatter()
        self.current_preset = "general"
        self._load_config()
    
    def _load_config(self):
        """Load formatting configuration"""
        config_path = get_formatting_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load custom presets
                    custom_presets = data.get('presets', {})
                    for name, preset_data in custom_presets.items():
                        self.presets[name] = FormattingPreset.from_dict(preset_data)
                    
                    # Load app mappings
                    self.app_presets = data.get('app_presets', {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save formatting configuration"""
        get_formatting_config_dir()
        config_path = get_formatting_config_path()
        
        # Separate default and custom presets
        custom_presets = {
            name: preset.to_dict()
            for name, preset in self.presets.items()
            if name not in DEFAULT_PRESETS
        }
        
        data = {
            'presets': custom_presets,
            'app_presets': self.app_presets
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_app_preset(self, app_name: str, preset_name: str):
        """Set preset for specific application"""
        if preset_name in self.presets:
            self.app_presets[app_name] = preset_name
            self._save_config()
    
    def get_preset(self, app_name: str = "") -> FormattingPreset:
        """Get formatting preset for app"""
        if app_name and app_name in self.app_presets:
            preset_name = self.app_presets[app_name]
            return self.presets.get(preset_name, self.presets["general"])
        
        return self.presets.get(self.current_preset, self.presets["general"])
    
    def format_text(self, text: str, app_name: str = "") -> str:
        """Format text according to preset"""
        preset = self.get_preset(app_name)
        
        result = text
        
        # Apply formatting rules
        if preset.add_periods and not result.endswith('.'):
            # Check if last line is complete thought
            lines = result.split('\n')
            if lines and lines[-1].strip() and not lines[-1].strip()[-1] in '.!?':
                lines[-1] += '.'
                result = '\n'.join(lines)
        
        if preset.add_commas:
            # Add commas after conjunctions in lists
            result = re.sub(r'\s+(and|or)\s+', ', \\1 ', result)
        
        if preset.auto_capitalize_first:
            # Capitalize first letter
            if result:
                result = result[0].upper() + result[1:]
        
        # Handle code formatting
        if preset.code_aware:
            # Detect code language
            lang = self.code_formatter.detect_language(text)
            if lang != CodeLanguage.UNKNOWN:
                self.code_formatter.set_language(lang)
                result = self.code_formatter.format_code(result)
        
        return result
    
    def add_custom_preset(self, name: str, preset: FormattingPreset):
        """Add custom formatting preset"""
        self.presets[name] = preset
        self._save_config()
    
    def get_available_presets(self) -> List[str]:
        """Get list of available presets"""
        return list(self.presets.keys())
    
    def get_app_mappings(self) -> Dict[str, str]:
        """Get app to preset mappings"""
        return self.app_presets.copy()


# Global instance
_formatting_manager_instance: Optional[AppFormattingManager] = None


def get_formatting_manager() -> AppFormattingManager:
    """Get or create the global formatting manager instance"""
    global _formatting_manager_instance
    if _formatting_manager_instance is None:
        _formatting_manager_instance = AppFormattingManager()
    return _formatting_manager_instance
