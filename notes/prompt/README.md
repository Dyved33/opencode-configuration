# The notes configuration

This folder holds the configuration of an OpenCode vault of university notes.
One note = one lesson.

## Prerequisites

npm install -g @opencode/cli@latest                # OpenCode v2

opencode plugin add opencode-parser                 # reads photos of documents (parse tool)
opencode plugin add @tarquinen/opencode-dcp@latest  # reduces tokens by pruning old outputs and duplicate calls
opencode plugin add @plannotator/opencode@latest    # interactive plan review with annotations
opencode plugin add @azumag/opencode-rate-limit-fallback  # automatic fallback to secondary model on rate limit (429)

sudo apt install tesseract-ocr tesseract-ocr-ita poppler-utils
python3 -m pip install --user --break-system-packages pypdf "obsidian-mcp-search[server]" docling

## What is here

| File | What it is |
|---|---|
| `Opencode_Guide.md` | the guide for the user: the commands, the scripts, what happens when something goes wrong |
| `chat_prompt.md` | short prompts to use outside OpenCode (Antigravity, web chat) |
| `README.md` | summary of the configuration |
| `../AGENTS.md` | the rules that always apply. Read at every session |
| `../.opencode/style.md` | how the notes must be written. Loaded at every session |
| `../.opencode/rules.md` | the writing discipline: no filler text, one idea per block. Loaded at every session |
| `../.opencode/agents/` | the 2 agents |
| `../.opencode/commands/` | the 7 commands |
| `../.opencode/scripts/` | the 5 scripts: slide reading (with Docling OCR fallback), structural check, loss check, splitting of single files, book reader |
| `../opencode.json` | permissions, models, rate limit fallback, the obsidian-search server |
| `../books/` | the textbooks, one PDF per course (input): read them with `/book` |
| `prompt/Guida_Opencode.md` | Italian guide (original vault) |
| `prompt/prompt_chat.md` | Italian prompts for external chats |

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
| `/reviewer` | runs the reviewer on a note without modifying anything (report-only, callable skill) |
| `/audit` | the structural check of a note, a course or the whole vault. It modifies nothing |
| `/slide` | shows the text of a page of the teacher's material |
| `/book` | reads a textbook in `books/`. It is a complement, never a default source |
| `/split` | splits a single notes file into one note per lesson |

## The models

| Role | Model | Why |
|---|---|---|
| default | `opencode/nemotron-3-ultra-free` | the most disciplined: 4 tool calls where `minimax` makes 22, clean writing, doesn't write files unless asked |
| session title | `opencode/minimax-m3.1-flash-free` | 5 s, the fastest |
| compaction | `opencode/nemotron-3-ultra-free` | 1M token window, summarises without losing note details |
| last resort | `ollama/qwen2.5:3b`, `ollama/qwen2.5-coder:3b` | offline and quota-free, runs on the NVIDIA GTX 1050 GPU |

No paid model, no process to keep running.

**Fallback chain** (`rate-limit-fallback.json`, 9 models): on quota exhaustion or a transient error, the agent moves to the next one, keeps working and goes back after the cooldown. The full order is in the guide; each model was tested on four tasks before entering the chain, and any model that failed was removed.

**Providers used**: the free tier of OpenCode (45 models, no key) and OpenRouter (`:free` models, one key). Other free providers are connected with `connect-free-providers.sh`; each key serves a separate account, and there is no way around that.

**OmniRoute is on pause.** The plugin `@omniroute/opencode-plugin` (0.2.1) exports the OpenCode 1.x plugin shape (`{ id, server }`); OpenCode 2.x accepts only `{ id, effect }` or `{ id, setup }` and refuses to load it with *"Plugin must export a default definition with an id and an effect or setup function"*. The plugin is therefore incompatible until upstream publishes a 0.3.x, and has been removed from `opencode.json`. The package remains installed and the `omniroute` service is no longer needed: its archive contains no provider connection, so it would not provide models anyway.

