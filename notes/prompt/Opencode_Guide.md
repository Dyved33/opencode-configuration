# OpenCode guide for this vault

## Starting up

OpenCode must be started from the general notes folder, the one that contains `opencode.json`:

```bash
cd path/to/notes/folder
opencode
```

After any change to `opencode.json` or to a file in `.opencode/` it has to be restarted: the configuration is read only at startup.

## Prerequisites

```bash
npm install -g @opencode/cli@latest                # OpenCode v2 (the package 'opencode-ai' is v1: it does not read this configuration)

opencode plugin add opencode-parser                 # reads photos of documents (parse tool)
opencode plugin add @tarquinen/opencode-dcp@latest  # reduces tokens by pruning old outputs and duplicate calls
opencode plugin add @plannotator/opencode@latest    # interactive plan review with annotations
opencode plugin add @azumag/opencode-rate-limit-fallback  # automatic fallback to secondary model on rate limit (429)

sudo apt install tesseract-ocr tesseract-ocr-ita poppler-utils
python3 -m pip install --user --break-system-packages pypdf "obsidian-mcp-search[server]" docling
```

The plugins are also declared in `opencode.json`, so OpenCode installs them at the first start: with no network the start fails, and `opencode plugin add <package>` installs them once, by hand.

Plannotator opens the plan in the browser at the end of the planning phase, to annotate it and approve it or send it back with changes. It is declared with options in `opencode.json`:

```json
{
  "package": "@plannotator/opencode@latest",
  "options": { "workflow": "all-agents" }
}
```

`all-agents` gives the `submit_plan` tool to the project agents, so the plan is reviewed before anything is written. The default, `plan-agent`, leaves the tool to the built-in `plan` agent only; `user-managed` registers it without pushing the agents to use it. The `reviewer` agent runs as `mode: subagent` so it never gets the plan reminder.

To check that everything is in place on a new machine:

```bash
/path/to/opencode-configuration/doctor.sh notes /path/to/this/vault
```

`pypdf` is for the book reader, `obsidian-mcp-search` for the semantic search server and `docling` for the OCR fallback on image-only PDFs. The search server is optional and runs as a user service (`systemctl --user status obsidian-mcp-search`).

## The models

Nothing to install and no key: the default models are free.

| Model | What it is for |
|---|---|
| `opencode/nemotron-3-ultra-free` | default: writes and revises the notes |
| `opencode/minimax-m3.1-flash-free` | session title; the fastest |
| `openrouter/*:free` | free OpenRouter models, integrated in the fallback chain |
| `ollama/qwen2.5:3b` | last resort, offline and quota-free, runs on the GPU (GTX 1050) |

The free tier of OpenCode asks for no credentials. OpenRouter asks for one (already saved). Other free providers can be added with `bash ~/.config/opencode/scripts/connect-free-providers.sh`: for each provider the command prints the link to create the key and then asks for it.

On OpenCode 2.x models are changed from the `/models` selector; the chosen model lasts for the session.

### How the free models behave

Measured on the same tasks, free models are not interchangeable:

| Model | Tools used | Quality | What to watch out for |
|---|---|---|---|
| `opencode/nemotron-3-ultra-free` | 4 | good, disciplined | searches well, doesn't invent |
| `opencode/minimax-m3.1-flash-free` | 22 | good, verbose | writes files even when not asked; adds a "Riepilogo" |
| `opencode/deepseek-v4.1-flash-free` | 9 | good | searches the wrong folders |
| `opencode/glm-5.3-flash-free` | 10 | decent | contradicts itself, repeats a path |
| `openrouter/thinkingmachines/inkling:free` | 4 | decent | says it did things it didn't do |

One thing to keep in mind when writing requests: **if you ask "write the text of X" to a free model, it can interpret it as "write X in the file"**. The default doesn't do that, but if it happens: `git diff` and `git restore "path"` to undo, as usual.

### The automatic fallback

