#!/usr/bin/env python3
"""Lightweight smart-editor evaluation runner."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.environ.setdefault("ACTIVE_APP", "eval")
os.environ.setdefault("USER_ADAPTATION", "0")
os.environ.setdefault("ADAPTIVE_DICTIONARY_PATH", str(REPO_ROOT / ".eval_adaptive_dictionary.json"))

from smart_editor import TranscriptState, smart_update_state


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{lineno}: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Row at {path}:{lineno} must be an object")
            rows.append(row)
    return rows


def run_eval(corpus_path: Path) -> int:
    corpus = _load_jsonl(corpus_path)
    if not corpus:
        print("No corpus entries found.")
        return 1

    states: dict[str, TranscriptState] = {}
    failures = 0
    action_checks = 0
    action_passes = 0
    output_checks = 0
    output_passes = 0

    filler_tokens = {"uh", "um", "erm", "ah", "hmm", "you", "know", "i", "mean"}
    filler_token_count = 0
    output_token_count = 0

    for idx, case in enumerate(corpus, start=1):
        session = str(case.get("session", "default"))
        utterance = str(case.get("utterance", ""))
        expected_action = case.get("expected_action")
        expected_output = case.get("expected_output")
        expected_contains = case.get("expected_contains")

        state = states.setdefault(session, TranscriptState())
        _, new_output, action = smart_update_state(state, utterance, mode="heuristic", allow_llm=False)

        if expected_action is not None:
            action_checks += 1
            if action == expected_action:
                action_passes += 1
            else:
                failures += 1
                print(f"[FAIL #{idx}] action expected={expected_action} got={action} utterance={utterance!r}")

        if expected_output is not None:
            output_checks += 1
            if new_output == expected_output:
                output_passes += 1
            else:
                failures += 1
                print(f"[FAIL #{idx}] output mismatch")
                print(f"  utterance: {utterance!r}")
                print(f"  expected:  {expected_output!r}")
                print(f"  got:       {new_output!r}")
        elif expected_contains is not None:
            output_checks += 1
            if str(expected_contains) in new_output:
                output_passes += 1
            else:
                failures += 1
                print(f"[FAIL #{idx}] output missing substring {expected_contains!r}: {new_output!r}")

        tokens = [t.strip(".,!?;:").lower() for t in new_output.split()]
        output_token_count += len(tokens)
        filler_token_count += sum(1 for token in tokens if token in filler_tokens)

    action_rate = (action_passes / action_checks * 100.0) if action_checks else 100.0
    output_rate = (output_passes / output_checks * 100.0) if output_checks else 100.0
    filler_rate = (filler_token_count / output_token_count * 100.0) if output_token_count else 0.0

    print("\nSmart Editor Eval")
    print(f"- Cases: {len(corpus)}")
    print(f"- Action accuracy: {action_passes}/{action_checks} ({action_rate:.1f}%)")
    print(f"- Output checks: {output_passes}/{output_checks} ({output_rate:.1f}%)")
    print(f"- Filler leakage: {filler_token_count}/{output_token_count} tokens ({filler_rate:.2f}%)")
    print(f"- Status: {'PASS' if failures == 0 else 'FAIL'}")
    return 0 if failures == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run smart-editor quality evaluation.")
    parser.add_argument(
        "--corpus",
        default="tests/fixtures/smart_editor_corpus.jsonl",
        help="Path to corpus JSONL file.",
    )
    args = parser.parse_args()
    return run_eval(Path(args.corpus))


if __name__ == "__main__":
    sys.exit(main())
