"""
DictaPilot Quick Edit Commands Module
Handles real-time editing commands during dictation.

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

import re
import json
import os
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


def get_commands_config_path() -> Path:
    """Get platform-specific commands config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "edit_commands.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "edit_commands.json"


def get_commands_config_dir() -> Path:
    """Create and return commands config directory"""
    config_path = get_commands_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class EditCommandType(Enum):
    """Types of edit commands"""
    SCRATCH = "scratch"           # Delete last phrase
    UNDO = "undo"                 # Undo last edit
    REDO = "redo"                 # Redo undone edit
    CAPITALIZE = "capitalize"     # Capitalize last word
    LOWERCASE = "lowercase"       # Lowercase last word
    UPPERCASE = "uppercase"       # Uppercase last word
    NEW_PARAGRAPH = "new_paragraph"  # Insert paragraph break
    NEW_LINE = "new_line"         # Insert line break
    REPLACE = "replace"           # Replace last phrase
    CORRECTION = "correction"     # "no I meant..."
    SPELL = "spell"              # Spell out letters
    NUMBER = "number"             # Convert number word to digit
    PUNCTUATE = "punctuate"       # Add punctuation


@dataclass
class EditCommand:
    """Represents an edit command"""
    command_type: EditCommandType
    parameters: Dict[str, Any] = field(default_factory=dict)
    original_text: str = ""
    result_text: str = ""
    timestamp: str = ""


@dataclass
class EditState:
    """State for undo/redo"""
    text_before: str
    text_after: str
    command_type: str
    timestamp: str


class EditCommandParser:
    """Parser for quick edit commands during dictation"""
    
    # Default command patterns
    DEFAULT_COMMANDS = {
        # Scratch/undo commands
        "scratch that": EditCommandType.SCRATCH,
        "scratch": EditCommandType.SCRATCH,
        "delete that": EditCommandType.SCRATCH,
        "forget that": EditCommandType.SCRATCH,
        "never mind": EditCommandType.SCRATCH,
        "ignore that": EditCommandType.SCRATCH,
        
        # Undo/redo
        "undo": EditCommandType.UNDO,
        "undo that": EditCommandType.UNDO,
        "undo last": EditCommandType.UNDO,
        "redo": EditCommandType.REDO,
        "redo that": EditCommandType.REDO,
        
        # Capitalization
        "capitalize that": EditCommandType.CAPITALIZE,
        "capitalize": EditCommandType.CAPITALIZE,
        "caps that": EditCommandType.CAPITALIZE,
        "capitalize last": EditCommandType.CAPITALIZE,
        
        # Lowercase
        "lowercase that": EditCommandType.LOWERCASE,
        "lowercase": EditCommandType.LOWERCASE,
        "lower that": EditCommandType.LOWERCASE,
        
        # Uppercase
        "uppercase that": EditCommandType.UPPERCASE,
        "uppercase": EditCommandType.UPPERCASE,
        "caps lock that": EditCommandType.UPPERCASE,
        
        # Paragraph/line breaks
        "new paragraph": EditCommandType.NEW_PARAGRAPH,
        "new line": EditCommandType.NEW_LINE,
        "line break": EditCommandType.NEW_LINE,
        "paragraph": EditCommandType.NEW_PARAGRAPH,
        
        # Corrections
        "no i meant": EditCommandType.CORRECTION,
        "i meant": EditCommandType.CORRECTION,
        "change that to": EditCommandType.REPLACE,
        "change to": EditCommandType.REPLACE,
        "instead of": EditCommandType.REPLACE,
        
        # Number conversion
        "number": EditCommandType.NUMBER,
    }
    
    # Number words mapping
    NUMBER_WORDS = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13",
        "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
        "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30",
        "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70",
        "eighty": "80", "ninety": "90", "hundred": "100", "thousand": "1000"
    }
    
    def __init__(self):
        self.commands = self.DEFAULT_COMMANDS.copy()
        self.custom_commands: Dict[str, str] = {}
        self._load_custom_commands()
    
    def _load_custom_commands(self):
        """Load custom commands from config"""
        config_path = get_commands_config_path()
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    self.custom_commands = data.get('custom_commands', {})
            except (json.JSONDecodeError, IOError):
                self.custom_commands = {}
    
    def _save_custom_commands(self):
        """Save custom commands to config"""
        get_commands_config_dir()
        config_path = get_commands_config_path()
        
        data = {
            "custom_commands": self.custom_commands,
            "updated_at": "2026-02-19"
        }
        
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def parse_command(self, text: str) -> Optional[Tuple[EditCommandType, str]]:
        """Parse text to detect edit commands"""
        text_lower = text.lower().strip()
        
        # Check custom commands first
        for phrase, cmd_type in self.custom_commands.items():
            if phrase in text_lower:
                try:
                    return (EditCommandType(cmd_type), text)
                except ValueError:
                    pass
        
        # Check default commands
        for phrase, cmd_type in self.DEFAULT_COMMANDS.items():
            if text_lower == phrase or text_lower.startswith(phrase + ' '):
                return (cmd_type, text)
        
        return None
    
    def is_command(self, text: str) -> bool:
        """Check if text is a command"""
        return self.parse_command(text) is not None
    
    def add_custom_command(self, phrase: str, command_type: str):
        """Add a custom command phrase"""
        self.custom_commands[phrase.lower()] = command_type
        self._save_custom_commands()
    
    def remove_custom_command(self, phrase: str):
        """Remove a custom command"""
        phrase_lower = phrase.lower()
        if phrase_lower in self.custom_commands:
            del self.custom_commands[phrase_lower]
            self._save_custom_commands()
    
    def get_custom_commands(self) -> Dict[str, str]:
        """Get all custom commands"""
        return self.custom_commands.copy()


