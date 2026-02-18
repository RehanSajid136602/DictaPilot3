# Voice Commands Reference

DictaPilot3 supports smart voice commands for editing and controlling your dictation. Commands are processed in real-time and work across all applications.

## Command Categories

- [Editing Commands](#editing-commands) - Delete, undo, clear text
- [Replacement Commands](#replacement-commands) - Replace words or phrases
- [Formatting Commands](#formatting-commands) - Capitalize, rewrite, fix grammar
- [Control Commands](#control-commands) - Ignore, skip utterances
- [Inline Corrections](#inline-corrections) - Self-correct while speaking

---

## Editing Commands

### Delete Last Segment

Remove the most recently dictated text.

**Commands:**
- "delete that"
- "delete previous"
- "undo"
- "undo that"
- "scratch that"
- "remove that"
- "remove previous"
- "take that out"
- "erase that"
- "drop that"
- "backspace that"

**Example:**
```
You say: "Hello world"
Text: "Hello world"

You say: "delete that"
Text: "" (cleared)
```

**Example with continuation:**
```
You say: "The quick brown fox"
Text: "The quick brown fox"

You say: "delete that jumps over the lazy dog"
Text: "jumps over the lazy dog"
```

### Clear All Text

Remove all dictated text and start fresh.

**Commands:**
- "clear all"
- "clear everything"
- "reset"
- "reset all"
- "start over"
- "wipe all"
- "wipe everything"
- "erase all"

**Example:**
```
You say: "This is a long paragraph with multiple sentences"
Text: "This is a long paragraph with multiple sentences"

You say: "clear all"
Text: "" (all cleared)
```

### Clear (Simple)

Short form of clear all.

**Commands:**
- "clear"
- "reset"
- "wipe"

**Example:**
```
You say: "Some text here"
Text: "Some text here"

You say: "clear"
Text: "" (cleared)
```

---

## Replacement Commands

### Replace Word or Phrase

Replace specific text with new text.

**Commands:**
- "replace [target] with [replacement]"
- "change [target] to [replacement]"
- "swap [target] for [replacement]"

**Example:**
```
You say: "Hello world"
Text: "Hello world"

You say: "replace hello with goodbye"
Text: "goodbye world"
```

**Example with phrases:**
```
You say: "The quick brown fox jumps"
Text: "The quick brown fox jumps"

You say: "replace quick brown with slow red"
Text: "The slow red fox jumps"
```

---

## Formatting Commands

### Rewrite with Tone

Rewrite text in a specific tone or style.

**Commands:**
- "rewrite [tone]"
- "rephrase [tone]"
- "polish [tone]"
- "improve [tone]"
- "make it [tone]"

**Supported tones:**
- formal
- polite
- casual
- friendly
- concise
- professional
- natural

**Example:**
```
You say: "Hey can you help me out"
Text: "Hey can you help me out"

You say: "rewrite formal"
Text: "Could you please assist me"
```

**Example:**
```
You say: "I need this done ASAP"
Text: "I need this done ASAP"

You say: "make it polite"
Text: "I would appreciate if this could be completed soon"
```

### Capitalize

Capitalize the last word or phrase.

**Commands:**
- "capitalize that"
- "capitalize last"
- "make that capitalized"
- "uppercase that"

**Example:**
```
You say: "python is great"
Text: "python is great"

You say: "capitalize that"
Text: "Python is great"
```

### Fix Grammar

Correct grammar in the text.

**Commands:**
- "fix grammar"
- "correct grammar"
- "fix that"

**Example:**
```
You say: "I is going to the store"
Text: "I is going to the store"

You say: "fix grammar"
Text: "I am going to the store"
```

---

## Control Commands

### Ignore Utterance

Don't include the current utterance in the transcript.

**Commands:**
- "ignore"
- "ignore that"
- "ignore this"
- "ignore it"
- "skip"
- "skip that"
- "disregard"
- "omit"
- "don't include"
- "don't include that"
- "do not include"
- "don't add"
- "do not add"
- "leave that out"
- "cancel that"
- "nevermind"
- "never mind"

**Example:**
```
You say: "This is important"
Text: "This is important"

You say: "ignore this is not important"
Text: "This is important" (second utterance ignored)
```

**Trailing ignore:**
```
You say: "Maybe we should add this ignore that"
Text: "Maybe we should add this" (trailing part ignored)
```

---

## Inline Corrections

### Self-Correction While Speaking

Correct yourself mid-sentence using natural phrases.

**Correction phrases:**
- "no"
- "no no"
- "nope"
- "sorry"
- "I mean"
- "actually"

**Example:**
```
You say: "Use Python no JavaScript for this project"
Text: "Use JavaScript for this project"
```

**Example:**
```
You say: "The meeting is at 3 PM sorry I mean 4 PM"
Text: "The meeting is at 4 PM"
```

### Negation Replacement

Use "not X but Y" pattern for corrections.

**Pattern:**
- "not [wrong] [right]"
- "not [wrong] use [right]"
- "not [wrong] but [right]"

**Example:**
```
You say: "not Python JavaScript"
Text: "JavaScript"
```

**Example:**
```
You say: "We'll use not MySQL but PostgreSQL"
Text: "We'll use PostgreSQL"
```

---

## Smart Cleanup Features

DictaPilot automatically cleans up your dictation:

### Filler Word Removal

Automatically removes: "uh", "um", "erm", "ah", "hmm"

**Example:**
```
You say: "Um this is uh a test"
Text: "This is a test"
```

### Filler Phrase Removal

Removes: "you know", "I mean", "kind of", "sort of"

**Example:**
```
You say: "This is kind of important you know"
Text: "This is important"
```

### Repeated Word Removal

Removes duplicate words.

**Example:**
```
You say: "The the quick brown brown fox"
Text: "The quick brown fox"
```

### Punctuation Cleanup

Fixes repeated punctuation.

**Example:**
```
You say: "What??? Really!!!"
Text: "What? Really!"
```

---

## Command Prefaces

You can preface commands with natural phrases:

- "oh no"
- "oops"
- "please"
- "hey"
- "okay"
- "wait"
- "well"

**Example:**
```
You say: "Hello world"
Text: "Hello world"

You say: "oh no delete that"
Text: "" (deleted)
```

---

## Tips for Best Results

1. **Speak naturally** - Don't over-enunciate or speak robotically
2. **Use pauses** - Brief pauses help separate commands from content
3. **Be specific** - "replace hello with hi" is clearer than "change it"
4. **Combine commands** - "delete that and start over" works
5. **Practice common commands** - Muscle memory helps with frequently used commands

---

## Configuration

### Cleanup Levels

Control how aggressively DictaPilot cleans up your speech:

```bash
# In .env file
CLEANUP_LEVEL=basic      # Minimal cleanup
CLEANUP_LEVEL=balanced   # Moderate cleanup (default)
CLEANUP_LEVEL=aggressive # Maximum cleanup
```

### Smart Edit Modes

Choose between heuristic and LLM-based editing:

```bash
SMART_MODE=heuristic  # Fast, rule-based
SMART_MODE=llm        # AI-powered (default)
```

### Dictation Modes

Balance speed vs accuracy:

```bash
DICTATION_MODE=speed    # Fast, minimal processing
DICTATION_MODE=balanced # Moderate (default)
DICTATION_MODE=accurate # Maximum quality
```

---

## Troubleshooting

**Commands not recognized?**
- Speak clearly and at normal pace
- Check that SMART_EDIT=1 in .env
- Try SMART_MODE=llm for better recognition

**Cleanup too aggressive?**
- Set CLEANUP_LEVEL=basic
- Set CLEANUP_STRICTNESS=conservative

**Want more control?**
- Disable smart editing: SMART_EDIT=0
- Use manual editing after dictation

---

## See Also

- [Quick Start Guide](quick-start.md) - Get started with DictaPilot
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Platform Guides](platform-guides/) - Platform-specific setup

---

**Last Updated:** 2026-02-17
