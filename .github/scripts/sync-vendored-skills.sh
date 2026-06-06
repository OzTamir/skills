#!/usr/bin/env bash
#
# Sync every skill listed in .github/vendored-skills.json from its upstream repo.
#
# Usage:
#   sync-vendored-skills.sh            # fetch + write files, report what changed, no git ops
#   sync-vendored-skills.sh --commit   # additionally: if anything changed, bump the patch
#                                       # version of the plugin and push a commit (used by CI)
#
# Why a shared script + manifest instead of one workflow per skill: we want a single
# place that knows how to vendor any skill, so importing a new one is just a manifest
# entry — not a new pipeline to maintain.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

MANIFEST=".github/vendored-skills.json"
PLUGIN_JSON=".claude-plugin/plugin.json"
MARKETPLACE_JSON=".claude-plugin/marketplace.json"

COMMIT=0
[ "${1:-}" = "--commit" ] && COMMIT=1

command -v jq >/dev/null || { echo "::error::jq is required" >&2; exit 1; }

changed_files=()

count="$(jq '.skills | length' "$MANIFEST")"
echo "Syncing $count vendored skill(s) from $MANIFEST"

for i in $(seq 0 $((count - 1))); do
  name="$(jq -r ".skills[$i].name" "$MANIFEST")"
  repo="$(jq -r ".skills[$i].repo" "$MANIFEST")"
  ref="$(jq -r ".skills[$i].ref // \"main\"" "$MANIFEST")"
  upstream_dir="$(jq -r ".skills[$i].upstream_dir // \".\"" "$MANIFEST")"

  # Normalize the upstream path prefix so "." yields no leading segment.
  prefix=""
  [ "$upstream_dir" != "." ] && prefix="${upstream_dir%/}/"

  # Read paths into an array portably (macOS bash 3.2 has no `mapfile`).
  paths=()
  while IFS= read -r p; do paths+=("$p"); done < <(jq -r ".skills[$i].paths[]" "$MANIFEST")

  for path in "${paths[@]}"; do
    url="https://raw.githubusercontent.com/$repo/$ref/$prefix$path"
    dest="skills/$name/$path"
    tmp="$(mktemp)"

    echo "  $name: $url -> $dest"
    if ! curl --fail --silent --show-error --location "$url" -o "$tmp"; then
      echo "::error::Failed to fetch $url" >&2
      rm -f "$tmp"
      exit 1
    fi
    if [ ! -s "$tmp" ]; then
      echo "::error::$url returned an empty file" >&2
      rm -f "$tmp"
      exit 1
    fi
    # A SKILL.md without YAML frontmatter is broken — never let it overwrite a good one.
    if [ "$(basename "$path")" = "SKILL.md" ] && ! head -n1 "$tmp" | grep -q '^---'; then
      echo "::error::$url is missing YAML frontmatter; refusing to write $dest" >&2
      rm -f "$tmp"
      exit 1
    fi

    mkdir -p "$(dirname "$dest")"
    if [ ! -f "$dest" ] || ! cmp -s "$tmp" "$dest"; then
      mv "$tmp" "$dest"
      changed_files+=("$dest")
      echo "    updated."
    else
      rm -f "$tmp"
      echo "    unchanged."
    fi
  done
done

if [ "${#changed_files[@]}" -eq 0 ]; then
  echo "All vendored skills already up to date."
  exit 0
fi

echo "Changed: ${changed_files[*]}"

if [ "$COMMIT" -ne 1 ]; then
  echo "(--commit not set: leaving changes in the working tree without committing or bumping the version.)"
  exit 0
fi

# A vendored skill changed, so the installed plugin's behavior changed: bump the patch
# version in both manifests so installed users are offered the update.
cur="$(jq -r .version "$PLUGIN_JSON")"
IFS=. read -r MAJOR MINOR PATCH <<< "$cur"
new="$MAJOR.$MINOR.$((PATCH + 1))"
echo "Bumping plugin version $cur -> $new"

tmp="$(mktemp)"; jq --arg v "$new" '.version = $v' "$PLUGIN_JSON" > "$tmp" && mv "$tmp" "$PLUGIN_JSON"
tmp="$(mktemp)"; jq --arg v "$new" '.plugins[0].version = $v' "$MARKETPLACE_JSON" > "$tmp" && mv "$tmp" "$MARKETPLACE_JSON"

git config user.name  "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add "${changed_files[@]}" "$PLUGIN_JSON" "$MARKETPLACE_JSON"
git commit -m "chore: sync vendored skills from upstream (v$new)"
git push
