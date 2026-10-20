# opencode-configuration

Two OpenCode configurations, each one a complete payload: copy the whole folder
into the target directory, start OpenCode, and it works.

| Folder | Copy it into | What it is for |
|---|---|---|
| `notes/` | your Obsidian vault of university notes | one note = one lesson: writing, integrating, reviewing, with OCR, semantic search and a book reader |
| `web/` | a web project (portals and websites) | writing and reviewing code: C# + React today, adaptable |

Both carry `AGENTS.md` and `opencode.json` at the top and everything else under
`.opencode/`, which is where OpenCode looks for agents, commands, skills and
instructions. No file inside them needs editing before the first run.

## Prerequisites

Both configurations:

```bash
npm install -g opencode-ai@latest                             # latest version of opencode
python3 --version                                             # python 3 for scripts

opencode plugin @tarquinen/opencode-dcp@latest                # reduces token usage using old outputs 
opencode plugin @plannotator/opencode@latest                  # reviews the plan
opencode plugin @azumag/opencode-rate-limit-fallback          # automatic fallback to secondary model on rate limit (429)

# Ollama (local models for zero-token titles, compaction and fallbacks)
ollama pull qwen2.5:7b                                        # balanced model (~4.7 GB)
ollama pull qwen2.5:3b                                        # ultralight model for 8GB RAM machines (~1.9 GB)
ollama pull qwen2.5-coder:7b                                  # coding model (~4.7 GB)
```

Notes configuration only:

```bash
opencode plugin opencode-parser -g                            # the parser that reads photos of documents
sudo apt install tesseract-ocr tesseract-ocr-ita poppler-utils # photo reader & pdftoppm / pdftotext for PDFs
python3 -m pip install --user --break-system-packages pypdf "obsidian-mcp-search[server]" docling
```

The pip line installs the Python side: `pypdf` for the book reader, `obsidian-mcp-search`
for the semantic search server and `docling` for the OCR fallback on image-only PDFs. The
search server runs as a user service; see the "Semantic search" section below.

## Install

With the script (it never overwrites an existing file unless you pass `--force`,
and with `--force` it backs everything up first):

```bash
./install.sh notes "/path/to/vault"
./install.sh web   "/path/to/project"
./install.sh notes "/path/to/vault" --force    # replace what is already there
```

By hand, the same thing:

```bash
cp -r notes/. "/path/to/vault/"
cp -r web/.   "/path/to/project/"
```

Then start OpenCode from the target folder. After any change to `opencode.json`
or to a file in `.opencode/` it has to be restarted: the configuration is read
only at startup.

To check what OpenCode actually loaded:

```bash
opencode debug config
```

If a configuration is broken and OpenCode refuses to start:
`OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode`, fix the file and restart.

## `notes/` — what is inside

| Repo path | Installed path | What it is |
|---|---|---|
| `notes/AGENTS.md` | `AGENTS.md` | structure, 11 rules, tools table (read every session) |
| `notes/opencode.json` | `opencode.json` | permissions (v2 ruleset), local Ollama provider, rate limit fallback, obsidian-search MCP server, experimental todowrite |
| `notes/.opencode/rate-limit-fallback.json` | `.opencode/rate-limit-fallback.json` | fallback models and retry policy for rate limits (429) |
| `notes/.opencode/tui.json` | `.opencode/tui.json` | TUI plugins configuration (DCP) |
| `notes/.opencode/style.md` | `.opencode/style.md` | single source for the note style, loaded at every session |
| `notes/.opencode/agents/notes.md` | `.opencode/agents/` | the agent that writes (`default_agent`) |
| `notes/.opencode/agents/reviewer.md` | `.opencode/agents/` | checks correctness and verbosity, never edits |
| `notes/.opencode/commands/` | `.opencode/commands/` | `/lesson`, `/review`, `/audit`, `/slide`, `/split`, `/book` |
| `notes/.opencode/scripts/` | `.opencode/scripts/` | slide reader (with Docling OCR fallback), structural audit, loss check, splitter, book reader |
| `notes/Opencode_Guide.md` | `Opencode_Guide.md` | guide for the user, with examples and troubleshooting |
| `notes/chat_prompt.md` | `chat_prompt.md` | short prompts for Antigravity and web chat |
| `notes/books/` | `books/` | textbooks, one PDF per course (empty: you fill it) |
| `notes/.gitignore` | `.gitignore` | lines merged into yours, never replacing them |

