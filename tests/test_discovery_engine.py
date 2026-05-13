"""Unit tests for GitHub discovery engine and parser tool handler."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from posthog_llma.discovery.engine import (
    GitHubDiscoveryError,
    build_discovery_stats,
    build_tree_from_paths,
    detect_tech_stack,
    filter_discovery_noise,
    parse_github_url,
    persist_discovery_map,
    render_navigation_markdown,
    suggest_integration_roots,
    _resolve_markdown_export_path,
)
from posthog_llma.parser import (
    GITHUB_DISCOVERY_SKILL_ID,
    handle_github_discovery_tool,
    invoke_skill_tool_handler,
)


class TestParseGithubUrl:
    def test_owner_repo(self):
        p = parse_github_url("octocat/Hello-World")
        assert p.owner == "octocat"
        assert p.repo == "Hello-World"
        assert p.ref is None

    def test_https(self):
        p = parse_github_url("https://github.com/foo/bar")
        assert p.owner == "foo" and p.repo == "bar"

    def test_tree_url(self):
        p = parse_github_url("https://github.com/foo/bar/tree/main/src/pkg")
        assert p.ref == "main"
        assert p.path_prefix == "src/pkg"

    def test_empty_raises(self):
        with pytest.raises(GitHubDiscoveryError):
            parse_github_url("  ")


class TestBuildTreeFromPaths:
    def test_nested(self):
        tree = build_tree_from_paths(
            [
                {"path": "Providers/Adobe/x.md", "sha": "a", "size": 1},
                {"path": "Internal/Registry.json", "sha": "b", "size": 2},
            ]
        )
        assert tree["type"] == "tree"
        assert "Providers" in tree["children"]
        assert tree["children"]["Providers"]["descendantFolders"] >= 1
        blob = tree["children"]["Providers"]["children"]["Adobe"]["children"]["x.md"]
        assert blob["type"] == "blob"
        assert blob["path"] == "Providers/Adobe/x.md"


class TestBuildDiscoveryStats:
    def test_sums_sizes_and_counts(self):
        tree = build_tree_from_paths(
            [
                {"path": "a.txt", "sha": "1", "size": 100},
                {"path": "b/c.txt", "sha": "2", "size": 200},
                {"path": "b/d.txt", "sha": "3", "size": None},
            ]
        )
        blobs = [
            {"path": "a.txt", "sha": "1", "size": 100},
            {"path": "b/c.txt", "sha": "2", "size": 200},
            {"path": "b/d.txt", "sha": "3", "size": None},
        ]
        stats = build_discovery_stats(
            tree, blobs, duration_seconds=0.123456, api_strategy="recursive"
        )
        assert stats["total_files"] == tree["descendantFiles"] == 3
        assert stats["total_folders"] == tree["descendantFolders"] == 1
        assert stats["total_size_bytes"] == 300
        assert stats["api_strategy"] == "recursive"
        assert stats["duration_seconds"] == pytest.approx(0.123456)
        assert isinstance(stats["total_size_bytes"], int)
        assert stats["tech_stack"] == []
        assert "smart_summaries" not in stats

    def test_smart_summaries_in_stats(self):
        tree = build_tree_from_paths([{"path": "a.txt", "sha": "1", "size": 1}])
        blobs = [{"path": "a.txt", "sha": "1", "size": 1}]
        prev = [{"path": "README.md", "content_preview": "hi", "importance_score": 100}]
        stats = build_discovery_stats(
            tree,
            blobs,
            duration_seconds=0.1,
            api_strategy="recursive",
            tech_stack=["nodejs"],
            smart_summaries=prev,
        )
        assert stats["tech_stack"] == ["nodejs"]
        assert stats["smart_summaries"] == prev


class TestFilterNoise:
    def test_skips_node_modules_and_lock(self):
        blobs = [
            {"path": "src/index.ts", "sha": "1", "size": 10},
            {"path": "node_modules/foo/x.js", "sha": "2", "size": 1},
            {"path": "yarn.lock", "sha": "3", "size": 2},
            {"path": "README.md", "sha": "4", "size": 3},
        ]
        f = filter_discovery_noise(blobs)
        paths = {b["path"] for b in f}
        assert paths == {"src/index.ts", "README.md"}


class TestDetectTechStack:
    def test_root_signatures(self):
        blobs = [
            {"path": "package.json", "sha": "a", "size": 1},
            {"path": "README.md", "sha": "b", "size": 1},
            {"path": "src/x.ts", "sha": "c", "size": 1},
        ]
        assert "nodejs" in detect_tech_stack(blobs)


class TestMarkdownNav:
    def test_render_top_level_table(self):
        tree = build_tree_from_paths(
            [
                {"path": "README.md", "sha": "1", "size": 10},
                {"path": "src/a.ts", "sha": "2", "size": 5},
            ]
        )
        tree["repo"] = {"owner": "o", "name": "n", "commit_sha": "abcdef1", "ref": "main"}
        md = render_navigation_markdown(tree)
        assert "# Repository navigation" in md
        assert "| `README.md` | file |" in md
        assert "| `src` | directory |" in md

    def test_resolve_markdown_path(self):
        assert _resolve_markdown_export_path("dir/map.json", None).endswith("map_nav.md")
        assert _resolve_markdown_export_path("dir/map.json", "") is None
        assert _resolve_markdown_export_path(None, "x.md") == "x.md"
        assert _resolve_markdown_export_path(None, None) is None


class TestPersistDiscoveryMap:
    def test_writes_json_with_indent_and_saved_to(self, tmp_path):
        tree = build_tree_from_paths([{"path": "a.txt", "sha": "1", "size": 5}])
        tree["repo"] = {"owner": "o", "name": "r", "commit_sha": "abc", "ref": "main"}
        tree["integration_hints"] = {}
        tree["discovery_stats"] = build_discovery_stats(
            tree, [{"path": "a.txt", "sha": "1", "size": 5}],
            duration_seconds=0.01,
            api_strategy="recursive",
        )
        out = tmp_path / "nested" / "map.json"
        resolved = persist_discovery_map(tree, str(out))
        assert resolved == str(out.resolve())
        assert tree["saved_to"] == resolved
        text = out.read_text(encoding="utf-8")
        assert '"name": "root"' in text
        assert "\n" in text
        loaded = json.loads(text)
        assert loaded["saved_to"] == resolved
        assert loaded["discovery_stats"]["total_files"] == 1

    def test_empty_path_raises(self):
        tree = {"name": "root", "children": {}}
        with pytest.raises(GitHubDiscoveryError):
            persist_discovery_map(tree, "   ")


class TestSuggestIntegrationRoots:
    def test_providers(self):
        tree = build_tree_from_paths(
            [{"path": "Providers/X/y.md", "sha": "1", "size": None}],
        )
        h = suggest_integration_roots(tree)
        assert "Providers" in h["likely_provider_roots"]


class TestParserHandler:
    def test_missing_url(self):
        r = handle_github_discovery_tool({})
        assert r["ok"] is False

    def test_invoke_dispatch(self):
        r = invoke_skill_tool_handler("nonexistent-skill", {})
        assert r["ok"] is False

    def test_skill_id_constant(self):
        assert GITHUB_DISCOVERY_SKILL_ID == "Github-Discovery"
