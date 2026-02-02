---
name: learn
description: Analyze sessions and manage project learnings. Captures insights, updates CLAUDE-learned.md, and helps promote knowledge to CLAUDE.md.
---

# Continual Learning Skill

You are helping the user manage project learnings from Claude Code sessions.

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

- **Hook** (`session-end.py`): Runs automatically, creates stub entries with metadata
- **Skill** (`/learn`): Manual deep analysis, review, and promotion

## Commands

Parse the user's intent from how they invoked this skill:

| Invocation | Action |
|------------|--------|
| `/learn` | Analyze current session, extract insights |
| `/learn review` | Review pending stub entries in CLAUDE-learned.md |
| `/learn promote` | Move insights from CLAUDE-learned.md to CLAUDE.md |
| `/learn consolidate` | Merge similar learnings into patterns |
| `/learn organize` | Analyze CLAUDE.md structure, suggest consolidation |
| `/learn search <topic>` | Search across both memory files for topic |
| `/learn [topic]` | Focus analysis on specific topic |

## Workflow

### 0. Setup Check (Required First Step)

**Before processing ANY command**, verify setup is complete:

1. Check for `CLAUDE-learned.md` in project root
2. **If exists** → Proceed to the requested command
3. **If missing** → Run automated setup below

#### Automated Setup

Detect the platform and run the appropriate setup commands directly:

**Step 1: Detect Platform**
```bash
uname -s  # Returns "Linux", "Darwin" (macOS), or fails on Windows
```

**Step 2: Run Setup Commands**

**Linux/macOS:**
```bash
# Create hooks directory
mkdir -p .claude/hooks

# Copy hook script from installed plugin (most recent version)
cp "$(ls -td ~/.claude/plugins/cache/continual-learning-marketplace/continual-learning/*/continual-learning/hooks/session-end.py | head -1)" .claude/hooks/

# Create or update settings.json with hook configuration
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/session-end.py",
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

<!-- New session entries will be added here by the SessionEnd hook -->

## Consolidated Learnings

<!-- Patterns identified across multiple sessions -->

## Archived

<!-- Sessions reviewed but not containing promotable learnings -->
EOF
```

**Windows (PowerShell):**
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

<!-- New session entries will be added here by the SessionEnd hook -->

## Consolidated Learnings

<!-- Patterns identified across multiple sessions -->

## Archived