class EditExecutor:
    """Executes edit commands and maintains edit history"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.undo_stack: List[EditState] = []
        self.redo_stack: List[EditState] = []
        self.current_text: str = ""
    
    def set_text(self, text: str):
        """Set the current text"""
        self.current_text = text
    
    def get_text(self) -> str:
        """Get the current text"""
        return self.current_text
    
    def execute_command(self, command: EditCommandType, 
                      params: Optional[Dict[str, Any]] = None,
                      original_text: str = "") -> Tuple[str, EditState]:
        """Execute an edit command and return new text + state"""
        params = params or {}
        
        old_text = self.current_text
        new_text = old_text
        
        if command == EditCommandType.SCRATCH:
            new_text = self._scratch_that(old_text)
        
        elif command == EditCommandType.UNDO:
            new_text, state = self._undo()
            if state:
                self.redo_stack.append(state)
                self.current_text = new_text
                return new_text, state
        
        elif command == EditCommandType.REDO:
            new_text, state = self._redo()
            if state:
                self.undo_stack.append(state)
                self.current_text = new_text
                return new_text, state
        
        elif command == EditCommandType.CAPITALIZE:
            new_text = self._capitalize_last(old_text)
        
        elif command == EditCommandType.LOWERCASE:
            new_text = self._lowercase_last(old_text)
        
        elif command == EditCommandType.UPPERCASE:
            new_text = self._uppercase_last(old_text)
        
        elif command == EditCommandType.NEW_PARAGRAPH:
            new_text = self._new_paragraph(old_text)
        
        elif command == EditCommandType.NEW_LINE:
            new_text = self._new_line(old_text)
        
        elif command == EditCommandType.CORRECTION:
            correction_text = params.get('correction', '')
            new_text = self._apply_correction(old_text, correction_text)
        
        elif command == EditCommandType.REPLACE:
            replace_text = params.get('replace', '')
            new_text = self._apply_replace(old_text, replace_text)
        
        elif command == EditCommandType.NUMBER:
            new_text = self._convert_numbers(old_text)
        
        # Save to undo stack
        if new_text != old_text:
            state = EditState(
                text_before=old_text,
                text_after=new_text,
                command_type=command.value,
                timestamp=params.get('timestamp', '')
            )
            self.undo_stack.append(state)
            self.redo_stack.clear()  # Clear redo stack on new edit
            
            # Trim history if needed
            if len(self.undo_stack) > self.max_history:
                self.undo_stack.pop(0)
        
        self.current_text = new_text
        return new_text, EditState(
            text_before=old_text,
            text_after=new_text,
            command_type=command.value,
            timestamp=params.get('timestamp', '')
        )
    
    def _scratch_that(self, text: str) -> str:
        """Remove the last phrase (up to last sentence or phrase)"""
        if not text:
            return text
        
        # Try to remove up to last sentence
        text = text.strip()
        
        # Remove trailing punctuation and last word/phrase
        # Look for common sentence endings
        for ending in ['. ', '? ', '! ', '\n']:
            last_pos = text.rfind(ending)
            if last_pos > 0:
                return text[:last_pos + 1].strip()
        
        # If no sentence ending, remove last word
        words = text.split()
        if len(words) > 1:
            return ' '.join(words[:-1])
        
        return ""
    
    def _undo(self) -> Tuple[str, Optional[EditState]]:
        """Undo last edit"""
        if not self.undo_stack:
            return self.current_text, None
        
        state = self.undo_stack.pop()
        self.current_text = state.text_before
        return state.text_before, state
    
    def _redo(self) -> Tuple[str, Optional[EditState]]:
        """Redo last undone edit"""
        if not self.redo_stack:
            return self.current_text, None
        
        state = self.redo_stack.pop()
        self.current_text = state.text_after
        return state.text_after, state
    
    def _capitalize_last(self, text: str) -> str:
        """Capitalize the last word"""
        if not text:
            return text
        
        text = text.strip()
        words = text.split()
        
        if not words:
            return text
        
        words[-1] = words[-1].capitalize()
        return ' '.join(words)
    
    def _lowercase_last(self, text: str) -> str:
        """Lowercase the last word"""
        if not text:
            return text
        
        text = text.strip()
        words = text.split()
        
        if not words:
            return text
        
        words[-1] = words[-1].lower()
        return ' '.join(words)
    
    def _uppercase_last(self, text: str) -> str:
        """Uppercase the last word"""
        if not text:
            return text
        
        text = text.strip()
        words = text.split()
        
        if not words:
            return text
        
        words[-1] = words[-1].upper()
        return ' '.join(words)
    
    def _new_paragraph(self, text: str) -> str:
        """Insert paragraph break"""
        if not text:
            return "\n\n"
        
        text = text.rstrip()
        return text + "\n\n"
    
    def _new_line(self, text: str) -> str:
        """Insert line break"""
        if not text:
            return "\n"
        
        text = text.rstrip()
        return text + "\n"
    
    def _apply_correction(self, text: str, correction: str) -> str:
        """Apply correction ("no I meant...")"""
        # Find the last phrase and replace it with correction
        text = text.strip()
        
        # Remove the last incomplete sentence if any
        for ending in ['. ', '? ', '! ']:
            last_pos = text.rfind(ending)
            if last_pos > 0:
                text = text[:last_pos + 1].strip()
                break
        
        # Append correction
        if text:
            return text + " " + correction
        return correction
    
    def _apply_replace(self, text: str, replace_text: str) -> str:
        """Apply replacement"""
        text = text.strip()
        
        # Similar to correction but explicit
        for ending in ['. ', '? ', '! ']:
            last_pos = text.rfind(ending)
            if last_pos > 0:
                text = text[:last_pos + 1].strip()
                break
        
        if text:
            return text + " " + replace_text
        return replace_text
    
    def _convert_numbers(self, text: str) -> str:
        """Convert number words to digits"""
        words = text.split()
        result = []
        
        for word in words:
            word_lower = word.lower().rstrip('.,!?;:\'"')
            if word_lower in self.NUMBER_WORDS:
                # Preserve original punctuation
                prefix = word[:len(word) - len(word.lstrip('.,!?;:\'"'))]
                suffix = word[len(word.rstrip('.,!?;:\'"')):]
                result.append(prefix + self.NUMBER_WORDS[word_lower] + suffix)
            else:
                result.append(word)
        
        return ' '.join(result)
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get edit history"""
        return [asdict(state) for state in self.undo_stack]
    
    def clear_history(self):
        """Clear undo/redo history"""
        self.undo_stack.clear()
        self.redo_stack.clear()


