# Agentic Guidance

Base system prompt, onboarding kit, and benchmark framework for AI-assisted engineering at Moonsong Labs.

## Quick start

```bash
bash <(curl -sSL https://raw.githubusercontent.com/Moonsong-Labs/agentic-guidance/main/setup.sh)
```

This configures your machine for AI-assisted engineering at MSL:

1. **Prompt-Train** — connects Claude Code to MSL's proxy for monitoring and shared account pooling
2. **Core-engineering plugin** — skills for brainstorming, TDD, debugging, code review, and more
3. **MSL engineering values** — injected into every session automatically

Supports Claude Code, Cursor, and Codex. Idempotent — safe to re-run.

### How it works per platform

| Platform | Values delivery | Skills | Updates |
|---|---|---|---|
| **Claude Code** | Plugin session-start hook | Plugin marketplace | Auto-updates on session start |
| **Cursor** | Global rules file (`~/.cursor/rules/`) | Via Claude Code plugin | Re-run `setup.sh` |
| **Codex** | Plugin session-start hook (via clone) | Symlinked from clone | Re-run `setup.sh` |

> Cursor's `sessionStart` hooks from plugins [don't fire reliably](https://forum.cursor.com/t/claude-hooks-dont-work/153614) as of v2.6.x. The script uses global rules as a workaround.

### Flags

```bash
./setup.sh --install-claude    # Prompt to install Claude Code even if other tools exist
./setup.sh --help
```

## The prompt

The MSL engineering values prompt lives in [knowledge-work-plugins](https://github.com/Moonsong-Labs/knowledge-work-plugins/blob/main/core-engineering/shared/msl-engineering-values.md) (source of truth) and is distributed via the core-engineering plugin's session-start hook.

## Why values over rules

See [`benchmark/README.md`](benchmark/README.md) for the full benchmark methodology, results, and rationale.

## Repository structure

```
agentic-guidance/
├── setup.sh              <- zero-to-one installer
├── benchmark/            <- validation framework
└── README.md
```
