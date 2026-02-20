"""
DictaPilot Demo Mode Module
Provides interactive demo and tutorial functionality.

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
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


def get_demo_config_path() -> Path:
    """Get platform-specific demo config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "demo.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "demo.json"


def get_demo_config_dir() -> Path:
    """Create and return demo config directory"""
    config_path = get_demo_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class DemoState(Enum):
    """Demo state"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class DemoStepType(Enum):
    """Types of demo steps"""
    INTRODUCTION = "introduction"
    TEXT_DISPLAY = "text_display"
    VOICE_INPUT = "voice_input"
    TEXT_EDIT = "text_edit"
    INTERACTION = "interaction"
    CHECKPOINT = "checkpoint"
    COMPLETION = "completion"


@dataclass
class DemoStep:
    """A single step in the demo"""
    step_id: str
    title: str
    description: str
    step_type: DemoStepType
    content: Optional[str] = None
    expected_input: Optional[str] = None
    hint: Optional[str] = None
    duration_seconds: int = 0
    animation: Optional[str] = None


@dataclass
class DemoScenario:
    """A demo scenario with multiple steps"""
    scenario_id: str
    title: str
    description: str
    steps: List[DemoStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    difficulty: str = "beginner"
    estimated_time: int = 5  # minutes


# Demo scenarios
DEMO_SCENARIOS: Dict[str, DemoScenario] = {
    "basic_dictation": DemoScenario(
        scenario_id="basic_dictation",
        title="Basic Dictation",
        description="Learn the fundamentals of voice dictation",
        tags=["basics", "getting started"],
        difficulty="beginner",
        estimated_time=5,
        steps=[
            DemoStep(
                step_id="intro",
                title="Welcome to DictaPilot",
                description="This interactive tutorial will teach you the basics of voice dictation.",
                step_type=DemoStepType.INTRODUCTION,
                duration_seconds=5
            ),
            DemoStep(
                step_id="speak",
                title="Start Speaking",
                description="Press the microphone button and speak naturally. DictaPilot will convert your speech to text in real-time.",
                step_type=DemoStepType.VOICE_INPUT,
                hint="Try saying: 'Hello, this is a test of DictaPilot's dictation capabilities.'",
                duration_seconds=30
            ),
            DemoStep(
                step_id="edit",
                title="Edit Your Text",
                description="Use voice commands to edit. Say 'scratch that' to undo, 'capitalize' to fix capitalization.",
                step_type=DemoStepType.INTERACTION,
                hint="Say 'scratch that' to undo your last input"
            ),
            DemoStep(
                step_id="complete",
                title="Great Job!",
                description="You've completed the basic dictation tutorial!",
                step_type=DemoStepType.COMPLETION
            )
        ]
    ),
    
    "voice_commands": DemoScenario(
        scenario_id="voice_commands",
        title="Voice Commands",
        description="Master DictaPilot's voice command system",
        tags=["voice commands", "editing"],
        difficulty="intermediate",
        estimated_time=7,
        steps=[
            DemoStep(
                step_id="intro",
                title="Voice Commands Overview",
                description="DictaPilot supports many voice commands for editing and formatting.",
                step_type=DemoStepType.INTRODUCTION,
                duration_seconds=3
            ),
            DemoStep(
                step_id="correction",
                title="Correction Commands",
                description="Say 'scratch that' to undo, 'undo' to revert changes, 'redo' to reapply.",
                step_type=DemoStepType.TEXT_DISPLAY,
                content="Example: 'The quick brown fox [scratch that] lazy dog' → 'The quick brown fox '",
                animation="highlight"
            ),
            DemoStep(
                step_id="formatting",
                title="Formatting Commands",
                description="Use commands like 'new line', 'new paragraph', 'capitalize', 'all caps'.",
                step_type=DemoStepType.TEXT_DISPLAY,
                content="Say 'new line' to start a new line.\nSay 'new paragraph' for a new paragraph.\nSay 'capitalize' to capitalize the last word.",
                animation="typing"
            ),
            DemoStep(
                step_id="punctuation",
                title="Punctuation Commands",
                description="Say 'period', 'comma', 'question mark', 'exclamation point' for punctuation.",
                step_type=DemoStepType.INTERACTION,
                hint="Try: 'Hello comma world period'"
            ),
            DemoStep(
                step_id="complete",
                title="Command Mastery",
                description="You're now ready to use voice commands for efficient editing!",
                step_type=DemoStepType.COMPLETION
            )
        ]
    ),
    
    "advanced_editing": DemoScenario(
        scenario_id="advanced_editing",
        title="Advanced Editing",
        description="Learn advanced text editing with voice commands",
        tags=["advanced", "editing", "power user"],
        difficulty="advanced",
        estimated_time=10,
        steps=[
            DemoStep(
                step_id="intro",
                title="Advanced Editing Features",
                description="Learn powerful editing commands for efficient text manipulation.",
                step_type=DemoStepType.INTRODUCTION,
                duration_seconds=3
            ),
            DemoStep(
                step_id="selection",
                title="Selection Commands",
                description="Select text using voice: 'select all', 'select last sentence', 'select paragraph'.",
                step_type=DemoStepType.TEXT_DISPLAY,
                content="Use: 'select last word', 'select next sentence', 'select all'"
            ),
            DemoStep(
                step_id="replacement",
                title="Find and Replace",
                description="Replace text with: 'replace X with Y', 'change all X to Y'.",
                step_type=DemoStepType.INTERACTION,
                content="Example: 'replace cat with dog' changes 'cat' to 'dog'",
                hint="Try: 'replace hello with greeting'"
            ),
            DemoStep(
                step_id="navigation",
                title="Navigation Commands",
                description="Navigate through text: 'go to start', 'go to end', 'go to line five'.",
                step_type=DemoStepType.INTERACTION,
                hint="Say 'go to end' to jump to the end of your text"
            ),
            DemoStep(
                step_id="complete",
                title="Advanced Editing Complete",
                description="You now have full control over text editing with voice commands!",
                step_type=DemoStepType.COMPLETION
            )
        ]
    ),
    
    "customization": DemoScenario(
        scenario_id="customization",
        title="Customization & Settings",
        description="Personalize DictaPilot to your workflow",
        tags=["settings", "personalization"],
        difficulty="beginner",
        estimated_time=6,
        steps=[
            DemoStep(
                step_id="intro",
                title="Customize Your Experience",
                description="DictaPilot offers many customization options to match your workflow.",
                step_type=DemoStepType.INTRODUCTION,
                duration_seconds=3
            ),
            DemoStep(
                step_id="presets",
                title="Application Presets",
                description="Set different formatting for different apps: email, code, chat, documents.",
                step_type=DemoStepType.TEXT_DISPLAY,
                content="Go to Settings → Formatting to set presets for each application"
            ),
            DemoStep(
                step_id="shortcuts",
                title="Custom Commands",
                description="Create your own voice snippets and commands in the Snippet Library.",
                step_type=DemoStepType.INTERACTION,
                hint="Open Snippet Library to create custom voice snippets"
            ),
            DemoStep(
                step_id="complete",
                title="Personalization Complete",
                description="Your DictaPilot is now personalized to your needs!",
                step_type=DemoStepType.COMPLETION
            )
        ]
    )
}


class DemoProgressTracker:
    """Tracks user progress through demos"""
    
    def __init__(self):
        self.progress: Dict[str, Dict[str, Any]] = {}
        self._load_progress()
    
    def _load_progress(self):
        """Load progress from file"""
        config_path = get_demo_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.progress = data.get('progress', {})
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_progress(self):
        """Save progress to file"""
        get_demo_config_dir()
        config_path = get_demo_config_path()
        
        data = {'progress': self.progress}
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def start_scenario(self, scenario_id: str):
        """Mark a scenario as started"""
        if scenario_id not in self.progress:
            self.progress[scenario_id] = {}
        
        self.progress[scenario_id]['state'] = DemoState.IN_PROGRESS.value
        self.progress[scenario_id]['started_at'] = time.time()
        self.progress[scenario_id]['current_step'] = 0
        self._save_progress()
    
    def complete_step(self, scenario_id: str, step_id: str, step_index: int):
        """Mark a step as completed"""
        if scenario_id not in self.progress:
            return
        
        if 'completed_steps' not in self.progress[scenario_id]:
            self.progress[scenario_id]['completed_steps'] = []
        
        self.progress[scenario_id]['completed_steps'].append(step_id)
        self.progress[scenario_id]['current_step'] = step_index + 1
        self._save_progress()
    
    def complete_scenario(self, scenario_id: str):
        """Mark a scenario as completed"""
        if scenario_id not in self.progress:
            return
        
        self.progress[scenario_id]['state'] = DemoState.COMPLETED.value
        self.progress[scenario_id]['completed_at'] = time.time()
        self._save_progress()
    
    def skip_scenario(self, scenario_id: str):
        """Skip a scenario"""
        if scenario_id not in self.progress:
            self.progress[scenario_id] = {}
        
        self.progress[scenario_id]['state'] = DemoState.SKIPPED.value
        self._save_progress()
    
    def get_progress(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for a scenario"""
        return self.progress.get(scenario_id)
    
    def get_all_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get all progress"""
        return self.progress
    
    def reset_progress(self, scenario_id: str = None):
        """Reset progress"""
        if scenario_id:
            self.progress.pop(scenario_id, None)
        else:
            self.progress = {}
        self._save_progress()


class DemoPlayer:
    """Plays demo scenarios"""
    
    def __init__(self):
        self.scenarios = DEMO_SCENARIOS
        self.progress = DemoProgressTracker()
        self.current_scenario: Optional[DemoScenario] = None
        self.current_step_index = 0
        self.state = DemoState.NOT_STARTED
        self.callbacks: Dict[str, List[Callable]] = {
            'on_step_start': [],
            'on_step_complete': [],
            'on_scenario_complete': [],
            'on_state_change': []
        }
    
    def register_callback(self, event: str, callback: Callable):
        """Register event callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs):
        """Emit event to callbacks"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass
    
    def start_scenario(self, scenario_id: str) -> bool:
        """Start a demo scenario"""
        if scenario_id not in self.scenarios:
            return False
        
        self.current_scenario = self.scenarios[scenario_id]
        self.current_step_index = 0
        self.state = DemoState.IN_PROGRESS
        
        self.progress.start_scenario(scenario_id)
        self._emit('on_state_change', self.state)
        self._emit('on_step_start', self.current_scenario.steps[0])
        
        return True
    
    def next_step(self) -> Optional[DemoStep]:
        """Move to next step"""
        if not self.current_scenario:
            return None
        
        # Mark current step complete
        if self.current_step_index < len(self.current_scenario.steps):
            current_step = self.current_scenario.steps[self.current_step_index]
            self.progress.complete_step(
                self.current_scenario.scenario_id,
                current_step.step_id,
                self.current_step_index
            )
        
        # Move to next
        self.current_step_index += 1
        
        if self.current_step_index >= len(self.current_scenario.steps):
            # Scenario complete
            self.state = DemoState.COMPLETED
            self.progress.complete_scenario(self.current_scenario.scenario_id)
            self._emit('on_scenario_complete', self.current_scenario)
            self._emit('on_state_change', self.state)
            return None
        
        next_step = self.current_scenario.steps[self.current_step_index]
        self._emit('on_step_start', next_step)
        
        return next_step
    
    def previous_step(self) -> Optional[DemoStep]:
        """Move to previous step"""
        if not self.current_scenario or self.current_step_index == 0:
            return None
        
        self.current_step_index -= 1
        prev_step = self.current_scenario.steps[self.current_step_index]
        self._emit('on_step_start', prev_step)
        
        return prev_step
    
    def skip_scenario(self):
        """Skip current scenario"""
        if self.current_scenario:
            self.progress.skip_scenario(self.current_scenario.scenario_id)
            self.state = DemoState.SKIPPED
            self._emit('on_state_change', self.state)
    
    def get_current_step(self) -> Optional[DemoStep]:
        """Get current step"""
        if not self.current_scenario:
            return None
        
        if self.current_step_index < len(self.current_scenario.steps):
            return self.current_scenario.steps[self.current_step_index]
        
        return None
    
    def get_scenario(self, scenario_id: str) -> Optional[DemoScenario]:
        """Get scenario by ID"""
        return self.scenarios.get(scenario_id)
    
    def get_all_scenarios(self) -> List[DemoScenario]:
        """Get all available scenarios"""
        return list(self.scenarios.values())
    
    def get_scenario_progress(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for a scenario"""
        return self.progress.get_progress(scenario_id)
    
    def get_recommended_scenario(self) -> Optional[DemoScenario]:
        """Get recommended scenario based on user progress"""
        completed = [
            sid for sid, p in self.progress.get_all_progress().items()
            if p.get('state') == DemoState.COMPLETED.value
        ]
        
        # Recommend next uncompleted scenario
        for scenario in self.scenarios.values():
            if scenario.scenario_id not in completed:
                return scenario
        
        # All completed, return first
        return next(iter(self.scenarios.values()), None)