If a provider answers 429 (quota exhausted) or a transient error, the agent moves on its own to the next model in the chain and goes back when the quota frees up. The chain is in `.opencode/rate-limit-fallback.json` (in the vault) and in `~/.config/opencode/rate-limit-fallback.json` (in every project):

```
opencode/nemotron-3-ultra-free
opencode/minimax-m3.1-flash-free
opencode/deepseek-v4.1-flash-free
openrouter/thinkingmachines/inkling:free
openrouter/minimax/minimax-m3.1-flash:free
opencode/glm-5.3-flash-free
openrouter/liquid/lfm-2.5-2.6b:free
ollama/qwen2.5:3b
ollama/qwen2.5-coder:3b
```

The switch keeps the active agent, the session and the context: the agent keeps working on the same task on the other model. After the last model in the chain the plugin returns to the first one and waits a time that doubles at each round (1, 2, 4 minutes, up to one hour). A message from the user puts the session back on its model.

The chain is in order of measured reliability: each model has been tried on four tasks before entering it. If a new model fails, remove it from the chain instead of leaving it: a fallback that makes mistakes costs more than a 429.

## Token and context

Every request carries the static context (rules, style, agent prompt) and re-sends it at every turn; the part that grows is the conversation. The figures for this vault:

- static context: ~6.8k tokens per request (it was ~11.9k: the two skills were replaced by `.opencode/rules.md`, 530 tokens);
- a long session (157 messages) had processed 13M tokens: now the DCP plugin prunes history above 120k tokens and leaves the last 3 turns untouched.

Practical rules:

1. **One session per lesson.** History is the main expense: `/compact` or a new session cuts more than any other setting.
2. **The most disciplined model is also the cheapest.** The default makes 4 tool calls where another makes 22: tokens grow with tool calls.
3. **`title` and `compaction` can use Ollama.** On this machine there is an NVIDIA GTX 1050 GPU: `qwen2.5:3b` answers in a few seconds. They remain the last resort for frequent tasks, but are usable for title and compaction without slowing down the session.

## Loops

A loop is the agent repeating the same thing and consuming tokens without progressing. Three defenses:

- `doom_loop` is denied in `opencode.json`: after three identical calls OpenCode blocks the repetition;
- rule 10 of `AGENTS.md` requires stopping after two equivalent attempts and asking, instead of retrying;
- DCP warns the model before the context fills up (`iterationNudgeThreshold`), and deduplicates identical calls already made.

In practice free models have not looped: zero repeated identical calls in all tests. The real problem is another: the model repeating a search with different words (for example `minimax` with 22 calls for a search `nemotron` does in 4) spends tokens without adding anything. If you see it, choose the most disciplined model for that task.

## Nothing is lost

The rule is rule 2 of `AGENTS.md`: everything in your notes, in the raw notes and in the teacher's material stays in the note; the agent only removes words. A written rule, though, is not enough, because a model can make mistakes: that is why the check is done by a script.

1. before modifying a note the agent saves a copy of it in `.opencode/originals/`;
2. at the end `check-losses.py` compares the note against the copy, the raw notes and the slides, and lists what it can no longer find: formulas, lines of code, images, numbers, lines of text, slide pages. The code linked from the note by a wikilink (in `esercizi/`) counts as part of the note too;
3. for every item the agent rereads the source and puts back what is missing.

The script compares words, not meanings, and cannot check slides made only of images: after `/review` it is worth running it by hand and looking at `git diff` on the important notes.

## The agents

| Agent | What it does | How to use it |
|---|---|---|
| `notes` | writes and edits the notes. It is the one active at startup | just write the request |
| `reviewer` | checks a note (correctness, completeness, verbosity) and returns the list of corrections. It modifies nothing | runs by itself with `/lesson` and `/review`; by hand with `@reviewer` |

## The commands

**`/lesson`** closes the note of a lesson. The first path is the note, the others are raw notes or material; if they are missing it looks for them in the same folder.

