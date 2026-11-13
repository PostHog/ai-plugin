"""Install the repository with the real Claude Code CLI and check the consumer header it sends.

Claude Code runs `headersHelper` through `sh` on macOS and Linux and through cmd.exe on Windows. When
the helper fails, Claude Code sends the static `plugin` header and reports no error, so only a real
run on each OS shows which value the MCP server receives. Skipped when `claude` is not on PATH.
"""

import json
import os
import shutil
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(shutil.which("claude") is None, reason="claude is not installed")


def _recording_server(consumers):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            consumers.append(self.headers.get("x-posthog-mcp-consumer"))
            self.send_response(405)
            self.end_headers()

        def do_POST(self):
            consumers.append(self.headers.get("x-posthog-mcp-consumer"))
            request = json.loads(self.rfile.read(int(self.headers.get("content-length", 0))))
            if "id" not in request:
                self.send_response(202)
                self.end_headers()
                return
            results = {
                "initialize": {
                    "protocolVersion": request.get("params", {}).get("protocolVersion"),
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "recorder", "version": "0"},
                },
                "tools/list": {"tools": []},
            }
            body = json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": results.get(request["method"], {})})
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(body.encode())

    return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


def _claude(workdir, *args):
    # A shell command, because npm installs `claude` as a .cmd shim on Windows.
    result = subprocess.run(
        " ".join(["claude", *args]),
        shell=True,
        cwd=workdir,
        env={**os.environ, "CLAUDE_CONFIG_DIR": str(workdir / "config")},
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_installed_plugin_sends_the_plugin_learn_consumer(tmp_path):
    consumers = []
    server = _recording_server(consumers)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    repo = tmp_path / "repo"
    shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache"))
    mcp_config = json.loads((repo / ".mcp.json").read_text())
    mcp_config["mcpServers"]["posthog"]["url"] = f"http://127.0.0.1:{server.server_port}/mcp"
    (repo / ".mcp.json").write_text(json.dumps(mcp_config))

    try:
        _claude(tmp_path, "plugin", "marketplace", "add", "./repo")
        _claude(tmp_path, "plugin", "install", "posthog@posthog")
        _claude(tmp_path, "mcp", "list")
    finally:
        server.shutdown()

    assert consumers and set(consumers) == {"plugin-learn"}, consumers
