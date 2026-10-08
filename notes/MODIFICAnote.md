# MODIFICA.md — notes payload

Step-by-step changes to apply to the **notes** opencode configuration. Each section gives an exact `before → after`; apply it in your copy and verify with `opencode` (or a JSON check for `opencode.json`).

Changes in short:
- `opencode.json`: `small_model`, `lsp`, `formatter`, `compaction`, `watcher`, `permission.doom_loop`
- `.opencode/agents/notes.md`: `steps: 40`, efficiency section, grouped image question
- `.opencode/agents/reviewer.md`: `steps: 25`, one-line efficiency rule
- `.opencode/style.md`: one grouped question for images without placeholder
- `AGENTS.md`: rule 10, stop on loops
- `.opencode/commands/lesson.md`: hint the procedure instead of listing the steps
- `.opencode/commands/audit.md`: `--short` on the inline check

---

## 1. `opencode.json`

Replace the whole file with:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "notes",
  "instructions": [".opencode/style.md"],
  "small_model": "opencode/minimax-m2.5-free",
  "lsp": false,
  "formatter": false,
  "compaction": {
    "auto": true,
    "prune": true,
    "tail_turns": 10
  },
  "watcher": {
    "ignore": [
      "**/*.png",
      "**/*.jpg",
      "**/*.jpeg",
      "**/*.gif",
      "**/*.webp",
      "**/*.pdf",
      "**/*.ppt",
      "**/*.pptx",
      ".git/**",
      "**/node_modules/**"
    ]
  },
  "permission": {
    "external_directory": {
      "*": "deny"
    },
    "doom_loop": "ask",
    "edit": {
      "*": "deny",
      "*.md": "allow",
      "*/esercizi/*": "deny",
      "AGENTS.md": "deny",
      "Opencode_Guide.md": "deny",
      "chat_prompt.md": "deny",
      "opencode.json": "deny",
      ".opencode/*": "deny"
    },
    "read": {
      "*": "allow",
      "*.env": "deny",
      "*.env.*": "deny"
    },
    "bash": {
      "*": "deny",
      "python3 .opencode/scripts/vault-audit.py*": "allow",
      "python3 .opencode/scripts/read-slides.py*": "allow",
      "python3 .opencode/scripts/check-losses.py*": "allow",
      "python3 .opencode/scripts/split-notes.py*": "allow",
      "python3 .opencode/scripts/split-notes.py*--write*": "ask",
      "pdfinfo*": "allow",
      "pdftotext*": "allow",
      "pdftoppm*": "ask",
      "tesseract*": "allow",
      "ls*": "allow",
      "wc*": "allow",
      "grep*": "allow",
      "rg*": "allow",
      "git status*": "allow",
      "git diff*": "allow",
      "git log*": "allow",
      "git show*": "allow"
    },
    "webfetch": "allow",
    "websearch": "allow",
    "task": "allow",
    "question": "allow",
    "todowrite": "allow"
  }
}
```

What is new compared to the current file: `small_model`, `lsp: false`, `formatter: false`, `compaction`, `watcher`, `permission.doom_loop`. Nothing else changed.

Why each key:
- `small_model`: fast free model (`opencode/minimax-m2.5-free`) for titles, summaries and compaction. Alternative free ids: `opencode/ling-3.0-tiny-free`, `opencode/glm-4.7-free`.
- `lsp`/`formatter`: the vault is Markdown, no language servers, no formatting; disabling saves token and latency.
- `compaction`: automatic compaction keeps the conversation under the window; `prune` drops the middle of old messages, `tail_turns: 10` keeps the last 10 user/model turns.
- `watcher.ignore`: don't watch images, PDFs, slides, `.git` and `node_modules`; less file-change noise.
- `doom_loop: "ask"`: when the agent repeats the same tool call 3 times, stop and ask instead of spinning.

---

## 2. `.opencode/agents/notes.md`

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
steps: 40
```

### 2.2 Before writing, step 3 — tone note only for B and C

Before:

> 3. Read another note of the same course, if there is one, to pick up the tone.

After:

