#!/usr/bin/env python3
"""Updates README.md with live counts of merged external PRs/repos and a
recent-merges feed, pulled via gh CLI.

Cheap-checks unread notifications where reason == "author" first; only
runs the full scan (and rewrites README) if something author-relevant
showed up since the last run. Marks notifications read afterward.
"""

import json
import subprocess
import sys
from pathlib import Path

USERNAME = "1HazyOne707"
README = Path(__file__).resolve().parent.parent / "README.md"
STATS_START, STATS_END = "<!-- STATS:START -->", "<!-- STATS:END -->"
RECENT_START, RECENT_END = "<!-- RECENT:START -->", "<!-- RECENT:END -->"
RECENT_COUNT = 5
NL = chr(10)


def run(args):
    return subprocess.run(args, capture_output=True, text=True, check=True)


def author_notifications():
    result = run(["gh", "api", "notifications"])
    try:
        items = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        items = []
    return [n for n in items if n.get("reason") == "author"]


def mark_notifications_read():
    subprocess.run(["gh", "api", "-X", "PUT", "notifications"],
                    capture_output=True, text=True)


def gh_merged_prs():
    """Full merged-PR data: repo, number, title, closedAt, url -- used for
    both the stats count and the recent-activity feed."""
    result = run([
        "gh", "search", "prs", "--author=" + USERNAME, "--merged",
        "--limit", "200", "--json", "repository,number,title,closedAt,url",
    ])
    return json.loads(result.stdout)


def confirm_still_merged(pr):
    """Notifications can fire on close-without-merge too; verify the real
    state via the PR own API before trusting it."""
    try:
        result = run(["gh", "pr", "view", pr["url"], "--json", "state"])
        return json.loads(result.stdout).get("state") == "MERGED"
    except subprocess.CalledProcessError:
        return False


def replace_between(text, start, end, block):
    if start not in text or end not in text:
        print("Markers " + start + "/" + end + " not found.", file=sys.stderr)
        sys.exit(1)
    pre = text.split(start)[0]
    post = text.split(end)[1]
    return pre + start + NL + block + NL + end + post


def update_readme(all_prs):
    external = [p for p in all_prs
                if not p["repository"]["nameWithOwner"].startswith(USERNAME + "/")]
    repo_count = len({p["repository"]["nameWithOwner"] for p in external})
    pr_count = len(external)

    stats_block = (
        "- **Merged external PRs:** " + str(pr_count) + NL +
        "- **External repositories contributed to:** " + str(repo_count)
    )

    recent = sorted(external, key=lambda p: p["closedAt"], reverse=True)[:RECENT_COUNT]
    recent_lines = [
        "- [" + p["repository"]["nameWithOwner"] + " #" + str(p["number"]) + "](" + p["url"] + "): " + p["title"]
        for p in recent
    ] or ["(none yet)"]
    recent_block = NL.join(recent_lines)

    text = README.read_text()
    text = replace_between(text, STATS_START, STATS_END, stats_block)
    text = replace_between(text, RECENT_START, RECENT_END, recent_block)

    old_text = README.read_text()
    if text != old_text:
        README.write_text(text)
        print("Updated: " + str(pr_count) + " merged PRs across " + str(repo_count) + " repos.")
        return True
    print("No change.")
    return False


def main():
    force = "--force" in sys.argv
    notifs = author_notifications() if not force else None

    if not force and not notifs:
        print("No author-relevant notifications -- skipping scan.")
        return

    all_prs = gh_merged_prs()

    if notifs:
        for n in notifs[:5]:
            url = n.get("subject", {}).get("url", "")
            if "/pulls/" in url:
                num = url.rstrip("/").split("/")[-1]
                match = next((p for p in all_prs if str(p["number"]) == num), None)
                if match:
                    confirm_still_merged(match)

    changed = update_readme(all_prs)
    mark_notifications_read()
    if not changed:
        print("Notifications cleared; no README change needed.")


if __name__ == "__main__":
    main()
