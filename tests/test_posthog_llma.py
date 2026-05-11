"""Tests for the PostHog LLM Analytics event builders and sender."""

import os
import sys
import tempfile

import pytest

# Add plugin root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posthog_llma.events import build_ai_generation, build_ai_span, build_ai_trace
from posthog_llma.sender import send_batch, validate_host, write_status, read_status, STATUS_FILE


# ---------------------------------------------------------------------------
# $ai_generation
# ---------------------------------------------------------------------------


class TestBuildAiGeneration:
    def test_basic_generation(self):
        ev = build_ai_generation(
            model="claude-opus-4-6",
            input_tokens=100,
            output_tokens=50,
            trace_id="trace-1",
            session_id="session-1",
        )
        assert ev["event"] == "$ai_generation"
        props = ev["properties"]
        assert props["$ai_model"] == "claude-opus-4-6"
        assert props["$ai_provider"] == "anthropic"
        assert props["$ai_input_tokens"] == 100
        assert props["$ai_output_tokens"] == 50
        assert props["$ai_total_tokens"] == 150
        assert props["$ai_trace_id"] == "trace-1"
        assert props["$ai_session_id"] == "session-1"
        assert props["$ai_framework"] == "claude-code"

    @pytest.mark.parametrize("cc_reason,expected", [
        ("end_turn", "stop"),
        ("tool_use", "tool_calls"),
        ("max_tokens", "length"),
        ("error", "error"),
    ])
    def test_stop_reason_mapping(self, cc_reason, expected):
        ev = build_ai_generation(
            model="m", stop_reason=cc_reason, trace_id="t", session_id="s",
        )
        assert ev["properties"]["$ai_stop_reason"] == expected

    def test_privacy_mode_redacts(self):
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
            input_messages=[{"role": "user", "content": "secret"}],
            output_choices=[{"role": "assistant", "content": "answer"}],
            user_prompt="secret",
            privacy_mode=True,
        )
        props = ev["properties"]
        assert props["$ai_input"] is None
        assert props["$ai_output_choices"] is None
        assert "$ai_user_prompt" not in props

    def test_privacy_mode_off_includes_content(self):
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
            input_messages=[{"role": "user", "content": "hello"}],
            output_choices=[{"role": "assistant", "content": "hi"}],
            user_prompt="hello",
            privacy_mode=False,
        )
        props = ev["properties"]
        assert props["$ai_input"][0]["content"] == "hello"
        assert props["$ai_output_choices"][0]["content"] == "hi"
        assert props["$ai_user_prompt"] == "hello"

    def test_timestamp_passthrough(self):
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"

    def test_no_timestamp_means_no_key(self):
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
        )
        assert "timestamp" not in ev

    def test_cache_tokens(self):
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
            input_tokens=10, output_tokens=20,
            cache_read_tokens=5, cache_creation_tokens=3,
        )
        props = ev["properties"]
        assert props["cache_read_input_tokens"] == 5
        assert props["cache_creation_input_tokens"] == 3

    def test_no_cost_properties(self):
        """Cost is calculated by PostHog ingestion, we should not send it."""
        ev = build_ai_generation(
            model="m", trace_id="t", session_id="s",
            input_tokens=100, output_tokens=50,
        )
        props = ev["properties"]
        assert "$ai_total_cost_usd" not in props
        assert "$ai_input_cost_usd" not in props
        assert "$ai_output_cost_usd" not in props


# ---------------------------------------------------------------------------
# $ai_span
# ---------------------------------------------------------------------------


class TestBuildAiSpan:
    def test_basic_span(self):
        ev = build_ai_span(
            span_name="Bash",
            trace_id="trace-1",
            session_id="session-1",
        )
        assert ev["event"] == "$ai_span"
        assert ev["properties"]["$ai_span_name"] == "Bash"
        assert ev["properties"]["$ai_trace_id"] == "trace-1"

    def test_parent_id(self):
        ev = build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            parent_span_id="parent-123",
        )
        assert ev["properties"]["$ai_parent_id"] == "parent-123"

    def test_privacy_mode_redacts_state(self):
        ev = build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            input_state={"command": "ls"},
            output_state="file list",
            privacy_mode=True,
        )
        assert ev["properties"]["$ai_input_state"] is None
        assert ev["properties"]["$ai_output_state"] is None

    def test_truncation(self):
        ev = build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            input_state="x" * 20000,
            max_attribute_length=100,
        )
        assert len(ev["properties"]["$ai_input_state"]) == 100

    def test_extra_properties(self):
        ev = build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            extra_properties={"ai_product": "my-app", "team": "platform"},
        )
        assert ev["properties"]["ai_product"] == "my-app"
        assert ev["properties"]["team"] == "platform"

    def test_timestamp_passthrough(self):
        ev = build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"


# ---------------------------------------------------------------------------
# $ai_trace
# ---------------------------------------------------------------------------


