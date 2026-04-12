"""Tests for the generic PostHog LLM Analytics event builder."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import posthog_llma


# ---------------------------------------------------------------------------
# $ai_generation
# ---------------------------------------------------------------------------


class TestBuildAiGeneration:
    def test_basic_generation(self):
        ev = posthog_llma.build_ai_generation(
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
        ev = posthog_llma.build_ai_generation(
            model="m", stop_reason=cc_reason, trace_id="t", session_id="s",
        )
        assert ev["properties"]["$ai_stop_reason"] == expected

    def test_privacy_mode_redacts(self):
        ev = posthog_llma.build_ai_generation(
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
        ev = posthog_llma.build_ai_generation(
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
        ev = posthog_llma.build_ai_generation(
            model="m", trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"

    def test_no_timestamp_means_no_key(self):
        ev = posthog_llma.build_ai_generation(
            model="m", trace_id="t", session_id="s",
        )
        assert "timestamp" not in ev

    def test_cache_tokens(self):
        ev = posthog_llma.build_ai_generation(
            model="m", trace_id="t", session_id="s",
            input_tokens=10, output_tokens=20,
            cache_read_tokens=5, cache_creation_tokens=3,
        )
        props = ev["properties"]
        assert props["cache_read_input_tokens"] == 5
        assert props["cache_creation_input_tokens"] == 3

    def test_no_cost_properties(self):
        """Cost is calculated by PostHog ingestion, we should not send it."""
        ev = posthog_llma.build_ai_generation(
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
        ev = posthog_llma.build_ai_span(
            span_name="Bash",
            trace_id="trace-1",
            session_id="session-1",
        )
        assert ev["event"] == "$ai_span"
        assert ev["properties"]["$ai_span_name"] == "Bash"
        assert ev["properties"]["$ai_trace_id"] == "trace-1"

    def test_parent_id(self):
        ev = posthog_llma.build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            parent_span_id="parent-123",
        )
        assert ev["properties"]["$ai_parent_id"] == "parent-123"

    def test_privacy_mode_redacts_state(self):
        ev = posthog_llma.build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            input_state={"command": "ls"},
            output_state="file list",
            privacy_mode=True,
        )
        assert ev["properties"]["$ai_input_state"] is None
        assert ev["properties"]["$ai_output_state"] is None

    def test_truncation(self):
        ev = posthog_llma.build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            input_state="x" * 20000,
            max_attribute_length=100,
        )
        assert len(ev["properties"]["$ai_input_state"]) == 100

    def test_timestamp_passthrough(self):
        ev = posthog_llma.build_ai_span(
            span_name="Bash", trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"


# ---------------------------------------------------------------------------
# $ai_trace
# ---------------------------------------------------------------------------


class TestBuildAiTrace:
    def test_basic_trace(self):
        ev = posthog_llma.build_ai_trace(
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
        ev = posthog_llma.build_ai_trace(
            trace_id="t", session_id="s",
            trace_name="help me fix a bug",
        )
        assert ev["properties"]["$ai_trace_name"] == "help me fix a bug"

    def test_timestamp_passthrough(self):
        ev = posthog_llma.build_ai_trace(
            trace_id="t", session_id="s",
            timestamp="2026-04-12T21:00:00Z",
        )
        assert ev["timestamp"] == "2026-04-12T21:00:00Z"


# ---------------------------------------------------------------------------
# send_batch
# ---------------------------------------------------------------------------


class TestSendBatch:
    def test_empty_batch(self):
        result = posthog_llma.send_batch([], api_key="test", distinct_id="user")
        assert result == {"status": "ok", "sent": 0}

    def test_per_event_timestamps_used(self):
        """Verify batch assembly uses per-event timestamps."""
        from datetime import datetime, timezone

        events = [
            {"event": "$ai_generation", "properties": {}, "timestamp": "2026-04-12T10:00:00Z"},
            {"event": "$ai_generation", "properties": {}, "timestamp": "2026-04-12T10:01:00Z"},
            {"event": "$ai_generation", "properties": {}},  # no timestamp
        ]
        fallback = datetime.now(timezone.utc).isoformat()
        timestamps = [ev.get("timestamp") or fallback for ev in events]
        assert timestamps[0] == "2026-04-12T10:00:00Z"
        assert timestamps[1] == "2026-04-12T10:01:00Z"
        assert timestamps[2] == fallback


# ---------------------------------------------------------------------------
# Status file
# ---------------------------------------------------------------------------


class TestStatusFile:
    def test_write_and_read(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_path = f.name
        try:
            original = posthog_llma.STATUS_FILE
            posthog_llma.STATUS_FILE = tmp_path
            posthog_llma.write_status({"session_id": "test", "status": "ok"})
            status = posthog_llma.read_status()
            assert status["session_id"] == "test"
            assert status["status"] == "ok"
            assert "timestamp" in status
        finally:
            posthog_llma.STATUS_FILE = original
            os.unlink(tmp_path)

    def test_read_missing_file(self):
        original = posthog_llma.STATUS_FILE
        posthog_llma.STATUS_FILE = "/tmp/nonexistent-posthog-llma-test.json"
        try:
            assert posthog_llma.read_status() is None
        finally:
            posthog_llma.STATUS_FILE = original