## `web/` — what is inside

| Repo path | Installed path | What it is |
|---|---|---|
| `web/AGENTS.md` | `AGENTS.md` | structure, 10 rules, tools table (read every session) |
| `web/opencode.json` | `opencode.json` | permissions, local Ollama provider, Playwright MCP, rate limit fallback, experimental todowrite |
| `web/.opencode/rate-limit-fallback.json` | `.opencode/rate-limit-fallback.json` | fallback models and retry policy for rate limits (429) |
| `web/.opencode/tui.json` | `.opencode/tui.json` | TUI plugins configuration (DCP) |
| `web/.opencode/style.md` | `.opencode/style.md` | code conventions: React, C#, accessibility, SEO, hygiene |
| `web/.opencode/agents/webdev.md` | `.opencode/agents/` | the agent that writes code (`default_agent`) |
| `web/.opencode/agents/reviewer.md` | `.opencode/agents/` | reviews a change without touching it |
| `web/.opencode/commands/` | `.opencode/commands/` | `/page`, `/review`, `/audit`, `/preview` |
| `web/Opencode_Guide.md` | `Opencode_Guide.md` | guide for the user |

The web configuration assumes nothing about the stack: the agent reads
`package.json` and the files around the change first. Today that means C# in the
backend and React in the frontend; when the stack changes, `.opencode/style.md`
is the only file to update.

What it is allowed to do: create and change any file of the project, run
`npm`/`node`/`dotnet`/`git` and the usual tools, search the web, open the page in
a browser. What it is not: leave the project, deploy or publish anything
(blocked), delete files or run `git reset` (asks for confirmation), commit or
push (only when you ask for it in that message, and then it asks for
confirmation).

The web payload shares the resource-saving keys of the notes one: the local
model for titles and compaction (`agents.title` and `agents.compaction`, both
`ollama/qwen2.5:7b`), `compaction` (`auto: true`), rate-limit fallback and
`doom_loop: "deny"`.
Unlike the notes config, `lsp` and `formatter` stay enabled and `bash` stays
`allow` (npm, build, tests, Playwright); there are no `watcher` or Markdown-edit
rules because it works on code. Both agents add an `## Efficiency` section and
rule 10 ("No loops") tells the agent to stop and ask instead of retrying.

## The choices, and why (notes)

**The style comes from your own notes.** The first sections of both files
("Compilatori e interpreti", "Evoluzione hardware e multiprogrammazione") have
Every Word Capitalised, `[!NOTE] Nota del Prof`, bold everywhere, titles like "Il
Motore dell'Infinito": that is the AI style you want to avoid. Further on the
style changes: `*Definition:*`, `**Topic:**` labels at the start of a paragraph,
`-` lists, glosses with ` = `, `<u>` for the key sentence, callouts in lowercase.
`style.md` encodes this second style and lists the first one among the things not
to do. If it was read wrong, `style.md` is the file to change.

**Nothing the teacher said is ever lost.** That is rule 2 of `AGENTS.md` and the
opening of `style.md`: the agent fixes the shape, corrects and adds; it only
removes words. On top of the rule there is `check-losses.py`: the agent saves a
copy before editing and at the end the script lists formulas, code, images,
numbers, lines and slide pages it can no longer find. It is a word-by-word
comparison, so it lowers the risk without eliminating it: on important notes it is
still worth looking at `git diff`.

