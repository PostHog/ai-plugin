"""Headless GitHub repo discovery: URL parsing, recursive tree mapping, JSON map.

Output shape aligns with Integration Registry-style trees:
  { name, path, type: tree|blob, children: {...}, descendantFiles, descendantFolders }

Uses the GitHub REST API (git trees + refs). Set GITHUB_TOKEN for higher rate limits.
"""

from __future__ import annotations

import asyncio
import base64
import binascii
import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

GITHUB_API = "https://api.github.com"


class GitHubDiscoveryError(Exception):
    """Raised for unrecoverable API, parse, or limit errors."""


@dataclass(frozen=True)
class ParsedRepoRef:
    owner: str
    repo: str
    ref: Optional[str] = None
    path_prefix: Optional[str] = None


def parse_github_url(url: str) -> ParsedRepoRef:
    """Parse owner/repo and optional ref + path from a GitHub URL or ``owner/repo`` shorthand.

    Supported:
    - ``https://github.com/octocat/Hello-World``
    - ``https://github.com/octocat/Hello-World/tree/main``
    - ``https://github.com/octocat/Hello-World/blob/main/src``
    - ``octocat/Hello-World`` (for branch names containing ``/``, pass ``ref`` explicitly)
    """
    raw = (url or "").strip()
    if not raw:
        raise GitHubDiscoveryError("Empty URL or repo string.")

    if raw.startswith("git@github.com:"):
        raw = "https://github.com/" + raw.removeprefix("git@github.com:").removesuffix(".git")

    raw = raw.removesuffix(".git")

    # owner/repo shorthand
    if re.fullmatch(r"[\w.-]+/[\w.-]+", raw):
        o, r = raw.split("/", 1)
        return ParsedRepoRef(owner=o, repo=r, ref=None, path_prefix=None)

    # After repo: optional /tree|/blob/<ref>[/<path>]. Single-segment ref; for
    # branches with slashes pass ``ref`` explicitly to discover_repository*.
    m = re.match(
        r"^https?://github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+)"
        r"(?:/(?:tree|blob)/(?P<ref>[^/]+)(?:/(?P<path>.+))?)?/?$",
        raw,
    )
    if not m:
        raise GitHubDiscoveryError(
            f"Could not parse GitHub URL: {url!r}. "
            "Expected https://github.com/<owner>/<repo> or owner/repo."
        )
    owner = m.group("owner")
    repo = m.group("repo")
    ref = m.group("ref")
    path_prefix = m.group("path")
    if not ref:
        return ParsedRepoRef(owner=owner, repo=repo, ref=None, path_prefix=None)
    return ParsedRepoRef(owner=owner, repo=repo, ref=ref, path_prefix=path_prefix)


# Directory path segments whose entire subtrees are omitted from discovery maps.
IGNORED_DIR_SEGMENTS: frozenset[str] = frozenset({
    "node_modules",
    ".git",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "coverage",
    ".venv",
    "venv",
    "target",
})

# Basenames (lowercased) skipped as files.
_NOISE_FILE_BASENAMES_LOWER: frozenset[str] = frozenset(
    {
        ".ds_store",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "pnpm-lock.yml",
        "poetry.lock",
        "pipfile.lock",
        "composer.lock",
        "gemfile.lock",
        "go.sum",
        "cargo.lock",
        "bun.lockb",
        "npm-shrinkwrap.json",
    }
)


def _is_noise_path(path: str) -> bool:
    if not path:
        return True
    parts = path.replace("\\", "/").split("/")
    for seg in parts[:-1]:
        if seg in IGNORED_DIR_SEGMENTS:
            return True
    if parts:
        if parts[-1].lower() in _NOISE_FILE_BASENAMES_LOWER:
            return True
    return False


