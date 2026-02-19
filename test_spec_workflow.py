"""
Test script for spec-driven workflow
"""

from spec_generator import SpecGenerator, SpecTemplate
from intent_classifier import IntentClassifier
from spec_store import SpecStore
from workflow_engine import WorkflowEngine

print("=== DictaPilot Spec Mode Integration Test ===\n")

# Test 1: Complete workflow
print("Test 1: Complete Voice-to-Spec Workflow")
print("-" * 50)

engine = WorkflowEngine()

# Simulate voice input for creating a spec
voice_input_1 = "Start new spec: Add dark mode to settings dashboard"
result = engine.process_voice_input(voice_input_1)
print(f"✓ Input: {voice_input_1}")
print(f"  Action: {result['action']}")
print(f"  State: {result.get('state', 'N/A')}")

# Add more details
voice_input_2 = "Context: Users need dark mode for late-night coding. Acceptance criteria: Toggle in settings, persists across sessions, applies to all views. Constraint: Must support system theme detection."
result = engine.process_voice_input(voice_input_2)
print(f"\n✓ Input: {voice_input_2[:60]}...")
print(f"  Action: {result['action']}")

# Save the spec
result = engine.save_current_spec()
print(f"\n✓ Save spec")
print(f"  Success: {result['success']}")
if result['success']:
    print(f"  Spec ID: {result['spec_id']}")

# Export the spec
result = engine.export_current_spec("standard")
print(f"\n✓ Export spec")
print(f"  Format: standard")
print(f"  Content preview:\n")
print(result['content'][:300] + "...")

print("\n" + "=" * 50)
print("Test 2: Intent Classification")
print("-" * 50)

classifier = IntentClassifier()

test_inputs = [
    "Start new spec: User authentication",
    "Write a function to validate email addresses",
    "Document the API endpoints in the README",
    "Send to Cursor",
    "The goal is to implement JWT authentication"
]

for text in test_inputs:
    result = classifier.classify(text)
    print(f"Input: {text[:50]}")
    print(f"  Intent: {result.intent.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Indicators: {', '.join(result.indicators[:3])}")
    print()

print("=" * 50)
print("Test 3: Spec Templates")
print("-" * 50)

templates = ['feature', 'bugfix', 'refactor', 'minimal']
gen = SpecGenerator()

for template in templates:
    spec = gen.start_new_spec(f"Test {template.title()}", template)
    md = spec.to_markdown()
    print(f"✓ {template.title()} template ({len(md)} chars)")

print("\n" + "=" * 50)
print("Test 4: Export Formats")
print("-" * 50)

gen = SpecGenerator()
spec = gen.start_new_spec("Multi-format Test", "feature")
gen.parse_voice_input("Goal: Test all export formats. Context: Verify compatibility.")

formats = ['standard', 'openspec', 'luna', 'github']
for fmt in formats:
    md = spec.to_markdown(fmt)
    print(f"✓ {fmt.title()} format ({len(md)} chars)")
    print(f"  Preview: {md[:80]}...")
    print()

print("=" * 50)
print("Test 5: Spec Storage")
print("-" * 50)

store = SpecStore()
info = store.get_storage_info()

print(f"Storage location: {info['storage_path']}")
print(f"Total specs: {info['total_specs']}")
print(f"Total size: {info['total_size_mb']} MB")

# List specs
specs = store.list_specs()
if specs:
    print(f"\nRecent specs:")
    for spec_entry in specs[:5]:
        print(f"  - {spec_entry['title']} ({spec_entry['id']})")
else:
    print("\nNo specs stored yet")

print("\n" + "=" * 50)
print("✓ All integration tests completed successfully!")
print("=" * 50)