## Token: where they go and how they are reduced

Every request carries the whole static context (rules, style, agent prompt), and that block is re-sent at every turn: it is the most invisible cost.

| | Before | Now |
|---|---|---|
| static block in context (rules, style, agent prompt) | ~11,9k tokens | ~6,8k tokens |
| full request measured (static block + tool schema) | 22.748 input tokens | 19.049 input tokens |
| 157-message session | 13M tokens processed | history pruned to 120k |

The levers used:

- **`.opencode/rules.md`**: the two skills (`no-ai-slop`, `i-have-adhd`) cost 4.5k tokens at every request and at every subagent; now `instructions` contains a 530-token summary and the full files are only read when writing a note (the agent prompt already says so).
- **DCP tuned** (`.opencode/dcp.jsonc`): prunes also in subagent sessions (`allowSubAgents`), leaves the last 3 turns untouched (`turnProtection`), and warns the model before it enters a loop (`iterationNudgeThreshold` 10 instead of 15).
- **`compaction.keep.tokens: 30000`**: after compaction, useful context remains instead of starting from zero.
- **The most disciplined model**: tokens grow with the number of tool calls, and free models are not equal (see the guide).

Not done, to avoid losing quality: truncating tool outputs (`tool_output`), removing `style.md` from `instructions` (DCP might compress it away), giving up the `obsidian-search` MCP server or the `parse` plugin.

## The choices, and why

**Style comes from your notes.** The first sections of both files ("Compilatori e interpreti", "Evoluzione hardware e multiprogrammazione") have Title Case Every Word, `[!NOTE] Professor's Note`, bold everywhere, titles like "The Engine of Infinity": that is the AI style you want to avoid. Later the style changes: `*Definition:*`, `**Topic:**` labels at the start of paragraphs, lists with `-`, glosses with ` = `, `<u>` for the key phrase, lowercase callouts. `style.md` encodes this second style and puts the first among the things to avoid. You never confirmed or corrected it: if I misread, it is `style.md` the file to change.

**Nothing of what the teacher said is lost.** It is rule 2 of `AGENTS.md` and the opening of `style.md`: the agent fixes the style, corrects and adds; it removes only words. In the first version the rule protected only some categories (definitions, theorems, formulas) and for slides it said "one example per concept, skip background slides": it left the model to choose what was secondary. Now it does not leave that choice. In addition there is `check-losses.py`: the agent saves a copy before modifying, and at the end the script lists formulas, code, images, numbers, lines and slide pages it can no longer find. It is a word comparison, so it reduces the risk but does not eliminate it: on important notes it is still useful to look at `git diff`.

**Two agents instead of six.** With a free model every subagent is a new session that must re-read everything. I kept only the separation that matters: who writes and who checks. The reviewer works in a clean context, so it is not influenced by what the other just wrote. `vault`, `materiale` and `indici` became cases inside `notes`. `lettore` became a script.

**The default model is the most disciplined, not the best.** Free models were tested on four tasks (read a file and count, write and run Python, probability, document to structure) and then on two behavior tests. Results: `nemotron-3-ultra-free` solves everything and uses 4 tools where `minimax-m3.1-flash-free` uses 22; neither looped (zero repeated identical calls), but `minimax` ended up writing inside a real note when asked only for a text, and adds a final "Riepilogo"; `deepseek-v4.1-flash-free` writes well but searches the wrong folders; `glm-5.3-flash-free` contradicts itself; on OpenRouter `nemotron-3-super-120b:free` and `gemma-4-31b-it:free` failed all tasks, `nemotron-3-ultra-550b:free` solves them but takes 12 minutes. On respect for writing rules they are all similar (zero forbidden words): on ADHD rule compliance only `minimax` uses the numbered list, and none of the free models starts with the action. Hence the default.