def filter_discovery_noise(blobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop blobs under ignored directories and common lock / junk files."""
    return [b for b in blobs if not _is_noise_path(b.get("path") or "")]


# (root filename lowercased, stack label) — order defines priority in output list.
_ROOT_FILE_STACK: tuple[tuple[str, str], ...] = (
    ("package.json", "nodejs"),
    ("pnpm-workspace.yaml", "pnpm-workspace"),
    ("tsconfig.json", "typescript"),
    ("requirements.txt", "python"),
    ("pyproject.toml", "python"),
    ("setup.py", "python"),
    ("setup.cfg", "python"),
    ("pipfile", "python"),
    ("cargo.toml", "rust"),
    ("go.mod", "go"),
    ("gemfile", "ruby"),
    ("pom.xml", "jvm-maven"),
    ("build.gradle", "jvm-gradle"),
    ("build.gradle.kts", "jvm-gradle"),
    ("dockerfile", "docker"),
    ("containerfile", "docker"),
    ("docker-compose.yml", "compose"),
    ("docker-compose.yaml", "compose"),
    ("compose.yaml", "compose"),
    ("compose.yml", "compose"),
    ("deno.json", "deno"),
    ("deno.jsonc", "deno"),
    ("next.config.js", "nextjs"),
    ("next.config.mjs", "nextjs"),
    ("next.config.ts", "nextjs"),
    ("vite.config.ts", "vite"),
    ("vite.config.js", "vite"),
    ("nuxt.config.ts", "nuxt"),
    ("vue.config.js", "vue"),
)


def detect_tech_stack(blobs: list[dict[str, Any]]) -> list[str]:
    """Infer stack tags from root-level manifest files (post-filter paths)."""
    root_lower: set[str] = set()
    for b in blobs:
        p = b.get("path") or ""
        if "/" in p:
            continue
        root_lower.add(p.lower())
    out: list[str] = []
    seen: set[str] = set()
    for fname, tag in _ROOT_FILE_STACK:
        if fname in root_lower and tag not in seen:
            seen.add(tag)
            out.append(tag)
    return out


def _importance_score(path: str) -> int:
    """Higher = more important for smart summary previews."""
    p = path.replace("\\", "/")
    pl = p.lower()
    base = p.rsplit("/", 1)[-1].lower()
    if base in ("readme.md", "readme.rst", "readme.txt", "readme.mdown"):
        return 100
    if base == "readme":
        return 99
    if pl.endswith("internal/registry.json"):
        return 98
    if base == "registry.json":
        return 95
    if pl == "package.json" or base == "package.json":
        return 90
    if base in ("pyproject.toml", "requirements.txt", "cargo.toml", "go.mod"):
        return 88
    if base in ("main.py", "app.py", "__main__.py", "index.ts", "index.tsx", "main.ts", "main.tsx"):
        return 82
    if pl in ("src/main.py", "src/index.ts", "src/index.tsx", "lib/index.ts"):
        return 80
    if base in ("dockerfile", "containerfile", "makefile"):
        return 72
    if base.endswith(".md") and "/" not in p:  # root markdown
        return 65
    return 0


def _empty_tree_node(name: str, path: str) -> dict[str, Any]:
    return {
        "name": name,
        "path": path,
        "type": "tree",
        "children": {},
        "descendantFiles": 0,
        "descendantFolders": 0,
    }


def _blob_node(name: str, path: str, sha: str, size: Optional[int]) -> dict[str, Any]:
    n: dict[str, Any] = {
        "name": name,
        "path": path,
        "type": "blob",
        "children": {},
        "descendantFiles": 0,
        "descendantFolders": 0,
        "sha": sha,
    }
    if size is not None:
        n["size"] = size
    return n


def build_tree_from_paths(
    blobs: list[dict[str, Any]],
    *,
    root_name: str = "root",
) -> dict[str, Any]:
    """Build nested Integration-Registry-style JSON from flat blob rows.

    Each blob dict: ``{"path": str, "sha": str, "size": int|None}``.
    """
    root = _empty_tree_node(root_name, "")

    for row in sorted(blobs, key=lambda r: r["path"]):
        path = row["path"]
        sha = row.get("sha", "")
        size = row.get("size")
        if not path:
            continue
        parts = path.split("/")
        parent = root
        acc: list[str] = []
        for i, seg in enumerate(parts):
            acc.append(seg)
            rel = "/".join(acc)
            is_leaf = i == len(parts) - 1
            ch = parent["children"]
            if is_leaf:
                ch[seg] = _blob_node(seg, rel, sha, size)
            else:
                if seg not in ch:
                    ch[seg] = _empty_tree_node(seg, rel)
                parent = ch[seg]
    _recompute_descendants(root)
    return root


def _recompute_descendants(node: dict[str, Any]) -> tuple[int, int]:
    """Returns (descendantFiles, descendantFolders) for subtree under node."""
    if node["type"] == "blob":
        return 0, 0
    d_files = 0
    d_folders = 0
    for child in node["children"].values():
        cf, cdir = _recompute_descendants(child)
        d_files += cf
        d_folders += cdir
        if child["type"] == "blob":
            d_files += 1
        else:
            d_folders += 1
    node["descendantFiles"] = d_files
    node["descendantFolders"] = d_folders
    return d_files, d_folders


def _filter_by_prefix(blobs: list[dict[str, Any]], prefix: Optional[str]) -> list[dict[str, Any]]:
    if not prefix:
        return blobs
    p = prefix.strip().strip("/")
    if not p:
        return blobs
    out = []
    plen = len(p) + 1
    for b in blobs:
        path = b["path"]
        if path == p:
            continue
        if path.startswith(p + "/"):
            out.append({**b, "path": path[plen:]})
        elif path == p and b.get("type") == "blob":
            out.append(b)
    return out


def suggest_integration_roots(tree: dict[str, Any]) -> dict[str, Any]:
    """Heuristic hints for Integration-Registry-style layouts (Providers, Internal, etc.)."""
    children = tree.get("children") or {}
    hints: dict[str, Any] = {"likely_provider_roots": [], "registry_json_paths": []}

    def walk(n: dict[str, Any], base: str) -> None:
        name = n.get("name", "")
        path = n.get("path", "")
        typ = n.get("type", "")
        if typ != "tree":
            if name.lower() == "registry.json" or path.endswith("Internal/Registry.json"):
                hints["registry_json_paths"].append(path)
            return
        rel = path or name
        if name in ("Providers", "Provider", "integrations", "Integrations"):
            hints["likely_provider_roots"].append(rel)
        for c in (n.get("children") or {}).values():
            walk(c, base)

    walk(tree, "")
    if "Providers" in children and "Providers" not in hints["likely_provider_roots"]:
        hints["likely_provider_roots"].append("Providers")
    return hints


def build_discovery_stats(
    tree: dict[str, Any],
    blobs: list[dict[str, Any]],
    *,
    duration_seconds: float,
    api_strategy: str,
    tech_stack: Optional[list[str]] = None,
    smart_summaries: Optional[list[dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Aggregate operational metrics for agent scale/latency decisions."""
    total_size_bytes = 0
    for b in blobs:
        s = b.get("size")
        if s is None:
            continue
        try:
            total_size_bytes += int(s)
        except (TypeError, ValueError):
            continue
    stats: dict[str, Any] = {
        "duration_seconds": float(duration_seconds),
        "total_files": int(tree.get("descendantFiles", 0)),
        "total_folders": int(tree.get("descendantFolders", 0)),
        "total_size_bytes": total_size_bytes,
        "api_strategy": api_strategy,
        "tech_stack": list(tech_stack or []),
    }
    if smart_summaries:
        stats["smart_summaries"] = smart_summaries
    return stats


def persist_discovery_map(tree: dict[str, Any], output_file: str) -> str:
    """Write ``tree`` as UTF-8 JSON with ``indent=2`` for human inspection.

    Sets ``tree["saved_to"]`` to the resolved absolute path (also present in the file).
    Returns that resolved path.
    """
    raw = (output_file or "").strip()
    if not raw:
        raise GitHubDiscoveryError("output_file is empty.")
    path = Path(raw).expanduser()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        resolved = str(path.resolve())
        tree["saved_to"] = resolved
        with path.open("w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise GitHubDiscoveryError(f"Could not write discovery map to {raw!r}: {e}") from e
    return resolved


def _default_markdown_path(output_file: str) -> str:
    p = Path(output_file.strip()).expanduser()
    return str(p.with_name(f"{p.stem}_nav.md"))


def _resolve_markdown_export_path(
    output_file: Optional[str],
    markdown_file: Optional[str],
) -> Optional[str]:
    """Explicit ``markdown_file`` overrides; empty string disables; else derive from JSON path."""
    if markdown_file is not None:
        s = str(markdown_file).strip()
        return s if s else None
    if output_file and str(output_file).strip():
        return _default_markdown_path(str(output_file).strip())
    return None


def render_navigation_markdown(tree: dict[str, Any]) -> str:
    """Condensed Markdown table of immediate children of the map root for quick scanning."""
    meta = tree.get("repo") or {}
    owner = meta.get("owner", "")
    name = meta.get("name", "")
    sha_full = meta.get("commit_sha") or ""
    sha = sha_full[:7] if sha_full else ""
    lines = [
        "# Repository navigation (top level)",
        "",
        f"**{owner}/{name}** `{sha}`",
        "",
        "| Name | Type | Subfiles | Subfolders | Size (bytes) |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    children = tree.get("children") or {}
    for key in sorted(children.keys()):
        node = children[key]
        typ = node.get("type", "")
        esc = key.replace("|", "\\|")
        if typ == "tree":
            lines.append(
                f"| `{esc}` | directory | {node.get('descendantFiles', 0)} | "
                f"{node.get('descendantFolders', 0)} | — |"
            )
        else:
            sz = node.get("size", "")
            lines.append(f"| `{esc}` | file | — | — | {sz!s} |")
    lines.append("")
    lines.append("_Generated by Github-Discovery._")
    return "\n".join(lines)


def persist_navigation_markdown(tree: dict[str, Any], markdown_file: str) -> str:
    """Write :func:`render_navigation_markdown` output to disk; returns resolved path."""
    raw = (markdown_file or "").strip()
    if not raw:
        raise GitHubDiscoveryError("markdown_file is empty.")
    path = Path(raw).expanduser()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        resolved = str(path.resolve())
        body = render_navigation_markdown(tree)
        with path.open("w", encoding="utf-8") as f:
            f.write(body)
    except OSError as e:
        raise GitHubDiscoveryError(f"Could not write navigation markdown to {raw!r}: {e}") from e
    return resolved


async def _github_request(
    client: Any,
    method: str,
    path: str,
    *,
    headers: dict[str, str],
    params: Optional[dict[str, str]] = None,
) -> Any:
    url = f"{GITHUB_API}{path}"
    r = await client.request(method, url, headers=headers, params=params, timeout=60.0)
    if r.status_code == 403:
        raise GitHubDiscoveryError(
            "GitHub API returned 403 (rate limit or forbidden). "
            "Set GITHUB_TOKEN in the environment."
        )
    if r.status_code == 404:
        raise GitHubDiscoveryError(f"GitHub API 404 for {path}: {r.text[:200]}")
    if r.status_code != 200:
        raise GitHubDiscoveryError(f"GitHub API {r.status_code} for {path}: {r.text[:300]}")
    return r.json()


async def _fetch_blob_text_preview(
    client: Any,
    owner: str,
    repo: str,
    file_sha: str,
    headers: dict[str, str],
    *,
    max_chars: int = 500,
) -> str:
    """Decode up to ``max_chars`` UTF-8 text from a git blob (base64 from GitHub API)."""
    if not file_sha:
        return ""
    data = await _github_request(
        client,
        "GET",
        f"/repos/{owner}/{repo}/git/blobs/{file_sha}",
        headers=headers,
    )
    enc = data.get("encoding")
    raw = data.get("content")
    if not isinstance(raw, str):
        return ""
    if enc == "base64":
        try:
            decoded = base64.b64decode(raw)
        except (ValueError, TypeError):
            return ""
    else:
        decoded = raw.encode("utf-8", errors="replace")
    return decoded.decode("utf-8", errors="replace")[:max_chars]


async def collect_smart_summaries(
    client: Any,
    owner: str,
    repo: str,
    blobs: list[dict[str, Any]],
    headers: dict[str, str],
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Fetch short text previews for the highest-importance files (README, Registry, etc.)."""
    scored: list[tuple[int, str, str]] = []
    for b in blobs:
        path = b.get("path") or ""
        sha = b.get("sha") or ""
        if not path or not sha:
            continue
        sc = _importance_score(path)
        if sc <= 0:
            continue
        scored.append((sc, path, sha))
    scored.sort(key=lambda x: (-x[0], x[1]))
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for sc, path, sha in scored:
        if path in seen:
            continue
        seen.add(path)
        preview = await _fetch_blob_text_preview(
            client, owner, repo, sha, headers, max_chars=500
        )
        out.append(
            {
                "path": path,
                "sha": sha,
                "content_preview": preview,
                "importance_score": sc,
            }
        )
        if len(out) >= limit:
            break
    return out


async def _resolve_commit_sha(
    client: Any,
    owner: str,
    repo: str,
    ref: str,
    headers: dict[str, str],
) -> str:
    data = await _github_request(
        client,
        "GET",
        f"/repos/{owner}/{repo}/commits/{ref}",
        headers=headers,
    )
    sha = data.get("sha")
    if not sha:
        raise GitHubDiscoveryError(f"No commit sha for ref {ref!r}")
    return sha


async def _default_branch(client: Any, owner: str, repo: str, headers: dict[str, str]) -> str:
    data = await _github_request(client, "GET", f"/repos/{owner}/{repo}", headers=headers)
    b = data.get("default_branch")
    if not b:
        raise GitHubDiscoveryError("Could not read default_branch from repo metadata.")
    return b


async def _commit_tree_sha(
    client: Any,
    owner: str,
    repo: str,
    commit_sha: str,
    headers: dict[str, str],
) -> str:
    data = await _github_request(
        client,
        "GET",
        f"/repos/{owner}/{repo}/git/commits/{commit_sha}",
        headers=headers,
    )
    tree = data.get("tree") or {}
    sha = tree.get("sha")
    if not sha:
        raise GitHubDiscoveryError("Commit payload missing tree.sha.")
    return sha


async def _fetch_tree_recursive_flat(
    client: Any,
    owner: str,
    repo: str,
    tree_sha: str,
    headers: dict[str, str],
) -> tuple[list[dict[str, Any]], bool]:
    """Return (blob_rows, truncated_flag)."""
    data = await _github_request(
        client,
        "GET",
        f"/repos/{owner}/{repo}/git/trees/{tree_sha}",
        headers=headers,
        params={"recursive": "1"},
    )
    truncated = bool(data.get("truncated"))
    blobs: list[dict[str, Any]] = []
    for item in data.get("tree") or []:
        if item.get("type") == "blob":
            blobs.append(
                {
                    "path": item["path"],
                    "sha": item.get("sha", ""),
                    "size": item.get("size"),
                }
            )
    return blobs, truncated


async def _fetch_tree_bfs_flat(
    client: Any,
    owner: str,
    repo: str,
    root_tree_sha: str,
    headers: dict[str, str],
    *,
    max_tree_nodes: int,
) -> list[dict[str, Any]]:
    """Walk git trees without recursive=1 (handles truncated large repos)."""
    blobs: list[dict[str, Any]] = []
    queue: list[tuple[str, str]] = [(root_tree_sha, "")]
    seen_trees = 0
    while queue:
        sha, prefix = queue.pop(0)
        seen_trees += 1
        if seen_trees > max_tree_nodes:
            raise GitHubDiscoveryError(
                f"Exceeded max_tree_nodes={max_tree_nodes} while walking git trees."
            )
        data = await _github_request(
            client,
            "GET",
            f"/repos/{owner}/{repo}/git/trees/{sha}",
            headers=headers,
        )
        for item in data.get("tree") or []:
            name = item.get("path") or ""
            typ = item.get("type")
            item_sha = item.get("sha")
            full = f"{prefix}/{name}" if prefix else name
            if typ == "blob" and item_sha:
                blobs.append(
                    {
                        "path": full,
                        "sha": item_sha,
                        "size": item.get("size"),
                    }
                )
            elif typ == "tree" and item_sha:
                queue.append((item_sha, full))
    return blobs


async def discover_repository_async(
    url_or_repo: str,
    *,
    ref: Optional[str] = None,
    path_prefix: Optional[str] = None,
    max_tree_nodes: int = 50_000,
    token: Optional[str] = None,
    output_file: Optional[str] = None,
    markdown_file: Optional[str] = None,
) -> dict[str, Any]:
    """Async: fetch repo tree and return structured JSON (Integration-Registry compatible).

    Parameters
    ----------
    url_or_repo
        GitHub HTTPS URL, or ``owner/repo``.
    ref
        Optional branch/tag/commit (overrides ref embedded in URL).
    path_prefix
        Only include paths under this directory (relative paths in output).
    max_tree_nodes
        Safety cap when falling back to BFS tree walks.
    output_file
        If set, write the full returned tree (including ``discovery_stats``) as JSON
        with ``indent=2`` to this path (relative paths resolve against the process cwd).
    markdown_file
        If a non-empty string, write the navigation Markdown table there.
        If ``None`` and ``output_file`` ends with ``.json``, a sibling ``*_nav.md`` is written.
        Pass ``""`` to skip Markdown when ``output_file`` is set.
    """
    try:
        import httpx
    except ImportError as e:
        raise GitHubDiscoveryError(
            "The httpx package is required for GitHub discovery. "
            "Install with: pip install httpx"
        ) from e

    t0 = time.perf_counter()
    parsed = parse_github_url(url_or_repo)
    owner, repo = parsed.owner, parsed.repo
    eff_ref = ref or parsed.ref
    eff_prefix = path_prefix if path_prefix is not None else parsed.path_prefix

    tok = token if token is not None else os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "posthog-llma-discovery",
    }
    if tok:
        headers["Authorization"] = f"Bearer {tok}"

    api_strategy = "recursive"
    tech_stack: list[str] = []
    summaries: list[dict[str, Any]] = []
    async with httpx.AsyncClient() as client:
        if eff_ref:
            commit_sha = await _resolve_commit_sha(client, owner, repo, eff_ref, headers)
        else:
            branch = await _default_branch(client, owner, repo, headers)
            commit_sha = await _resolve_commit_sha(client, owner, repo, branch, headers)

        root_tree_sha = await _commit_tree_sha(client, owner, repo, commit_sha, headers)
        blobs, truncated = await _fetch_tree_recursive_flat(
            client, owner, repo, root_tree_sha, headers
        )
        if truncated:
            api_strategy = "bfs_fallback"
            blobs = await _fetch_tree_bfs_flat(
                client,
                owner,
                repo,
                root_tree_sha,
                headers,
                max_tree_nodes=max_tree_nodes,
            )

        blobs = _filter_by_prefix(blobs, eff_prefix)
        blobs = filter_discovery_noise(blobs)
        tech_stack = detect_tech_stack(blobs)
        summaries = await collect_smart_summaries(
            client, owner, repo, blobs, headers, limit=5
        )

    tree = build_tree_from_paths(blobs)
    tree["repo"] = {"owner": owner, "name": repo, "commit_sha": commit_sha, "ref": eff_ref}
    tree["integration_hints"] = suggest_integration_roots(tree)
    elapsed = time.perf_counter() - t0
    tree["discovery_stats"] = build_discovery_stats(
        tree,
        blobs,
        duration_seconds=elapsed,
        api_strategy=api_strategy,
        tech_stack=tech_stack,
        smart_summaries=summaries if summaries else None,
    )
    tree["markdown_saved_to"] = None
    out_f = str(output_file).strip() if output_file else ""
    md_target = _resolve_markdown_export_path(out_f or None, markdown_file)
    if md_target:
        tree["markdown_saved_to"] = persist_navigation_markdown(tree, md_target)
    tree["saved_to"] = None
    if out_f:
        persist_discovery_map(tree, out_f)
    return tree


def discover_repository(
    url_or_repo: str,
    *,
    ref: Optional[str] = None,
    path_prefix: Optional[str] = None,
    max_tree_nodes: int = 50_000,
    token: Optional[str] = None,
    output_file: Optional[str] = None,
    markdown_file: Optional[str] = None,
) -> dict[str, Any]:
    """Sync wrapper around :func:`discover_repository_async`."""
    return asyncio.run(
        discover_repository_async(
            url_or_repo,
            ref=ref,
            path_prefix=path_prefix,
            max_tree_nodes=max_tree_nodes,
            token=token,
            output_file=output_file,
            markdown_file=markdown_file,
        )
    )
