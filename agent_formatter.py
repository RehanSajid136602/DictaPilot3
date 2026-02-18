"""
DictaPilot Agent Formatter
Formats transcriptions as structured prompts for coding agents

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
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
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AgentPrompt:
    """Structured prompt for coding agents"""
    task: str = ""
    context: str = ""
    constraints: str = ""
    acceptance_criteria: str = ""
    files_locations: List[str] = None
    # Enhanced fields
    priority: str = "normal"  # "urgent", "normal", "low"
    complexity: str = "moderate"  # "simple", "moderate", "complex"
    language: str = ""  # Detected programming language
    frameworks: List[str] = None  # Detected frameworks
    code_references: List[str] = None  # Class/function names mentioned

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        md = "# Agent Task\n\n"

        if self.task:
            md += f"## Task\n{self.task}\n\n"

        if self.context:
            md += f"## Context\n{self.context}\n\n"

        if self.constraints:
            md += f"## Constraints\n{self.constraints}\n\n"

        if self.acceptance_criteria:
            md += f"## Acceptance Criteria\n{self.acceptance_criteria}\n\n"

        if self.files_locations:
            md += f"## Files/Locations\n"
            for file_loc in self.files_locations:
                md += f"- {file_loc}\n"
            md += "\n"

        # Enhanced fields
        meta = []
        if self.priority and self.priority != "normal":
            meta.append(f"**Priority:** {self.priority}")
        if self.complexity and self.complexity != "moderate":
            meta.append(f"**Complexity:** {self.complexity}")
        if self.language:
            meta.append(f"**Language:** {self.language}")
        if self.frameworks:
            meta.append(f"**Frameworks:** {', '.join(self.frameworks)}")
        if self.code_references:
            meta.append(f"**Code References:** {', '.join(self.code_references)}")

        if meta:
            md += "## Metadata\n"
            md += " | ".join(meta) + "\n\n"

        return md.strip()

    def to_text(self) -> str:
        """Convert to plain text format"""
        text = ""

        if self.task:
            text += f"TASK: {self.task}\n\n"

        if self.context:
            text += f"CONTEXT: {self.context}\n\n"

        if self.constraints:
            text += f"CONSTRAINTS: {self.constraints}\n\n"

        if self.acceptance_criteria:
            text += f"ACCEPTANCE CRITERIA: {self.acceptance_criteria}\n\n"

        if self.files_locations:
            text += f"FILES/LOCATIONS:\n"
            for file_loc in self.files_locations:
                text += f"  - {file_loc}\n"

        # Enhanced fields
        if self.priority and self.priority != "normal":
            text += f"\nPRIORITY: {self.priority}\n"
        if self.complexity and self.complexity != "moderate":
            text += f"COMPLEXITY: {self.complexity}\n"
        if self.language:
            text += f"LANGUAGE: {self.language}\n"
        if self.frameworks:
            text += f"FRAMEWORKS: {', '.join(self.frameworks)}\n"
        if self.code_references:
            text += f"CODE REFERENCES: {', '.join(self.code_references)}\n"

        return text.strip()


class AgentFormatter:
    """
    Formats transcriptions into structured prompts for coding agents
    Detects patterns and extracts structured information from natural language
    """

    # Programming language keywords
    LANGUAGES = {
        'python': ['python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'pytest'],
        'javascript': ['javascript', 'js', 'node', 'nodejs', 'express', 'react', 'vue', 'angular', 'npm'],
        'typescript': ['typescript', 'ts', 'tsx', 'deno', 'nestjs'],
        'java': ['java', 'spring', 'springboot', 'maven', 'gradle', 'kotlin'],
        'csharp': ['c#', 'csharp', '.net', 'dotnet', 'asp.net', 'unity'],
        'cpp': ['c++', 'cpp', 'qt', 'cmake', 'boost'],
        'go': ['golang', 'go', 'gin', 'echo'],
        'rust': ['rust', 'cargo', 'tokio', 'actix'],
        'ruby': ['ruby', 'rails', 'ruby on rails', 'gem'],
        'php': ['php', 'laravel', 'symfony', 'wordpress'],
        'sql': ['sql', 'postgres', 'postgresql', 'mysql', 'sqlite', 'database'],
    }

    # Framework keywords
    FRAMEWORKS = {
        'react': ['react', 'reactjs', 'jsx'],
        'vue': ['vue', 'vuejs', 'vuex'],
        'angular': ['angular', 'angularjs'],
        'django': ['django'],
        'flask': ['flask'],
        'fastapi': ['fastapi'],
        'express': ['express', 'expressjs'],
        'spring': ['spring', 'springboot', 'spring boot'],
        'rails': ['rails', 'ruby on rails'],
        'laravel': ['laravel'],
        'nextjs': ['nextjs', 'next.js', 'next'],
        'tailwind': ['tailwind', 'tailwindcss'],
        'bootstrap': ['bootstrap'],
        'tensorflow': ['tensorflow', 'tf'],
        'pytorch': ['pytorch', 'torch'],
    }

    def __init__(self):
        # Regex patterns to identify different parts of agent instructions
        self.patterns = {
            'task': [
                r'(?:task:?\s*)(.*)',
                r'(?:implement|create|build|add|develop|make)\s+(.+?)(?:\s+(?:that|which|where)|\s*\.)',
                r'(?:i\s+want|need)\s+(.+?)(?:\s+(?:so|that|when)|\s*\.)',
            ],
            'context': [
                r'(?:context:?\s*)(.*)',
                r'(?:because|since|due to)\s+(.+?)(?:\s*\.)',
                r'(?:currently|right now|at present),?\s+(.+?)(?:\s*\.)',
            ],
            'constraint': [
                r'(?:constraint|requirement|must|should not|avoid):?\s*(.*)',
                r'(?:using|with|utilizing|implement in)\s+(.+?)(?:\s*\.)',
                r'(?:without|excluding|not using)\s+(.+?)(?:\s*\.)',
            ],
            'acceptance': [
                r'(?:acceptance|criteria|condition|expected|should):?\s*(.*)',
                r'(?:so that|such that|in order that)\s+(.+?)(?:\s*\.)',
                r'(?:the\s+result|it)\s+should\s+(.+?)(?:\s*\.)',
            ],
            'priority': [
                r'\b(urgent|asap|critical|important|high priority)\b',
                r'\b(low priority|when you have time|eventually|later)\b',
            ],
            'complexity': [
                r'\b(simple|easy|quick|straightforward|basic)\b',
                r'\b(complex|complicated|advanced|sophisticated|elaborate)\b',
            ],
        }

        # File/path detection patterns
        self.file_patterns = [
            r'[./~][\w/\-.]+\.(?:py|js|ts|jsx|tsx|html|css|scss|java|cpp|c|h|go|rs|rb|php|sql|json|yaml|yml|xml|md|txt)',
            r'(?<=\W)(?:src|lib|test|dist|public|private|assets|components|views|controllers|routes|api)/[\w/\-.]+(?=\W|$)',
        ]

        # Code reference patterns (class names, function names)
        self.code_ref_patterns = [
            r'\b([A-Z][a-zA-Z0-9]*(?:Service|Controller|Repository|Factory|Builder|Handler|Manager|Provider|Helper|Utils?|Model|View|Component|Class|Interface|Abstract|Base))\b',
            r'\b([a-z][a-zA-Z0-9]*(?:Function|Method|Handler|Callback|Validator|Parser|Formatter))\b',
            r'(?:function|method|class|interface)\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'(?:in the|in a|the)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:function|method|class)',
        ]

    def extract_structured_info(self, text: str) -> AgentPrompt:
        """
        Extract structured information from natural language text
        """
        text = self._normalize_text(text)

        # Extract different components
        task = self._extract_task(text)
        context = self._extract_context(text)
        constraints = self._extract_constraints(text)
        acceptance_criteria = self._extract_acceptance_criteria(text)
        files_locations = self._extract_files_locations(text)
        
        # Enhanced extraction
        priority = self._extract_priority(text)
        complexity = self._extract_complexity(text)
        language = self._detect_language(text)
        frameworks = self._detect_frameworks(text)
        code_references = self._extract_code_references(text)

        return AgentPrompt(
            task=task,
            context=context,
            constraints=constraints,
            acceptance_criteria=acceptance_criteria,
            files_locations=files_locations,
            priority=priority,
            complexity=complexity,
            language=language,
            frameworks=frameworks,
            code_references=code_references,
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize text for processing"""
        if not text:
            return ""

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Normalize common contractions and expansions
        replacements = {
            "i'd like": "I want",
            "i would like": "I want",
            "can you": "implement",
            "could you": "implement",
            "would you": "implement",
        }

        for old, new in replacements.items():
            text = re.sub(r'\b' + re.escape(old) + r'\b', new, text, flags=re.IGNORECASE)

        return text

    def _extract_task(self, text: str) -> str:
        """Extract the main task from the text"""
        # Try explicit patterns first
        for pattern in self.patterns['task']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task = match.group(1).strip()
                if len(task) > 3:  # Skip very short matches
                    return task

        # If no explicit task found, use the first sentence that sounds like a task
        sentences = self._split_sentences(text)
        for sentence in sentences:
            sentence = sentence.strip()
            if any(word in sentence.lower() for word in ['implement', 'create', 'add', 'build', 'develop']):
                return sentence

        # Default to first substantial sentence
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                return sentence

        return ""

    def _extract_context(self, text: str) -> str:
        """Extract context/background information"""
        for pattern in self.patterns['context']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = match.group(1).strip()
                if len(context) > 3:
                    return context
        return ""

    def _extract_constraints(self, text: str) -> str:
        """Extract constraints and requirements"""
        constraints = []

        for pattern in self.patterns['constraint']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                constraint = match.group(1).strip()
                if len(constraint) > 3:
                    constraints.append(constraint)

        return "; ".join(constraints)

    def _extract_acceptance_criteria(self, text: str) -> str:
        """Extract acceptance criteria"""
        criteria = []

        for pattern in self.patterns['acceptance']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                criterion = match.group(1).strip()
                if len(criterion) > 3:
                    criteria.append(criterion)

        return "; ".join(criteria)

    def _extract_files_locations(self, text: str) -> List[str]:
        """Extract file paths and locations mentioned in the text"""
        files = set()

        for pattern in self.file_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                file_path = match.group(0).strip()
                files.add(file_path)

        # Also look for common directory patterns mentioned in text
        dir_patterns = [
            r'\b(src|lib|test|dist|public|private|assets|components|views|controllers|routes|api)\b',
        ]

        for pattern in dir_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                directory = match.group(0)
                files.add(directory)

        return sorted(list(files))

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split on sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        # Filter out empty strings and clean up
        return [s.strip() for s in sentences if s.strip()]

    def _extract_priority(self, text: str) -> str:
        """Extract priority level from text"""
        text_lower = text.lower()
        
        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'critical', 'important', 'high priority', 'immediately', 'right now']
        for keyword in urgent_keywords:
            if keyword in text_lower:
                return "urgent"
        
        # Check for low priority keywords
        low_keywords = ['low priority', 'when you have time', 'eventually', 'later', 'no rush', 'whenever']
        for keyword in low_keywords:
            if keyword in text_lower:
                return "low"
        
        return "normal"

    def _extract_complexity(self, text: str) -> str:
        """Estimate complexity from text"""
        text_lower = text.lower()
        
        # Check for simple keywords
        simple_keywords = ['simple', 'easy', 'quick', 'straightforward', 'basic', 'small', 'minor']
        for keyword in simple_keywords:
            if keyword in text_lower:
                return "simple"
        
        # Check for complex keywords
        complex_keywords = ['complex', 'complicated', 'advanced', 'sophisticated', 'elaborate', 'comprehensive', 'full']
        for keyword in complex_keywords:
            if keyword in text_lower:
                return "complex"
        
        # Heuristic: count technical terms and file mentions
        technical_count = 0
        if self._extract_files_locations(text):
            technical_count += len(self._extract_files_locations(text))
        
        # Words that suggest complexity
        complexity_indicators = ['integrate', 'migrate', 'refactor', 'architect', 'design', 'system', 'multiple']
        for indicator in complexity_indicators:
            if indicator in text_lower:
                technical_count += 1
        
        if technical_count >= 3:
            return "complex"
        elif technical_count >= 1:
            return "moderate"
        
        return "moderate"

    def _detect_language(self, text: str) -> str:
        """Detect programming language from text"""
        text_lower = text.lower()
        
        for lang, keywords in self.LANGUAGES.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return lang
        
        # Try to detect from file extensions
        for pattern in self.file_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                file_path = match.group(0).lower()
                for lang, keywords in self.LANGUAGES.items():
                    for keyword in keywords:
                        if keyword in file_path:
                            return lang
        
        return ""

    def _detect_frameworks(self, text: str) -> List[str]:
        """Detect frameworks mentioned in text"""
        text_lower = text.lower()
        detected = set()
        
        for framework, keywords in self.FRAMEWORKS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.add(framework)
        
        return sorted(list(detected))

    def _extract_code_references(self, text: str) -> List[str]:
        """Extract class names, function names, and other code references"""
        references = set()
        
        for pattern in self.code_ref_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ref = match.group(1).strip()
                # Filter out common words
                if ref and len(ref) > 2 and ref.lower() not in ['the', 'a', 'an', 'this', 'that', 'class', 'function', 'method']:
                    references.add(ref)
        
        return sorted(list(references))

    def format_for_agent(self, text: str, mode: str = "structured") -> str:
        """
        Format text for agent consumption

        Args:
            text: Input text to format
            mode: "structured", "markdown", or "plain"
        """
        if not text.strip():
            return ""

        # If the text is already in structured format (contains headers), return as-is
        if any(header in text.lower() for header in ["task:", "context:", "constraint:", "acceptance:"]):
            return text

        # Extract structured information
        structured = self.extract_structured_info(text)

        if mode == "markdown":
            return structured.to_markdown()
        elif mode == "plain":
            return structured.to_text()
        else:  # structured (default)
            result = []

            if structured.task:
                result.append(f"TASK: {structured.task}")

            if structured.context:
                result.append(f"CONTEXT: {structured.context}")

            if structured.constraints:
                result.append(f"CONSTRAINTS: {structured.constraints}")

            if structured.acceptance_criteria:
                result.append(f"ACCEPTANCE CRITERIA: {structured.acceptance_criteria}")

            if structured.files_locations:
                result.append(f"FILES/LOCATIONS: {', '.join(structured.files_locations)}")

            # Enhanced fields
            if structured.priority and structured.priority != "normal":
                result.append(f"PRIORITY: {structured.priority}")

            if structured.complexity and structured.complexity != "moderate":
                result.append(f"COMPLEXITY: {structured.complexity}")

            if structured.language:
                result.append(f"LANGUAGE: {structured.language}")

            if structured.frameworks:
                result.append(f"FRAMEWORKS: {', '.join(structured.frameworks)}")

            if structured.code_references:
                result.append(f"CODE REFERENCES: {', '.join(structured.code_references)}")

            return "\n\n".join(result)


