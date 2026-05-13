"""Local GitHub repository structure discovery (no external Explorer site)."""

from posthog_llma.discovery.engine import (
    GitHubDiscoveryError,
    ParsedRepoRef,
    build_discovery_stats,
    build_tree_from_paths,
    detect_tech_stack,
    discover_repository,
    discover_repository_async,
    filter_discovery_noise,
    parse_github_url,
    persist_discovery_map,
    persist_navigation_markdown,
    render_navigation_markdown,
    suggest_integration_roots,
)

__all__ = [
    "GitHubDiscoveryError",
    "ParsedRepoRef",
    "build_discovery_stats",
    "build_tree_from_paths",
    "detect_tech_stack",
    "discover_repository",
    "discover_repository_async",
    "filter_discovery_noise",
    "parse_github_url",
    "persist_discovery_map",
    "persist_navigation_markdown",
    "render_navigation_markdown",
    "suggest_integration_roots",
]
