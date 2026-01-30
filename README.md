# Continual Learning Skill for Claude Code

Automatically capture and curate session insights to build persistent project memory.

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

## Commands

| Command | Purpose |
|---------|---------|
| `/learn` | Analyze current session, extract insights |
| `/learn review` | Curate pending stub entries |
| `/learn promote` | Move valuable insights to CLAUDE.md |
| `/learn consolidate` | Merge similar learnings into patterns |
| `/learn organize` | Check CLAUDE.md structure, suggest consolidation |
| `/learn search <topic>` | Search across both memory files |

## Installation

### Via Claude Code CLI (Recommended)

```bash
claude skill add bryce0515/continual-learning-skill
```

### Manual Installation

1. Copy `SKILL.md` to `.claude/skills/continual-learning/SKILL.md` in your project
2. Copy `hooks/session-end.py` to `.claude/hooks/session-end.py`
3. Add hook configuration to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": ["python", ".claude/hooks/session-end.py"]
          }
        ]
      }
    ]
  }
}
```

4. Create `CLAUDE-learned.md` in your project root:

```markdown
# Learned Knowledge

> Auto-captured session learnings. Review periodically and promote valuable insights to CLAUDE.md.
>
> **Last curated**: YYYY-MM-DD

## Recent Sessions

<!-- New entries are prepended below this line -->

---

## Consolidated Learnings

<!-- Patterns that emerge across multiple sessions -->

## Archived

<!-- Older learnings moved here after review -->
```

## How It Works

1. **SessionEnd hook** runs automatically after each Claude Code session
2. Extracts: topics, files modified, git commits, tool usage counts
3. Creates a stub entry in `CLAUDE-learned.md`
4. Run `/learn review` periodically to:
   - Upgrade valuable stubs to full analyzed entries
   - Archive low-value sessions
   - Promote stable knowledge to `CLAUDE.md`

## Cross-Platform Support

The hook works on both Linux and Windows:
- Uses `python` (not `python3`) for Windows compatibility
- Uses relative paths instead of environment variables
- Portable temp file handling

## License

MIT
