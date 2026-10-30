# OpenCode guide for this vault

## Launch

OpenCode is launched from the general notes folder, the one containing `opencode.json`:

```bash
cd path/to/notes/folder
opencode
```

OpenCode 2 automatically rereads `opencode.json` and files in `.opencode/` when they change; if an agent, command or plugin does not update, use `/reload` or restart.

## How it is organized

| File | Purpose |
|---|---|
| `AGENTS.md` | the few rules that always apply. Read every session |
| `.opencode/style.md` | how notes are written. Loaded every session |
| `.opencode/rules.md` | summary of the two writing skills, loaded every session |
| `.opencode/agents/` | `notes` for writing and `reviewer` selectable as primary or callable as subagent |
| `.opencode/plugins/free-model-router/` | enables all free models, disables paid ones and chooses the default; sends no probe requests |
| `.opencode/commands/` | the 8 commands |
| `.opencode/scripts/` | the 5 scripts: slide reader, book reader, structural check, loss check, single-file splitter |
| `.opencode/dcp.jsonc` | how the DCP plugin prunes session context |
| `~/.config/opencode/rate-limit-fallback.json` | single fallback model chain, shared between projects |
| `opencode.json` | models, plugins, permissions, MCP server and context compaction |
| `prompt_chat.md` | prompts for use outside OpenCode (Antigravity, web chat) |
| `books/` | textbooks, one PDF per course (`books/<Course name>.pdf`); read with `books.py` (command `/book`); complement, not default source |
| `<Course>/esercizi/` | code written by you (input): the agent does not touch it |
| `rollback/`, `.review/` | not notes: old single files and review work. Searches are done in `first semester/` |

To change note style, modify only `.opencode/style.md`.

## Models

There is no fixed model in `opencode.json`: the local plugin enables all free models in the current catalog and disables paid ones. The `preferred` list in `.opencode/plugins/free-model-router/index.ts` only serves to choose the default: it is no longer a whitelist. The plugin sends no probe requests. The catalog does not expose remaining credits or real-time health: these errors depend on the fallback.

Free models without tool support remain visible but are not chosen as default.

| Model | Purpose |
|---|---|
| `opencode/nemotron-3.5-super-vl-free` | default: writes and reviews notes; supports images and documents |
| `opencode/nemotron-3-ultra-free` | second choice, disciplined in tool use; context compaction |
| `opencode/glm-5.3-flash-free` | session title and `plan` agent; flash model, suitable for short tasks |
| `openrouter/*:free` | 21 OpenRouter `:free` models, all visible and selectable |
| `ollama/*` | 15 local models, last resort offline and without quota (GTX 1050 GPU) |

The OpenCode free tier does not ask for credentials. OpenRouter asks for one (already saved). Other free providers can be added with `bash ~/.config/opencode/scripts/connect-free-providers.sh`: for each provider the command prints the link to create the key and then asks for it.

Free models and their limits change. Nemotron 3.5 Super VL Free is temporarily free and its NVIDIA endpoint may log requests to improve models: do not send personal or reserved data.

The default applies to new sessions. You can change model with `/models` for the current session; the plugin reapplies the default at the next one. With all free models visible you can also choose a model outside the fallback chain.

## Native skills (loaded on demand)

Writing rules are divided into two levels:

- **`.opencode/rules.md`** (530 tokens): operational summary, loaded every session in the static context. Must be read and applied always.
- **`.opencode/skills/`**: complete skills, loaded only when needed with the `skill` tool. They do not weigh on the static context.

| Skill | File | When to use |
|---|---|---|
| `no-ai-slop` | `.opencode/skills/no-ai-slop/SKILL.md` | before writing or reviewing a note, to avoid AI-style words and formulas |
| `i-have-adhd` | `.opencode/skills/i-have-adhd/SKILL.md` | before writing or reviewing a note, for layout (one idea per block, lists instead of prose) |
| `note-quality` | `.opencode/skills/note-quality/SKILL.md` | before closing a note, to verify nothing of the teacher is lost and style is correct |

