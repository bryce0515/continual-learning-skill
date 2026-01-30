# Continual Learning Skills Marketplace

Automatically capture and curate session insights to build persistent project memory.

📊 **[View the workflow diagram](docs/continual-learning-workflow.pptx)** - Visual overview of how the system works

## Quick Start

### 1. Add the marketplace and install the skill

```bash
claude plugin marketplace add bryce0515/continual-learning-skill
claude plugin install continual-learning
```

### 2. Set up the hook in your project

**Option A: Ask Claude to do it (Recommended)**

After installing, just tell Claude:

> Set up the continual-learning hook in this project using the README from the continual-learning-marketplace plugin.

Claude will read this README and configure everything for you.

**Option B: Manual setup**

Copy these commands to set up auto-capture in your project:

```bash
# Create directories
mkdir -p .claude/hooks

# Copy the hook from the installed plugin (gets latest version)
cp "$(ls -td ~/.claude/plugins/cache/continual-learning-marketplace/continual-learning/*/continual-learning/hooks/session-end.py | head -1)" .claude/hooks/

# Create the hook configuration
cat > .claude/settings.json << 'EOF'
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
EOF

# Create the learnings file
cat > CLAUDE-learned.md << 'EOF'
# Learned Knowledge

> Auto-captured session learnings. Review periodically and promote valuable insights to CLAUDE.md.
>
> **Last curated**: (not yet curated)

## Recent Sessions

<!-- New entries are prepended below this line -->

---

## Consolidated Learnings

<!-- Patterns that emerge across multiple sessions -->

## Archived

<!-- Older learnings moved here after review -->
EOF
```

### 3. Start using it

The hook runs automatically after each session. Use these commands to manage learnings:

| Command | Purpose |
|---------|---------|
| `/learn` | Analyze current session |
| `/learn review` | Curate pending entries |
| `/learn promote` | Move insights to CLAUDE.md |
| `/learn organize` | Check CLAUDE.md structure |
| `/learn search <topic>` | Search knowledge base |

---

## What It Does

```
session-end.py (hook)     /learn (skill)          CLAUDE.md
       │                         │                      │
       │ Auto-captures           │ Deep analysis        │ Permanent
       │ stub entries            │ and curation         │ knowledge
       ▼                         ▼                      ▼
   ┌─────────────────────────────────────────────────────────┐
   │                    CLAUDE-learned.md                    │
   │  Recent Sessions → Consolidated → Archived/Promoted     │
   └─────────────────────────────────────────────────────────┘
```

- **Automatic capture**: SessionEnd hook extracts metadata (files edited, commits, tool usage) from every session
- **Manual curation**: `/learn` commands let you review, consolidate, and promote insights
- **Scaling support**: `/learn organize` helps keep CLAUDE.md well-structured as knowledge grows

## How It Works

1. **SessionEnd hook** runs automatically after each Claude Code session
2. Extracts: topics, files modified, git commits, tool usage counts
3. Creates a stub entry in `CLAUDE-learned.md`
4. Run `/learn review` periodically to:
   - Upgrade valuable stubs to full analyzed entries
   - Archive low-value sessions
   - Promote stable knowledge to `CLAUDE.md`

## Windows Setup

On Windows (PowerShell), use these commands instead:

```powershell
# Create directories
New-Item -ItemType Directory -Force -Path .claude\hooks

# Copy the hook (gets latest version)
$hookDir = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\continual-learning-marketplace\continual-learning" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item "$($hookDir.FullName)\continual-learning\hooks\session-end.py" -Destination .claude\hooks\

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
'@ | Set-Content .claude\settings.json

# Create CLAUDE-learned.md
@'
# Learned Knowledge

> Auto-captured session learnings. Review periodically and promote valuable insights to CLAUDE.md.
>
> **Last curated**: (not yet curated)

## Recent Sessions

<!-- New entries are prepended below this line -->

---

## Consolidated Learnings

<!-- Patterns that emerge across multiple sessions -->

## Archived

<!-- Older learnings moved here after review -->
'@ | Set-Content CLAUDE-learned.md
```

## License

MIT
