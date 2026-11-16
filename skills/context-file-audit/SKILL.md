---
name: context-file-audit
description: Measures what each project's CLAUDE.md (with its @imports) costs in tokens before the first prompt, and flags the heavy ones. Use when the user asks, for example, "how big is my CLAUDE.md", "context file audit", "why is my session start so heavy", "CLAUDE.md 토큰 얼마나 먹어?".
---

# context-file-audit

Measures what each project's CLAUDE.md (with its @imports) costs in tokens before the first prompt, and flags the heavy ones. A small Python tool shipped in this plugin: standard library only, nothing to install, runs locally.

## Run

Use `python` (Windows: `py -3` also works; macOS/Linux: `python3`). On Windows add `-X utf8` if the console shows broken characters.

    python "${CLAUDE_PLUGIN_ROOT}/claude_md_audit.py" <folder-with-projects>
    python "${CLAUDE_PLUGIN_ROOT}/claude_md_audit.py" --sections <project-folder>

Run it from the user's project folder and pass the path they mean. If no path is given, ask which folder or file to check.

## Read the result

Lead with the heaviest project and its largest sections; suggest what could move out of the always-loaded file.

Show the tool's own output (shortened if long) and then a two- or three-line summary. Do not change the user's files unless they ask.
