"""Tests for the Claude Code session JSONL parser and event builder."""

import json
import os
import sys
import tempfile

import pytest

# Add plugin root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posthog_llma.parser import parse_session, find_session_log
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


def _make_session(prompts_and_tools=None) -> list[dict]:
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
# find_session_log
# ---------------------------------------------------------------------------


class TestFindSessionLog:
    """Regression coverage for #48 and follow-ups (Windows backslash/colon,
    underscores, spaces). Claude Code's project dir name collapses many
    characters; we use a glob fallback rather than mirror its rules."""

    def _stub_projects_dir(self, monkeypatch, tmp_path):
        projects = tmp_path / ".claude" / "projects"
        projects.mkdir(parents=True)
        monkeypatch.setattr("posthog_llma.parser.Path.home", lambda: tmp_path)
        return projects

    def test_direct_lookup_still_works(self, monkeypatch, tmp_path):
        projects = self._stub_projects_dir(monkeypatch, tmp_path)
        (projects / "-Users-test-myproject").mkdir()
        sid = "11111111-1111-1111-1111-111111111111"
        log = projects / "-Users-test-myproject" / f"{sid}.jsonl"
        log.write_text("{}")
        assert find_session_log(sid, "/Users/test/myproject") == str(log)

    def test_glob_fallback_handles_dots(self, monkeypatch, tmp_path):
        projects = self._stub_projects_dir(monkeypatch, tmp_path)
        # cwd contains a dot; Claude Code stores under dot-collapsed name
        (projects / "-Users-me-dev--claude-worktrees-feature").mkdir()
        sid = "22222222-2222-2222-2222-222222222222"
        log = projects / "-Users-me-dev--claude-worktrees-feature" / f"{sid}.jsonl"
        log.write_text("{}")
        assert find_session_log(sid, "/Users/me/dev/.claude/worktrees/feature") == str(log)

    def test_glob_fallback_handles_windows_path(self, monkeypatch, tmp_path):
        projects = self._stub_projects_dir(monkeypatch, tmp_path)
        (projects / "c--Users-me-PYProjs-my-project").mkdir()
        sid = "33333333-3333-3333-3333-333333333333"
        log = projects / "c--Users-me-PYProjs-my-project" / f"{sid}.jsonl"
        log.write_text("{}")
        assert find_session_log(sid, r"c:\Users\me\PYProjs\my-project") == str(log)

    def test_glob_fallback_handles_underscores_and_spaces(self, monkeypatch, tmp_path):
        projects = self._stub_projects_dir(monkeypatch, tmp_path)
        (projects / "-Users-me-00-Projects-Project-Name").mkdir()
        sid = "44444444-4444-4444-4444-444444444444"
        log = projects / "-Users-me-00-Projects-Project-Name" / f"{sid}.jsonl"
        log.write_text("{}")
        assert find_session_log(sid, "/Users/me/00_Projects/Project Name") == str(log)

    def test_returns_none_when_not_found(self, monkeypatch, tmp_path):
        self._stub_projects_dir(monkeypatch, tmp_path)
        assert find_session_log("nonexistent-uuid", "/some/path") is None


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

    def test_custom_properties_on_all_events(self):
        config = {**DEFAULT_CONFIG, "custom_properties": {"ai_product": "test-app"}}
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, config)
            events = build_events(parsed, config)
            for e in events:
                assert e["properties"].get("ai_product") == "test-app", \
                    f"{e['event']} missing custom property"
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

    def test_insert_id_set_on_all_events(self):
        """Regression coverage for #85: deterministic $insert_id lets
        PostHog dedupe re-sends of the same session."""
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert e["properties"].get("$insert_id"), \
                    f"{e['event']} missing $insert_id"

            # Insert IDs must be unique within a single send
            ids = [e["properties"]["$insert_id"] for e in events]
            assert len(ids) == len(set(ids))
        finally:
            os.unlink(path)

    def test_insert_id_stable_across_reparses(self):
        """Same JSONL parsed twice yields identical $insert_ids, so PostHog
        dedupes — even though span_ids are regenerated each parse."""
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            events_a = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)
            events_b = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)

            ids_a = sorted(e["properties"]["$insert_id"] for e in events_a)
            ids_b = sorted(e["properties"]["$insert_id"] for e in events_b)
            assert ids_a == ids_b
        finally:
            os.unlink(path)

    def test_insert_id_stable_in_message_mode(self):
        config = {**DEFAULT_CONFIG, "trace_grouping": "message"}
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            events_a = build_events(parse_session(path, config), config)
            events_b = build_events(parse_session(path, config), config)

            ids_a = sorted(e["properties"]["$insert_id"] for e in events_a)
            ids_b = sorted(e["properties"]["$insert_id"] for e in events_b)
            assert ids_a == ids_b
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
    def _clean_env(self):
        """Remove all POSTHOG_ env vars."""
        for k in list(os.environ):
            if k.startswith("POSTHOG_"):
                del os.environ[k]

    def test_disabled_by_default(self):
        env = dict(os.environ)
        self._clean_env()
        try:
            config = load_config()
            assert config["enabled"] is False
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_enabled_when_set(self):
        env = dict(os.environ)
        self._clean_env()
        os.environ["POSTHOG_LLMA_CC_ENABLED"] = "true"
        os.environ["POSTHOG_API_KEY"] = "phc_test"
        try:
            config = load_config()
            assert config["enabled"] is True
            assert config["api_key"] == "phc_test"
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_custom_properties_parsed(self):
        env = dict(os.environ)
        self._clean_env()
        os.environ["POSTHOG_LLMA_CUSTOM_PROPERTIES"] = '{"ai_product": "my-app", "team": "platform"}'
        try:
            config = load_config()
            assert config["custom_properties"] == {"ai_product": "my-app", "team": "platform"}
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_custom_properties_invalid_json_ignored(self):
        env = dict(os.environ)
        self._clean_env()
        os.environ["POSTHOG_LLMA_CUSTOM_PROPERTIES"] = "not json"
        try:
            config = load_config()
            assert config["custom_properties"] == {}
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_custom_properties_empty_by_default(self):
        env = dict(os.environ)
        self._clean_env()
        try:
            config = load_config()
            assert config["custom_properties"] == {}
        finally:
            os.environ.clear()
            os.environ.update(env)
