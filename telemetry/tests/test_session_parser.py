"""Tests for the Claude Code session JSONL parser and event builder."""

import http.server
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error

import pytest

# Add plugin root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posthog_llma.parser import parse_session, parse_session_with_subagents, find_session_log
from posthog_llma.event_builder import build_events, parse_git_remote_url
import posthog_llma.sender as sender_mod
import posthog_llma.sent_events as sent_events_mod
from posthog_llma.sender import chunk_events
from posthog_llma.sent_events import send_new_events
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

    def test_thinking_preserved_when_split_across_chunks(self):
        """Regression coverage for #55 Defect 2: streaming entries can
        split content blocks across chunks (e.g. thinking on chunk 1,
        tool_use on chunk 2). The merge must preserve both."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "think then act"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            # Chunk 1: thinking only
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "thinking", "thinking": "deep thoughts"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            # Chunk 2: tool_use only, complete usage
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "tool_use",
                    "usage": {"input_tokens": 10, "output_tokens": 20, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "tool_use", "id": "t-1", "name": "Bash", "input": {"cmd": "ls"}}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 1
            gen = parsed["generations"][0]

            # Both the thinking text and the tool_use survived
            assert gen["output_blocks"] == [{"type": "thinking", "thinking": "deep thoughts"}]
            assert len(gen["tool_use_blocks"]) == 1
            assert gen["tool_use_blocks"][0]["name"] == "Bash"

            # Latest non-empty metadata wins
            assert gen["stop_reason"] == "tool_use"
            assert gen["input_tokens"] == 10
            assert gen["output_tokens"] == 20

            # Tool use is registered for span emission
            assert len(parsed["tool_uses"]) == 1
            assert parsed["tool_uses"][0]["name"] == "Bash"

            # Downstream events include thinking in output_choices, typed as a
            # thinking block rather than flattened into assistant text.
            events = build_events(parsed, DEFAULT_CONFIG)
            gen_ev = next(e for e in events if e["event"] == "$ai_generation")
            content_blocks = gen_ev["properties"]["$ai_output_choices"][0]["content"]
            thinking_blocks = [b for b in content_blocks if b.get("type") == "thinking"]
            assert thinking_blocks and thinking_blocks[0]["thinking"] == "deep thoughts"
            assert not [b for b in content_blocks if b.get("type") == "text"]
        finally:
            os.unlink(path)

    def test_session_id_extracted_from_agent_sdk_jsonl(self):
        """Regression coverage for #55 Defect 1: Claude Agent SDK JSONLs
        don't emit a permission-mode entry, but every entry carries
        sessionId. The parser should still pick it up."""
        # No permission-mode entry, no system/turn_duration entry.
        entries = [
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "hi"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "sdk-session-abc",
                "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "text", "text": "hello"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "sdk-session-abc",
                "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert parsed["session_id"] == "sdk-session-abc"

            # Downstream events must have a non-empty trace_id / session_id
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert e["properties"]["$ai_session_id"] == "sdk-session-abc"
                assert e["properties"]["$ai_trace_id"]
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

    def test_session_id_prefers_permission_mode_when_present(self):
        """When both permission-mode and other entries carry sessionId,
        permission-mode wins (it's the canonical source). Guards against
        accidentally picking up a sessionId from a malformed entry first."""
        entries = [
            # Pre-permission-mode user entry with a different sessionId
            # (shouldn't happen in practice, but pin the precedence rule)
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "isMeta": True,
                "message": {"role": "user", "content": ""},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "early-stray-id",
                "version": "2.1.0", "cwd": "/tmp",
            },
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "canonical-id"},
            {
                "type": "user", "uuid": "u-2", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "hi"},
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "canonical-id",
                "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-2",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                    "content": [{"type": "text", "text": "hello"}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "canonical-id",
                "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert parsed["session_id"] == "canonical-id"
        finally:
            os.unlink(path)

    def test_missing_session_id_returns_empty_without_crashing(self):
        """A JSONL with no sessionId anywhere parses cleanly and leaves
        session_id as empty string (rather than crashing)."""
        entries = [
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "hi"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                    "content": [{"type": "text", "text": "hello"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert parsed["session_id"] == ""
            assert len(parsed["generations"]) == 1
        finally:
            os.unlink(path)

    def test_merge_preserves_first_seen_block_order(self):
        """Regression coverage for codex review on PR #86:
        _finalize_generation must not impose a fixed thinking → text →
        tool_use order. If a chunk arrives text-first, output should
        reflect that order rather than reshuffling by type."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "go"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            # Chunk 1: text first
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "text", "text": "preface"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            # Chunk 2: thinking arrives after text
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                    "content": [{"type": "thinking", "thinking": "afterthought"}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 1
            # Text came first in the source, so it must lead rather than
            # thinking being reshuffled ahead of it, and each block keeps its type.
            blocks = parsed["generations"][0]["output_blocks"]
            assert blocks == [
                {"type": "text", "text": "preface"},
                {"type": "thinking", "thinking": "afterthought"},
            ]
        finally:
            os.unlink(path)

    def test_thinking_and_text_stay_separate_blocks(self):
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "go"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                    "content": [
                        {"type": "thinking", "thinking": "weighing the options"},
                        {"type": "text", "text": "Here is the answer."},
                    ],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            gen_ev = next(e for e in events if e["event"] == "$ai_generation")
            content = gen_ev["properties"]["$ai_output_choices"][0]["content"]

            thinking = [b for b in content if b.get("type") == "thinking"]
            text = [b for b in content if b.get("type") == "text"]
            assert len(thinking) == 1 and thinking[0]["thinking"] == "weighing the options"
            assert len(text) == 1 and text[0]["text"] == "Here is the answer."
        finally:
            os.unlink(path)

    @staticmethod
    def _usage_session(*usages):
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "go"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        for i, usage in enumerate(usages):
            entries.append({
                "type": "assistant", "uuid": f"a-{i}", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": usage,
                    "content": [{"type": "text", "text": f"chunk {i}"}],
                },
                "timestamp": f"2026-04-12T10:00:0{i + 1}.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            })
        return entries

    def _parse_generation(self, *usages):
        path = _write_jsonl(self._usage_session(*usages))
        try:
            return parse_session(path, DEFAULT_CONFIG)
        finally:
            os.unlink(path)

    def test_cache_creation_ttl_split_reaches_generation_event(self):
        parsed = self._parse_generation({
            "input_tokens": 2, "output_tokens": 9,
            "cache_creation_input_tokens": 300,
            "cache_creation": {"ephemeral_5m_input_tokens": 100, "ephemeral_1h_input_tokens": 200},
        })
        gen_ev = next(e for e in build_events(parsed, DEFAULT_CONFIG) if e["event"] == "$ai_generation")
        props = gen_ev["properties"]
        assert (
            props["$ai_cache_creation_input_tokens"],
            props["$ai_cache_creation_5m_input_tokens"],
            props["$ai_cache_creation_1h_input_tokens"],
        ) == (300, 100, 200)

    def test_cache_creation_ttl_split_absent_without_breakdown(self):
        parsed = self._parse_generation({
            "input_tokens": 2, "output_tokens": 9, "cache_creation_input_tokens": 300,
        })
        gen_ev = next(e for e in build_events(parsed, DEFAULT_CONFIG) if e["event"] == "$ai_generation")
        assert "$ai_cache_creation_1h_input_tokens" not in gen_ev["properties"]

    def test_cache_creation_ttl_split_taken_from_latest_chunk_not_summed(self):
        parsed = self._parse_generation(
            {"cache_creation_input_tokens": 300,
             "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 300}},
            {"cache_creation_input_tokens": 300,
             "cache_creation": {"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 300}},
        )
        gen = parsed["generations"][0]
        assert (gen["cache_creation_5m_tokens"], gen["cache_creation_1h_tokens"]) == (0, 300)

    def test_three_chunk_merge_preserves_all_block_types(self):
        """Thinking, text, and tool_use arriving in three separate chunks
        all survive the merge."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "do stuff"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "thinking", "thinking": "ponder"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "text", "text": "here goes"}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "tool_use",
                    "usage": {"input_tokens": 10, "output_tokens": 20},
                    "content": [{"type": "tool_use", "id": "t-1", "name": "Bash", "input": {}}],
                },
                "timestamp": "2026-04-12T10:00:03.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 1
            gen = parsed["generations"][0]
            assert gen["output_blocks"] == [
                {"type": "thinking", "thinking": "ponder"},
                {"type": "text", "text": "here goes"},
            ]
            assert len(gen["tool_use_blocks"]) == 1
            assert gen["stop_reason"] == "tool_use"
            assert gen["input_tokens"] == 10
        finally:
            os.unlink(path)

    def test_cumulative_text_streaming_keeps_only_latest(self):
        """When the same content type arrives in two chunks (cumulative
        streaming — chunk 2 carries a longer/extended version of chunk 1),
        the later chunk replaces the earlier and no duplicate appears."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "tell me"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "text", "text": "Hello"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 15},
                    "content": [{"type": "text", "text": "Hello, world."}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 1
            assert parsed["generations"][0]["output_blocks"] == [{"type": "text", "text": "Hello, world."}]
        finally:
            os.unlink(path)

    def test_delta_tool_use_across_chunks_known_limitation(self):
        """Pin current behaviour: if tool_use blocks arrive split delta-style
        ([A] then [B] for the same msg_id), the later chunk replaces the
        earlier one rather than unioning. Claude Code's wire format is
        cumulative for tool_use, so this case shouldn't arise in practice
        — but if that ever changes, this test will surface it."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "do two things"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": None,
                    "usage": {},
                    "content": [{"type": "tool_use", "id": "t-A", "name": "Bash", "input": {}}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "tool_use",
                    "usage": {"input_tokens": 5, "output_tokens": 15},
                    "content": [{"type": "tool_use", "id": "t-B", "name": "Read", "input": {}}],
                },
                "timestamp": "2026-04-12T10:00:02.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            assert len(parsed["generations"]) == 1
            tool_names = [tu["name"] for tu in parsed["tool_uses"]]
            # Current behaviour: only the last chunk's tool_use survives.
            # If this changes (e.g. we move to id-keyed union), revisit
            # event_builder.py's $insert_id derivation for tool spans.
            assert tool_names == ["Read"]
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

    def test_git_metadata_on_all_event_types(self, monkeypatch):
        # Derive a stable repo so we can assert it without touching real git.
        monkeypatch.setattr(
            "posthog_llma.event_builder._git_repo_for_cwd",
            lambda cwd: "PostHog/ai-plugin",
        )
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            # Generation, span, and trace must all be present and carry git context.
            kinds = {e["event"] for e in events}
            assert {"$ai_generation", "$ai_span", "$ai_trace"} <= kinds
            for e in events:
                assert e["properties"]["$ai_git_branch"] == "main"
                assert e["properties"]["$ai_git_repo"] == "PostHog/ai-plugin"
        finally:
            os.unlink(path)

    def test_git_branch_omitted_when_absent(self, monkeypatch):
        monkeypatch.setattr(
            "posthog_llma.event_builder._git_repo_for_cwd",
            lambda cwd: None,
        )
        # Session with no gitBranch and no derivable repo.
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "hi"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    "role": "assistant", "id": "msg-1",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0},
                    "content": [{"type": "text", "text": "hello"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert "$ai_git_branch" not in e["properties"]
                assert "$ai_git_repo" not in e["properties"]
        finally:
            os.unlink(path)

    def test_purpose_emitted_when_env_set(self, monkeypatch):
        # Trimmed and lowercased, passed through without enum enforcement.
        monkeypatch.setenv("POSTHOG_AI_PURPOSE", "  Review  ")
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert e["properties"]["$ai_purpose"] == "review"
        finally:
            os.unlink(path)

    def test_purpose_absent_when_env_unset(self, monkeypatch):
        monkeypatch.delenv("POSTHOG_AI_PURPOSE", raising=False)
        path = _write_jsonl(_make_session())
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert "$ai_purpose" not in e["properties"]
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
        """Regression coverage for #85: deterministic dedup key lets
        PostHog dedupe re-sends of the same session.

        PostHog's /batch endpoint dedupes on the event-level `uuid`
        field via ClickHouse's ReplacingMergeTree. $insert_id in
        properties is kept as a visible mirror so the dedup key is
        easy to spot in the UI."""
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            parsed = parse_session(path, DEFAULT_CONFIG)
            events = build_events(parsed, DEFAULT_CONFIG)
            for e in events:
                assert e["properties"].get("$insert_id"), \
                    f"{e['event']} missing $insert_id"
                assert e.get("uuid"), f"{e['event']} missing top-level uuid"
                # Both must match — uuid is what PostHog actually dedupes on
                assert e["uuid"] == e["properties"]["$insert_id"]

            # Dedup keys must be unique within a single send
            uuids = [e["uuid"] for e in events]
            assert len(uuids) == len(set(uuids))
        finally:
            os.unlink(path)

    def test_insert_id_stable_across_reparses(self):
        """Same JSONL parsed twice yields identical events, span IDs
        included, so PostHog dedupes them and the sender can skip the
        ones it already sent."""
        path = _write_jsonl(_make_session([{"prompt": "run ls", "tools": ["Bash"]}]))
        try:
            events_a = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)
            events_b = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)

            ids_a = sorted(e["properties"]["$insert_id"] for e in events_a)
            ids_b = sorted(e["properties"]["$insert_id"] for e in events_b)
            assert ids_a == ids_b
            assert events_a == events_b
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
            assert events_a == events_b
        finally:
            os.unlink(path)

    def test_insert_id_differs_across_sessions(self):
        """Guards against over-deduping: two different sessions with
        identical msg_ids (rare but possible — Anthropic msg_ids aren't
        guaranteed globally unique) must produce different $insert_ids."""
        entries_a = _make_session([{"prompt": "x", "tools": []}])
        entries_b = []
        for entry in _make_session([{"prompt": "x", "tools": []}]):
            new = dict(entry)
            if "sessionId" in new:
                new["sessionId"] = "different-session-id"
            if new.get("type") == "permission-mode":
                new["sessionId"] = "different-session-id"
            entries_b.append(new)

        path_a = _write_jsonl(entries_a)
        path_b = _write_jsonl(entries_b)
        try:
            events_a = build_events(parse_session(path_a, DEFAULT_CONFIG), DEFAULT_CONFIG)
            events_b = build_events(parse_session(path_b, DEFAULT_CONFIG), DEFAULT_CONFIG)
            ids_a = {e["properties"]["$insert_id"] for e in events_a}
            ids_b = {e["properties"]["$insert_id"] for e in events_b}
            assert ids_a.isdisjoint(ids_b), \
                "Different sessions must not share $insert_id"
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_insert_id_falls_back_to_span_id_when_msg_id_missing(self):
        """Pin current limitation: if the assistant message has no `id`
        field, the $insert_id derivation falls back to the parser's
        span_id (which is a fresh uuid4 per parse). PostHog cannot dedupe
        re-sends in that case. If this becomes a real problem we'd need
        a different stable identifier (entry uuid + timestamp, say)."""
        entries = [
            {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
            {
                "type": "user", "uuid": "u-1", "parentUuid": None,
                "promptId": "p-1", "isMeta": False,
                "message": {"role": "user", "content": "hi"},
                "timestamp": "2026-04-12T10:00:00.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
            {
                "type": "assistant", "uuid": "a-1", "parentUuid": "u-1",
                "message": {
                    # No "id" field on the assistant message
                    "role": "assistant",
                    "model": "claude-opus-4-6", "stop_reason": "end_turn",
                    "usage": {"input_tokens": 5, "output_tokens": 10},
                    "content": [{"type": "text", "text": "hello"}],
                },
                "timestamp": "2026-04-12T10:00:01.000Z",
                "sessionId": "s1", "version": "2.1.0", "cwd": "/tmp",
            },
        ]
        path = _write_jsonl(entries)
        try:
            events_a = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)
            events_b = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)
            gen_a = next(e for e in events_a if e["event"] == "$ai_generation")
            gen_b = next(e for e in events_b if e["event"] == "$ai_generation")
            # Known limitation: insert_id is NOT stable when msg_id is missing.
            # If we ever change the fallback to use entry_uuid, flip this
            # assertion to assertEqual.
            assert gen_a["properties"]["$insert_id"] != gen_b["properties"]["$insert_id"]
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# send_new_events
# ---------------------------------------------------------------------------


class _FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *a): return False


class _FakePostHog:
    def __init__(self):
        self.batches = []
        self.bodies = []
        self.fail = False
        # 1-based numbers of the POST calls that fail.
        self.fail_on = set()
        self.calls = 0

    def urlopen(self, req, timeout=None):
        self.calls += 1
        if self.fail or self.calls in self.fail_on:
            raise urllib.error.HTTPError(req.full_url, 503, "unavailable", {}, None)
        self.bodies.append(req.data)
        self.batches.append(json.loads(req.data.decode("utf-8"))["batch"])
        return _FakeResponse()

    def end_session(self, entries):
        path = _write_jsonl(entries)
        try:
            events = build_events(parse_session(path, DEFAULT_CONFIG), DEFAULT_CONFIG)
        finally:
            os.unlink(path)
        return send_new_events(events, session_id="test-session-id", api_key="phc_test", distinct_id="user")


@pytest.fixture
def posthog(monkeypatch, tmp_path):
    fake = _FakePostHog()
    monkeypatch.setattr(sent_events_mod, "SENT_DIR", str(tmp_path))
    monkeypatch.setattr("urllib.request.urlopen", fake.urlopen)
    return fake


class TestSendNewEvents:
    def test_session_end_sends_only_new_and_changed_events(self, posthog):
        first = _make_session([{"prompt": "run ls", "tools": ["Bash"]}])
        resumed = _make_session([{"prompt": "run ls", "tools": ["Bash"]}, {"prompt": "hello", "tools": []}])

        posthog.end_session(first)
        assert posthog.end_session(first)["sent"] == 0
        posthog.end_session(resumed)

        first_batch, resumed_batch = posthog.batches
        assert sorted(e["event"] for e in first_batch) == ["$ai_generation", "$ai_generation", "$ai_span", "$ai_trace"]
        assert sorted(e["event"] for e in resumed_batch) == ["$ai_generation", "$ai_trace"]
        first_uuids = {e["uuid"]: e["event"] for e in first_batch}
        assert [first_uuids.get(e["uuid"]) for e in resumed_batch if e["event"] == "$ai_trace"] == ["$ai_trace"]
        assert all(e["uuid"] not in first_uuids for e in resumed_batch if e["event"] == "$ai_generation")

    def test_span_sent_again_with_its_result_keeps_its_parent(self, posthog):
        full = _make_session([{"prompt": "run ls", "tools": ["Bash"]}])
        # The session ends before the tool result and the reply after it.
        before_result = full[:-2]

        posthog.end_session(before_result)
        posthog.end_session(full)

        first_batch, second_batch = posthog.batches
        generation = next(e for e in first_batch if e["event"] == "$ai_generation")
        span = next(e for e in second_batch if e["event"] == "$ai_span")
        assert span["properties"]["$ai_output_state"] == "tool output here"
        assert span["properties"]["$ai_parent_id"] == generation["properties"]["$ai_span_id"]
        assert generation["uuid"] not in {e["uuid"] for e in second_batch}

    def test_failed_send_is_sent_again_at_the_next_session_end(self, posthog):
        session = _make_session([{"prompt": "hello", "tools": []}])

        posthog.fail = True
        assert posthog.end_session(session)["status"] == "error"
        posthog.fail = False
        posthog.end_session(session)

        assert sorted(e["event"] for e in posthog.batches[0]) == ["$ai_generation", "$ai_trace"]

    def test_records_of_expired_sessions_are_removed(self, posthog, tmp_path):
        expired = tmp_path / "expired-session.json"
        expired.write_text("{}")
        old = time.time() - sent_events_mod.RETENTION_SECONDS - 60
        os.utime(expired, (old, old))

        posthog.end_session(_make_session([{"prompt": "hello", "tools": []}]))

        assert not expired.exists()
        assert (tmp_path / "test-session-id.json").exists()


class TestChunkedSend:
    def _events(self, count, config=DEFAULT_CONFIG):
        session = _make_session([{"prompt": f"prompt {i}", "tools": ["Bash"]} for i in range(count)])
        path = _write_jsonl(session)
        try:
            return build_events(parse_session(path, config), config)
        finally:
            os.unlink(path)

    def _send(self, events, **kwargs):
        return send_new_events(events, session_id="test-session-id", api_key="phc_test", distinct_id="user", **kwargs)

    def test_chunk_events_splits_in_order_within_limit(self):
        events = self._events(12)
        max_bytes = 3000
        chunks = chunk_events(events, distinct_id="user", max_bytes=max_bytes)

        assert len(chunks) > 1
        assert [e["uuid"] for c in chunks for e in c] == [e["uuid"] for e in events]
        for chunk in chunks:
            entries = [sender_mod._batch_entry(e, "user", "2026-01-01T00:00:00+00:00") for e in chunk]
            body = json.dumps({"api_key": "phc_test", "batch": entries}, separators=(",", ":")).encode("utf-8")
            assert len(body) <= max_bytes or len(chunk) == 1

    def test_chunk_events_empty_list(self):
        assert chunk_events([], distinct_id="user") == []

    def test_oversize_event_goes_alone(self):
        events = self._events(3)
        chunks = chunk_events(events, distinct_id="user", max_bytes=1)
        assert len(chunks) == len(events)
        assert all(len(c) == 1 for c in chunks)
        assert [c[0]["uuid"] for c in chunks] == [e["uuid"] for e in events]

    def test_every_request_body_stays_under_the_limit(self, posthog, monkeypatch):
        monkeypatch.setattr(sender_mod, "MAX_BATCH_BYTES", 3000)
        events = self._events(12)
        result = self._send(events)

        assert result["status"] == "ok"
        assert len(posthog.bodies) > 1
        assert all(len(body) <= 3000 for body in posthog.bodies)
        sent_uuids = [e["uuid"] for batch in posthog.batches for e in batch]
        assert sorted(sent_uuids) == sorted(e["uuid"] for e in events)
        assert result["sent"] == len(events)

    def test_failed_chunk_is_recorded_once_and_the_rest_resumes(self, posthog, monkeypatch):
        monkeypatch.setattr(sender_mod, "MAX_BATCH_BYTES", 3000)
        events = self._events(12)
        chunks = chunk_events(events, distinct_id="user")
        assert len(chunks) > 2
        first_chunk = chunks[0]
        first_uuids = {e["uuid"] for e in first_chunk}

        posthog.fail_on = {2}
        result = self._send(events)
        assert result["status"] == "error"
        assert result["sent"] == len(first_chunk)
        assert [e["uuid"] for e in posthog.batches[0]] == [e["uuid"] for e in first_chunk]

        posthog.fail_on = set()
        result = self._send(events)
        assert result["status"] == "ok"
        resent = [e["uuid"] for batch in posthog.batches[1:] for e in batch]
        assert not first_uuids & set(resent)
        assert sorted(resent) == sorted(e["uuid"] for e in events if e["uuid"] not in first_uuids)

    def test_deadline_passed_sends_nothing_and_records_nothing(self, posthog, tmp_path):
        events = self._events(3)
        result = self._send(events, deadline=time.monotonic() - 1)

        assert result["status"] == "error"
        assert result["sent"] == 0
        assert posthog.batches == []
        assert not (tmp_path / "test-session-id.json").exists()

    def test_in_flight_post_is_cut_off_at_the_deadline(self, monkeypatch):
        timeouts = []

        def fake_urlopen(req, timeout=None):
            timeouts.append(timeout)
            raise socket.timeout("timed out")

        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
        events = self._events(12)
        result = sender_mod.send_chunks(
            events,
            api_key="phc_test",
            host="http://posthog.test",
            distinct_id="user",
            max_bytes=3000,
            deadline=time.monotonic() + 2.5,
        )

        assert result["status"] == "error"
        assert result["sent"] == 0
        assert len(timeouts) == 1
        assert 0 < timeouts[0] <= 2.5

    @pytest.mark.parametrize("trace_grouping", ["session", "message"])
    def test_deadline_keeps_trace_events_in_first_chunk(self, posthog, monkeypatch, trace_grouping):
        """$ai_trace events go out before generations and spans, so a
        deadline that cuts the send later still delivers trace names and
        token totals."""
        monkeypatch.setattr(sender_mod, "MAX_BATCH_BYTES", 3000)
        config = {**DEFAULT_CONFIG, "trace_grouping": trace_grouping}
        events = self._events(12, config)

        kinds = [e["event"] for e in events]
        trace_idx = [i for i, k in enumerate(kinds) if k == "$ai_trace"]
        other_idx = [i for i, k in enumerate(kinds) if k != "$ai_trace"]
        assert trace_idx and other_idx and max(trace_idx) < min(other_idx)

        clock = [1000.0]
        monkeypatch.setattr(time, "monotonic", lambda: clock[0])
        real_urlopen = posthog.urlopen

        def urlopen_then_expire(req, timeout=None):
            resp = real_urlopen(req, timeout=timeout)
            clock[0] += 60
            return resp

        monkeypatch.setattr("urllib.request.urlopen", urlopen_then_expire)
        result = self._send(events, deadline=clock[0] + 25)

        assert result["status"] == "error"
        assert len(posthog.batches) == 1
        assert result["sent"] == len(posthog.batches[0])
        sent_kinds = [e["event"] for e in posthog.batches[0]]
        assert "$ai_trace" in sent_kinds
        trace = next(e for e in posthog.batches[0] if e["event"] == "$ai_trace")
        assert "$ai_trace_name" in trace["properties"]
        assert "$ai_total_output_tokens" in trace["properties"]

    def test_many_small_events_stay_within_max_bytes(self, posthog, monkeypatch):
        monkeypatch.setattr(sender_mod, "MAX_BATCH_BYTES", 45_000)
        events = [
            {
                "event": "$ai_span",
                "uuid": f"ev-{i}",
                "properties": {},
                "timestamp": "2026-04-12T10:00:00Z",
            }
            for i in range(350)
        ]
        result = self._send(events)

        assert result["status"] == "ok"
        assert len(posthog.bodies) > 1
        assert all(len(body) <= 45_000 for body in posthog.bodies)

    def test_default_max_batch_bytes_is_one_megabyte(self):
        assert sender_mod.MAX_BATCH_BYTES == 1024 * 1024

    def test_deadline_with_less_than_min_post_seconds_sends_nothing(self, posthog):
        events = self._events(3)
        result = self._send(events, deadline=time.monotonic() + sender_mod.MIN_POST_SECONDS - 1)

        assert result["status"] == "error"
        assert result["sent"] == 0
        assert posthog.batches == []


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


class TestParseGitRemoteUrl:
    @pytest.mark.parametrize("url,expected", [
        ("git@github.com:PostHog/ai-plugin.git", "PostHog/ai-plugin"),
        ("git@github.com:PostHog/ai-plugin", "PostHog/ai-plugin"),
        ("https://github.com/PostHog/ai-plugin.git", "PostHog/ai-plugin"),
        ("https://github.com/PostHog/ai-plugin", "PostHog/ai-plugin"),
        ("ssh://git@github.com/PostHog/ai-plugin.git", "PostHog/ai-plugin"),
        ("https://user@gitlab.com/PostHog/ai-plugin.git", "PostHog/ai-plugin"),
        ("  git@github.com:PostHog/ai-plugin.git\n", "PostHog/ai-plugin"),
        ("", None),
        ("   ", None),
        ("not-a-url", None),
        ("git@github.com:justname", None),
    ])
    def test_parse(self, url, expected):
        assert parse_git_remote_url(url) == expected


# ---------------------------------------------------------------------------
# SessionEnd hook
# ---------------------------------------------------------------------------


def _main_user(uuid="u-1", prompt_id="p-1",
               session="55555555-5555-5555-5555-555555555555",
               timestamp="2026-04-12T10:00:00.000Z", text="go"):
    return {
        "type": "user", "uuid": uuid, "parentUuid": None, "promptId": prompt_id,
        "sessionId": session, "timestamp": timestamp,
        "message": {"role": "user", "content": text},
    }


def _subagent_user(uuid="su-1", prompt_id="p-1",
                   session="55555555-5555-5555-5555-555555555555",
                   timestamp="2026-04-12T10:00:00.500Z"):
    """Real subagent transcripts open with an isSidechain user entry that
    carries the parent prompt's promptId."""
    return {
        "type": "user", "isSidechain": True, "uuid": uuid, "parentUuid": None,
        "promptId": prompt_id, "sessionId": session, "timestamp": timestamp,
        "message": {"role": "user", "content": "subagent task"},
    }


def _subagent_asst(uuid, msg_id, content, *, parent_uuid="su-1",
                   session="55555555-5555-5555-5555-555555555555",
                   timestamp="2026-04-12T10:00:01.000Z", is_sidechain=True):
    entry = {
        "type": "assistant", "uuid": uuid, "parentUuid": parent_uuid,
        "sessionId": session, "timestamp": timestamp,
        "message": {"role": "assistant", "id": msg_id, "model": "claude-opus-4-6",
                    "stop_reason": "end_turn", "usage": {"output_tokens": 5},
                    "content": content},
    }
    if is_sidechain:
        entry["isSidechain"] = True
    return entry


def _text_asst(uuid, msg_id, text, **kwargs):
    return _subagent_asst(uuid, msg_id, [{"type": "text", "text": text}], **kwargs)


def _write_subagent_project(tmp_path, session, main_entries, agents):
    """Write proj/<session>.jsonl plus proj/<session>/subagents/agent-*.jsonl.
    Returns the main log path."""
    project = tmp_path / "proj"
    subagents = project / session / "subagents"
    subagents.mkdir(parents=True)
    main = project / f"{session}.jsonl"
    main.write_text("".join(json.dumps(e) + "\n" for e in main_entries))
    for name, entries in agents.items():
        (subagents / name).write_text("".join(json.dumps(e) + "\n" for e in entries))
    return main


def test_session_end_captures_subagent_usage(tmp_path):
    """E2E coverage for #166: the hook also sends generations from
    <project>/<session_id>/subagents/agent-*.jsonl in the same batch."""
    session = "55555555-5555-5555-5555-555555555555"
    cwd = "/tmp/myproject"
    project = tmp_path / ".claude" / "projects" / cwd.replace("/", "-")
    subagents = project / session / "subagents"
    subagents.mkdir(parents=True)

    (project / f"{session}.jsonl").write_text("".join(json.dumps(e) + "\n" for e in [
        _main_user(session=session),
        _text_asst("a-1", "m-1", "main reply", parent_uuid="u-1", is_sidechain=False),
    ]))
    (subagents / "agent-0.jsonl").write_text("".join(json.dumps(e) + "\n" for e in [
        _subagent_user(session=session),
        _text_asst("a-2", "m-2", "subagent reply"),
    ]))

    bodies = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            bodies.append(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        hook = os.path.join(os.path.dirname(__file__), "..", "hooks", "session-end-llma.py")
        env = {"PATH": os.environ.get("PATH", ""), "HOME": str(tmp_path),
               "POSTHOG_LLMA_CC_ENABLED": "true", "POSTHOG_API_KEY": "phc_test",
               "POSTHOG_HOST": f"http://127.0.0.1:{server.server_address[1]}"}
        subprocess.run([sys.executable, hook],
                       input=json.dumps({"session_id": session, "cwd": cwd}),
                       text=True, env=env, timeout=60, check=True)
    finally:
        server.shutdown()

    sent = b"\n".join(bodies).decode("utf-8", "replace")
    assert "main reply" in sent
    assert sent.count("subagent reply") == 1


def test_parse_session_with_subagents_merges_subagent_files(tmp_path):
    session = "66666666-6666-6666-6666-666666666666"
    main = _write_subagent_project(
        tmp_path, session,
        main_entries=[
            _main_user(session=session),
            _text_asst("a-1", "m-1", "main reply", parent_uuid="u-1", is_sidechain=False),
        ],
        # agent-0 holds a new subagent reply and a repeat of the main reply.
        agents={"agent-0.jsonl": [
            _subagent_user(session=session),
            _text_asst("a-2", "m-2", "subagent reply"),
            _text_asst("a-1", "m-1", "main reply"),
        ]},
    )

    parsed = parse_session_with_subagents(str(main), DEFAULT_CONFIG)
    msg_ids = [g["msg_id"] for g in parsed["generations"]]
    assert "m-2" in msg_ids
    assert msg_ids.count("m-1") == 1


def test_parse_session_with_subagents_deduplicates_duplicate_subagent_files(tmp_path):
    session = "77777777-7777-7777-7777-777777777777"
    reply = [{"type": "text", "text": "subagent reply"}]
    main = _write_subagent_project(
        tmp_path, session,
        main_entries=[
            _main_user(session=session),
            _text_asst("a-1", "m-1", "main reply", parent_uuid="u-1", is_sidechain=False),
        ],
        agents={
            "agent-0.jsonl": [
                _subagent_user(session=session),
                _subagent_asst("a-2", "m-2", reply),
            ],
            "agent-1.jsonl": [
                _subagent_user(session=session),
                _subagent_asst("a-2", "m-2", reply),
            ],
        },
    )

    parsed = parse_session_with_subagents(str(main), DEFAULT_CONFIG)
    msg_ids = [g["msg_id"] for g in parsed["generations"]]
    assert msg_ids.count("m-2") == 1
    assert "m-1" in msg_ids


def test_parse_session_with_subagents_deduplicates_tool_uses_and_keeps_unique_ones(tmp_path):
    session = "88888888-8888-8888-8888-888888888888"

    def tool_asst(uuid, msg_id, tool_id, name):
        entry = _subagent_asst(uuid, msg_id, [
            {"type": "tool_use", "id": tool_id, "name": name, "input": {}},
        ])
        entry["message"]["stop_reason"] = "tool_use"
        return entry

    repeated = tool_asst("a-4", "m-4", "tu-4", "SubagentOnlyTool")
    main = _write_subagent_project(
        tmp_path, session,
        main_entries=[
            _main_user(session=session),
            _text_asst("a-1", "m-1", "main reply", parent_uuid="u-1", is_sidechain=False),
        ],
        agents={
            "agent-0.jsonl": [_subagent_user(session=session), repeated],
            # The same tool reply in a second subagent file: the dup_spans
            # filter must drop this copy's tool use, or the tool name is
            # counted twice. The unique reply beside it must be kept.
            "agent-1.jsonl": [
                _subagent_user(session=session),
                repeated,
                tool_asst("a-5", "m-5", "tu-5", "SecondSubagentTool"),
            ],
        },
    )

    parsed = parse_session_with_subagents(str(main), DEFAULT_CONFIG)
    msg_ids = [g["msg_id"] for g in parsed["generations"]]
    assert msg_ids.count("m-4") == 1
    assert "m-5" in msg_ids
    names = [tu["name"] for tu in parsed["tool_uses"]]
    assert names.count("SubagentOnlyTool") == 1
    assert names.count("SecondSubagentTool") == 1


def test_parse_session_with_subagents_sorts_by_timestamp_for_latency(tmp_path):
    """Merging appends subagent entries after the main ones, so the merged
    lists must be re-sorted or $ai_latency measures list order, not time."""
    session = "99999999-9999-9999-9999-999999999999"

    def tool_asst(uuid, msg_id, name, timestamp, **kwargs):
        entry = _subagent_asst(uuid, msg_id, [
            {"type": "tool_use", "id": f"tu-{msg_id}", "name": name, "input": {}},
        ], timestamp=timestamp, **kwargs)
        entry["message"]["stop_reason"] = "tool_use"
        return entry

    main = _write_subagent_project(
        tmp_path, session,
        main_entries=[
            _main_user(session=session),
            tool_asst("a-1", "m-1", "MainToolA", "2026-04-12T10:00:01.000Z",
                      parent_uuid="u-1", is_sidechain=False),
            tool_asst("a-2", "m-2", "MainToolB", "2026-04-12T10:05:00.000Z",
                      parent_uuid="u-1", is_sidechain=False),
        ],
        agents={"agent-0.jsonl": [
            _subagent_user(session=session),
            tool_asst("a-3", "m-3", "SubTool", "2026-04-12T10:02:00.000Z"),
        ]},
    )

    parsed = parse_session_with_subagents(str(main), DEFAULT_CONFIG)
    expected = [
        "2026-04-12T10:00:01.000Z",
        "2026-04-12T10:02:00.000Z",
        "2026-04-12T10:05:00.000Z",
    ]
    assert [g["timestamp"] for g in parsed["generations"]] == expected
    assert [tu["timestamp"] for tu in parsed["tool_uses"]] == expected

    events = build_events(parsed, DEFAULT_CONFIG)
    trace = next(e for e in events if e["event"] == "$ai_trace")
    assert trace["properties"]["$ai_latency"] == 299.0


def test_subagent_generation_lands_in_parent_prompt_trace_in_message_mode(tmp_path):
    session = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    sub_reply = _subagent_asst("a-2", "m-2", [
        {"type": "tool_use", "id": "tu-2", "name": "SubTool", "input": {}},
        {"type": "text", "text": "subagent reply"},
    ])
    sub_reply["message"]["usage"]["output_tokens"] = 7
    sub_reply["message"]["stop_reason"] = "tool_use"
    main = _write_subagent_project(
        tmp_path, session,
        main_entries=[
            _main_user(session=session),
            _text_asst("a-1", "m-1", "main reply", parent_uuid="u-1", is_sidechain=False),
        ],
        agents={"agent-0.jsonl": [
            _subagent_user(session=session),
            sub_reply,
        ]},
    )

    config = {**DEFAULT_CONFIG, "trace_grouping": "message"}
    parsed = parse_session_with_subagents(str(main), config)
    sub_gen = next(g for g in parsed["generations"] if g["msg_id"] == "m-2")
    assert sub_gen["prompt_id"] == "p-1"

    events = build_events(parsed, config)
    traces = [e for e in events if e["event"] == "$ai_trace"]
    assert len(traces) == 1
    props = traces[0]["properties"]
    assert props["$ai_trace_id"] == "p-1"
    assert props["$ai_trace_name"] == "go"
    assert props["$ai_total_output_tokens"] == 12
    for e in events:
        if e["event"] in ("$ai_generation", "$ai_span"):
            assert e["properties"]["$ai_trace_id"] == "p-1"


_MALFORMED_JSONL_LINES = [
    b"\xff\n",
    b"null\n",
    b'{"type":"assistant","message":null}\n',
    (json.dumps(_subagent_asst(
        "a-bad", "m-bad", [{"type": []}],
        parent_uuid="u-1", is_sidechain=False)) + "\n").encode(),
]


@pytest.mark.parametrize("bad_line", _MALFORMED_JSONL_LINES)
def test_parse_session_skips_malformed_lines_in_main_log(tmp_path, bad_line):
    session = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    entries = [
        _main_user(session=session),
        _text_asst("a-1", "m-before", "before", parent_uuid="u-1", is_sidechain=False),
    ]
    path = tmp_path / f"{session}.jsonl"
    path.write_bytes(
        b"".join(json.dumps(e).encode() + b"\n" for e in entries)
        + bad_line
        + json.dumps(_text_asst("a-2", "m-after", "after",
                                parent_uuid="u-1", is_sidechain=False)).encode() + b"\n")

    parsed = parse_session(str(path), DEFAULT_CONFIG)
    msg_ids = [g["msg_id"] for g in parsed["generations"]]
    assert "m-before" in msg_ids
    assert "m-after" in msg_ids


@pytest.mark.parametrize("bad_line", _MALFORMED_JSONL_LINES)
def test_parse_session_with_subagents_skips_malformed_lines_without_dropping_file(tmp_path, bad_line):
    session = "cccccccc-cccc-cccc-cccc-cccccccccccc"
    project = tmp_path / "proj"
    subagents = project / session / "subagents"
    subagents.mkdir(parents=True)

    main = project / f"{session}.jsonl"
    main.write_text("".join(json.dumps(e) + "\n" for e in [
        _main_user(session=session),
        _text_asst("a-1", "m-main", "main reply", parent_uuid="u-1", is_sidechain=False),
    ]))
    good = [
        _subagent_user(session=session),
        _text_asst("a-2", "m-sub1", "sub one", timestamp="2026-04-12T10:00:02.000Z"),
    ]
    after = _text_asst("a-3", "m-sub2", "sub two", timestamp="2026-04-12T10:00:03.000Z")
    (subagents / "agent-0.jsonl").write_bytes(
        b"".join(json.dumps(e).encode() + b"\n" for e in good)
        + bad_line
        + json.dumps(after).encode() + b"\n")

    parsed = parse_session_with_subagents(str(main), DEFAULT_CONFIG)
    msg_ids = [g["msg_id"] for g in parsed["generations"]]
    assert "m-main" in msg_ids
    assert "m-sub1" in msg_ids
    assert "m-sub2" in msg_ids