class ModeDetector:
    """
    Detects whether input should be processed as regular dictation or agent mode
    """

    AGENT_MODE_TRIGGERS = [
        r'\bagency\b',  # "send to agency" or similar
        r'\bagent mode\b',
        r'\bcoding task\b',
        r'\bimplement (?:a|the|this)\b',
        r'\bcreate (?:a|the|this)\b',
        r'\bbuild (?:a|the|this)\b',
        r'\bdevelopment\b',
        r'\bcoding\b',
        r'\bsoftware\b',
        r'\bprogram\b',
        r'\bapplication\b',
        r'\bfeature\b',
        r'\bfunctionality\b',
        r'\balgorithm\b',
    ]

    DICTATION_MODE_TRIGGERS = [
        r'\bdictation mode\b',
        r'\bregular mode\b',
        r'\bnormal mode\b',
    ]

    def __init__(self):
        pass

    def detect_mode(self, text: str) -> str:
        """
        Detect if the input suggests agent mode or dictation mode
        Returns "agent" or "dictation"
        """
        text_lower = text.lower()

        # Check for explicit mode triggers
        for pattern in self.DICTATION_MODE_TRIGGERS:
            if re.search(pattern, text_lower):
                return "dictation"

        for pattern in self.AGENT_MODE_TRIGGERS:
            if re.search(pattern, text_lower):
                return "agent"

        # If no explicit trigger, return "dictation" as default
        return "dictation"


# Example usage and testing
if __name__ == "__main__":
    formatter = AgentFormatter()
    detector = ModeDetector()

    # Test examples
    test_cases = [
        "I want to implement a function that validates email addresses using regex, and it should return true for valid emails and false for invalid ones.",
        "Create a React component called UserCard that displays user information. It should include name, avatar, and email. Make sure it's responsive and use TypeScript.",
        "I need to build a REST API endpoint at /api/users that returns a list of users. It should connect to a PostgreSQL database and handle pagination.",
        "Write a Python script to process CSV files in the data/ directory. The script should clean the data and save results to processed/ folder.",
    ]

    for i, text in enumerate(test_cases):
        print(f"\n--- Test Case {i+1} ---")
        print(f"Input: {text}")
        print(f"Detected Mode: {detector.detect_mode(text)}")

        formatted = formatter.format_for_agent(text, mode="structured")
        print(f"Formatted:\n{formatted}")

        markdown = formatter.format_for_agent(text, mode="markdown")
        print(f"Markdown:\n{markdown}")