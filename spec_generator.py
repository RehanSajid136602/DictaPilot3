"""
DictaPilot Specification Generator
Converts voice input into structured specification documents

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class SpecSection:
    """A section within a specification"""
    title: str
    content: str
    subsections: List['SpecSection'] = field(default_factory=list)


@dataclass
class Specification:
    """Structured specification document"""
    title: str
    goal: str = ""
    context: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    non_goals: List[str] = field(default_factory=list)
    files_locations: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    custom_sections: List[SpecSection] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_markdown(self, format_style: str = "standard") -> str:
        """Convert specification to markdown format"""
        if format_style == "openspec":
            return self._to_openspec_format()
        elif format_style == "luna":
            return self._to_luna_format()
        elif format_style == "github":
            return self._to_github_format()
        else:
            return self._to_standard_format()

    def _to_standard_format(self) -> str:
        """Standard spec.md format"""
        md = f"# {self.title}\n\n"
        
        if self.goal:
            md += f"## Goal\n{self.goal}\n\n"
        
        if self.context:
            md += f"## Context\n{self.context}\n\n"
        
        if self.acceptance_criteria:
            md += "## Acceptance Criteria\n"
            for criterion in self.acceptance_criteria:
                md += f"- {criterion}\n"
            md += "\n"
        
        if self.constraints:
            md += "## Constraints\n"
            for constraint in self.constraints:
                md += f"- {constraint}\n"
            md += "\n"
        
        if self.non_goals:
            md += "## Non-Goals\n"
            for non_goal in self.non_goals:
                md += f"- {non_goal}\n"
            md += "\n"
        
        if self.files_locations:
            md += "## Files/Locations\n"
            for file_loc in self.files_locations:
                md += f"- `{file_loc}`\n"
            md += "\n"
        
        for section in self.custom_sections:
            md += self._render_section(section)
        
        if self.metadata:
            md += "## Metadata\n"
            for key, value in self.metadata.items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        return md.strip()

    def _to_openspec_format(self) -> str:
        """OpenSpec format"""
        md = f"# {self.title}\n\n"
        md += f"**Created:** {self.created_at}\n"
        md += f"**Updated:** {self.updated_at}\n\n"
        
        if self.goal:
            md += f"## Overview\n{self.goal}\n\n"
        
        if self.context:
            md += f"## Context\n{self.context}\n\n"
        
        if self.acceptance_criteria:
            md += "## Requirements\n"
            for i, criterion in enumerate(self.acceptance_criteria, 1):
                md += f"{i}. {criterion}\n"
            md += "\n"
        
        if self.constraints:
            md += "## Constraints\n"
            for constraint in self.constraints:
                md += f"- {constraint}\n"
            md += "\n"
        
        return md.strip()

    def _to_luna_format(self) -> str:
        """Luna Drive format"""
        md = f"# Specification: {self.title}\n\n"
        
        if self.goal:
            md += f"## Intent\n{self.goal}\n\n"
        
        if self.acceptance_criteria:
            md += "## Success Criteria\n"
            for criterion in self.acceptance_criteria:
                md += f"- [ ] {criterion}\n"
            md += "\n"
        
        if self.context:
            md += f"## Background\n{self.context}\n\n"
        
        if self.constraints:
            md += "## Boundaries\n"
            for constraint in self.constraints:
                md += f"- {constraint}\n"
            md += "\n"
        
        return md.strip()

    def _to_github_format(self) -> str:
        """GitHub issue/PR format"""
        md = f"## {self.title}\n\n"
        
        if self.goal:
            md += f"### Description\n{self.goal}\n\n"
        
        if self.context:
            md += f"### Context\n{self.context}\n\n"
        
        if self.acceptance_criteria:
            md += "### Acceptance Criteria\n"
            for criterion in self.acceptance_criteria:
                md += f"- [ ] {criterion}\n"
            md += "\n"
        
        if self.files_locations:
            md += "### Files to Modify\n"
            for file_loc in self.files_locations:
                md += f"- `{file_loc}`\n"
            md += "\n"
        
        return md.strip()

    def _render_section(self, section: SpecSection, level: int = 2) -> str:
        """Render a custom section"""
        md = f"{'#' * level} {section.title}\n{section.content}\n\n"
        for subsection in section.subsections:
            md += self._render_section(subsection, level + 1)
        return md


class SpecTemplate:
    """Pre-built specification templates"""
    
    @staticmethod
    def feature() -> Specification:
        """Template for new feature"""
        return Specification(
            title="New Feature",
            goal="[Describe what this feature does and why it's needed]",
            context="[Provide background information]",
            acceptance_criteria=[
                "[Criterion 1]",
                "[Criterion 2]",
                "[Criterion 3]"
            ],
            constraints=["[Any technical or business constraints]"],
            metadata={"type": "feature", "priority": "normal"}
        )
    
    @staticmethod
    def bugfix() -> Specification:
        """Template for bug fix"""
        return Specification(
            title="Bug Fix",
            goal="[Describe the bug and expected behavior]",
            context="[Steps to reproduce, error messages, impact]",
            acceptance_criteria=[
                "Bug is fixed and no longer reproducible",
                "No regression in related functionality",
                "Tests added to prevent recurrence"
            ],
            constraints=["Must not break existing functionality"],
            metadata={"type": "bugfix", "priority": "high"}
        )
    
    @staticmethod
    def refactor() -> Specification:
        """Template for refactoring"""
        return Specification(
            title="Refactoring",
            goal="[Describe what needs to be refactored and why]",
            context="[Current state, technical debt, maintainability issues]",
            acceptance_criteria=[
                "Code is cleaner and more maintainable",
                "All existing tests pass",
                "No change in external behavior"
            ],
            constraints=["Must maintain backward compatibility"],
            non_goals=["Adding new features", "Changing external APIs"],
            metadata={"type": "refactor", "priority": "normal"}
        )
    
    @staticmethod
    def minimal() -> Specification:
        """Minimal template for quick specs"""
        return Specification(
            title="Quick Spec",
            goal="[What needs to be done]",
            acceptance_criteria=["[Done when...]"],
            metadata={"type": "quick", "priority": "normal"}
        )


class SpecGenerator:
    """Generates specifications from voice input"""
    
    GOAL_PATTERNS = [
        r"(?:goal|objective|purpose|aim)(?:\s+is)?:\s*(.+)",
        r"(?:we need to|we want to|we should|let's)\s+(.+)",
        r"(?:the goal is to|the purpose is to)\s+(.+)"
    ]
    
    CONTEXT_PATTERNS = [
        r"(?:context|background|situation)(?:\s+is)?:\s*(.+)",
        r"(?:currently|right now|at the moment),?\s+(.+)",
        r"(?:the problem is|the issue is)\s+(.+)"
    ]
    
    CRITERIA_PATTERNS = [
        r"(?:acceptance criteria|success criteria|done when)(?:\s+is)?:\s*(.+)",
        r"(?:it should|must|needs to)\s+(.+)",
        r"(?:we'll know it's done when)\s+(.+)"
    ]
    
    CONSTRAINT_PATTERNS = [
        r"(?:constraint|limitation|restriction)(?:\s+is)?:\s*(.+)",
        r"(?:must not|cannot|should not)\s+(.+)",
        r"(?:we can't|we cannot)\s+(.+)"
    ]
    
    FILE_PATTERNS = [
        r"(?:file|files|location|path)(?:\s+is)?:\s*(.+)",
        r"(?:in|modify|update|change)\s+([a-zA-Z0-9_/\\.]+\.py)",
        r"(?:in|modify|update|change)\s+([a-zA-Z0-9_/\\.]+\.js)"
    ]
    
    def __init__(self, template_type: str = "standard"):
        self.template_type = template_type
        self.current_spec: Optional[Specification] = None
    
    def start_new_spec(self, title: str, template: str = "feature") -> Specification:
        """Start a new specification"""
        if template == "feature":
            self.current_spec = SpecTemplate.feature()
        elif template == "bugfix":
            self.current_spec = SpecTemplate.bugfix()
        elif template == "refactor":
            self.current_spec = SpecTemplate.refactor()
        elif template == "minimal":
            self.current_spec = SpecTemplate.minimal()
        else:
            self.current_spec = Specification(title=title)
        
        self.current_spec.title = title
        return self.current_spec
    
    def parse_voice_input(self, text: str) -> Specification:
        """Parse voice input and extract spec components"""
        if not self.current_spec:
            self.current_spec = Specification(title="Untitled Spec")
        
        text = text.strip()
        
        for pattern in self.GOAL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.current_spec.goal = match.group(1).strip()
                break
        
        for pattern in self.CONTEXT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.current_spec.context = match.group(1).strip()
                break
        
        for pattern in self.CRITERIA_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                criterion = match.group(1).strip()
                if criterion not in self.current_spec.acceptance_criteria:
                    self.current_spec.acceptance_criteria.append(criterion)
        
        for pattern in self.CONSTRAINT_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                constraint = match.group(1).strip()
                if constraint not in self.current_spec.constraints:
                    self.current_spec.constraints.append(constraint)
        
        for pattern in self.FILE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                file_ref = match.group(1).strip()
                if file_ref not in self.current_spec.files_locations:
                    self.current_spec.files_locations.append(file_ref)
        
        self.current_spec.updated_at = datetime.now().isoformat()
        return self.current_spec
    
    def update_spec(self, command: str, content: str) -> Specification:
        """Update specific section of current spec"""
        if not self.current_spec:
            self.current_spec = Specification(title="Untitled Spec")
        
        command = command.lower().strip()
        content = content.strip()
        
        if "goal" in command or "objective" in command:
            self.current_spec.goal = content
        elif "context" in command or "background" in command:
            self.current_spec.context = content
        elif "criteria" in command or "acceptance" in command:
            if content not in self.current_spec.acceptance_criteria:
                self.current_spec.acceptance_criteria.append(content)
        elif "constraint" in command or "limitation" in command:
            if content not in self.current_spec.constraints:
                self.current_spec.constraints.append(content)
        elif "file" in command or "location" in command:
            if content not in self.current_spec.files_locations:
                self.current_spec.files_locations.append(content)
        elif "non-goal" in command or "out of scope" in command:
            if content not in self.current_spec.non_goals:
                self.current_spec.non_goals.append(content)
        
        self.current_spec.updated_at = datetime.now().isoformat()
        return self.current_spec
    
    def export_spec(self, format_style: str = "standard") -> str:
        """Export current spec to markdown"""
        if not self.current_spec:
            return ""
        return self.current_spec.to_markdown(format_style)
    
    def save_spec(self, filepath: Path, format_style: str = "standard") -> bool:
        """Save spec to file"""
        if not self.current_spec:
            return False
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(self.export_spec(format_style))
            return True
        except Exception as e:
            print(f"Error saving spec: {e}")
            return False
