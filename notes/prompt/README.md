# Prerequisites

npm install -g @opencode/cli@latest                            # install latest OpenCode version
opencode plugin opencode-parser -g                              # install parser to read document photos
sudo apt install tesseract-ocr tesseract-ocr-ita               # install photo reader

opencode plugin @tarquinen/opencode-dcp@latest                 # reduces tokens pruning old outputs and duplicate calls
opencode plugin @plannotator/opencode@latest                   # interactive plan review, with annotations
opencode plugin @azumag/opencode-rate-limit-fallback@2.1.1     # automatic fallback to secondary model on rate limit (429)

# Ollama (last resort offline: runs on NVIDIA GTX 1050 GPU, a few seconds per response with small models)
ollama pull qwen2.5:3b                                          # balanced model (~2 GB, fits in 4 GB VRAM)
ollama pull qwen2.5-coder:3b                                    # code variant (~2 GB, fits in 4 GB VRAM)

# Connect other free providers: prints signup link and asks for key, one at a time
bash ~/.config/opencode/scripts/connect-free-providers.sh

pip install --user --break-system-packages docling "obsidian-mcp-search[server]" pypdf
                                                               # OCR for image slides, semantic note search, book reading

## What's here

| File | Replaces | Notes |
|---|---|---|
| `AGENTS.md` | `AGENTS.md` | from 84 to 38 lines: structure, 9 rules, tools |
| `.opencode/style.md` | the two prompts and `div style.txt` | single source for style, loaded every session |
| `.opencode/rules.md` | new | summary of `no-ai-slop` and `i-have-adhd` in 530 tokens, loaded every session |
| `.opencode/dcp.jsonc` | new | tuning of the plugin that prunes context |
| `~/.agents/skills/no-ai-slop/SKILL.md` | — | no filler text: read every session that writes |
| `~/.config/opencode/vendor/i-have-adhd/skills/i-have-adhd/SKILL.md` | — | layout (one idea per block, lists instead of prose): read every session that writes |
| `.opencode/agents/notes.md` | `vault`, `notes`, `material`, `indices` | single agent that writes |
| `.opencode/agents/reviewer.md` | `reviewer` | checks correctness and verbosity, does not modify |
| `.opencode/commands/` | the 7 commands | `/lesson`, `/review`, `/reviewer`, `/audit`, `/slide`, `/split`, `/book` |
| `.opencode/scripts/vault-audit.py` | old script | rewritten: no tags, frontmatter, yearly indexes |
| `.opencode/scripts/read-slides.py` | old `reader` agent | reads PDF, PPTX and PPT one page at a time; image pages with Docling and OCR Tesseract (it) |
| `.opencode/scripts/books.py` | new | reads books in `books/`: list, index, page, search |
| `.opencode/scripts/split-notes.py` | new | divides a single file into one note per lesson |
| `.opencode/scripts/check-losses.py` | new | verifies nothing is lost in the note compared to source |
| `opencode.json` | `opencode.json` | free default models, fallback chain, shell permissions, MCP server |
| `~/.config/opencode/rate-limit-fallback.json` | — | same fallback chain, valid in every project |
| `~/.config/opencode/scripts/connect-free-providers.sh` | new | connects free providers with keys in one go |
| `Guida_Opencode.md` | `Guida_Opencode.md` | rewritten on the new structure |
| `prompt_chat.md` | — | short prompts for Antigravity and web chat |

## Models: only free, no paid provider

No paid model; for local models only Ollama is needed, which starts alone.

| Role | Model | Why |
|---|---|---|
| default | `opencode/nemotron-3.5-super-vl-free` | first in plugin ranking: writes and reviews notes and accepts images; `nemotron-3-ultra-free` is second choice, most disciplined in tool use |
| session title | `opencode/glm-5.3-flash-free` | flash model, suitable for short tasks |
| plan (`plan`) | `opencode/glm-5.3-flash-free` | same model as title: planning without modifications, with Plannotator |
| compaction | `opencode/nemotron-3-ultra-free` | 1M token window, summarizes without losing note details |
| last resort | `ollama/qwen2.5:3b` (in chain); other Ollama models selectable | offline and without quota, runs on GTX 1050 GPU |

