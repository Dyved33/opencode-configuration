# opencode-configuration

Two OpenCode configurations, each one a complete payload: copy the whole folder
into the target directory, start OpenCode, and it works.

| Folder | Copy it into | What it is for |
|---|---|---|
| `notes/` | your Obsidian vault of university notes | one note = one lesson: writing, integrating, reviewing |
| `web/` | a web project (portals and websites) | writing and reviewing code: C# + React today, adaptable |

Both carry `AGENTS.md` and `opencode.json` at the top and everything else under
`.opencode/`, which is where OpenCode looks for agents, commands, skills and
instructions. No file inside them needs editing before the first run.

## Prerequisites

Both configurations:

```bash
npm install -g opencode-ai@latest    # latest version of opencode
python3 --version                    # the scripts are python3
```

Notes configuration only:

```bash
opencode plugin opencode-parser -g   # the parser that reads photos of documents
sudo apt install tesseract-ocr tesseract-ocr-ita   # photo reader
sudo apt install poppler-utils       # pdftoppm / pdftotext for PDFs
```

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
| `notes/AGENTS.md` | `AGENTS.md` | structure, 10 rules, tools table (read every session) |
| `notes/opencode.json` | `opencode.json` | permissions: markdown only, no leaving the vault, no code execution |
| `notes/.opencode/style.md` | `.opencode/style.md` | single source for the note style, loaded at every session |
| `notes/.opencode/agents/notes.md` | `.opencode/agents/` | the agent that writes (`default_agent`) |
| `notes/.opencode/agents/reviewer.md` | `.opencode/agents/` | checks correctness and verbosity, never edits |
| `notes/.opencode/commands/` | `.opencode/commands/` | `/lesson`, `/review`, `/audit`, `/slide`, `/split` |
| `notes/.opencode/scripts/` | `.opencode/scripts/` | slide reader, structural audit, loss check, splitter |
| `notes/Opencode_Guide.md` | `Opencode_Guide.md` | guide for the user, with examples and troubleshooting |
| `notes/chat_prompt.md` | `chat_prompt.md` | short prompts for Antigravity and web chat |
| `notes/.gitignore` | `.gitignore` | lines merged into yours, never replacing them |

## `web/` — what is inside

| Repo path | Installed path | What it is |
|---|---|---|
| `web/AGENTS.md` | `AGENTS.md` | structure, 10 rules, tools table (read every session) |
| `web/opencode.json` | `opencode.json` | permissions, no leaving the project, no deploy, Playwright MCP |
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

The web payload shares the resource-saving keys of the notes one: `small_model`,
`compaction` (`auto`, `prune`, `tail_turns: 10`) and `permission.doom_loop: "ask"`.
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

**Fewer tokens, less noise.** `small_model` (`opencode/minimax-m2.5-free`) answers
titles, summaries and compaction, so the main model isn't spent on them.
`compaction` (`auto`, `prune`, `tail_turns: 10`) keeps the conversation inside the
window on its own. `lsp: false` and `formatter: false` are off because the vault
is Markdown: no language servers, no formatting. `watcher.ignore` skips images,
PDFs, slides, `.git` and `node_modules`, so file changes don't spam the session.
`permission.doom_loop: "ask"` stops the agent when it repeats the same tool call
three times.

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