**Two agents instead of six.** With a free model every subagent is a new session
that has to reread everything. I kept only the separation that matters: who writes
and who checks. The reviewer works in a clean context, so it is not influenced by
what the other one just wrote.

**The reviewer runs once, when the lesson is finished.** It is started by
`/lesson` and by `/review`. After any edit the agent only updates the index and
runs the structural check.

**`style.md` is always loaded** (the `instructions` field of `opencode.json`): a
weak model sometimes skips reading, and the style is exactly the part that must
not be skipped.

**Fewer tokens, less noise.** The local model (`ollama/qwen2.5:7b`) answers titles
and compaction with zero API token cost: it is set on the two built-in agents,
`agents.title` and `agents.compaction` (the old `small_model` key is deprecated and
no longer read).
`compaction` (`auto: true`) keeps the conversation inside the window.
`lsp: false` and `formatter: false` are off because the vault
is Markdown: no language servers, no formatting. `watcher.ignore` skips images,
PDFs, slides, `.git` and `node_modules`, so file changes don't spam the session.
`permission.doom_loop: "deny"` stops the agent immediately if it loops.

**The todo list is an experimental tool.** OpenCode 2.1 ships the `todowrite` tool
behind a flag: `"experimental": { "todo": true }` in `opencode.json` gives the model
the tool and shows the task list in the session and in the sidebar. The permissions
have to allow it too (`"todowrite": "allow"`, or `{ "action": "todowrite",
"resource": "*", "effect": "allow" }` in the v2 ruleset). Both payloads set it.

**The permission ruleset is the v2 one.** The notes payload uses the ordered
`permissions` array (`{ "action", "resource", "effect" }`) instead of the
deprecated `permission` object: the last matching rule wins, so the specific
denies (`*/esercizi/*`, `AGENTS.md`, `.opencode/**`) come after `*.md`.

**Image-only PDFs are read with OCR.** `read-slides.py` uses `pdftotext` first; if
more than half of the pages come out empty it retries with Docling automatically. It
only kicks in for files up to 60 pages (override with `READ_SLIDES_DOCLING_LIMIT`;
force with `READ_SLIDES_DOCLING_FORCE=1`), so a 2000-page book is never converted page
by page. The first run downloads the OCR models.

**Search by meaning, not by word.** The `obsidian-search` MCP server (the
`obsidian-mcp-search` package) embeds the notes and answers queries by similarity, so
the agent finds a lesson by topic instead of by exact wording. It is optional: without
the server the agent falls back to `grep` and the structural audit.

**Fallback & context pruning.** `@tarquinen/opencode-dcp` optimizes context
by pruning stale outputs and duplicate calls. `@azumag/opencode-rate-limit-fallback`
cycles automatically through secondary Ollama fallback models if a 429 rate limit
is encountered, preventing task interruption.

**The textbooks are a complement, not a source.** Books live in
`books/<Course name>.pdf`, one per course, and are read with `books.py` (command
`/book`: `list`, `info`, `toc`, `page`, `search`). A note is complete without the
book: the agent asks for consent once, at the end of a lesson, before integrating
anything from it.