**Fallback chain** (`rate-limit-fallback.json`, 11 models): on quota exhausted or transient error the agent passes to the next, keeping the agent active. When the chain ends it stops (`fallbackMode: "stop"`), without restarting in a loop; a model chosen manually but outside the chain is retried on itself after cooldown (`otherModels: "wait"`). Full order is in the guide; the chain contains only free models with tool support, and local models are at the bottom because they are slower.

**Providers used**: OpenCode free tier (9 models, no key), OpenRouter (21 `:free` models, one key) and Ollama (15 local models, no key). In total the local plugin shows 45 free models and no paid model. Other free providers are connected with `connect-free-providers.sh`; each key serves a separate account, there is no way to bypass it.

**OmniRoute is paused.** The `@omniroute/opencode-plugin` plugin (0.2.1) exports OpenCode 1.x plugin form (`{ id, server }`); OpenCode 2.x accepts only `{ id, effect }` or `{ id, setup }` and rejects loading with *"Plugin must export a default definition with an id and an effect or setup function"*. The plugin is therefore incompatible until upstream publishes a 0.3.x, and has been removed from `opencode.json`. The package remains installed and the `omniroute` service is no longer needed: its archive contains no provider connection, so it would not provide models anyway.

## Tokens: where they go and how they are reduced

A request carries all static context, and that block is resent every turn: it is the most invisible expense.

| | Before | Now |
|---|---|---|
| static block in context (rules, style, agent prompt) | ~11.9k tokens | ~6.8k tokens |
| full request measured (static block + tool schema) | 22,748 input tokens | 19,049 input tokens |
| 157-message session | 13M tokens processed | history pruned to 120k |

Levers used:

- **`.opencode/rules.md`**: the two skills (`no-ai-slop`, `i-have-adhd`) cost 4.5k tokens per request and per subagent; now `instructions` has a 530-token summary and full files are read only when writing a note (the agent prompt already says so).
- **DCP tuned** (`.opencode/dcp.jsonc`): prunes also in subagent sessions (`allowSubAgents`), leaves last 3 turns intact (`turnProtection`), and warns the model before it enters a loop (`iterationNudgeThreshold` 10 instead of 15).
- **`compaction.keep.tokens: 12000`**: after compaction useful context remains instead of starting from zero.
- **The most disciplined model**: tokens grow with tool call count, and free models are not equal (see the guide).

Not done, to avoid losing quality: truncating tool outputs (`tool_output`), removing `style.md` from `instructions` (DCP might compress it via), giving up MCP server `obsidian-search` or `parse` plugin.

## Choices, and why

**Style comes from your notes.** The first sections of both files ("Compilers and interpreters", "Hardware evolution and multiprogramming") have Every Word Capitalized, `[!NOTE] Teacher's Note`, bold everywhere, titles like "The Engine of Infinity": this is the AI style you want to avoid. Further on style changes: `*Definition:*`, `**Topic:**` labels at paragraph start, `-` lists, glosses with ` = `, `<u>` for key sentence, lowercase callouts. `style.md` encodes this second style and puts the first among things not to do. You neither confirmed nor corrected it: if I read it wrong, it is `style.md` the file to change.

**Nothing the teacher said is lost.** Rule 2 of `AGENTS.md` and opening of `style.md`: the agent fixes form, corrects and adds; removes only words. In the first version the rule protected only some categories (definitions, theorems, formulas) and for slides said "one example per concept, skip background slides": it left the model choosing what was secondary. Now it does not leave it. Plus `check-losses.py`: the agent saves a copy before modifying and at the end the script lists formulas, code, images, numbers, lines and slide pages it does not find. It is a word-by-word comparison, so it reduces risk but does not eliminate it: on important notes it is still useful to check `git diff`.

**Two agents instead of six.** With a free model every subagent is a new session that must reread everything. I kept only the separation that matters: who writes and who checks. The reviewer works in a clean context, so it is not influenced by what the other just wrote. `vault`, `material` and `indices` became cases inside `notes`. `reader` became a script.