**The OpenRouter key was wrong.** In OpenCode the locally saved OmniRoute key was stored, not an OpenRouter key: requests ended with a 401 "Missing Authentication header" and every OpenRouter model was unusable. The real key was already on the machine (`~/.aider/oauth-keys.env`) and was reconnected; wrong credentials were removed.

**The reviewer runs once, at the end of the lesson.** It starts with `/lesson` and with `/review`. After any modification the agent only updates the index and runs the structural check.

**`/review` modifies.** It has the note reviewed and applies corrections. With `report only` it touches nothing. Fixed rule: it never removes definitions, theorems, proofs, formulas, code, examples, images.

**The division of old files is done by a script, not the model.** A model that recopies 180 KB of notes into 20 files loses pieces. `split-notes.py` copies the text identically; the model intervenes after, with `/review`, one note at a time.

**`style.md` is always loaded** (the `instructions` field of `opencode.json`): a weak model sometimes skips reading it, and the style is exactly the part that must not be skipped.

**The three additions.** *Books:* textbooks in `books/<Course name>.pdf` are read with `books.py` (list, summary from bookmarks, a page, search) and with the `/book` command; they remain a complement of the note, never a default source (rule 11). *Docling:* if a PDF has no text layer (scanned pages or slides exported as images), `read-slides.py` reads it by itself with Docling, which uses Tesseract OCR in Italian and English; layout models download from HuggingFace into `~/.cache/huggingface` at first use, so the first time needs the network; on long files it skips, to avoid minutes, and reports it. *Semantic search:* the MCP server `obsidian-search` indexes the notes of `primo semestre/` and searches them by meaning (multilingual model `paraphrase-multilingual-MiniLM-L12-v2`, kept in `~/.cache/fastembed`), useful to find where a topic is covered and to create wikilinks. *Fallback & DCP:* `@tarquinen/opencode-dcp` optimizes context by pruning redundant outputs (tuned in `.opencode/dcp.jsonc`); `@azumag/opencode-rate-limit-fallback` avoids blocks by passing automatically to a secondary model on quota exhaustion (429), with a 9-model free chain. Local Ollama models are the last offline resort: on this machine there is an NVIDIA GTX 1050 (`nvidia-smi` works) and small models (`qwen2.5:3b`, `qwen2.5:1.5b`) answer in a few seconds. 7b models do not fit in 4 GB of VRAM and stay on CPU, so they are not used for title or compaction.

**The three style sources apply to every model.** `style.md`, `no-ai-slop` and `i-have-adhd` are the three writing rules of the vault: the first lives in `.opencode/style.md`, the other two in `~/.agents/skills/` and `~/.config/opencode/vendor/`. In `instructions` there are `style.md` and `.opencode/rules.md` (the summary of the two skills): they cost 4.5k tokens at every request and at every subagent, and free models are not the most attentive. The full versions of the two skills are read by the agent when it must write, because the prompt asks for them; the files remain outside the vault, so the agent cannot modify them (`edit` denies `.opencode/**`). `style.md` remains always in context: it is the part that must not be skipped.

**Removed:** tag table, years and Erasmus, frontmatter, navigation footer, `raw_notes/`, `attachments/`, `NN_` numbering, ban on non-ASCII characters, `[!NOTE]` and `[!LAW]` callouts, example models from old prompts.

**`esercizi/` is yours.** The `esercizi/` folder of each course contains the code written by you (`.py`, `.html`, `.sql`, subfolders for the exam). It is an input as much as the slides: the agent reads it to link it from notes but never modifies it, and does not run code. If you ask for an exercise, it gives it to you in the answer and you save it. `vault-audit.py` skips the folder (the `.md` files inside are not notes) and `check-losses.py` reads files linked from the note, so code moved to `esercizi/` does not come up as lost.

