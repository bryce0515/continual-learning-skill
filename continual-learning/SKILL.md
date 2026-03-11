---
name: learn
description: Analyze sessions and manage project learnings. Captures insights, updates CLAUDE-learned.md, and helps promote knowledge to CLAUDE.md.
---

# Continual Learning Skill

Manage project learnings from Claude Code sessions.

## Architecture

```
session-end.py (hook)     /learn (this skill)      CLAUDE.md
       │                         │                      │
       │ Auto-captures           │ Deep analysis        │ Permanent
       │ stub entries            │ and curation         │ knowledge
       ▼                         ▼                      ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    CLAUDE-learned.md                    │
   │  Recent Sessions → Consolidated → Archived/Promoted     │
   └─────────────────────────────────────────────────────────┘
```

- **Hook** (`session-end.py`): Auto-captures stubs for sessions with code changes (skips read-only sessions and duplicate session IDs)
- **Skill** (`/learn`): Manual deep analysis, review, and promotion

## Commands

| Invocation | Action |
|------------|--------|
| `/learn` | Analyze current session, extract insights |
| `/learn review` | Review pending stub entries in CLAUDE-learned.md |
| `/learn promote` | Move insights from CLAUDE-learned.md to CLAUDE.md |
| `/learn consolidate` | Merge similar learnings into patterns |
| `/learn organize` | Analyze CLAUDE.md structure, suggest consolidation |
| `/learn search <topic>` | Search across both memory files for topic |

> **Setup check** — Before ANY command, verify `CLAUDE-learned.md` exists in project root.
> If not, run [Setup Reference](#setup-reference) first.

## Review (`/learn review`)

1. Read `CLAUDE-learned.md`, find stubs without ✓ REVIEWED marker
2. **Auto-archive** sessions that match skip criteria (see below)
3. For remaining stubs, read the linked transcript
4. Upgrade valuable entries to analyzed format, mark ✓ REVIEWED
5. Merge duplicate session IDs into single entries
6. Update "Last curated" date

### Skip Criteria — Auto-Archive These

- No commits AND no meaningful file edits (only `.md` planning files)
- Duplicate session ID already analyzed
- Session was exploratory/research with no code outcome
- Cosmetic-only changes (formatting, style, comments)

### What Gets Promoted (Pattern From History)

Almost all promotions are **pitfalls where Claude would silently produce wrong code**. Examples:
- Default config values that cause silent wrong behavior
- Functions with generic fallbacks that silently use the wrong code path
- Non-deterministic operations (e.g., unsorted glob results)

Architecture/domain details that are **discoverable by reading code** rarely get promoted. Don't over-document things the agent can find by exploring.

## Entry Formats

### Auto-Captured Stub (from session-end hook)

```markdown
### {timestamp} - Session `{session_id}...`

**Files**: `file1.py`, `file2.py`, `new_file.py` (new)
**Commits**: "feat: add feature"; "fix: bug"
**Tools**: Edit(3), Write(1), Read(9), Bash(15)

**Summary**: {auto-extracted or "Session completed (no summary available)"}

**Transcript**: `{path to .jsonl}`

---
```

### Analyzed Entry (after /learn review)

```markdown
### {timestamp} - {brief descriptive title} ✓ REVIEWED

**Category**: pitfall|architecture|domain|workflow
**Source**: Session `{session_id}`

**Context**: {1-2 sentences: what problem, why it matters}

**Learnings**:
1. {Actionable insight}
2. {Actionable insight}

---
```

### Promoted Entry

```markdown
### {timestamp} - {title} ✓ PROMOTED

**Status**: Promoted to CLAUDE.md on {date}
...rest of entry...
```

## Promote (`/learn promote`)

**Promote when**: Claude would repeat a mistake without this knowledge. The pitfall is general (not one-off), stable (won't change soon), and not discoverable by reading the code.

**Don't promote**: Session-specific details, temporary workarounds, architecture/domain details that are discoverable by exploring the codebase.

## Organize (`/learn organize`)

Analyze CLAUDE.md for bloat. Report section sizes, flag entries >20 lines, suggest extractions to `docs/`. **Never auto-edit** — present suggestions and wait for approval.

Key principle: CLAUDE.md should be scannable by grep. If a section has too much detail, future sessions will miss context because it gets truncated. Extract deep details to `docs/` and leave a 1-2 line summary + link.

## Consolidate (`/learn consolidate`)

Merge related entries across sessions into single entries. Move to consolidated section, remove duplicates. Prefer one entry with 3 learnings over 3 entries with 1 learning each.

## Search (`/learn search <topic>`)

Search both CLAUDE.md and CLAUDE-learned.md for matching content. Return source, section, and snippet.

## Interaction Style

- Be concise — learnings should be 1-2 sentences each
- Ask before making changes to CLAUDE.md
- Archive aggressively — most sessions don't have reusable learnings
- Update "Last curated" date when reviewing

## Setup Reference

Run these commands to initialize continual-learning for a project. Return to [Commands](#commands) after setup completes.

### Detect Platform

```bash
uname -s  # Returns "Linux", "Darwin" (macOS), or fails on Windows
```

### Linux/macOS

```bash
# Create hooks directory
mkdir -p .claude/hooks

# Copy hook script from installed plugin (most recent version)
cp "$(ls -td ~/.claude/plugins/cache/continual-learning-marketplace/continual-learning/*/continual-learning/hooks/session-end.py | head -1)" .claude/hooks/

# Detect Python 3 command (handles systems where python is v2 or v3)
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is required but not found" >&2
    exit 1
fi

# Create settings.json with detected Python command
cat > .claude/settings.json << EOF
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$PYTHON_CMD .claude/hooks/session-end.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
EOF

# Create CLAUDE-learned.md with template
cat > CLAUDE-learned.md << 'EOF'
# Learned Knowledge

> Working memory for insights discovered during Claude Code sessions.
> Entries here are candidates for promotion to CLAUDE.md.

**Last curated**: (not yet curated)

## Recent Sessions

<!-- New entries are prepended below this line -->

## Consolidated Learnings

<!-- Patterns identified across multiple sessions -->

## Archived

<!-- Sessions reviewed but not containing promotable learnings -->
EOF
```

### Windows (PowerShell)

```powershell
# Create hooks directory
New-Item -ItemType Directory -Force -Path .claude\hooks

# Copy hook script (find most recent version)
$hookSource = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\continual-learning-marketplace\continual-learning\*\continual-learning\hooks\session-end.py" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item $hookSource.FullName -Destination .claude\hooks\session-end.py

# Create settings.json
@'
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/session-end.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
'@ | Set-Content -Path .claude\settings.json

# Create CLAUDE-learned.md
@'
# Learned Knowledge

> Working memory for insights discovered during Claude Code sessions.
> Entries here are candidates for promotion to CLAUDE.md.

**Last curated**: (not yet curated)

## Recent Sessions

<!-- New entries are prepended below this line -->

## Consolidated Learnings

<!-- Patterns identified across multiple sessions -->

## Archived

<!-- Sessions reviewed but not containing promotable learnings -->
'@ | Set-Content -Path CLAUDE-learned.md
```

### Verify Setup

Confirm all files exist before returning to workflow:
- `.claude/hooks/session-end.py`
- `.claude/settings.json`
- `CLAUDE-learned.md`