class QuickEditManager:
    """Main manager combining parser and executor"""
    
    def __init__(self):
        self.parser = EditCommandParser()
        self.executor = EditExecutor()
    
    def process_text(self, text: str) -> Optional[str]:
        """Process text and execute command if detected"""
        result = self.parser.parse_command(text)
        
        if result is None:
            return None
        
        command_type, original_text = result
        
        # Extract additional parameters from text
        params = {'original_text': original_text}
        
        if command_type == EditCommandType.CORRECTION:
            # Extract the correction part after "no I meant" or "I meant"
            for prefix in ['no i meant ', 'i meant ', 'change that to ', 'change to ']:
                if original_text.lower().startswith(prefix):
                    params['correction'] = original_text[len(prefix):].strip()
                    break
        
        elif command_type == EditCommandType.REPLACE:
            for prefix in ['change that to ', 'change to ']:
                if original_text.lower().startswith(prefix):
                    params['replace'] = original_text[len(prefix):].strip()
                    break
        
        new_text, _ = self.executor.execute_command(command_type, params, original_text)
        return new_text
    
    def is_edit_command(self, text: str) -> bool:
        """Check if text is an edit command"""
        return self.parser.is_command(text)
    
    def set_text(self, text: str):
        """Set current text in executor"""
        self.executor.set_text(text)
    
    def get_text(self) -> str:
        """Get current text from executor"""
        return self.executor.get_text()
    
    def undo(self) -> str:
        """Undo last edit"""
        new_text, state = self.executor._undo()
        if state:
            self.executor.redo_stack.append(state)
        return new_text
    
    def redo(self) -> str:
        """Redo last undone edit"""
        new_text, state = self.executor._redo()
        if state:
            self.executor.undo_stack.append(state)
        return new_text


# Global instance
_quick_edit_instance: Optional[QuickEditManager] = None


def get_quick_edit_manager() -> QuickEditManager:
    """Get or create the global quick edit manager instance"""
    global _quick_edit_instance
    if _quick_edit_instance is None:
        _quick_edit_instance = QuickEditManager()
    return _quick_edit_instance