```
/lesson "Semester/Languages/Lesson 3 - Stack Automaton.md"
/lesson "Semester/Languages/Lesson 3 - Stack Automaton.md" "Semester/Languages/automata.pdf"
```

It understands by itself which case it is in:
- the note already has text: it integrates it (placeholders, errors, missing parts) without rewriting it;
- the note is empty and there is a `.txt`: it writes it from the raw notes;
- the note is empty and there is only the material: it writes it from the slides.

**`/review`** has a note reviewed and applies the corrections: errors, missing parts, cuts. It is the command for trimming verbose notes: it removes words, not content, and has no length target to reach. On a folder it works one note at a time and stops after each one.

```
/review "Semester/Systems/Semaphores.md"
/review "Semester/Systems/Semaphores.md" report only     # modifies nothing
/review diff                                            # the notes modified and not yet committed
```

**`/audit`** runs the structural check and reports the result. It modifies nothing.

```
/audit                              # the whole vault
/audit "Semester/Systems"           # a course
```

It finds: broken links, missing images, unclosed formulas and code blocks, unbalanced `<div>`, wrong callouts, unresolved placeholders, lessons missing from the index, missing final summary, frontmatter and tags, titles out of convention, typical AI phrases, open `[!todo]`, very long paragraphs.

**`/slide`** shows the text of a page of the material, so you can check it with your own eyes.

```
/slide "Semester/Systems/automata.pdf" 28
/slide "Semester/Systems/automata.pdf" 19-21
/slide "Semester/Systems/automata.pptx" --search "stack empty"
```

**`/book`** reads a textbook in `books/`: list of books, summary, a page or a search for a text. The book remains a complement of the note, to be used only with your consent (rule 11 of `AGENTS.md`).

```
/book list
/book "books/Introduction to AI.pdf" toc
/book "books/Introduction to AI.pdf" page 28
/book "books/Introduction to AI.pdf" search "firewall"
```

**`/split`** divides a single notes file into one note per lesson. It is needed only once, for the notes written so far.

```
/split "Semester/Systems/Notes course.md"
/split "Semester/Systems/Notes course.md" --per-section
```

It shows the plan first and writes only after your confirmation. See below.

Paths with spaces must always be quoted.

## What to write in the notes

**Placeholders.** Outside code blocks, `// ... //` is an instruction for the agent, to be carried out at that point:

```
// slide 28 //                         bring here the content of slide 28
// def automaton //                     look for the definition in the material
// go deeper with an example //         any other request
```

The placeholder disappears once it has been carried out. If the agent can't, it replaces it with a `[!todo]`.

**Images.** After the image you indicate the layout:

```
![[x.png]]                        no placeholder: the agent asks (resized to 300 if you don't care)
![[x.png]] // fit //               fitted to the width of the page
![[x.png]] // below: text //       with a caption underneath
![[x.png]] // side: text //        with text alongside
![[x.png]] // side //              the paragraph that follows goes alongside
```

If you don't write a placeholder, the agent asks you which layout to use, one question per image. The text for the caption or for the text alongside comes from the OCR or the agent asks you for it, and if you don't write it falls back to a resize.

Inside a callout the image stays `![[x.png|300]]`. The model cannot see images: it never describes what they show unless your text or the OCR does.

**Todo.** `> [!todo] something to review` marks a point to check. The agent tries to close them on every pass and leaves new ones when it is not sure about something. `/audit` lists them all.

**Summary.** Every note closes with `> [!info] Summary:`, 3 to 6 points. It is written by the agent with `/lesson` and `/review`.