**Permissions.** The `permissions` block of `opencode.json` makes technical what `AGENTS.md` asks: `edit` denies everything except `.md`, with explicit denial for `AGENTS.md`, `.opencode/**`, `*/esercizi/*` (after `*.md`, because the last matching rule wins), `opencode.json`, `CONFIG-CHANGES.md` and the two `prompt/` files; `bash` is an allowlist (the five scripts, `ls`, `grep`, `rg`, `wc`, `pdfinfo`, `pdftotext`, `tesseract`, read-only git); `external_directory` prevents leaving the vault. `pdftoppm` and `split-notes.py --write` ask for confirmation.

**Bash does not block mid-chain anymore.** OpenCode checks permissions command by command, even in a pipe: `script.py | head -40` evaluates `script.py` *and* `head -40`, and if the second is not in the allowlist the whole chain is denied. That is why pipe recipients and chain operators are also in the allowlist (`head`, `tail`, `cat`, `sort`, `uniq`, `cut`, `tr`, `jq`, `diff`, `basename`, `dirname`, `cd`, `pwd`, `which`, `echo`, `find`). The price is that these programs can write, so there are three shields, placed after so that the last matching rule wins: `echo*>*` (no files created by redirection), `find* -delete*` and `find* -exec*` (no deletions or arbitrary commands), `*env*` (no `cat .env`, `printenv`). `sed`, `awk`, `tee`, `xargs` remain out: they write or execute, and vault inputs are not touched.

## Implementation details

| # | Detail |
|---|---|
| 1 | no date in the note | the `#` title and the file name have no date; suggested name `Lesson 3 - Stack Automaton.md` |
| 2 | index and modules | `00 Index - <Course>.md` in every course or module folder |
| 4 | one `.txt` per lesson | the agent looks for the `.txt` with the same name or date as the note, otherwise asks |
| 5 | git from terminal | the guide uses `git diff` and `git restore` |
| 6 | splitting single files | `split-notes.py` script and `/split` command, see below |
| 7 | `// fit //` | replaces `// 400 //`: full-width image |
| 7b | image layout without placeholder | the agent asks a `question` per image (resized / fitted / caption below / text beside / leave as is), text from OCR if available |
| 9 | images in callouts | remain `![[x.png|300]]` |
| 10 | `→` in formulas | no conversion, no check |
| 11 | only `// ... //` | removed `%% ... %%` everywhere |
| 12 | em dash, web sources | only INFO in the audit; no source cited |
| 13 | end-of-lesson summary | every note closes with `> [!info] Summary:` (3-6 points); the audit flags if missing |
| 14 | length | no line limit: `style.md` asks for density (every concept once, explanation proportional to difficulty, cut words not content). The audit does not flag note length, only paragraphs over 150 words, as INFO |
| 15 | configuration and file creation | the agent does not modify configuration and does not create notes |
| 16 | reviewer | one pass, only with `/lesson` and `/review` |
| 17 | compaction | `auto` and `keep.tokens: 30000` in `opencode.json`; continuous pruning is done by the DCP plugin |

## Converting old notes to the new format (from single file to multiple files)

Note that with a multi-agent system it is convenient to have smaller files (it also ensures consistent token savings)

`/split "path/Notes course.md"` shows the plan and writes only after your confirmation. The script cuts the file on `###` headings, derives the date of each section from the name of its first image and merges consecutive sections with the same date. On your two files the plan is this:

- **SO:** 23 sections become 14 notes. One without date ("Evoluzione hardware e multiprogrammazione").
- **Linguaggi:** 26 sections become 23 notes. The first 6 sections have no images and stay without date, each in its own file: they are short (from 8 to 105 lines), it is convenient to merge them by hand into one or two lessons.

The dates are those of the screenshots, so they are approximate: in Linguaggi some are out of order (for example "Analisi lessicale" 11/04 before "Grammatiche regolari" 09/04). Correct them by renaming the file from Obsidian. Then `/review` one note at a time: trims, adds the summary and reports the word count before and after. Make a commit before starting.