**The default model is the first in plugin ranking, not the best in absolute.** Free models were tested on four tasks (read a file and count, write and execute Python, probability, structure a document) and then on two behavior tests. Results: `nemotron-3-ultra-free` solves everything and uses 4 tools where `minimax-m3.1-flash-free` uses 22; neither looped (zero identical repeated calls), but `minimax` ended up writing inside a real note when asked only for text, and adds a final "Summary"; `deepseek-v4.1-flash-free` writes well but searches in wrong folders; `glm-5.3-flash-free` contradicts itself; on OpenRouter `nemotron-3-super-120b:free` and `gemma-4-31b-it:free` failed all tasks, `nemotron-3-ultra-550b:free` solves them but takes 12 minutes. On writing rule compliance all are similar (zero forbidden words): on ADHD rule compliance only `minimax` uses a numbered list, and no free model starts with the action. Hence current order: `nemotron-3.5-super-vl-free` is default because it accepts images; `nemotron-3-ultra-free` is second choice, most disciplined. (`minimax-m3.1-flash-free` is no longer in catalog: remains cited only as comparison term of tests.)

**The OpenRouter key was wrong.** In OpenCode the OmniRoute local key was saved, not an OpenRouter key: requests ended with 401 "Missing Authentication header" and every OpenRouter model was unusable. The real key was already on the machine (`~/.aider/oauth-keys.env`) and was reconnected; wrong credentials were deleted.

**The reviewer runs once, at lesson end.** It starts with `/lesson` and `/review`. After any modification the agent only updates the index and runs the structural check.

**`/review` modifies.** It reviews and applies. With `solo report` it does not touch anything. Fixed rule: never removes definitions, theorems, demonstrations, formulas, code, examples, images.

**Dividing old files is done by a script, not the model.** A model recopying 180 KB of notes into 20 files loses pieces. `split-notes.py` copies text identically; the model intervenes after, with `/review`, one note at a time.

**`style.md` is always loaded** (`instructions` field of `opencode.json`): a weak model sometimes skips reading, and style is exactly the part that must not be skipped.

**The three additions.** *Books:* books in `books/<Course name>.pdf` are read with `books.py` (list, summary from bookmarks, one page, search) and `/book` command; they remain a complement, never a default source (rule 11). *Docling:* if a PDF has no text level (scanned pages or slides exported as images), `read-slides.py` reads it alone with Docling, which uses Tesseract in Italian and English for OCR; layout models download from HuggingFace in `~/.cache/huggingface` on first use, so first use needs network; on long files it skips, to avoid taking minutes, and reports it. *Semantic search:* MCP server `obsidian-search` indexes `first semester/` notes and searches them by meaning (multilingual model `paraphrase-multilingual-MiniLM-L12-v2`, kept in `~/.cache/fastembed`), useful to find where a topic is covered and to create wikilinks. *Fallback & DCP:* `@tarquinen/opencode-dcp` optimizes context pruning redundant outputs (tuned in `.opencode/dcp.jsonc`); `@azumag/opencode-rate-limit-fallback` avoids blocks passing automatically to a secondary model on quota exhausted (429), with 11-model free chain. Local Ollama models are last resort offline: on this machine there is a NVIDIA GTX 1050 GPU (`nvidia-smi` works) and small models (`qwen2.5:3b`, `qwen2.5:1.5b`) respond in a few seconds. 7b models do not fit in 4 GB VRAM and remain on CPU, so do not use them for title or compaction.

**The three style sources apply to every model.** `style.md`, `no-ai-slop` and `i-have-adhd` are the three vault writing rules: the first is in `.opencode/style.md`, the other two in `~/.agents/skills/` and `~/.config/opencode/vendor/`. In `instructions` there are `style.md` and `.opencode/rules.md` (summary of the two skills): they cost 4.5k tokens per request and per subagent, and free models are not the most attentive. Full versions of the two skills are read by the agent when it must write, because the prompt asks it; files remain outside the vault so the agent cannot modify them (`edit` denies `.opencode/**`). `style.md` remains always in context: it is the part that must not be skipped.

