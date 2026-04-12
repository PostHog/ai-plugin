"""Tests for the Claude Code session JSONL parser and event builder."""

import json
import os
import sys
import tempfile

import pytest

# Add plugin root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posthog_llma.parser import parse_session
from posthog_llma.event_builder import build_events
from posthog_llma.config import load_config
from posthog_llma.trace_naming import find_trace_name, clean_trace_name

DEFAULT_CONFIG = {"privacy_mode": False, "max_attribute_length": 12000, "trace_grouping": "session"}


def _write_jsonl(entries: list[dict]) -> str:
    """Write entries to a temp JSONL file and return the path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for entry in entries:
        f.write(json.dumps(entry) + "\n")
    f.close()
    return f.name


def _make_session(prompts_and_tools: list[dict] | None = None) -> list[dict]:
    """Build a minimal but realistic session JSONL."""
    if prompts_and_tools is None:
        prompts_and_tools = [
            {"prompt": "hello", "tools": []},
            {"prompt": "run ls", "tools": ["Bash"]},
        ]

    entries = []
    entries.append({
        "type": "permission-mode",
        "permissionMode": "default",
        "sessionId": "test-session-id",
    })

    msg_counter = 0
    for i, pt in enumerate(prompts_and_tools):
        prompt_id = f"prompt-{i}"
        user_uuid = f"user-uuid-{i}"

        entries.append({
            "type": "user",
            "uuid": user_uuid,
            "parentUuid": None,
            "promptId": prompt_id,
            "isMeta": False,
            "message": {"role": "user", "content": pt["prompt"]},
            "timestamp": f"2026-04-12T10:0{i}:00.000Z",
            "sessionId": "test-session-id",
            "version": "2.1.0",
            "cwd": "/Users/test/myproject",
            "gitBranch": "main",
        })

        tools = pt.get("tools", [])
        if tools:
            msg_id = f"msg-{msg_counter}"
            asst_uuid = f"asst-uuid-{msg_counter}"
            msg_counter += 1
            # First entry: no tool blocks (streaming)
            entries.append({
                "type": "assistant",
                "uuid": asst_uuid,
                "parentUuid": user_uuid,
                "message": {
                    "role": "assistant", "id": msg_id,
                    "model": "claude-opus-4-6", "stop_reason": "tool_use",
                    "usage": {"input_tokens": 10, "output_tokens": 80, "cache_read_input_tokens": 5, "cache_creation_input_tokens": 0},
                    "content": [],
                },
                "timestamp": f"2026-04-12T10:0{i}:01.000Z",
                "sessionId": "test-session-id", "version": "2.1.0", "cwd": "/Users/test/myproject",
            })
            # Second entry: has tool blocks (complete)
            entries.append({
                "type": "assistant",
                "uuid": asst_uuid,
                "parentUuid": user_uuid,
                "message": {
                    "role": "assistant", "id": msg_id,
                    "model": "claude-opus-4-6", "stop_reason": "tool_use",
                    "usage": {"input_tokens": 10, "output_tokens": 80, "cache_read_input_tokens": 5, "cache_creation_input_tokens": 0},
                    "content": [
                        {"type": "tool_use", "id": f"tool-{msg_id}", "name": tools[0], "input": {"command": "ls"}},
                    ],
                },
                "timestamp": f"2026-04-12T10:0{i}:01.000Z",
                "sessionId": "test-session-id", "version": "2.1.0", "cwd": "/Users/test/myproject",
            })
            # Tool result
            entries.append({
                "type": "user",
                "uuid": f"result-uuid-{msg_counter}",
                "parentUuid": asst_uuid,
                "isMeta": False,
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": f"tool-{msg_id}", "content": "tool output here", "is_error": False},
                    ],
                },
                "timestamp": f"2026-04-12T10:0{i}:02.000Z",
                "sessionId": "test-session-id", "version": "2.1.0", "cwd": "/Users/test/myproject",
            })
            # Follow-up response
            msg_id2 = f"msg-{msg_counter}"
            msg_counter += 1
            entries.append({
                "type": "assistant",
                "uuid": f"asst-uuid-{msg_counter}",
                "parentUuid": asst_uuid,
                "message": {
                    "role": "assistant", "id": msg_id2,
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 10, "output_tokens": 30, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "text", "text": "Done!"}],
                },
                "timestamp": f"2026-04-12T10:0{i}:03.000Z",
                "sessionId": "test-session-id", "version": "2.1.0", "cwd": "/Users/test/myproject",
            })
        else:
            msg_id = f"msg-{msg_counter}"
            msg_counter += 1
            entries.append({
                "type": "assistant",
                "uuid": f"asst-uuid-{msg_counter}",
                "parentUuid": user_uuid,
                "message": {
                    "role": "assistant", "id": msg_id,
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 10, "output_tokens": 40, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "text", "text": "Hello!"}],
                },
                "timestamp": f"2026-04-12T10:0{i}:01.000Z",
                "sessionId": "test-session-id", "version": "2.1.0", "cwd": "/Users/test/myproject",
            })

    return entries


# ---------------------------------------------------------------------------
# parse_session
# ---------------------------------------------------------------------------


class TestParseSession:
    def test_basic_parsing(self):
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert parsed["session_id"] == "test-session-id"
            assert len(parsed["prompts"]) == 2
            assert parsed["prompts"][0]["text"] == "hello"
            assert parsed["prompts"][1]["text"] == "run ls"
        finally:
            os.unlink(path)

    def test_dedup_keeps_last_entry(self):
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 2
            assert len(parsed["tool_uses"]) == 1
            assert parsed["tool_uses"][0]["name"] == "Bash"
        finally:
            os.unlink(path)

    def test_tool_result_matching(self):
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            tu = parsed["tool_uses"][0]
            assert "result" in tu
            assert tu["result"]["content"] == "tool output here"
        finally:
            os.unlink(path)

    def test_prompt_id_resolution_via_parent_chain(self):
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            for gen in parsed["generations"]:
                assert gen["prompt_id"] == "prompt-0"
        finally:
            os.unlink(path)

    def test_privacy_mode_redacts_prompts(self):
        config = {**DEFAULT_CONFIG, "privacy_mode": True}
        path = _write_jsonl(_make_session([{"prompt": "secret stuff", "tools": []}]))
        try:
            parsed = parse_session(path, config)
            assert parsed["prompts"][0]["text"] is None
        finally:
            os.unlink(path)

    def test_slash_command_without_prompt_id(self):
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "cmd-uuid", "parentUuid": None, "isMeta": False,
                "message": {"role": "user", "content": "<command-message>posthog:llma-cc-status</command-message>"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/test",
            },
            {
                "type": "assistant", "uuid": "asst-uuid", "parentUuid": "cmd-uuid",
                "message": {
                    "role": "assistant", "id": "msg-1", "model": "claude-opus-4-6",
                    "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 20, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "text", "text": "Status: ok"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/test",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["prompts"]) == 1
            assert len(parsed["generations"]) == 1
            assert parsed["generations"][0]["prompt_id"] != ""
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# build_events
# ---------------------------------------------------------------------------


class TestBuildEvents:
    def test_session_trace_grouping(self):
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            traces = [e for e in events if e["event"] == "$ai_trace"]
            gens = [e for e in events if e["event"] == "$ai_generation"]
            assert len(traces) == 1
            trace_ids = set(e["properties"]["$ai_trace_id"] for e in gens)
            assert len(trace_ids) == 1
            assert trace_ids.pop() == "test-session-id"
        finally:
            os.unlink(path)

    def test_message_trace_grouping(self):
        config = {**DEFAULT_CONFIG, "trace_grouping": "message"}
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, config)
            events = build_events(parsed, config)
            traces = [e for e in events if e["event"] == "$ai_trace"]
            assert len(traces) == 2
        finally:
            os.unlink(path)

    def test_tool_use_blocks_in_output_choices(self):
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            tool_gen = next(
                e for e in events
                if e["event"] == "$ai_generation" and e["properties"]["$ai_stop_reason"] == "tool_calls"
            )
            oc = tool_gen["properties"]["$ai_output_choices"]
            assert oc is not None
            content = oc[0]["content"]
            tool_blocks = [b for b in content if b.get("type") == "tool_use"]
            assert len(tool_blocks) == 1
            assert tool_blocks[0]["name"] == "Bash"
        finally:
            os.unlink(path)

    def test_input_messages_set(self):
        path = _write_jsonl(_make_session([{"prompt": "hello there", "tools": []}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            gen = next(e for e in events if e["event"] == "$ai_generation")
            assert gen["properties"]["$ai_input"] == [{"role": "user", "content": "hello there"}]
        finally:
            os.unlink(path)

    def test_span_has_parent_id(self):
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            span = next(e for e in events if e["event"] == "$ai_span")
            assert span["properties"]["$ai_parent_id"] is not None
            gen_span_ids = {e["properties"]["$ai_span_id"] for e in events if e["event"] == "$ai_generation"}
            assert span["properties"]["$ai_parent_id"] in gen_span_ids
        finally:
            os.unlink(path)

    def test_timestamps_are_real(self):
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                if "timestamp" in e:
                    assert e["timestamp"].startswith("2026-04-12T10:")
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# trace naming
# ---------------------------------------------------------------------------


class TestTraceNaming:
    def test_clean_strips_tags(self):
        assert clean_trace_name("<command-name>/clear</command-name>") == "/clear"

    def test_clean_collapses_whitespace(self):
        assert clean_trace_name("  hello   world  ") == "hello world"

    def test_clean_truncates(self):
        assert len(clean_trace_name("x" * 200, max_len=50)) == 50

    def test_find_skips_clear(self):
        prompts = [{"text": "/clear"}, {"text": "help me fix a bug"}]
        assert find_trace_name(prompts) == "help me fix a bug"

    def test_find_skips_exit(self):
        prompts = [{"text": "/exit"}, {"text": "real question"}]
        assert find_trace_name(prompts) == "real question"

    def test_find_skips_interrupted(self):
        prompts = [{"text": "[Request interrupted by user]"}, {"text": "actual task"}]
        assert find_trace_name(prompts) == "actual task"

    def test_find_falls_back_to_first(self):
        prompts = [{"text": "/clear"}]
        assert find_trace_name(prompts) == "/clear"

    def test_find_returns_none_for_empty(self):
        assert find_trace_name([]) is None


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------


class TestLoadConfig:
    def test_disabled_by_default(self):
        env = dict(os.environ)
        os.environ.pop("POSTHOG_LLMA_CC_ENABLED", None)
        os.environ.pop("POSTHOG_API_KEY", None)
        try:
            config = load_config()
            assert config["enabled"] is False
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_enabled_when_set(self):
        os.environ["POSTHOG_LLMA_CC_ENABLED"] = "true"
        os.environ["POSTHOG_API_KEY"] = "phc_test"
        try:
            config = load_config()
            assert config["enabled"] is True
            assert config["api_key"] == "phc_test"
        finally:
            os.environ.pop("POSTHOG_LLMA_CC_ENABLED", None)
            os.environ.pop("POSTHOG_API_KEY", None)