# Global instance
_demo_player_instance: Optional[DemoPlayer] = None


def get_demo_player() -> DemoPlayer:
    """Get or create the global demo player instance"""
    global _demo_player_instance
    if _demo_player_instance is None:
        _demo_player_instance = DemoPlayer()
    return _demo_player_instance


# Demo API functions for external use
def start_demo(scenario_id: str) -> bool:
    """Start a demo scenario"""
    player = get_demo_player()
    return player.start_scenario(scenario_id)


def get_demo_scenarios() -> List[Dict[str, Any]]:
    """Get all demo scenarios"""
    player = get_demo_player()
    scenarios = player.get_all_scenarios()
    
    return [
        {
            'id': s.scenario_id,
            'title': s.title,
            'description': s.description,
            'tags': s.tags,
            'difficulty': s.difficulty,
            'estimated_time': s.estimated_time,
            'steps_count': len(s.steps)
        }
        for s in scenarios
    ]


def get_demo_progress() -> Dict[str, Any]:
    """Get overall demo progress"""
    player = get_demo_player()
    progress = player.progress.get_all_progress()
    
    return {
        'completed': sum(1 for p in progress.values() if p.get('state') == DemoState.COMPLETED.value),
        'in_progress': sum(1 for p in progress.values() if p.get('state') == DemoState.IN_PROGRESS.value),
        'total': len(player.scenarios),
        'scenarios': progress
    }
