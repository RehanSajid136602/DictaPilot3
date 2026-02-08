import os
import tempfile

import smart_editor
from smart_editor import (
    TranscriptState,
    _cleanup_disfluencies,
    _handle_advanced_delete,
    _handle_advanced_replace,
    _handle_formatting_commands,
    apply_heuristic,
    needs_intent_handling,
    smart_update_state,
)

os.environ.setdefault("ACTIVE_APP", "test-editor")


def test_append_normal():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(state, "Hello world.", "heuristic")

    assert prev_out == ""
    assert new_out == "Hello world."
    assert action == "append"


def test_undo_deletes_last_segment():
    state = TranscriptState()
    smart_update_state(state, "First sentence.", "heuristic")
    smart_update_state(state, "Second sentence.", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "scratch that", "heuristic")

    assert prev_out == "First sentence. Second sentence."
    assert new_out == "First sentence."
    assert action == "undo"


def test_clear_all():
    state = TranscriptState()
    smart_update_state(state, "One", "heuristic")
    smart_update_state(state, "Two", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "clear all", "heuristic")

    assert prev_out == "One. Two."
    assert new_out == ""
    assert action == "clear"


def test_ignore_utterance():
    state = TranscriptState()
    smart_update_state(state, "Keep this", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "don't include that", "heuristic")

    assert prev_out == "Keep this."
    assert new_out == "Keep this."
    assert action == "ignore"


def test_ignore_it_variant():
    state = TranscriptState()
    smart_update_state(state, "Keep this too", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "ignore it please", "heuristic")

    assert prev_out == "Keep this too."
    assert new_out == "Keep this too."
    assert action == "ignore"


def test_nevermind_variant():
    state = TranscriptState()
    smart_update_state(state, "Alpha beta", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "never mind that", "heuristic")

    assert prev_out == "Alpha beta."
    assert new_out == "Alpha beta."
    assert action == "ignore"


def test_undo_plus_append_remainder():
    state = TranscriptState()
    smart_update_state(state, "Hello world.", "heuristic")
    smart_update_state(state, "Old ending.", "heuristic")

    prev_out, new_out, action = smart_update_state(
        state,
        "oh no delete that and write: Hello again.",
        "heuristic",
    )

    assert prev_out == "Hello world. Old ending."
    assert new_out == "Hello world. Hello again."
    assert action == "undo_append"


def test_clear_everything_variant():
    state = TranscriptState()
    smart_update_state(state, "One", "heuristic")
    smart_update_state(state, "Two", "heuristic")

    prev_out, new_out, action = smart_update_state(state, "clear everything", "heuristic")

    assert prev_out == "One. Two."
    assert new_out == ""
    assert action == "clear"


def test_inline_self_correction_replaces_prior_clause():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(
        state,
        "Hello, how are you? My name is Rehan. No, no, my name is Numan, not Rehan.",
        "heuristic",
    )

    assert prev_out == ""
    assert new_out == "Hello, how are you? My name is Numan, not Rehan."
    assert action == "append"


def test_inline_no_sentence_without_overlap_is_kept():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(
        state,
        "Let's leave now. No, I disagree.",
        "heuristic",
    )

    assert prev_out == ""
    assert new_out == "Let's leave now. No, I disagree."
    assert action == "append"


def test_inline_not_use_rewrites_single_clause():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(
        state,
        "Now your task is to build a solid plan with tasks to change it into GUI using Twinker, not Twinker, PyQT6.",
        "heuristic",
    )

    assert prev_out == ""
    assert new_out == "Now your task is to build a solid plan with tasks to change it into GUI using PyQT6."
    assert action == "append"


def test_inline_not_use_rewrites_previous_clause():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(
        state,
        "Build a solid plan for convert this into GUI using Twinkler. Oh no no not Twinkler use PYQT",
        "heuristic",
    )

    assert prev_out == ""
    assert new_out == "Build a solid plan for convert this into GUI using PYQT."
    assert action == "append"


def test_filler_and_repetition_cleanup():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(state, "um um this this is is a test", "heuristic")

    assert prev_out == ""
    assert new_out == "This is a test."
    assert action == "append"


