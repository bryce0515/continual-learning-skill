#!/usr/bin/env python3
"""
SessionEnd hook for continual learning.

Captures session metadata and appends a stub entry to CLAUDE-learned.md.
Reads session info from stdin (JSON) and extracts summaries from transcript.

Enhanced extraction:
- Tool usage counts (Edit, Write, Bash, MCP tools, etc.)
- Files edited/created (from Edit/Write tool calls)
- Git commits (from Bash commands containing 'git commit')

Exit codes:
- 0: Always (to not block session end)

Errors are logged to stderr but don't prevent session from ending.
"""

import json
import os
import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Portable debug log path
DEBUG_LOG = Path(tempfile.gettempdir()) / "claude-session-end.log"
DEBUG = os.environ.get("CLAUDE_HOOK_DEBUG", "").lower() in ("1", "true")


def log_debug(message: str) -> None:
    """Append debug message to temp log file (only when DEBUG enabled)."""
    if not DEBUG:
        return
    try:
        with open(DEBUG_LOG, "a") as f:
            f.write(f"{datetime.now()}: {message}\n")
    except Exception:
        pass  # Don't fail hook if debug logging fails


def extract_summaries_from_transcript(transcript_path: str) -> list[dict]:
    """Extract summary entries from a transcript JSONL file."""
    summaries = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "summary":
                        summaries.append(entry)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, IOError) as e:
        print(f"Warning: Could not read transcript: {e}", file=sys.stderr)
    return summaries


def extract_key_topics_from_transcript(transcript_path: str) -> list[str]:
    """Extract key topics from assistant messages in transcript."""
    topics = set()
    keywords = [
        "implement",
        "fix",
        "create",
        "update",
        "refactor",
        "add",
        "remove",
        "debug",
        "test",
        "deploy",
        "configure",
        "optimize",
        "migrate",
    ]

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    # Look for assistant messages
                    if entry.get("type") == "assistant":
                        message = entry.get("message", {})
                        content = message.get("content", [])
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text = block.get("text", "").lower()
                                for kw in keywords:
                                    if kw in text:
                                        topics.add(kw)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, IOError):
        pass

    return list(topics)[:5]  # Limit to 5 topics


def extract_commit_message(cmd: str) -> str:
    """Extract commit message from a git commit command."""
    # Try heredoc style first: -m "$(cat <<'EOF'\nmessage\nEOF)"
    # This needs to be checked before simple -m patterns
    heredoc_match = re.search(r"<<'?EOF'?\n(.+?)(?:\n\s*Co-Authored|\nEOF)", cmd, re.DOTALL)
    if heredoc_match:
        msg = heredoc_match.group(1).strip().split("\n")[0]  # First line only
        return msg[:60]

    # Try -m "message" or -m 'message' (simple single-line case)
    m_match = re.search(r'-m\s+["\']([^"\']+)["\']', cmd)
    if m_match:
        return m_match.group(1)[:60]  # Truncate long messages

    return "(commit message not parsed)"


def extract_tool_usage(transcript_path: str) -> dict:
    """
    Extract tool calls, file edits, and git commits from transcript.

    Returns dict with:
        - tools: dict of tool_name -> count
        - files_edited: list of unique filenames edited
        - files_created: list of unique filenames created
        - git_commits: list of commit messages
    """
    tools_used = {}
    files_edited = set()
    files_created = set()
    git_commits = []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("type") == "assistant":
                        message = entry.get("message", {})
                        content = message.get("content", [])
                        for block in content:
                            if isinstance(block, dict) and block.get("type") == "tool_use":
                                name = block.get("name", "")
                                inp = block.get("input", {})

                                # Count tool usage
                                tools_used[name] = tools_used.get(name, 0) + 1

                                # Extract file operations
                                if name == "Write":
                                    fp = inp.get("file_path", "")
                                    if fp:
                                        files_created.add(Path(fp).name)
                                elif name == "Edit":
                                    fp = inp.get("file_path", "")
                                    if fp:
                                        files_edited.add(Path(fp).name)
                                elif name == "Bash":
                                    cmd = inp.get("command", "")
                                    if "git commit" in cmd and "-m" in cmd:
                                        msg = extract_commit_message(cmd)
                                        if msg and msg not in git_commits:
                                            git_commits.append(msg)
                except json.JSONDecodeError:
                    continue
    except (FileNotFoundError, PermissionError, IOError) as e:
        print(f"Warning: Could not read transcript for tool usage: {e}", file=sys.stderr)

    # Remove files from edited if they were created (Write overwrites Edit)
    files_edited -= files_created

    return {
        "tools": tools_used,
        "files_edited": sorted(files_edited),
        "files_created": sorted(files_created),
        "git_commits": git_commits,
    }


def format_tools_summary(tools: dict) -> str:
    """Format tool usage into a compact summary string."""
    if not tools:
        return "none"

    # Group MCP tools together
    mcp_count = sum(v for k, v in tools.items() if k.startswith("mcp__"))
    core_tools = {k: v for k, v in tools.items() if not k.startswith("mcp__")}

    parts = []
    # Show key tools first
    priority_tools = ["Edit", "Write", "Read", "Bash", "Glob", "Grep", "Task"]
    for tool in priority_tools:
        if tool in core_tools:
            parts.append(f"{tool}({core_tools[tool]})")

    # Add MCP summary if any
    if mcp_count > 0:
        parts.append(f"MCP({mcp_count})")

    return ", ".join(parts) if parts else "minimal"