The two skills already present in `~/.agents/skills/` and `~/.config/opencode/vendor/` remain valid as global reference; those in `.opencode/skills/` are the project version.

## Per-agent MCP tools

The MCP server `obsidian-search` is no longer global: its tool schema is sent only to agents that need it (`notes` and `reviewer`). In other turns the static context is lighter. If another agent needs semantic search, ask to add it to the `agent` section of `opencode.json`.

## New plugins

| Plugin | Purpose | Status |
|---|---|---|
| `opencode-parser` | OCR and parsing of images and documents | installed |
| `@tarquinen/opencode-dcp` | Context pruning and call deduplication | installed, tuned in `.opencode/dcp.jsonc` |
| `@plannotator/opencode` | Interactive plan with Plannotator | installed |
| `@azumag/opencode-rate-limit-fallback` | Automatic fallback to secondary model | installed, version 2.1.1 |

To install a missing plugin:

```bash
opencode plugin add <plugin-name>
```

Then restart OpenCode.

## Automatic fallback

For errors recognized by the plugin (429, quota exhausted, transient errors), the request tries the next model in the chain. When the chain ends it stops, without restarting in a loop (`fallbackMode: "stop"`). A generic `504 Gateway Timeout` is not guaranteed to be recognized: the timeout limits the wait, but does not guarantee fallback passage. The unique configuration is `~/.config/opencode/rate-limit-fallback.json`; do not create copies in the vault:

```
opencode/nemotron-3.5-super-vl-free
opencode/nemotron-3-ultra-free
opencode/nemotron-3.5-lightning-free
opencode/deepseek-v4.1-flash-free
opencode/mimo-v2.6-flash-free
opencode/glm-5.3-flash-free
openrouter/thinkingmachines/inkling:free
openrouter/nvidia/nemotron-3-ultra-550b-a55b:free
openrouter/nvidia/nemotron-3-super-120b-a12b:free
openrouter/openrouter/free
ollama/qwen2.5:3b
```

The passage preserves the active agent, session and context and follows the static order above. After a complete passage without a usable model, the request stops: it does not restart in a loop and does not wait for an hour. Models chosen manually but absent from the chain are retried on the same model after the cooldown (`otherModels: "wait"`, 30 seconds, with increasing backoff).

`openrouter/openrouter/free` is OpenRouter's free router: it chooses a compatible free model only within OpenRouter. The plugin's ranking is a curated preference, not a measure of quality or current quota; local models are at the bottom because they can be slower. The chain is managed by the `@azumag/opencode-rate-limit-fallback@2.1.1` plugin.

## Tokens and context

Each request carries the static context (rules, style, agent prompt) and resends it every turn; the growing part is the conversation. Numbers for this vault:

- static context: ~6.8k tokens per request (was ~11.9k: the two skills were replaced by `.opencode/rules.md`, 530 tokens);
- a long session (157 messages) had processed 13M tokens: now the DCP plugin prunes history above 120k tokens and leaves the last 3 turns intact.

Practical rules:

1. **One session per lesson.** History is the main expense: `/compact` or a new session cuts more than any other setting.
2. **The most disciplined model is also the cheapest.** The default makes 4 tool calls where another makes 22: tokens grow with calls.
3. **`title` and `compaction` use dedicated free models.** Title uses `glm-5.3-flash-free`, compaction `nemotron-3-ultra-free`. Ollama remains the last resort: on this machine `qwen2.5:3b` responds in a few seconds with the GTX 1050 GPU, but local models are slower than hosted free ones.

## Loops

A loop is the agent repeating the same thing and consuming tokens without progressing. Three defenses:

- `doom_loop` is denied in `opencode.json`: after three identical calls OpenCode blocks the repetition;
- rule 10 of `AGENTS.md` requires stopping after two equivalent attempts and asking, instead of retrying;
- DCP warns the model before context fills (`iterationNudgeThreshold`), and deduplicates identical calls already made.

