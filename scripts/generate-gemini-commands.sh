#!/usr/bin/env bash
# Generates Gemini CLI TOML command files from Claude Code MD command files.
# The .md files are the single source of truth — this script derives .toml equivalents.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMANDS_DIR="$(cd "$SCRIPT_DIR/../commands" && pwd)"

for md_file in "$COMMANDS_DIR"/*.md; do
  [ -f "$md_file" ] || continue

  name="$(basename "$md_file" .md)"
  toml_file="$COMMANDS_DIR/${name}.toml"

  # Extract body after YAML frontmatter (skip lines between --- delimiters)
  # and skip the bare "name: xyz" line that follows the frontmatter
  body="$(awk '
    /^---$/ { fm++; next }
    fm < 2 { next }
    /^name:/ && !printed { printed=1; next }
    { printed=1; print }
  ' "$md_file")"

  # Write TOML command file
  cat > "$toml_file" <<TOML
# Auto-generated from ${name}.md — do not edit manually.
# Regenerate via: scripts/generate-gemini-commands.sh

prompt = """
${body}

User request: {{args}}
"""
TOML

done

echo "Generated $(ls "$COMMANDS_DIR"/*.toml 2>/dev/null | wc -l | tr -d ' ') TOML command files"