**Code.** The snippet that serves the theory stays in the note, in a ```` ``` ```` block. Exercises and complete solutions live in `esercizi/`, with the name you choose: the note keeps only the relevant piece with the wikilink `[[esercizi/es3.py|es3]]`. Files in `esercizi/` are yours: the agent never opens them for writing, and if you ask for an exercise it gives it to you in the answer and you save it.

## What OpenCode can and can't do

- Writes only `.md` files. It cannot modify `AGENTS.md`, the files in `.opencode/` nor anything in `esercizi/`.
- Doesn't create notes: you create them and it fills them. It can create only the course index. The only exception is `/split`, which asks for confirmation.
- Doesn't touch `.txt`, PDFs, slides, images and files in `esercizi/`. It doesn't run code.
- Doesn't leave the vault.
- In the terminal it can run only the five scripts (also `books.py`), `ls`, `grep`, `rg`, `wc`, `pdfinfo`, `pdftotext`, read-only git commands and server status commands `obsidian-mcp-search`. For `pdftoppm` (which creates images) it asks for confirmation. Slide reading as images with Docling happens inside `read-slides.py`.
- Can search the web.
- Doesn't commit or push: those stay with you.

These restrictions are not only written: they are imposed by the `permissions` block of `opencode.json`. `edit` denies everything except `.md`, with explicit denial for `AGENTS.md`, `.opencode/**`, `esercizi/`, `opencode.json`, `CONFIG-CHANGES.md` and the two files of `prompt/`; `bash` denies everything except the commands in the allowlist above; `external_directory` prevents leaving the vault.

## The scripts, also by hand

```bash
python3 .opencode/scripts/read-slides.py FILE              # page list
python3 .opencode/scripts/read-slides.py FILE 28           # one page
python3 .opencode/scripts/read-slides.py FILE --search "x" # where x appears
python3 .opencode/scripts/vault-audit.py "Semester/Systems"
python3 .opencode/scripts/vault-audit.py --short           # only ERROR and WARN
python3 .opencode/scripts/check-losses.py NOTE --save      # copy before editing
python3 .opencode/scripts/check-losses.py NOTE             # what was lost compared to the copy
python3 .opencode/scripts/check-losses.py NOTE --with SOURCE   # compared to a .txt or the slides
python3 .opencode/scripts/split-notes.py FILE             # split plan
python3 .opencode/scripts/split-notes.py FILE --write     # creates the notes
python3 .opencode/scripts/books.py list                   # books present and matched course
python3 .opencode/scripts/books.py info FILE              # pages, title, course
python3 .opencode/scripts/books.py toc FILE               # table of contents
python3 .opencode/scripts/books.py page FILE 28           # text of a page (or 19-21)
python3 .opencode/scripts/books.py search FILE "firewall" # pages containing the text
```

`read-slides.py` reads PDF, PPTX and PPT (the PPTs are converted with LibreOffice into a temporary folder). If the text layer is missing (more than half of the pages empty) it retries with Docling, i.e. OCR: only files up to 60 pages, change the limit with `READ_SLIDES_DOCLING_LIMIT` or force it with `READ_SLIDES_DOCLING_FORCE=1`. The first run downloads the OCR models. `books.py` reads the textbooks in `books/` with the same engine.

Two environment variables change where the scripts look:

| Variable | Default | What it is |
|---|---|---|
| `BOOKS_DIR` | `books` | the folder with the textbooks |
| `COURSES_DIR` | every first-level folder | the folder that holds the courses |
| `NOTES_SUMMARY_TITLES` | `summary,sintesi` | the accepted titles of the final callout of a note |

## The opencode-parser plugin

It adds the `parse` tool, which extracts text from PDF, Word, PowerPoint and, with OCR, from images. It doesn't create or insert images. Here it is used for one thing only: reading the text inside a screenshot (`parse` with OCR in the language of the notes). For slides and PDF the agent uses `read-slides.py`, because `parse` returns the document from the start and not a precise page.

## Semantic search (obsidian-search server)

In the notes there is also a search by meaning, not only by exact word: asking "where is traffic protection discussed" finds the firewall lesson even if the word "firewall" is not in the question. It is the MCP server `obsidian-search` (`opencode.json`, section `mcp`), which indexes the notes of `Semester/` with a multilingual embedding model and searches them on `http://127.0.0.1:8848/mcp`. It exposes four tools: `list_vaults`, `search`, `read_note`, `reindex`.

The server is a user systemd service (`~/.config/systemd/user/obsidian-mcp-search.service`), so it starts by itself at boot. Useful commands:

```bash
systemctl --user status obsidian-mcp-search     # status
systemctl --user restart obsidian-mcp-search    # restart (reloads the index)
obsidian-mcp-search status                      # indexed notes and blocks
```

The index updates by itself when a note changes (watcher). The model and the indexed notes are in the cache folder `~/.cache/obsidian-mcp-search/`. The agent uses it only to find linked lessons, not to read the file to modify.

## The ACP plugin

The plugin `@tuanhung303/opencode-acp` compacts the context by time, not only by size: as the conversation lengthens it removes old parts while keeping active constraints, so long work is not lost. It requires no configuration.

## Context compaction

As the conversation lengthens, OpenCode summarizes old parts on its own to free space in the model's context window. In `opencode.json` the `compaction` section sets:

- `auto: true` — compacts automatically when the context is full (default: `true`);
- `keep.tokens: 30000` — after the summary, 30k tokens of useful context remain, instead of starting from zero.

There are also `reserved` (reserve tokens for compaction) and `preserve_recent_tokens` (recent tokens to keep). There is no fixed cadence "every N messages": compaction starts when the context fills up, and a summary at intervals would require a plugin calling `session.summarize`.

The summary is done by the model indicated in `agents.compaction` (`opencode/nemotron-3-ultra-free`, 1M token window): the model must be able to keep the note in mind, not summarize it in pieces.

This is in addition to the DCP plugin, which prunes the context as the session proceeds instead of waiting for compaction. It is tuned in `.opencode/dcp.jsonc`: it prunes also in subagent sessions, leaves the last 3 turns untouched, warns the model before the context fills up and deduplicates identical calls. Its values take precedence over the global ones in `~/.config/opencode/dcp.jsonc`.

## When something goes wrong

- **A plugin doesn't load:** check the OpenCode version and the plugin shape. OpenCode 1.x plugins (shape `{ id, server }`) don't load on 2.x (which accepts `{ id, effect }` or `{ id, setup }`): this is the case of `@omniroute/opencode-plugin`, removed from `opencode.json` awaiting 0.3.x.
- **A provider answers 401 "Missing Authentication header":** the saved credential is not the right one. Check with `opencode auth list` and reconnect with `opencode auth login <provider>`.
- **The 429 doesn't move to the next model:** look at the chain in `rate-limit-fallback.json`; if the failing model is not in the chain, the plugin leaves it to OpenCode, which retries it alone.
- **A piped command is denied:** OpenCode checks permissions for every command in the chain, even `| head`. Missing rules are added in `opencode.json`, section `permissions`, as `shell` + `allow`, after the generic `deny` rule.
- **Agent or command doesn't appear:** restart OpenCode.
- **OpenCode doesn't start due to a configuration error:** `OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode`, fix it and restart. To see the configuration OpenCode actually loaded: `opencode debug config`.
- **The agent wrote too much or ruined a note:** `git diff` shows what changed, `git restore "path"` brings the note back to the last commit. Without git, the previous version is in `.opencode/originals/`. It is worth committing before `/review` and `/split`.
- **An image in a `<div>` is not visible:** check that the name in `src` is identical to the file's. If it is right and still not visible, see `LEGGIMI.md`.
- **Vague requests:** "improve the note" produces a random rewrite. Better "the section on semaphores is too long, trim it" or a placeholder in the right spot.
- **Ollama:** on this machine there is an NVIDIA GTX 1050 GPU; small models (`qwen2.5:3b`, `qwen2.5:1.5b`) answer in a few seconds. Don't use 7b models for frequent tasks: they don't fit in 4 GB of VRAM and stay on CPU.