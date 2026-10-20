# The notes configuration

This folder holds the configuration of an OpenCode vault of university notes.
One note = one lesson.

## What is here

| File | What it is |
|---|---|
| `Opencode_Guide.md` | the guide for the user: the commands, the scripts, what happens when something goes wrong |
| `chat_prompt.md` | short prompts to use outside OpenCode (Antigravity, web chat) |
| `../AGENTS.md` | the rules that always apply. Read at every session |
| `../.opencode/style.md` | how the notes must be written. Loaded at every session |
| `../.opencode/rules.md` | the writing discipline: no filler text, one idea per block. Loaded at every session |
| `../.opencode/agents/` | the 2 agents |
| `../.opencode/commands/` | the 6 commands |
| `../.opencode/scripts/` | the 5 scripts: slide reading (with Docling OCR fallback), structural check, loss check, splitting of single files, book reader |
| `../opencode.json` | permissions, models, rate limit fallback, the obsidian-search server |
| `../books/` | the textbooks, one PDF per course (input): read them with `/book` |

To change the note style you edit only `../.opencode/style.md`.
To change the writing discipline you edit only `../.opencode/rules.md`.

## The rules in one line

- It writes only `.md` files, and it doesn't create notes: you create them and it fills them.
- It never loses content: everything the teacher said stays in the note.
- It doesn't touch the inputs: `.txt`, PDFs, slides, images, the books, the exercises.
- It doesn't leave the vault and it doesn't commit or push.
- It writes the final summary of the note and has it reviewed once, at the end of the lesson.

## The commands in one line

| Command | What it does |
|---|---|
| `/lesson` | completes the note of a lesson, closes it with the summary, checks it and has it reviewed |
| `/review` | has a note reviewed and applies the corrections (it removes words, not content) |
| `/audit` | the structural check of a note, a course or the whole vault. It modifies nothing |
| `/slide` | shows the text of a page of the teacher's material |
| `/book` | reads a textbook in `books/`. It is a complement, never a default source |
| `/split` | splits a single notes file into one note per lesson |

## The models

| Role | Model |
|---|---|
| default | `opencode/nemotron-3-ultra-free` |
| session title | `opencode/minimax-m3.1-flash-free` |
| compaction | `opencode/nemotron-3-ultra-free` |
| fallback | 9 models, in `.opencode/rate-limit-fallback.json` |

Nothing to install to use them: they are free and need no key. Ollama is only the
last resort of the fallback chain, for a machine without network.
