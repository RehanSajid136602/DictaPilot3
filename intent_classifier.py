"""
DictaPilot Intent Classifier
Detects user intent from voice input (spec, code, documentation, review)

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Types of user intent"""
    SPEC = "spec"
    CODE = "code"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    COMMAND = "command"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: IntentType
    confidence: float
    indicators: List[str]
    metadata: Dict[str, any] = None


class IntentClassifier:
    """Classifies user intent from voice input"""
    
    # Spec mode indicators
    SPEC_KEYWORDS = [
        "spec", "specification", "requirement", "requirements",
        "goal", "objective", "purpose", "acceptance criteria",
        "constraint", "limitation", "non-goal", "out of scope",
        "we need to", "we want to", "we should", "let's build",
        "feature request", "new feature", "enhancement"
    ]
    
    SPEC_PHRASES = [
        r"start (?:new )?spec",
        r"create (?:a )?spec(?:ification)?",
        r"(?:the )?goal is",
        r"(?:the )?purpose is",
        r"acceptance criteria",
        r"success criteria",
        r"done when",
        r"we need to (?:build|create|implement)",
        r"(?:add|update) (?:constraint|requirement)"
    ]
    
    # Code mode indicators
    CODE_KEYWORDS = [
        "function", "class", "method", "variable", "import",
        "define", "declare", "initialize", "return", "loop",
        "if statement", "else", "elif", "try", "except",
        "async", "await", "lambda", "decorator"
    ]
    
    CODE_PHRASES = [
        r"write (?:a )?(?:function|class|method)",
        r"create (?:a )?(?:function|class|variable)",
        r"define (?:a )?(?:function|class)",
        r"implement (?:the )?(?:function|method|class)",
        r"add (?:a )?(?:function|method|class)",
        r"(?:for|while) loop",
        r"if (?:statement|condition)",
        r"try catch|try except"
    ]
    
    # Documentation mode indicators
    DOC_KEYWORDS = [
        "document", "documentation", "docstring", "comment",
        "readme", "guide", "tutorial", "example", "usage",
        "api reference", "changelog", "release notes"
    ]
    
    DOC_PHRASES = [
        r"write (?:the )?(?:documentation|docs|readme)",
        r"add (?:a )?(?:comment|docstring)",
        r"document (?:the )?(?:function|class|module)",
        r"create (?:a )?(?:guide|tutorial)",
        r"update (?:the )?(?:readme|changelog)"
    ]
    
    # Review mode indicators
    REVIEW_KEYWORDS = [
        "review", "feedback", "suggestion", "improvement",
        "issue", "problem", "bug", "error", "fix",
        "refactor", "optimize", "clean up", "improve"
    ]
    
    REVIEW_PHRASES = [
        r"(?:code )?review",
        r"(?:give|provide) feedback",
        r"(?:this|that) (?:looks|seems|appears)",
        r"(?:should|could|might) (?:be|improve|change)",
        r"(?:there's|there is) (?:a|an) (?:issue|problem|bug)",
        r"(?:needs|requires) (?:refactoring|improvement)"
    ]
    
    # Command mode indicators
    COMMAND_KEYWORDS = [
        "delete", "clear", "undo", "ignore", "replace",
        "send to", "export", "save", "load", "open"
    ]
    
    COMMAND_PHRASES = [
        r"(?:delete|remove|clear) (?:that|this|it)",
        r"send to (?:cursor|windsurf|cline|ide)",
        r"export (?:as|to)",
        r"save (?:spec|file|document)",
        r"(?:start|stop|pause) (?:recording|dictation)"
    ]
    
    def __init__(self, auto_detect: bool = True):
        self.auto_detect = auto_detect
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        self.spec_patterns = [re.compile(p, re.IGNORECASE) for p in self.SPEC_PHRASES]
        self.code_patterns = [re.compile(p, re.IGNORECASE) for p in self.CODE_PHRASES]
        self.doc_patterns = [re.compile(p, re.IGNORECASE) for p in self.DOC_PHRASES]
        self.review_patterns = [re.compile(p, re.IGNORECASE) for p in self.REVIEW_PHRASES]
        self.command_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_PHRASES]
    
    def classify(self, text: str) -> IntentResult:
        """Classify intent from text"""
        if not self.auto_detect:
            return IntentResult(IntentType.UNKNOWN, 0.0, [])
        
        text_lower = text.lower()
        
        # Calculate scores for each intent type
        spec_score, spec_indicators = self._calculate_score(
            text_lower, self.SPEC_KEYWORDS, self.spec_patterns
        )
        code_score, code_indicators = self._calculate_score(
            text_lower, self.CODE_KEYWORDS, self.code_patterns
        )
        doc_score, doc_indicators = self._calculate_score(
            text_lower, self.DOC_KEYWORDS, self.doc_patterns
        )
        review_score, review_indicators = self._calculate_score(
            text_lower, self.REVIEW_KEYWORDS, self.review_patterns
        )
        command_score, command_indicators = self._calculate_score(
            text_lower, self.COMMAND_KEYWORDS, self.command_patterns
        )
        
        # Find highest score
        scores = {
            IntentType.SPEC: (spec_score, spec_indicators),
            IntentType.CODE: (code_score, code_indicators),
            IntentType.DOCUMENTATION: (doc_score, doc_indicators),
            IntentType.REVIEW: (review_score, review_indicators),
            IntentType.COMMAND: (command_score, command_indicators)
        }
        
        max_intent = max(scores.items(), key=lambda x: x[1][0])
        intent_type = max_intent[0]
        score, indicators = max_intent[1]
        
        # Normalize confidence (0-1 range)
        confidence = min(score / 10.0, 1.0)
        
        # If confidence too low, mark as unknown
        if confidence < 0.3:
            return IntentResult(IntentType.UNKNOWN, confidence, [])
        
        # Extract metadata based on intent
        metadata = self._extract_metadata(text, intent_type)
        
        return IntentResult(intent_type, confidence, indicators, metadata)
    
    def _calculate_score(
        self, 
        text: str, 
        keywords: List[str], 
        patterns: List[re.Pattern]
    ) -> Tuple[float, List[str]]:
        """Calculate score for a specific intent type"""
        score = 0.0
        indicators = []
        
        # Check keywords (1 point each)
        for keyword in keywords:
            if keyword in text:
                score += 1.0
                indicators.append(keyword)
        
        # Check patterns (2 points each, more specific)
        for pattern in patterns:
            if pattern.search(text):
                score += 2.0
                match = pattern.search(text)
                if match:
                    indicators.append(match.group(0))
        
        return score, indicators
    
    def _extract_metadata(self, text: str, intent: IntentType) -> Dict[str, any]:
        """Extract metadata based on intent type"""
        metadata = {}
        
        if intent == IntentType.SPEC:
            # Extract spec type (feature, bugfix, refactor)
            if re.search(r"(?:new )?feature", text, re.IGNORECASE):
                metadata["spec_type"] = "feature"
            elif re.search(r"bug(?:fix)?", text, re.IGNORECASE):
                metadata["spec_type"] = "bugfix"
            elif re.search(r"refactor", text, re.IGNORECASE):
                metadata["spec_type"] = "refactor"
            else:
                metadata["spec_type"] = "general"
        
        elif intent == IntentType.CODE:
            # Extract programming language hints
            if re.search(r"python|\.py", text, re.IGNORECASE):
                metadata["language"] = "python"
            elif re.search(r"javascript|\.js", text, re.IGNORECASE):
                metadata["language"] = "javascript"
            elif re.search(r"typescript|\.ts", text, re.IGNORECASE):
                metadata["language"] = "typescript"
        
        elif intent == IntentType.COMMAND:
            # Extract command target
            if re.search(r"cursor", text, re.IGNORECASE):
                metadata["target"] = "cursor"
            elif re.search(r"windsurf", text, re.IGNORECASE):
                metadata["target"] = "windsurf"
            elif re.search(r"cline", text, re.IGNORECASE):
                metadata["target"] = "cline"
        
        return metadata
    
    def is_spec_mode(self, text: str) -> bool:
        """Quick check if text indicates spec mode"""
        result = self.classify(text)
        return result.intent == IntentType.SPEC and result.confidence > 0.5
    
    def is_code_mode(self, text: str) -> bool:
        """Quick check if text indicates code mode"""
        result = self.classify(text)
        return result.intent == IntentType.CODE and result.confidence > 0.5
    
    def is_doc_mode(self, text: str) -> bool:
        """Quick check if text indicates documentation mode"""
        result = self.classify(text)
        return result.intent == IntentType.DOCUMENTATION and result.confidence > 0.5
    
    def is_review_mode(self, text: str) -> bool:
        """Quick check if text indicates review mode"""
        result = self.classify(text)
        return result.intent == IntentType.REVIEW and result.confidence > 0.5
    
    def suggest_mode(self, text: str) -> str:
        """Suggest appropriate mode based on text"""
        result = self.classify(text)
        
        if result.confidence < 0.5:
            return "dictation"
        
        mode_map = {
            IntentType.SPEC: "spec",
            IntentType.CODE: "code",
            IntentType.DOCUMENTATION: "documentation",
            IntentType.REVIEW: "review",
            IntentType.COMMAND: "command"
        }
        
        return mode_map.get(result.intent, "dictation")