**Efficiency and loops.** Both agents carry a short `## Efficiency` section (read
each file once, `grep` first, group reads) and rule 10 of `AGENTS.md` ("Stop on
loops") tells the agent to stop and ask instead of retrying a failing action.

**Splitting the old files is done by a script, not by the model.** A model that
recopies 180 KB of notes into 20 files will lose pieces of them. `split-notes.py`
copies the text verbatim; the model steps in afterwards, with `/review`, one note
at a time.

**Permissions.** The agent cannot edit `AGENTS.md`, `opencode.json`, the guide,
`.opencode/` or anything inside `esercizi/` (`"*/esercizi/*": "deny"`, placed
after `*.md` so that the last matching rule wins). `pdftoppm` (creates images) and
`split-notes.py --write` (creates notes) ask for confirmation. Both
configurations set `"external_directory": {"*": "deny"}`: the agent never leaves
the folder it was started in.

**`esercizi/` is yours.** The `esercizi/` folder of every course holds the code
you write (`.py`, `.html`, `.sql`). It is an input just like the slides: the agent
reads it to link it from the notes, but it doesn't modify it and it doesn't run
code.

## Semantic search (notes)

The `obsidian-search` MCP server indexes the Markdown notes and answers queries by
embedding similarity (hybrid lexical + vector). It runs as an HTTP MCP server on
`http://127.0.0.1:8848/mcp`; OpenCode connects to it through the `mcp` block in
`opencode.json`. Install the Python side with the pip line in Prerequisites, then run
it as a user service:

```bash
systemctl --user status  obsidian-mcp-search
systemctl --user restart obsidian-mcp-search     # reloads and re-indexes
journalctl --user -u obsidian-mcp-search -n 50
```

The embedding model is
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dim): the tool's own
default, `intfloat/multilingual-e5-small`, is not supported by the installed
`fastembed` and must be overridden through `OMCS_EMBED_MODEL`. The registry lives in
`~/.config/obsidian-mcp-search/config.toml` and the index in
`~/.cache/obsidian-mcp-search/`. Register a vault (note the env var) and keep it fresh:

```bash
OMCS_EMBED_MODEL="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" \
  obsidian-mcp-search add-vault notes "/path/to/vault"
```

The server watches the notes and re-indexes changed files automatically; after bulk
edits call the MCP tool `reindex` or restart the service. Do not use the
`obsidian-mcp-search search` CLI: it ignores `OMCS_EMBED_MODEL` and builds a throwaway
index at `<vault>/.omcs-index.sqlite`, and if you pass a vault *name* it creates a
stray folder in the cwd. Use the MCP server instead.

## Implementation details (notes)

| 1 | date only in the file name | the `#` title has no date; the audit reports files without a date in the name; suggested format `2026-05-07 Automi a pila.md` |
| 2 | index and modules | `00 Index - <Course>.md` in every course or module folder |
| 4 | one `.txt` per lesson | the agent looks for the `.txt` with the same name or the same date as the note, otherwise it asks |
| 5 | git from the terminal | the guide uses `git diff` and `git restore` |
| 6 | splitting single files | script `split-notes.py` and command `/split` |
| 7 | `// adatta //` | replaces `// 400 //`: full-width image |
| 7b | layout of an image without a placeholder | the agent asks a single `question` listing all the images in order (resize / adatta / caption sotto / testo a lato / lascia com'è), text from the OCR if available |
| 9 | images inside callouts | stay as `![[x.png\|300]]` |
| 10 | `→` in formulas | no conversion, no check |
| 11 | only `// ... //` | `%% ... %%` removed everywhere |
| 12 | em dash, web sources | INFO only in the audit; no source is cited |
| 13 | summary at the end of the lesson | every note ends with `> [!info] Sintesi:` (3-6 points); the audit reports it if missing |
| 14 | length | no line limit: `style.md` asks for density. The audit reports single paragraphs over 150 words, as INFO |
| 15 | configuration and file creation | the agent does not change the configuration and does not create notes |
| 16 | reviewer | one pass, only with `/lesson` and `/review` |

## Converting old notes to the new format (from a single file to multiple files)

`/split "path/Notes course.md"` shows the plan and only writes after
confirmation. The script cuts on the `###` headings, derives the date of each
section from the name of its first image and joins consecutive sections that
share the same date. The dates come from the screenshots, so they are
approximate: fix them by renaming the file from Obsidian. Then `/review` one note
at a time: it trims, adds the summary and reports the word count before and
after. Make a commit before you start.

Note that with a multi-agent system it is convenient to have smaller files (it
also saves a fair amount of tokens).

## Repository layout

```
README.md      this file
install.sh     copies notes/ or web/ into a target folder, with backup
notes/         complete payload for the notes vault
web/           complete payload for a web project
```

Nothing else: the two payloads are self-contained, and each one is exactly what
must end up in the target folder.