In practice free models have not looped: zero identical repeated calls in all tests. The real problem is another: the model repeating a search with different words (e.g. the old `minimax-m3.1-flash-free` made 22 calls for a search that `nemotron` does in 4; it is no longer in the catalog) spends tokens without adding anything. If you see it, choose the most disciplined model for that task.

## How free models behave

Measured on the same tasks, free models are not interchangeable:

| Model | Tool calls | Quality | What to watch out for |
|---|---|---|---|
| `opencode/nemotron-3-ultra-free` | 4 | good, disciplined | searches well, does not invent |
| `opencode/deepseek-v4.1-flash-free` | 9 | good | searches in wrong folders |
| `opencode/glm-5.3-flash-free` | 10 | fair | contradicts itself, repeats a path |
| `openrouter/thinkingmachines/inkling:free` | 4 | fair | says it did things it did not do |

`minimax-m3.1-flash-free` is no longer in the catalog: it was used in early tests and remains cited only as a comparison term. Models added later (`nemotron-3.5-super-vl-free`, `nemotron-3.5-lightning-free`, OpenRouter Nemotron free models) do not yet have a row in this table.

One thing to keep in mind when writing requests: **if you ask a free model to "write the text of X" it may interpret it as "write X into the file"**. The default does not do this, but if it happens: `git diff` and `git restore "path"` to undo, as usual.

## Lesson flow

1. You create the note in the course folder (e.g. `Lesson 3-Automata on stack.md`). In the same folder put the raw notes (`.txt`, one per lesson), slides and in `images/` the images.
2. Write in the note what you have, with placeholders `// ... //` where needed.
3. To plan without modifying, select `plan`: Plannotator shows the plan and the agent cannot modify notes. After approval pass to `notes` to execute the work. For normal requests `notes` does not open Plannotator.
4. At the end of the lesson launch `/lesson`: completes the note, asks whether to integrate the textbook from `books/` as a complement, writes the final summary, runs the reviewer once and applies corrections.

## Nothing is lost

The rule is rule 2 of `AGENTS.md`: everything that is in your notes, in the raw notes and in the slides remains in the note; the agent removes only words. A written rule is not enough, because a model can err: for this the check is done by a script.

1. Before modifying a note the agent saves a copy in `.opencode/originali/`;
2. at the end `check-losses.py` compares the note with the copy, with raw notes and with slides, and lists what it does not find: formulas, code lines, images, numbers, text lines, slide pages. Code linked by a wikilink (in `esercizi/`) counts as part of the note;
3. for each item the agent rereads the source and puts back what is missing.

The script compares words, not meanings, and does not check image-only slides: after `/review` it is worth running it manually and checking `git diff` on important notes.

## Agents

| Agent | What it does | How to use |
|---|---|---|
| `notes` | writes and modifies notes. It is active at launch | just write the request |
| `reviewer` | checks a note (correctness, completeness, verbosity) and returns the list of corrections. Does not modify anything | primary selectable and subagent; starts with `/lesson`, or manually with `@reviewer` or `/reviewer` |
| `audit` | read-only structural check: runs `vault-audit.py` and `check-losses.py` and returns a report | call manually |

## Commands

**`/lesson`** closes a lesson note. The first path is the note, the others are raw notes or material; if missing it looks for them in the same folder.

```
/lesson "First semester/Languages/Lesson 3-Automata on stack.md"
/lesson "First semester/Languages/Lesson 3-Automata on stack.md" "First semester/Languages/automata.pdf"
```

It understands by itself which case it is in:
- the note already has text: it integrates it (placeholders, errors, missing parts) without rewriting it;
- the note is empty and there is a `.txt`: it writes it from raw notes;
- the note is empty and there is only material: it writes it from slides.

**`/review`** reviews a note and applies corrections: errors, missing parts, cuts. It is the command to condense verbose notes: removes words, not content, and has no length limit to reach. On a folder it works on one note at a time and stops after each.

