"""
DictaPilot Workflow Engine
Implements specification-driven workflows

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

from spec_generator import Specification, SpecGenerator
from intent_classifier import IntentClassifier, IntentType
from spec_store import SpecStore


class WorkflowState(Enum):
    """Workflow states"""

    IDLE = "idle"
    SPEC_CREATION = "spec_creation"
    SPEC_REFINEMENT = "spec_refinement"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    COMPLETED = "completed"


@dataclass
class WorkflowContext:
    """Context for current workflow"""

    state: WorkflowState = WorkflowState.IDLE
    current_spec: Optional[Specification] = None
    spec_id: Optional[str] = None
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Manages specification-driven workflows"""

    def __init__(
        self,
        spec_store: Optional[SpecStore] = None,
        auto_detect_intent: bool = True,
    ):
        self.spec_store = spec_store or SpecStore()
        self.spec_generator = SpecGenerator()
        self.intent_classifier = IntentClassifier(auto_detect=auto_detect_intent)
        self.context = WorkflowContext()

    def process_voice_input(self, text: str) -> Dict[str, Any]:
        """Process voice input and route to appropriate workflow"""
        # Classify intent
        intent_result = self.intent_classifier.classify(text)

        # Route based on intent and current state
        if intent_result.intent == IntentType.SPEC:
            return self._handle_spec_input(text, intent_result)
        elif intent_result.intent == IntentType.CODE:
            return self._handle_code_input(text, intent_result)
        elif intent_result.intent == IntentType.DOCUMENTATION:
            return self._handle_doc_input(text, intent_result)
        elif intent_result.intent == IntentType.COMMAND:
            return self._handle_command_input(text, intent_result)
        else:
            return self._handle_general_input(text)

    def _handle_spec_input(self, text: str, intent_result) -> Dict[str, Any]:
        """Handle specification-related input"""
        # Check for spec creation triggers
        if any(
            trigger in text.lower()
            for trigger in ["start new spec", "create spec", "new specification"]
        ):
            return self._start_new_spec(text, intent_result)

        # If we're already in spec mode, update current spec
        if self.context.state in [
            WorkflowState.SPEC_CREATION,
            WorkflowState.SPEC_REFINEMENT,
        ]:
            return self._update_current_spec(text)

        # Otherwise, start a new spec
        return self._start_new_spec(text, intent_result)

    def _start_new_spec(self, text: str, intent_result) -> Dict[str, Any]:
        """Start a new specification"""
        # Extract title from text
        title = self._extract_title(text)

        # Determine template type
        template = intent_result.metadata.get("spec_type", "feature")

        # Create new spec
        spec = self.spec_generator.start_new_spec(title, template)

        # Parse initial content
        self.spec_generator.parse_voice_input(text)

        # Update context
        self.context.state = WorkflowState.SPEC_CREATION
        self.context.current_spec = spec

        # Add to history
        self.context.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "spec_created",
                "title": title,
                "template": template,
            }
        )

        return {
            "success": True,
            "action": "spec_created",
            "spec": spec,
            "message": f"Started new {template} spec: {title}",
            "state": self.context.state.value,
        }

    def _update_current_spec(self, text: str) -> Dict[str, Any]:
        """Update current specification"""
        if not self.context.current_spec:
            return {"success": False, "error": "No active spec to update"}

        # Parse voice input and update spec
        self.spec_generator.parse_voice_input(text)

        # Update state
        self.context.state = WorkflowState.SPEC_REFINEMENT

        # Add to history
        self.context.history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "spec_updated",
                "content": text[:100],
            }
        )

        return {
            "success": True,
            "action": "spec_updated",
            "spec": self.context.current_spec,
            "message": "Specification updated",
            "state": self.context.state.value,
        }

    def _handle_code_input(self, text: str, intent_result) -> Dict[str, Any]:
        """Handle code-related input"""
        return {
            "success": True,
            "action": "code_input",
            "intent": intent_result.intent.value,
            "message": "Code mode detected - use standard dictation",
            "metadata": intent_result.metadata,
        }

    def _handle_doc_input(self, text: str, intent_result) -> Dict[str, Any]:
        """Handle documentation-related input"""
        return {
            "success": True,
            "action": "doc_input",
            "intent": intent_result.intent.value,
            "message": "Documentation mode detected",
            "metadata": intent_result.metadata,
        }

    def _handle_command_input(self, text: str, intent_result) -> Dict[str, Any]:
        """Handle command input"""
        text_lower = text.lower()

        # Save spec command
        if "save spec" in text_lower:
            return self.save_current_spec()

        # Export spec command
        if "export" in text_lower:
            format_style = self._extract_format(text)
            return self.export_current_spec(format_style)

        return {
            "success": True,
            "action": "command",
            "message": "Command processed",
            "metadata": intent_result.metadata,
        }

    def _handle_general_input(self, text: str) -> Dict[str, Any]:
        """Handle general input"""
        return {
            "success": True,
            "action": "general_input",
            "message": "General dictation mode",
            "text": text,
        }

    def save_current_spec(self, format_style: str = "standard") -> Dict[str, Any]:
        """Save current specification"""
        if not self.context.current_spec:
            return {"success": False, "error": "No active spec to save"}

        spec_id = self.spec_store.save_spec(self.context.current_spec, format_style)

        if spec_id:
            self.context.spec_id = spec_id
            self.context.history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "spec_saved",
                    "spec_id": spec_id,
                }
            )

            return {
                "success": True,
                "action": "spec_saved",
                "spec_id": spec_id,
                "message": f"Specification saved: {spec_id}",
            }
        else:
            return {"success": False, "error": "Failed to save specification"}

    def export_current_spec(self, format_style: str = "standard") -> Dict[str, Any]:
        """Export current specification"""
        if not self.context.current_spec:
            return {"success": False, "error": "No active spec to export"}

        markdown = self.spec_generator.export_spec(format_style)

        return {
            "success": True,
            "action": "spec_exported",
            "format": format_style,
            "content": markdown,
            "message": f"Specification exported as {format_style}",
        }

    def reset_workflow(self):
        """Reset workflow to idle state"""
        self.context = WorkflowContext()
        self.spec_generator.current_spec = None

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "state": self.context.state.value,
            "has_active_spec": self.context.current_spec is not None,
            "spec_id": self.context.spec_id,
            "history_count": len(self.context.history),
        }

    def _extract_title(self, text: str) -> str:
        """Extract title from text"""
        import re

        # Look for patterns like "start new spec: TITLE"
        match = re.search(
            r"(?:start new spec|create spec|new specification):\s*(.+?)(?:\.|$)",
            text,
            re.IGNORECASE,
        )
        if match:
            return match.group(1).strip()

        # Otherwise use first sentence
        sentences = text.split(".")
        if sentences:
            return sentences[0].strip()[:100]

        return "Untitled Spec"

    def _extract_format(self, text: str) -> str:
        """Extract format from text"""
        text_lower = text.lower()

        if "openspec" in text_lower:
            return "openspec"
        elif "luna" in text_lower:
            return "luna"
        elif "github" in text_lower:
            return "github"
        else:
            return "standard"
