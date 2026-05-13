---
name: github-discovery
description: >
  Github-Discovery Skill. Use this skill to discover and map the internal structure of any GitHub repository.
  This is your primary tool for gaining codebase context and locating specific integration logic.
  Invoke when the user gives a GitHub URL or owner/repo, needs a verified file tree before reasoning about
  integrations, or you must avoid inventing paths in large provider-style layouts.
---

# Github-Discovery Skill

## Instruction

Use this skill to discover and map the internal structure of any GitHub repository. This is your primary tool for gaining codebase context and locating specific integration logic.

Prefer **ground-truth paths** from the discovery map over guessing directory names, especially when the repo mirrors an Integration Registry layout (`Providers/...`, `Internal/Registry.json`, per-provider `Analysis/` folders).

Github-Discovery is a **high-context navigation suite**: it returns a filtered tree, **stack hints**, **short previews** of the most important files, optional **JSON + Markdown** artifacts, and **operational stats** so you can plan depth before burning tokens.

## Intelligent ignore (noise reduction)

The engine **drops** paths that are rarely useful for integration or code reasoning:

- **Directory segments** (entire subtree skipped): `node_modules`, `.git`, `__pycache__`, `dist`, `build`, `.next`, `.nuxt`, `coverage`, `.venv`, `venv`, `target`.
- **Files (basename)**: `.DS_Store`, common **lockfiles** (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Pipfile.lock`, `composer.lock`, `Gemfile.lock`, `go.sum`, `Cargo.lock`, `bun.lockb`, `npm-shrinkwrap.json`, …).

Counts in `discovery_stats` and the tree reflect this filtered view (not the raw GitHub tree).

## Using `tech_stack` to adjust analysis

`discovery_stats.tech_stack` lists inferred tags from **root-level manifest files** (after filtering), for example `nodejs`, `python`, `rust`, `go`, `docker`, `compose`, `typescript`, `nextjs`, `vite`, `nuxt`, `jvm-maven`, `jvm-gradle`, `ruby`, `deno`, `pnpm-workspace`.

**How to use it**

- Treat `tech_stack` as a **routing signal**, not proof of runtime: combine with `smart_summaries` and the tree before assuming versions or frameworks.
- **Order your investigation** by stack: e.g. if `python` appears, prioritize `pyproject.toml` / `requirements.txt` branches and Python entrypoints; if `nodejs` + `typescript`, prioritize `package.json`, `tsconfig`, and `src/` TypeScript trees.
- If `tech_stack` is **empty**, fall back to README / Registry paths from `integration_hints` and `smart_summaries`, then widen with a scoped `path_prefix` discovery.
- For **polyglot** repos (many tags), split work by directory (`path_prefix`) instead of one flat analysis.

## Smart summaries (`content_preview`)

`discovery_stats.smart_summaries` (when present) lists up to **five** high-value files (README, `Internal/Registry.json`, root manifests, common entrypoints). Each item includes:

| Field | Meaning |
| ----- | ------- |
| `path` | Repository path |
| `sha` | Git blob SHA |
| `content_preview` | First **500** UTF-8 characters (decoded from the Git blob API) |
| `importance_score` | Internal ranking (higher = more central) |

Use previews to **bootstrap context** before opening full files; respect repository scale rules and do not rely on previews alone for security-sensitive conclusions.

## How to run (local, headless)

From the plugin Python package, call the registered handler (same contract an agent tool would use):

```bash
python3 -c "
from posthog_llma.parser import invoke_skill_tool_handler
import json
out = invoke_skill_tool_handler('Github-Discovery', {
  'url': 'https://github.com/org/repo',
  'ref': 'main',
  'path_prefix': 'Providers'
})
print(json.dumps(out, indent=2)[:8000])
"
```

- Set `GITHUB_TOKEN` in the environment for reliable rate limits (optional but recommended).
- Install dependency once: `pip install httpx`.

### Tool input schema (Github-Discovery)

```json
{
  "url": "https://github.com/org/repo",
  "ref": "main",
  "path_prefix": "Providers",
  "max_tree_nodes": 50000,
  "token": null,
  "output_file": "docs/maps/integration-registry.json",
  "markdown_file": null
}
```

| Field | Required | Type | Description |
| ----- | -------- | ---- | ----------- |
| `url` or `repo` | yes | string | HTTPS GitHub URL or `owner/repo` |
| `ref` | no | string | Branch, tag, or commit (overrides ref parsed from a `/tree/...` URL when provided) |
| `path_prefix` | no | string | Only map paths under this directory (output paths are relative to that prefix) |
| `max_tree_nodes` | no | integer | Safety cap when GitHub truncates very large recursive tree responses (default 50000) |
| `token` | no | string | Per-call token; otherwise `GITHUB_TOKEN` is used |
| `output_file` | no | string | If set, writes the full discovery `map` (same object as in the response) as UTF-8 JSON with `indent=2` to this path; parent directories are created. Relative paths resolve from the process working directory (typically the workspace root). |
| `markdown_file` | no | string | If a non-empty string, writes the **navigation Markdown table** there. If omitted and `output_file` ends with `.json`, a sibling `*_nav.md` is written automatically. Pass `""` to **disable** Markdown when saving JSON. |

## Best practice — persistence

For large repositories, always provide an `output_file` (for example `docs/maps/repo_name.json`). This allows the user to inspect the tree on disk and lets you reload that JSON in a future session instead of re-scanning GitHub.

On success, `map.saved_to` is the absolute path where the JSON was written (or `null` if `output_file` was omitted). The saved file includes the same top-level fields as `map`, including `saved_to`, so artifacts are self-describing.

When Markdown is emitted, `map.markdown_saved_to` holds the absolute path to the **top-level navigation table** (or `null` if skipped). The Markdown file is optimized for quick scanning: one row per immediate child of the discovery root (directory rollup counts or file sizes).

## Technical specs — JSON output

The tool returns `{"ok": true, "map": <tree>}` on success. The `map` matches an Integration-Registry-style tree:

### Node types

- **`tree`**: A directory. Has `children` (object map keyed by **segment name**), plus rollup counts.
- **`blob`**: A file. `children` is always `{}`. Includes `sha` and `size` when available from the Git API.

### Fields (every node)

| Field | Meaning |
| ----- | ------- |
| `name` | Final path segment (`root` for the synthetic root) |
| `path` | POSIX path from repo root (or relative to `path_prefix` when scoped) |
| `type` | `"tree"` or `"blob"` |
| `children` | Map of child name → child node (empty for blobs) |
| `descendantFiles` | Total **file** count in the subtree (excluding the node itself) |
| `descendantFolders` | Total **folder** count in the subtree (excluding the node itself) |

### Extra top-level metadata on `map`

- **`repo`**: `{ owner, name, commit_sha, ref }` — exact commit resolved for the request.
- **`integration_hints`**: Heuristic `likely_provider_roots` and `registry_json_paths` to align with provider-registry style repos.
- **`discovery_stats`**: Operational intelligence for scale and latency decisions, for example:

```json
{
  "duration_seconds": 0.42,
  "total_files": 120,
  "total_folders": 18,
  "total_size_bytes": 450000,
  "api_strategy": "recursive",
  "tech_stack": ["python", "nodejs"],
  "smart_summaries": [
    {
      "path": "README.md",
      "sha": "abc…",
      "content_preview": "# My project\\n…",
      "importance_score": 100
    }
  ]
}
```

`api_strategy` is `"recursive"` when the full tree came from one recursive Git trees request, or `"bfs_fallback"` when GitHub truncated that response and the engine walked subtrees (BFS).

- **`saved_to`**: Absolute path where the map was written when `output_file` was provided; otherwise `null`. The on-disk JSON matches this `map` object (including `saved_to`).
- **`markdown_saved_to`**: Absolute path to the navigation Markdown file when written; otherwise `null`.

## Handling repository scale

Before analyzing code, always check `discovery_stats` on the returned `map`.

- If `total_files` > 500 **or** `total_size_bytes` > 5242880 (5 MiB), **do not** attempt to read or ingest every file from the repository in one pass.
- Instead, issue a **follow-up** `Github-Discovery` call with `path_prefix` set to a meaningful subdirectory (for example `src/`, `lib/`, `Providers/Adobe/`, or `posthog_llma/`) so the tree and downstream reads stay within a safe token budget.
- Prefer multiple scoped discoveries over one monolithic full-repo analysis when stats indicate a large footprint.

This prevents context-window overflow and keeps token usage predictable.

## Reasoning — why use this

- **Ground truth**: Paths and folder hierarchy come from GitHub’s tree API, not from memory. That prevents hallucinated file paths when navigating complex integrations.
- **Registry alignment**: Hints surface common roots (`Providers`, `Internal/Registry.json`) so you can jump to integration docs and analysis files the way the Integration Registry is organized.
- **Scope control**: Use `path_prefix` to map only `Providers/<Vendor>/...` when the full repo is huge.
- **Navigation table**: Open or paste `markdown_saved_to` for a compact top-level view before walking deep trees in the JSON.

On failure the handler returns `{"ok": false, "error": "<message>"}` (e.g. missing `httpx`, rate limit, bad URL) — read `error` and adjust `ref`, token, or prefix before retrying.