def format_learned_entry(
    session_id: str, transcript_path: str, cwd: str, summaries: list[dict], topics: list[str], tool_usage: dict | None = None
) -> str:
    """Format a markdown entry for CLAUDE-learned.md."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Get the most recent summary if available
    summary_text = "Session completed (no summary available)"
    if summaries:
        latest = summaries[-1]
        summary_text = latest.get("summary", summary_text)

    # Format topics
    topics_str = ", ".join(topics) if topics else "general work"

    # Build entry lines
    lines = [
        "",
        f"### {timestamp} - Session `{session_id[:8]}...`",
        "",
        f"**Topics**: {topics_str}",
    ]

    # Add tool usage details if available
    if tool_usage:
        files_edited = tool_usage.get("files_edited", [])
        files_created = tool_usage.get("files_created", [])
        git_commits = tool_usage.get("git_commits", [])
        tools = tool_usage.get("tools", {})

        # Files modified (combine edited and created)
        all_files = []
        if files_edited:
            all_files.extend(f"`{f}`" for f in files_edited[:5])  # Limit to 5
        if files_created:
            all_files.extend(f"`{f}` (new)" for f in files_created[:3])  # Limit to 3
        if all_files:
            lines.append(f"**Files**: {', '.join(all_files)}")

        # Git commits
        if git_commits:
            commits_str = "; ".join(f'"{c}"' for c in git_commits[:3])  # Limit to 3
            lines.append(f"**Commits**: {commits_str}")

        # Tools summary
        tools_str = format_tools_summary(tools)
        if tools_str != "none":
            lines.append(f"**Tools**: {tools_str}")

    lines.extend(["", f"**Summary**: {summary_text}", "", f"**Transcript**: `{transcript_path}`", "", "---", ""])

    return "\n".join(lines)


def prepend_to_learned_file(entry: str, project_dir: str) -> bool:
    """Prepend entry to CLAUDE-learned.md after the marker line."""
    learned_path = Path(project_dir) / "CLAUDE-learned.md"
    marker = "<!-- New entries are prepended below this line -->"

    try:
        if not learned_path.exists():
            print(f"Warning: {learned_path} does not exist", file=sys.stderr)
            return False

        content = learned_path.read_text(encoding="utf-8")

        if marker not in content:
            print(f"Warning: Marker not found in {learned_path}", file=sys.stderr)
            return False

        # Insert entry after the marker
        new_content = content.replace(marker, marker + entry)
        learned_path.write_text(new_content, encoding="utf-8")
        return True

    except (IOError, PermissionError) as e:
        print(f"Warning: Could not write to {learned_path}: {e}", file=sys.stderr)
        return False


def auto_commit_changes(project_dir: str) -> bool:
    """Optionally auto-commit changes to CLAUDE-learned.md."""
    import subprocess

    learned_file = "CLAUDE-learned.md"

    try:
        # Check if file has changes
        result = subprocess.run(["git", "diff", "--quiet", learned_file], cwd=project_dir, capture_output=True)

        if result.returncode == 0:
            # No changes
            return False

        # Stage and commit
        subprocess.run(["git", "add", learned_file], cwd=project_dir, capture_output=True, check=True)

        subprocess.run(
            ["git", "commit", "-m", "chore: auto-capture session learnings"], cwd=project_dir, capture_output=True, check=True
        )

        return True

    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Warning: Auto-commit failed: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    log_debug("Hook invoked")

    try:
        # Read session metadata from stdin
        stdin_data = sys.stdin.read()
        log_debug(f"stdin_data: {stdin_data[:500] if stdin_data else '(empty)'}")

        if not stdin_data.strip():
            print("No session data received", file=sys.stderr)
            return 0

        session_info = json.loads(stdin_data)

        # Extract fields
        session_id = session_info.get("session_id", "unknown")
        transcript_path = session_info.get("transcript_path", "")
        cwd = session_info.get("cwd", os.getcwd())

        # Get project directory from environment or cwd
        project_dir = os.environ.get("CLAUDE_PROJECT_DIR", cwd)

        # Skip if no transcript
        if not transcript_path or not Path(transcript_path).exists():
            print(f"No transcript found at: {transcript_path}", file=sys.stderr)
            return 0

        # Extract information from transcript
        summaries = extract_summaries_from_transcript(transcript_path)
        topics = extract_key_topics_from_transcript(transcript_path)
        tool_usage = extract_tool_usage(transcript_path)

        # Format and write entry
        entry = format_learned_entry(session_id, transcript_path, cwd, summaries, topics, tool_usage)

        if prepend_to_learned_file(entry, project_dir):
            print(f"Added learning entry for session {session_id[:8]}", file=sys.stderr)
            log_debug(f"SUCCESS: Added entry for {session_id[:8]}")

            # Optional: auto-commit (disabled by default, uncomment to enable)
            # if auto_commit_changes(project_dir):
            #     print("Auto-committed changes", file=sys.stderr)
        else:
            log_debug("FAILED: Could not write entry")

        return 0

    except json.JSONDecodeError as e:
        print(f"Failed to parse session data: {e}", file=sys.stderr)
        log_debug(f"ERROR: JSON decode failed: {e}")
        return 0  # Don't block session end
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        log_debug(f"ERROR: {e}")
        return 0  # Don't block session end


if __name__ == "__main__":
    sys.exit(main())
