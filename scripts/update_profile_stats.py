#!/usr/bin/env python3
"""Updates README.md with live counts of merged external PRs and repos,
pulled via the gh CLI. Runs daily via .github/workflows/profile-stats.yml."""

import json
import subprocess
import sys
from pathlib import Path

USERNAME = "1HazyOne707"
README = Path(__file__).resolve().parent.parent / "README.md"
START_MARKER = "<!-- STATS:START -->"
END_MARKER = "<!-- STATS:END -->"


def gh_json(args):
    result = subprocess.run(
        ["gh", *args, "--json", "repository", "--jq",
         ".[] | .repository.nameWithOwner"],
        capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def main():
    merged = gh_json([
        "search", "prs", f"--author={USERNAME}", "--merged", "--limit", "200",
    ])
    external = [r for r in merged if not r.startswith(f"{USERNAME}/")]
    external_repo_count = len(set(external))
    external_pr_count = len(external)

    stats_block = (
        f"{START_MARKER}\n"
        f"- **Merged external PRs:** {external_pr_count}\n"
        f"- **External repositories contributed to:** {external_repo_count}\n"
        f"{END_MARKER}"
    )

    text = README.read_text()
    if START_MARKER not in text or END_MARKER not in text:
        print(f"Markers not found in {README} — add {START_MARKER} / {END_MARKER} first.", file=sys.stderr)
        sys.exit(1)

    pre = text.split(START_MARKER)[0]
    post = text.split(END_MARKER)[1]
    new_text = pre + stats_block + post

    if new_text != text:
        README.write_text(new_text)
        print(f"Updated: {external_pr_count} merged PRs across {external_repo_count} repos.")
    else:
        print("No change.")


if __name__ == "__main__":
    main()