def test_question_mark_auto_punctuation():
    state = TranscriptState()
    prev_out, new_out, action = smart_update_state(state, "how are you", "heuristic")

    assert prev_out == ""
    assert new_out == "How are you?"
    assert action == "append"


def test_advanced_sentence_undo():
    """Test the advanced 'undo last sentence' command"""
    state = TranscriptState()
    state.output_text = "First sentence. Second sentence. Third sentence."
    state.segments = [state.output_text]

    # Test the specific function
    result_text, action = _handle_advanced_delete(state, "undo last sentence")

    assert "Third sentence" not in result_text
    assert "First sentence. Second sentence." in result_text
    assert action == "undo"


def test_advanced_paragraph_undo():
    """Test the advanced 'undo last paragraph' command"""
    state = TranscriptState()
    state.output_text = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
    state.segments = [state.output_text]

    result_text, action = _handle_advanced_delete(state, "remove last paragraph")

    assert "Third paragraph" not in result_text
    assert "First paragraph." in result_text
    assert action == "undo"


def test_formatting_capitalize():
    """Test the 'capitalize that' formatting command"""
    state = TranscriptState()
    state.output_text = "hello world"
    state.segments = ["hello world"]

    result_text, action = _handle_formatting_commands(state, "capitalize that")

    assert result_text == "Hello world"
    assert action == "append"


def test_formatting_heading():
    """Test the 'make it a heading' formatting command"""
    state = TranscriptState()
    state.output_text = "section title"
    state.segments = ["section title"]

    result_text, action = _handle_formatting_commands(state, "make it a heading")

    assert result_text == "# section title"
    assert action == "append"


def test_advanced_replace_insert_after():
    """Test the 'insert X after Y' command"""
    state = TranscriptState()
    state.output_text = "I want to go to the store"
    state.segments = [state.output_text]

    result_text, action = _handle_advanced_replace(state, "insert quickly after go")

    # Should result in "I want to go quickly to the store"
    assert "go quickly" in result_text
    assert action == "append"


def test_needs_intent_handling_avoids_false_positive_content():
    assert not needs_intent_handling("I need a clear explanation of the approach")


def test_cleanup_disfluencies_confidence_aware():
    high_conf = _cleanup_disfluencies(
        "this is like basically actually fine",
        transcription_confidence=0.95,
        cleanup_level="aggressive",
    )
    low_conf = _cleanup_disfluencies(
        "this is like basically actually fine",
        transcription_confidence=0.1,
        cleanup_level="aggressive",
    )

    assert high_conf == "this is fine"
    assert low_conf == "this is like basically actually fine"


def test_adaptive_learning_from_replace_command():
    with tempfile.TemporaryDirectory() as tmp_dir:
        adaptive_path = f"{tmp_dir}/adaptive_dictionary.json"

        prev_path = smart_editor.ADAPTIVE_DICTIONARY_PATH
        prev_enabled = smart_editor.USER_ADAPTATION_ENABLED
        prev_min_count = smart_editor.ADAPTIVE_MIN_COUNT
        prev_cache = dict(smart_editor._ADAPTIVE_CACHE)
        try:
            smart_editor.ADAPTIVE_DICTIONARY_PATH = adaptive_path
            smart_editor.USER_ADAPTATION_ENABLED = True
            smart_editor.ADAPTIVE_MIN_COUNT = 1
            smart_editor._ADAPTIVE_CACHE.update({"path": None, "mtime": None, "data": {}})

            state = TranscriptState()
            state.output_text = "we use twinker"
            state.segments = [state.output_text]
            _, action = apply_heuristic(
                state,
                "replace twinker with PyQt",
                app_id="editor-test-app",
            )
            assert action == "undo_append"

            learned_state = TranscriptState()
            updated, learned_action = apply_heuristic(
                learned_state,
                "twinker works well",
                app_id="editor-test-app",
            )
            assert learned_action == "append"
            assert "PyQt works well." == updated
        finally:
            smart_editor.ADAPTIVE_DICTIONARY_PATH = prev_path
            smart_editor.USER_ADAPTATION_ENABLED = prev_enabled
            smart_editor.ADAPTIVE_MIN_COUNT = prev_min_count
            smart_editor._ADAPTIVE_CACHE.clear()
            smart_editor._ADAPTIVE_CACHE.update(prev_cache)
