# Config-Changes — log of changes to the OpenCode setup

## v2 — alignment with OpenCode v2 (2026-10-29)

### Permissions
- Removed `edit deny` on `opencode.json`: the file can be modified to update configuration.
- Removed `edit deny` on `.opencode/**` and replaced with `edit deny` specific to `.opencode/style.md`: skills, agents and `dcp.jsonc` can be created/modified, but style remains protected.
- Removed `edit deny` on `prompt/Guida_Opencode.md`: the guide can be updated.
- Removed `edit deny` on `CONFIG-CHANGES.md`: this file can be updated.
- Maintained `edit deny` on: `AGENTS.md`, `.opencode/style.md`, `prompt/prompt_chat.md`, `prompt/README.md`.

### opencode.json
- `"@azumag/opencode-rate-limit-fallback@2.1.0"` → `"@azumag/opencode-rate-limit-fallback@2.1.1"`.
- Added `"protocol": "auto"` to the `obsidian-search` MCP server.
- Added `"tools": { "obsidian-search*": "deny" }` block at global level.
- Added `"agent"` block with per-agent MCP tools: `obsidian-search*` allowed only for `notes` and `reviewer`.
- `"@opencode-ai/plugin": "1.18.34"` → `"@opencode/cli": "latest"` in `.opencode/package.json`.
- `opencode-obsidian-vault` NOT installed: redundant with the already present `obsidian-search` MCP server.

### Command (new)
- `close-note.md`: runs `check-losses.py --save`, `check-losses.py`, `vault-audit.py --breve` and `@reviewer` in sequence on a single note, returning a unified report. Report-only, does not modify anything.

### To do (not yet applied)
- Evaluate `piagentsync` (synchronize configuration between vaults). `echoes-vault-opencode` NOT added: it does not optimize tokens, rather it adds persistent context.