<!-- Sessions reviewed but not containing promotable learnings -->
'@ | Set-Content -Path CLAUDE-learned.md
```

**Step 3: Verify Setup**

After running setup, verify all files exist:
- `.claude/hooks/session-end.py`
- `.claude/settings.json`
- `CLAUDE-learned.md`

Report success to the user, then proceed with the requested command.

### 1. Analyze Current Session (`/learn`)

Read the current session's transcript and extract meaningful learnings:

1. **Find the transcript**: Look in `~/.claude/projects/*/` for recent JSONL files
2. **Extract insights**: Look for:
   - Bugs discovered and their root causes
   - Architecture decisions made
   - Domain knowledge revealed
   - Useful commands or patterns
   - Pitfalls encountered
3. **Categorize** each insight:
   - `architecture`: Code structure, patterns, design decisions
   - `domain`: Project-specific business logic knowledge
   - `workflow`: Useful processes, commands, shortcuts
   - `pitfall`: Mistakes to avoid, gotchas, edge cases
4. **Update CLAUDE-learned.md**: Add structured entries under appropriate sections

### 2. Review Pending Entries (`/learn review`)

Review auto-captured stub entries and upgrade them to analyzed entries:

1. Read `CLAUDE-learned.md`
2. Look at stub entries in "Recent Sessions" (those without ✓ REVIEWED marker)
3. For each stub entry:
   - Read the linked transcript for full context
   - Determine if it contains valuable learnings
   - Suggest which category it belongs to (architecture/domain/workflow/pitfall)
   - Decide: **analyze** (upgrade to full entry), **archive** (not useful), or **skip** (needs more sessions)
4. For entries worth keeping:
   - Upgrade from stub format to analyzed format
   - Add descriptive title, context, and learnings
   - Mark with ✓ REVIEWED
5. Update "Last curated" date in CLAUDE-learned.md header

### 3. Promote to CLAUDE.md (`/learn promote`)

1. Identify high-value learnings ready for promotion
2. Show the user what will be added to CLAUDE.md
3. Format appropriately for the existing CLAUDE.md structure
4. Move entry from CLAUDE-learned.md to CLAUDE.md
5. Mark as promoted in CLAUDE-learned.md

### 4. Consolidate Learnings (`/learn consolidate`)

1. Find similar or related entries across sessions
2. Merge into a single, comprehensive entry
3. Move to "Consolidated Learnings" section
4. Remove duplicates

### 5. Organize Memory File (`/learn organize`)

Analyze CLAUDE.md structure and suggest improvements for scaling:

1. **Parse sections**: Identify `##` headers as sections
2. **Count entries**: Each `###` sub-header or distinct content block = 1 entry
3. **Apply soft limits**:
   - Sections: 6-8 entries max
   - Entries: 15-20 lines max
4. **Generate report** with:
   - Section-by-section entry counts
   - Flagged oversized entries
   - Consolidation suggestions for similar content
   - Extraction suggestions for large standalone topics
5. **Wait for approval** before any edits

**Report format:**
```markdown
## CLAUDE.md Organization Report

### Section Analysis
| Section | Entries | Status |
|---------|---------|--------|
| Domain Knowledge | 5 | ✓ OK |
| Pitfalls | 9 | ⚠ Consider consolidating (limit: 8) |

### Long Entries
- "QA Status" (32 lines) → Consider splitting or moving to dedicated doc

### Suggested Actions
1. Consolidate entries about path handling (3 similar entries)
2. Extract "Clone Project Channel Mode Script" to `docs/clone-project.md`

Approve changes? (describe which to apply)
```

**IMPORTANT**: Do NOT auto-edit CLAUDE.md. Present suggestions and let user decide.

### 6. Search Knowledge Base (`/learn search <topic>`)

Search across both memory files to find relevant knowledge:

1. Accept topic/keyword from user
2. Search both files:
   - CLAUDE.md (permanent knowledge)
   - CLAUDE-learned.md (recent + consolidated learnings)
3. Return matches with:
   - Source file and section
   - Matching snippet (50-100 chars context)
   - Entry status (for CLAUDE-learned.md: reviewed/promoted/pending)
4. Sort by relevance (exact match > partial match)

**Output format:**
```markdown
## Search Results for "path"

### CLAUDE.md
**Domain Knowledge > Clone Project Channel Mode Script**
> Image paths in history.jsonl can be absolute or relative...

### CLAUDE-learned.md (Consolidated)
**Pitfalls > Path normalization in history.jsonl**
> Always normalize image paths to filename only...

Found 2 matches across 2 files.
```

## Entry Formats

### Auto-Captured Stub (from session-end hook)

The SessionEnd hook automatically creates stub entries with metadata extracted from the transcript:

```markdown
### {timestamp} - Session `{session_id}...`

**Topics**: fix, implement, test
**Files**: `file1.py`, `file2.py`, `new_file.py` (new)
**Commits**: "feat: add feature"; "fix: bug"
**Tools**: Edit(3), Write(1), Read(9), Bash(15), MCP(50)

**Summary**: {auto-extracted or "Session completed (no summary available)"}

**Transcript**: `{path to .jsonl}`

---
```

### Analyzed Entry (after /learn review)

When you analyze a stub entry with `/learn`, upgrade it to this richer format:

```markdown
### {timestamp} - {brief descriptive title} ✓ REVIEWED

**Category**: {architecture|domain|workflow|pitfall}
**Source**: Session `{session_id}`

**Context**: {Why this came up - the problem being solved}

**Learnings**:
1. {First insight}
2. {Second insight}

**Files created/modified**:
- `filename.py` (new) - Description
- `other_file.py` (modified) - What changed

**Evidence**: {Code snippet, command, or file:line reference}

**Transcript**: `{path}`

---
```

### Promoted Entry

When promoting to CLAUDE.md, mark the original:

```markdown
### {timestamp} - {title} ✓ PROMOTED

**Status**: Promoted to CLAUDE.md on {date}
...rest of entry...
```

## Promotion Criteria

Promote to CLAUDE.md when:
- The learning is **generally applicable** (not one-off)
- It would **save time** in future sessions
- It represents **stable knowledge** (won't change soon)
- It fills a **gap** in existing CLAUDE.md

Do NOT promote:
- Session-specific details
- Temporary workarounds
- Incomplete understanding

## Analysis Categories

### Architecture Insights
- Code organization patterns
- Module responsibilities
- Data flow between components
- Naming conventions discovered
- File location patterns

### Domain Knowledge
- Business rules embedded in code
- Data format specifics
- External system integrations
- Configuration meanings

### Workflow Patterns
- Useful command sequences
- Development shortcuts
- Testing approaches
- Debugging techniques

### Pitfalls to Avoid
- Common mistakes in this codebase
- Subtle bugs and their causes
- Misleading code patterns
- Performance gotchas

## Anti-Patterns

Avoid capturing:
- Obvious information already in CLAUDE.md
- User preferences (belongs in settings)
- Temporary debugging notes
- Incomplete explorations
- Generic programming knowledge

## Example Session Analysis

Given a session where we fixed a bug in history.jsonl path handling:

```markdown
### 2026-01-27 14:30 - Path normalization in history.jsonl

**Category**: pitfall
**Source**: Session `797c448c`

**Context**: Clone project script was failing to deduplicate records because paths in history.jsonl can be absolute or relative.

**Learning**: Always normalize image paths to filename only (`Path(img_path).name`) when comparing records from history.jsonl. The file stores paths inconsistently.

**Evidence**: `scripts/clone_project_channel_mode.py` lines 45-50

---
```

## Tools for Transcript Analysis

When reviewing sessions, use these patterns to efficiently analyze large transcripts:

### Extract user messages (understand session intent)
```bash
python << 'EOF'  # Use python3 on Linux if needed
import json
transcript = '/path/to/transcript.jsonl'
with open(transcript) as f:
    for line in f:
        entry = json.loads(line)
        if entry.get('type') == 'user':
            content = entry.get('message', {}).get('content', '')
            if isinstance(content, str) and len(content) > 10:
                print(f"USER: {content[:150]}")
EOF
```

### Extract tool usage summary
```bash
python << 'EOF'  # Use python3 on Linux if needed
import json
from collections import Counter
transcript = '/path/to/transcript.jsonl'
tools = Counter()
with open(transcript) as f:
    for line in f:
        entry = json.loads(line)
        if entry.get('type') == 'assistant':
            for block in entry.get('message', {}).get('content', []):
                if block.get('type') == 'tool_use':
                    tools[block.get('name', '')] += 1
for tool, count in tools.most_common(10):
    print(f"{tool}: {count}")
EOF
```

### Check transcript size before reading
```bash
wc -l ~/.claude/projects/*/*.jsonl | tail -10
```

### Search for specific content
```bash
grep -l "keyword" ~/.claude/projects/*/*.jsonl
```

## Interaction Style

- Be concise in summaries
- Ask before making changes to CLAUDE.md
- Show diffs for significant changes
- Preserve existing CLAUDE.md formatting
- Update "Last curated" date when reviewing

## Efficiency Tips

- **Archive aggressively**: Setup/meta sessions rarely have reusable learnings
- **Check transcript size first**: Large transcripts (>1000 lines) need sampling
- **Use user messages**: They reveal session intent faster than tool calls
- **Skip promoted entries**: Already captured, don't re-analyze
