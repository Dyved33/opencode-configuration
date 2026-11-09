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

## v2.1 — alignment with David's vault and OpenCode 2.2.x (2026-11-09)

### opencode.json
- Added `"pool": true` to the `obsidian-search` MCP server: shared MCP connection across sessions (OpenCode 2.2.x).
- Added `{ "action": "mcp.use", "resource": "obsidian-search*", "effect": "allow" }` permission: new v2 action replacing the old `mcp:` resource prefix.

### Skills (new)
- `note-sintesi`: mandatory dense final summary `> [!info] Sintesi:` (3-6 points), no introductions or closures, no repeated information. Applied together with `note-quality` before closing a note.

### Files synchronized with David's vault
- `.opencode/style.md` (content from vault's `stile.md`): note style, single source loaded at every session.
- `.opencode/rules.md` (content from vault's `regole.md`): writing discipline, no filler text, one idea per block.
- `.opencode/dcp.jsonc`: context pruning (deduplication, error purge).
- `.opencode/rate-limit-fallback.json`: ordered zero-cost fallback chain, stops when exhausted.

### Commands and agents
- Already aligned with David's vault: `/lezione`, `/rivedi`, `/revisore`, `/revisione`, `/close-note`, `/slide`, `/dividi`, `/libro`; agents `appunti`, `revisore`, `audit`.