**Removed:** tag table, years and Erasmus, frontmatter, navigation footer, `raw_notes/`, `attachments/`, `NN_` numbering, non-ASCII character ban, `[!NOTE]` and `[!LAW]` callouts, old prompt example models.

**`esercizi/` is yours.** The `esercizi/` folder of each course contains code written by you (`.py`, `.html`, `.sql`, subfolders for exam). It is input like slides: the agent reads it to link it from notes but does not modify it and does not execute code. If you ask for an exercise it gives it in the answer and you save it. `vault-audit.py` skips the folder (`.md` inside are not notes) and `check-losses.py` reads files linked from the note, so code moved to `esercizi/` does not result lost.

**Permissions.** The `permissions` block of `opencode.json` makes technical what `AGENTS.md` asks: `edit` denies everything except `.md`, with explicit denial for `AGENTS.md`, `.opencode/**`, `*/esercizi/*` (after `*.md`, so last matching rule wins), `opencode.json`, `CONFIG-CHANGES.md` and the two `prompt/` files; `bash` is in allowlist (five scripts, `ls`, `grep`, `rg`, `wc`, `pdfinfo`, `pdftotext`, `tesseract`, read-only git); `external_directory` prevents leaving the vault. `pdftoppm` and `split-notes.py --write` ask for confirmation.

**Bash no longer blocks mid-chain.** OpenCode checks permissions command by command, even in a pipe: `script.py \| head -40` evaluates `script.py` *and* `head -40`, and if the second is not in allowlist the whole chain is denied. For this allowlist also contains pipe recipients and chain operators (`head`, `tail`, `cat`, `sort`, `uniq`, `cut`, `tr`, `jq`, `diff`, `basename`, `dirname`, `cd`, `pwd`, `which`, `echo`, `find`). The price is these programs can write, so there are three shields, placed after so last matching rule wins: `echo*>*` (no files created with redirection), `find* -delete*` and `find* -exec*` (no deletions nor arbitrary commands), `*env*` (no `cat .env`, `printenv`). `sed`, `awk`, `tee`, `xargs` remain out: they write or execute, and vault inputs are not touched.

## Implementation details

| 1 | no date in note | `#` title and file name have no date; recommended name `Lesson 3-Graph search.md` |
| 2 | index and modules | `00 Index - <Course>.md` in every course or module folder |
| 4 | one `.txt` per lesson | agent looks for `.txt` with same name or same date as note, otherwise asks |
| 5 | git from terminal | guide uses `git diff` and `git restore` |
| 6 | divide single files | script `split-notes.py` and command `/split` |
| 7 | `// fit //` | replaces `// 400 //`: full-width image |
| 7b | layout of image without placeholder | agent asks a single `question` listing all images in order (resize / fit / caption below / text beside / leave as is), text from OCR if available |
| 9 | images in callouts | remain `![[x.png|300]]` |
| 10 | `→` in formulas | no conversion, no check |
| 11 | only `// ... //` | `%% ... %%` removed everywhere |
| 12 | em dash, web sources | INFO only in audit; no source cited |
| 13 | summary at lesson end | every note closes with `> [!info] Summary:` (3-6 points); audit reports if missing |
| 14 | length | no line limit: `style.md` asks for density (each concept once, explanation proportioned to difficulty, cut words not content). Audit reports single paragraphs over 150 words as INFO |
| 15 | configuration and file creation | agent does not modify configuration and does not create notes |
| 16 | reviewer | one pass, only with `/lesson` and `/review` |
| 17 | compaction | `auto` and `keep.tokens: 12000` in `opencode.json`; continuous pruning by DCP plugin |

## Migrating old notes to new format (from single file to multiple files)

Note that with a multi-agent system it is convenient to have smaller files (it also guarantees consistent token saving)

`/split "path/Notes course.md"` shows the plan and writes only after confirmation. The script cuts on `###` headings, derives date of each section from first image name and joins consecutive sections with same date. Dates come from screenshots, so they are approximate: used to group sections, never to name files. Then `/review` one note at a time: it trims, adds summary and reports word count before and after. Make a commit before starting.

Note that with a multi-agent system it is convenient to have smaller files (it also guarantees consistent token saving)
