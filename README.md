# Prerequisites

npm install -g opencode-ai@latest #to install the latest version of opencode
opencode plugin opencode-parser -g #to install the parser that lets you take photos of documents
sudo apt install tesseract-ocr tesseract-ocr-ita # to install the photo reader

## What's here

| File | Replaces | Notes |
|---|---|---|
| `AGENTS.md` | `AGENTS.md` | from 84 to 38 lines: structure, 9 rules, tools |
| `.opencode/style.md` | the two prompts and `div style.txt` | single source for the style, loaded at every session |
| `.opencode/agents/notes.md` | `vault`, `appunti`, `materiale`, `indici` | one agent that writes |
| `.opencode/agents/reviewer.md` | `reviewer` | checks correctness and verbosity, never edits |
| `.opencode/commands/` | the 4 commands | `/lesson`, `/review`, `/audit`, `/slide`, plus `/split` |
| `.opencode/scripts/vault-audit.py` | the old script | rewritten: no tags, no frontmatter, no yearly indexes |
| `.opencode/scripts/read-slides.py` | the `reader` agent | reads PDF, PPTX and PPT one page at a time |
| `.opencode/scripts/split-notes.py` | new | splits a single file into one note per lesson |
| `.opencode/scripts/check-losses.py` | new | verifies that nothing was lost from the note compared to the source |
| `opencode.json` | `opencode.json` | updated permissions |
| `Opencode_Guide.md` | `Opencode_Guide.md` | rewritten around the new structure |
| `chat_prompt.md` | `prompt_appunti.md`, `prompt_materiale.md` | short prompts for Antigravity and web chat |

## The choices, and why

**The style comes from your own notes.** The first sections of both files ("Compilatori e interpreti", "Evoluzione hardware e multiprogrammazione") have Every Word Capitalised, `[!NOTE] Nota del Prof`, bold everywhere, titles like "Il Motore dell'Infinito": that is the AI style you want to avoid. Further on the style changes: `*Definition:*`, `**Topic:**` labels at the start of a paragraph, `-` lists, glosses with ` = `, `<u>` for the key sentence, callouts in lowercase. `style.md` encodes this second style and lists the first one among the things not to do. You neither confirmed nor corrected it for me: if I read it wrong, `style.md` is the file to change.

**Nothing the teacher said is ever lost.** That is rule 2 of `AGENTS.md` and the opening of `style.md`: the agent fixes the shape, corrects and adds; it only removes words. In the first version the rule protected only a few categories (definitions, theorems, formulas) and for slides it said "one example per concept, skip the filler slides": it left the choice of what was secondary to the model. Now it doesn't. On top of that there is `check-losses.py`: the agent saves a copy before editing and at the end the script lists formulas, code, images, numbers, lines and slide pages it can no longer find. It is a word-by-word comparison, so it lowers the risk without eliminating it: on important notes it is still worth looking at `git diff`.

**Two agents instead of six.** With a free model every subagent is a new session that has to reread everything. I kept only the separation that matters: who writes and who checks. The reviewer works in a clean context, so it is not influenced by what the other one just wrote. `vault`, `materiale` and `indici` became cases inside `notes`. `lettore` became a script.

**The reviewer runs once, when the lesson is finished.** It is started by `/lesson` and by `/review`. After any edit the agent only updates the index and runs the structural check.

**`/review` edits.** It has the note reviewed and applies the changes. With `report only` it touches nothing. Fixed rule: it never removes definitions, theorems, proofs, formulas, code, examples, images.

**Splitting the old files is done by a script, not by the model.** A model that recopies 180 KB of notes into 20 files will lose pieces of them. `split-notes.py` copies the text verbatim; the model steps in afterwards, with `/review`, one note at a time.

**`style.md` is always loaded** (the `instructions` field of `opencode.json`): a weak model sometimes skips reading, and the style is exactly the part that must not be skipped.

**Removed:** the tag table, years and Erasmus, frontmatter, navigation footer, `raw_notes/`, `attachments/`, `NN_` numbering, the ban on non-ASCII characters, `[!NOTE]` and `[!LAW]` callouts, the example templates from the old prompts.

**Permissions.** The agent cannot edit `AGENTS.md` or `.opencode/`. Removed `find`, `head`, `tail`, `sed`, `unzip`, `file`. `pdftoppm` (creates images) and `split-notes.py --write` (creates notes) ask for confirmation.

## Implementation details

| 1 | date only in the file name | the `#` title has no date; the audit reports files without a date in the name; suggested format `2026-05-07 Automi a pila.md` |
| 2 | index and modules | `00 Index - <Course>.md` in every course or module folder |
| 4 | one `.txt` per lesson | the agent looks for the `.txt` with the same name or the same date as the note, otherwise it asks |
| 5 | git from the terminal | the guide uses `git diff` and `git restore` |
| 6 | splitting single files | script `split-notes.py` and command `/split`, see below |
| 7 | `// adatta //` | replaces `// 400 //`: full-width image |
| 9 | images inside callouts | stay as `![[x.png|300]]` |
| 10 | `→` in formulas | no conversion, no check |
| 11 | only `// ... //` | `%% ... %%` removed everywhere |
| 12 | em dash, web sources | INFO only in the audit; no source is cited |
| 13 | summary at the end of the lesson | every note ends with `> [!info] Sintesi:` (3-6 points); the audit reports it if missing |
| 14 | length | no line limit: `style.md` asks for density (each concept once, explanation proportioned to the difficulty, cut words and not content). The audit does not report the length of the note, only single paragraphs over 150 words, as INFO |
| 15 | configuration and file creation | the agent does not change the configuration and does not create notes |
| 16 | reviewer | one pass, only with `/lesson` and `/review` |

## Converting old notes to the new format (from a single file to multiple files)

Note that with a multi-agent system it is convenient to have smaller files (it also saves a fair amount of tokens)

`/split "path/Notes course.md"` shows the plan and only writes after confirmation. The script cuts on the `###` headings, derives the date of each section from the name of its first image and joins consecutive sections that share the same date. On your two files the plan is this:

- **SO:** 23 sections become 14 notes. One has no date ("Evoluzione hardware e multiprogrammazione").
- **Linguaggi:** 26 sections become 23 notes. The first 6 sections have no images and stay dateless, each in its own file: they are short (8 to 105 lines), better to merge them by hand into one or two lessons.

The dates come from the screenshots, so they are approximate: in Linguaggi some are out of order (for example "Analisi lessicale" 11/04 before "Grammatiche regolari" 09/04). Fix them by renaming the file from Obsidian. Then `/review` one note at a time: it trims, adds the summary and reports the word count before and after. Make a commit before you start.
