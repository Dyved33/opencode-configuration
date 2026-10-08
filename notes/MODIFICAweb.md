# MODIFICA.md — web payload

Step-by-step changes to apply to the **web** opencode configuration. Each section gives an exact `before → after`; apply it in your copy and verify with `opencode` (or a JSON check for `opencode.json`).

Changes in short:
- `opencode.json`: `small_model`, `compaction`, `permission.doom_loop`
- `.opencode/agents/webdev.md`: `steps: 50`, efficiency section
- `.opencode/agents/reviewer.md`: `steps: 25`, one-line efficiency rule
- `AGENTS.md`: rule 10, stop on loops
- `.opencode/commands/audit.md`: batch the checks

**Nothing changes**: `page.md`, `preview.md`, `review.md`, `.opencode/style.md`. There is no README in the repo to update.

The web payload works with server code: `bash` stays `allow` (npm, build, tests, Playwright) and `lsp`/`formatter` stay enabled. Only the three additions below are applied.

---

## 1. `opencode.json`

Add `small_model` and `compaction` right after `instructions`, and `doom_loop` as the first key of `permission`. Replace the whole file with:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "webdev",
  "instructions": [".opencode/style.md"],
  "small_model": "opencode/minimax-m2.5-free",
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 10
  },
  "permission": {
    "external_directory": {
      "*": "deny"
    },
    "doom_loop": "ask",
    "edit": {
      "*": "allow",
      "AGENTS.md": "deny",
      "opencode.json": "deny",
      "Opencode_Guide.md": "deny",
      ".opencode/*": "deny"
    },
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny",
      "*.pem": "deny",
      "*.key": "deny",
      "id_rsa*": "deny"
    },
    "bash": {
      "*": "allow",
      "rm *": "ask",
      "sudo *": "deny",
      "git commit*": "ask",
      "git push*": "ask",
      "git reset*": "ask",
      "git clean*": "ask",
      "git restore*": "ask",
      "git rebase*": "ask",
      "*deploy*": "deny",
      "npm publish*": "deny",
      "pnpm publish*": "deny",
      "yarn publish*": "deny",
      "vercel*": "deny",
      "netlify*": "deny",
      "wrangler*": "deny",
      "flyctl*": "deny",
      "heroku*": "deny",
      "kubectl*": "deny",
      "docker push*": "deny",
      "gh release*": "deny"
    },
    "webfetch": "allow",
    "websearch": "allow",
    "task": "allow",
    "question": "allow",
    "todowrite": "allow"
  },
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp"],
      "enabled": true
    }
  }
}
```

Only three things are new: `small_model`, `compaction`, `permission.doom_loop`. Everything else stays as in the current file. **No** `lsp`, `formatter` or `watcher` changes here: code projects keep them.

Why each key:
- `small_model`: fast free model (`opencode/minimax-m2.5-free`) for titles, summaries and compaction. Alternative free ids: `opencode/ling-3.0-tiny-free`, `opencode/glm-4.7-free`.
- `compaction`: automatic compaction keeps the conversation under the window; `prune` drops the middle of old messages, `tail_turns: 10` keeps the last 10 user/model turns.
- `doom_loop: "ask"`: when the agent repeats the same tool call 3 times, stop and ask instead of spinning.

---

## 2. `.opencode/agents/webdev.md`

### 2.1 Frontmatter

Add `steps` after `mode`. Before:

```yaml
mode: primary
temperature: 0.2
```

After:

```yaml
mode: primary
temperature: 0.2
steps: 50
```

### 2.2 New section `## Efficiency`

Add between `## Before writing` and `## Understanding what is being asked`:

```markdown
## Efficiency

- Read each file once: if it is already in context, use that state and `git diff` instead of re-reading it.
- Before reading a long file in full, check with `grep` or `wc -l` whether you need all of it.
- Group independent reads in a single tool block.
- If the same attempt fails three times or brings no progress, stop and ask the user with the `question` tool instead of retrying.
```

---

## 3. `.opencode/agents/reviewer.md`

### 3.1 Frontmatter

Add `steps` after `mode`. Before:

```yaml
mode: all
temperature: 0.1
```

After:

```yaml
mode: all
temperature: 0.1
steps: 25
```

### 3.2 Efficiency line

Add at the end of the `## What you receive` section:

```markdown
Efficiency: read each source once; `grep` before a full read of a long file. If the call fails or the diff is not what was described, say so — don't retry the same read.
```

---

## 4. `AGENTS.md`

Add rule 10 after rule 9 (Final summary):

```markdown
10. **No loops.** If the same action fails three times or brings no progress, stop and ask the user instead of retrying. Another attempt adds cost, not certainty.
```

---

## 5. `.opencode/commands/audit.md`

Add one line after "Run these checks yourself, in this order, and only the ones that apply to the project:":

```markdown
Run the checks in batches: independent commands in one tool call, `rg -l` or `rg --count` first, and open only the files with a hit.
```

---

## Verification

- `opencode.json`: valid JSON (`python3 -m json.tool opencode.json`).
- After a change, reload opencode so the new config is read: only at startup.