```
/review "First semester/OS/Lesson 5-Semaphores, Messages.md"
/review "First semester/OS/Lesson 5-Semaphores, Messages.md" solo report     # does not modify anything
/review diff                                            # notes modified and not yet in a commit
```

**`/reviewer`** runs the reviewer on a note without modifying it: returns the corrections list (report-only). Useful to check a note at any time.

```
/reviewer "First semester/OS/Lesson 5-Semaphores, Messages.md"
```

**`/audit`** runs the structural check and reports the result. Does not modify anything.

```
/audit                              # whole vault
/audit "First semester/Languages"   # one course
```

Finds: broken links, missing images, formulas and code blocks not closed, unbalanced `<div>`, wrong callouts, unresolved placeholders, lessons missing from index, missing final summary, frontmatter and tags, off-convention titles, AI-style phrases, open `[!todo]`, very long paragraphs.

**`/close-note`** runs loss check, structure check and reviewer in sequence on a single note, returning a unified report. Does not modify anything: if something needs fixing, use `/review` afterwards.

```
/close-note "First semester/OS/Lesson 5-Semaphores, Messages.md"
/close-note "First semester/OS/Lesson 5-Semaphores, Messages.md" "First semester/OS/semaphores.pdf"
```

What it does, in order:

1. Saves a backup copy of the note in `.opencode/originali/`;
2. Runs `check-losses.py` and reports formulas, code, images, numbers and source lines not found in the note;
3. Runs `vault-audit.py --breve` and reports ERROR and WARN;
4. Calls the subagent `reviewer` and reports [ERROR], [MISSING], [CUT], [STYLE], [FORM];
5. Closes with a judgment: `Note correct` / `To correct: N errors` / `To complete: N missing items`.

Use it when you have finished writing a note and want to verify nothing was lost before considering it closed.

**`/slide`** shows the text of a material page, to check with your own eyes.

```
/slide "First semester/Languages/automata.pdf" 28
/slide "First semester/Languages/automata.pdf" 19-21
/slide "First semester/Languages/automata.pptx" --search "stack empty"
```

**`/book`** reads a textbook from `books/`: list of books, summary, one page or text search. The book remains a complement of the note, to be used only with your consent (rule 11 of `AGENTS.md`).

```
/book list
/book "books/Introduction to Security.pdf" index
/book "books/Introduction to Security.pdf" page 28
/book "books/Introduction to Security.pdf" search "firewall"
```

**`/split`** divides a single raw notes file into one note per lesson. Use once only, for notes written so far.

```
/split "First semester/OS/OS theory notes.md"
/split "First semester/OS/OS theory notes.md" --per-section
```

It shows the plan first and writes only after your confirmation. See below.

Paths with spaces always go in quotes.

## Migrating old notes to the new format

1. `/split "path/Notes course.md"`. The script cuts the file on `###` titles and uses the hidden date in image names only to group consecutive sections: the date does not end up in file names nor in the index. Text is copied identically, it does not pass through the model.
2. Check the plan. Groups follow images, so they are indicative: sections without images remain separate groups and must be merged manually if needed.
3. Confirm: creates the notes and index in the same folder. The single file remains intact: archive or delete it yourself after checking.
4. If a title or name does not suit you, rename the file from Obsidian: index links update automatically.
5. `/review` one note at a time. Each pass condenses, adds the final summary and reports words before and after.

## What to write in notes

**Placeholders.** Outside code blocks, `// ... //` is an instruction for the agent, to execute at that point:

```
// slide 28 //                         report slide 28 content here
// def automaton on stack //           search the definition in the material
// deepen with an example //           any other request
```

The placeholder disappears when it has been executed. If the agent cannot execute it, it replaces it with a `[!todo]`.

**Images.** After the image the layout is indicated:

```
![[x.png]]                        no placeholder: agent asks (resized to 300 if you don't care)
![[x.png]] // adatta //           adapted to page width
![[x.png]] // sotto: testo //     with text below
![[x.png]] // lato: testo //      with text beside
![[x.png]] // lato //             beside goes the following paragraph
```