class TestBuildAiTrace:
    def test_basic_trace(self):
        ev = build_ai_trace(
            trace_id="trace-1",
            session_id="session-1",
            total_input_tokens=1000,
            total_output_tokens=5000,
        )
        assert ev["event"] == "$ai_trace"
        assert ev["properties"]["$ai_trace_id"] == "trace-1"
        assert ev["properties"]["$ai_total_input_tokens"] == 1000
        assert ev["properties"]["$ai_total_output_tokens"] == 5000

    def test_trace_name(self):
        ev = build_ai_trace(
            trace_id="t", session_id="s",
            trace_name="help me fix a bug",
        )
        assert ev["properties"]["$ai_trace_name"] == "help me fix a bug"

    def test_extra_properties(self):
        ev = build_ai_trace(
            trace_id="t", session_id="s",
            extra_properties={"ai_product": "my-app"},
        )
        assert ev["properties"]["ai_product"] == "my-app"

    def test_timestamp_passthrough(self):
        ev = build_ai_trace(
            trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"


# ---------------------------------------------------------------------------
# send_batch
# ---------------------------------------------------------------------------


class TestSendBatch:
    def test_empty_batch(self):
        result = send_batch([], api_key="test", distinct_id="user")
        assert result == {"status": "ok", "sent": 0}

    def test_refuses_unknown_host(self, monkeypatch):
        monkeypatch.delenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", raising=False)
        result = send_batch(
            [{"event": "$ai_generation", "properties": {}}],
            api_key="phc_test",
            host="https://attacker.example.com",
            distinct_id="u",
        )
        assert result["status"] == "error"
        assert "refused to send" in result["error"]

    def test_refuses_http_for_non_localhost(self, monkeypatch):
        monkeypatch.delenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", raising=False)
        result = send_batch(
            [{"event": "$ai_generation", "properties": {}}],
            api_key="phc_test",
            host="http://us.i.posthog.com",
            distinct_id="u",
        )
        assert result["status"] == "error"
        assert "refused to send" in result["error"]

    def test_per_event_timestamps_used(self):
        from datetime import datetime, timezone

        events = [
            {"event": "$ai_generation", "properties": {}, "timestamp": "2026-04-12T10:00:00Z"},
            {"event": "$ai_generation", "properties": {}, "timestamp": "2026-04-12T10:01:00Z"},
            {"event": "$ai_generation", "properties": {}},
        ]
        fallback = datetime.now(timezone.utc).isoformat()
        timestamps = [ev.get("timestamp") or fallback for ev in events]
        assert timestamps[0] == "2026-04-12T10:00:00Z"
        assert timestamps[1] == "2026-04-12T10:01:00Z"
        assert timestamps[2] == fallback


# ---------------------------------------------------------------------------
# validate_host
# ---------------------------------------------------------------------------


class TestValidateHost:
    @pytest.mark.parametrize("host", [
        "https://us.i.posthog.com",
        "https://eu.i.posthog.com",
        "https://app.posthog.com",
        "https://posthog.com",
        "https://us.i.posthog.com/",
        "us.i.posthog.com",  # no scheme — defaulted to https
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])
    def test_accepts_known_endpoints(self, host, monkeypatch):
        monkeypatch.delenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", raising=False)
        ok, reason = validate_host(host)
        assert ok, reason

    @pytest.mark.parametrize("host", [
        "https://attacker.example.com",
        "https://evilposthog.com",       # substring, not suffix
        "https://posthog.com.evil.com",  # suffix attack
        "http://us.i.posthog.com",       # http to non-localhost
        "ftp://us.i.posthog.com",        # bad scheme
        "",                              # empty
    ])
    def test_rejects_untrusted_hosts(self, host, monkeypatch):
        monkeypatch.delenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", raising=False)
        ok, reason = validate_host(host)
        assert not ok
        assert reason

    def test_self_hosted_opt_in(self, monkeypatch):
        monkeypatch.setenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", "true")
        ok, reason = validate_host("https://posthog.internal.example.com")
        assert ok, reason

    def test_self_hosted_opt_in_still_requires_https(self, monkeypatch):
        monkeypatch.setenv("POSTHOG_LLMA_ALLOW_CUSTOM_HOST", "true")
        ok, reason = validate_host("http://posthog.internal.example.com")
        assert not ok
        assert "https" in reason


# ---------------------------------------------------------------------------
# Status file
# ---------------------------------------------------------------------------


class TestStatusFile:
    def test_write_and_read(self):
        import posthog_llma.sender as sender_mod
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name
        original = sender_mod.STATUS_FILE
        try:
            sender_mod.STATUS_FILE = tmp_path
            write_status({"session_id": "test", "status": "ok"})
            status = read_status()
            assert status["session_id"] == "test"
            assert status["status"] == "ok"
            assert "timestamp" in status
        finally:
            sender_mod.STATUS_FILE = original
            os.unlink(tmp_path)

    def test_read_missing_file(self):
        import posthog_llma.sender as sender_mod
        original = sender_mod.STATUS_FILE
        sender_mod.STATUS_FILE = "/tmp/nonexistent-posthog-llma-test.json"
        try:
            assert read_status() is None
        finally:
            sender_mod.STATUS_FILE = original