> 3. In cases B and C only: read another note of the same course, if there is one, to pick up the tone. In case A the tone is already in the note.

### 2.3 Case A — grouped image question

Before:

> apply the layouts to the images: for each image without a placeholder, ask the user which layout to use (`.opencode/style.md`, section "Images"), one question per image; then create the wikilinks to the other lessons of the course.

After:

> apply the layouts to the images: for all the images without a placeholder, ask the user once with the `question` tool which layout to use for each one, in the order the images appear (`.opencode/style.md`, section "Images"); then create the wikilinks to the other lessons of the course.

### 2.4 New section `## Efficiency`

Add between `## After writing` and `## When the lesson is finished`:

```markdown
## Efficiency

- Read each file once: if it is already in context, use that state instead of re-reading it.
- Before reading a long file in full, check with `grep` or `wc` whether you need all of it.
- Group independent reads in a single tool block.
- If the same attempt fails three times or brings no progress, stop and ask the user with the `question` tool instead of retrying.
```

### 2.5 Limits — remove the bullets that repeat `AGENTS.md`

Before:

> - Don't create, rename, move or delete files: the user creates the note, you fill it. Only exception: the index. Code is case E.
> - Don't modify `.txt`, PDFs, slides, images and the files in `esercizi/`.
> - The date doesn't go into the note. If the file name doesn't contain it, report that in the summary.

After (keep only what AGENTS.md doesn't already say):

> - The date doesn't go into the note. If the file name doesn't contain it, report that in the summary.

---

## 3. `.opencode/agents/reviewer.md`

### 3.1 Frontmatter

Before:

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
Efficiency: read each source once; `grep` before a full read of a long file. If the material can't be verified (missing file, wrong note), say so instead of guessing or retrying the same read.
```

---

## 4. `.opencode/style.md`

Replace the sentence about asking layouts (section "Images", paragraph "If the image has no placeholder"):

Before:

> If the image has no placeholder — or if you are inserting it yourself with `pdftoppm` — ask which layout to use with the `question` tool, one question per image, in the order the images appear.

After:

> If the image has no placeholder — or if you are inserting it yourself with `pdftoppm` — ask which layout to use with the `question` tool: a single question listing all the images, in the order they appear, each with the layout choices. No question for images inside a callout... (rest unchanged).

Complete final paragraph:

> If the image has no placeholder — or if you are inserting it yourself with `pdftoppm` — ask which layout to use with the `question` tool: a single question listing all the images, in the order they appear, each with the layout choices. No question for images inside a callout and for images already inside a `<div>`: their layout is already decided (see below).

The following question block, the list of options and the HTML templates stay exactly as they are. The option list to attach to the grouped question:

- resized to 300
- fitted to the width of the page
- with a caption underneath
- with text alongside
- leave it as it is

---

## 5. `AGENTS.md`

Add rule 10 after rule 9 (Final summary):

```markdown
10. **Stop on loops.** If the same action fails three times or brings no progress, stop and ask the user instead of retrying. Another attempt adds cost, not certainty.
```

---

## 6. `.opencode/commands/lesson.md`

Replace the last paragraph (the one starting "Consider the lesson finished...") with:

```markdown
Consider the lesson finished and follow your whole procedure (see your instructions, `notes.md`): understand which case you are in, write, close the note with the final summary, update the index, run the loss check and the structural check, call the reviewer once, apply its corrections, close with the summary.
```

Only the steps that were already listed are referenced; no information is removed.

---

## 7. `.opencode/commands/audit.md`

Line 7, before:

```markdown
!`python3 .opencode/scripts/vault-audit.py $ARGUMENTS`
```

After:

```markdown
!`python3 .opencode/scripts/vault-audit.py $ARGUMENTS --short`
```

`--short` prints only ERRORs and WARNs plus the counts, which is all the report below needs; INFO details still come from the counts line.

---

## Verification

- `opencode.json`: valid JSON (`python3 -m json.tool opencode.json`).
- After a change, reload opencode so the new config is read: only at startup.
- Optionally run `python3 .opencode/scripts/vault-audit.py -h` to check the `--short` flag in your copied scripts.