If you don't write a placeholder, the agent asks which layout to use, one question per image. The text for the text below or text beside comes from OCR or the agent asks you, and if you don't write it falls back to resizing.

Inside a callout the image remains `![[x.png|300]]`. The model does not see images: it never describes what they show unless your text or OCR says so.

**Todo.** `> [!todo] what to review` marks a point to check. The agent tries to close them at every pass and leaves new ones when unsure. `/audit` lists them all.

**Summary.** Every note closes with `> [!info] Summary:`, 3 to 6 points. It is written by the agent with `/lesson` and `/review`.

**Code.** The snippet that serves theory remains in the note, in a block ```` ``` ````. Exercises and complete solutions are in `esercizi/`, with the name you choose: in the note only the relevant piece remains, with the wikilink `[[esercizi/es3.py|es3]]`. `esercizi/` files are yours: the agent does not open them for writing and, if you ask for an exercise, it gives it in the answer and you save it.

## What OpenCode can and cannot do

- Writes only `.md` files. Cannot modify `AGENTS.md`, files in `.opencode/` nor anything in `esercizi/`.
- Does not create notes: you create them and it fills them. It can create only the course index. The only exception is `/split`, which asks for confirmation.
- Does not touch `.txt`, PDFs, slides, images and `esercizi/` files. Does not execute code.
- Does not leave the vault.
- In the terminal it can run only the five scripts (also `books.py`), `ls`, `grep`, `rg`, `wc`, `pdfinfo`, `pdftotext`, read-only git commands and `obsidian-mcp-search` status commands. For `pdftoppm` (which creates images) it asks for confirmation. Image slide reading with Docling happens inside `read-slides.py`.
- Can search the web.
- Does not commit or push: they remain yours.

These restrictions are not only written: they are enforced by the `permissions` block of `opencode.json`. `edit` denies everything except `.md`, with explicit denial for `AGENTS.md`, `.opencode/**`, `esercizi/`, `opencode.json`, `CONFIG-CHANGES.md` and the two `prompt/` files; `bash` denies everything except the allowlist commands above; `external_directory` prevents leaving the vault.

## Scripts, also manually

```bash
python3 .opencode/scripts/read-slides.py FILE              # list of pages
python3 .opencode/scripts/read-slides.py FILE 28           # one page
python3 .opencode/scripts/read-slides.py FILE --search "x"  # where x appears
python3 .opencode/scripts/books.py list                    # present books and associated course
python3 .opencode/scripts/books.py index FILE              # book summary
python3 .opencode/scripts/books.py page FILE 28            # one book page
python3 .opencode/scripts/books.py search FILE "x"         # where x appears in the book
python3 .opencode/scripts/vault-audit.py "First semester/Languages"
python3 .opencode/scripts/vault-audit.py --breve           # only ERROR and WARN
python3 .opencode/scripts/check-losses.py NOTE --save       # copy before modifying
python3 .opencode/scripts/check-losses.py NOTE               # what was lost compared to copy
python3 .opencode/scripts/check-losses.py NOTE --with SOURCE  # compared to a .txt or slides
python3 .opencode/scripts/split-notes.py FILE           # division plan
python3 .opencode/scripts/split-notes.py FILE --write  # creates the notes
```

`read-slides.py` reads PDF, PPTX and PPT (PPTs are converted with LibreOffice into a temporary folder). If a PDF is made of image pages, text is automatically read with Docling (OCR); on long files the fallback is skipped, to avoid taking too long, and the script reports it: in that case the page is viewed as a photo. With `READ_SLIDES_DOCLING_FORZA=1` Docling is forced even on long files.

## opencode-parser plugin

Adds the `parse` tool, which extracts text from PDF, Word, PowerPoint and, with OCR, from images. Installed globally as `opencode-parser@2.0.1`, compatible with OpenCode 2; it does not create or insert images. Here it serves to read text inside a screenshot (`parse` with OCR in Italian). For slides and PDFs the agent uses `read-slides.py`, because `parse` returns the document from the beginning and not a specific page.

## Semantic search (obsidian-search server)

Notes also have a search by meaning, not just exact word: asking "where is traffic protection discussed" finds the firewall lesson even if the word "firewall" is not in the question. It is done by the MCP server `obsidian-search` (`opencode.json`, `mcp` section), which indexes `first semester/` notes with a multilingual embedding model and searches them on `http://127.0.0.1:8848/mcp`. It exposes four tools: `list_vaults`, `search`, `read_note`, `reindex`.

The server is a user systemd service (`~/.config/systemd/user/obsidian-mcp-search.service`), so it starts alone at boot. Useful commands:

```bash
systemctl --user status obsidian-mcp-search     # status
systemctl --user restart obsidian-mcp-search    # restart (reloads index)
obsidian-mcp-search status                      # indexed notes and blocks
```

The index updates automatically when a note changes (watcher). The model and indexed notes are in the cache folder `~/.cache/obsidian-mcp-search/`. The agent uses it only to find linked lessons, not to read the file to modify.

## Context compaction

When the conversation lengthens, OpenCode summarizes old parts alone to free space in the model context window. In `opencode.json` the `compaction` section sets:

- `auto: true` — compacts automatically when context is full (default: `true`);
- `keep.tokens: 12000` — keeps a more compact summary, reducing context resent in subsequent turns.

There are also `reserved` (reserve tokens for compaction) and `preserve_recent_tokens` (recent tokens to keep). There is no fixed cadence "every N messages": compaction starts when context fills, and a summary at intervals would require a plugin calling `session.summarize`.

The summary is done by the model indicated in `agents.compaction` (`opencode/nemotron-3-ultra-free`, 1M token window): the model must be able to keep the note in mind, not summarize it in pieces.

Added to this is the DCP plugin, which prunes context as the session proceeds instead of waiting for compaction. It is tuned in `.opencode/dcp.jsonc`: it prunes also in subagent sessions, leaves the last 3 turns intact, warns the model before context fills and deduplicates identical calls. Its values take precedence over global ones in `~/.config/opencode/dcp.jsonc`.

## When something goes wrong

- **A plugin does not load:** check OpenCode version and plugin form. OpenCode 1.x plugins (form `{ id, server }`) do not load on 2.x (which accepts `{ id, effect }` or `{ id, setup }`): this is the case of `@omniroute/opencode-plugin`, removed from `opencode.json` awaiting 0.3.x.
- **A provider replies 401 "Missing Authentication header":** the saved credential is not the right one. Check with `opencode auth list` and reconnect with `opencode auth login <provider>`.
- **429 does not pass to the next model:** check the chain in `rate-limit-fallback.json`; if the failing model is not in the chain, with `otherModels: "wait"` the plugin retries it on the same model after cooldown, does not pass to another.
- **A command with a pipe is denied:** OpenCode checks permissions for every command in the chain, even `| head`. Missing rules are added in `opencode.json`, `permissions` section, as `shell` + `allow`, after the generic `deny` rule.
- **Agent or command do not appear:** run `/reload`; if not enough, restart OpenCode.
- **OpenCode does not start due to configuration error:** `OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode`, correct and restart. To see the configuration OpenCode really loaded: `opencode debug config`.
- **The agent wrote too much or ruined a note:** `git diff` shows what changed, `git restore "path"` returns the note to the last commit. Without git, the previous version is in `.opencode/originali/`. It is advisable to commit before `/review` and `/split`.
- **An image in a `<div>` is not visible:** check that the name in `src` is identical to the file name. If it is correct and still not visible, see `LEGGIMI.md`.
- **Vague requests:** "improve the note" produces a random rewrite. Better "the semaphore section is too long, condense it" or a placeholder in the right point.
- **Ollama:** on this machine there is a NVIDIA GTX 1050 GPU; small models (`qwen2.5:3b`, `qwen2.5:1.5b`) respond in a few seconds. Do not use 7b models for frequent tasks: they do not fit in 4 GB VRAM and remain on CPU.
