# OpenCode guide for this vault

## Starting up

OpenCode must be started from the general notes folder, the one that contains `opencode.json`:

```bash
cd path/to/notes/folder
opencode
```

After any change to `opencode.json` or to a file in `.opencode/` it has to be restarted: the configuration is only read at startup.

## How it is organized

| File | What it is for |
|---|---|
| `AGENTS.md` | the few rules that always apply. It is read at every session |
| `.opencode/style.md` | how the notes must be written. It is loaded at every session |
| `.opencode/agents/` | the 2 agents |
| `.opencode/commands/` | the 5 commands |
| `.opencode/scripts/` | the 4 scripts: slide reading, structural check, loss check, splitting of single files |
| `opencode.json` | permissions |
| `chat_prompt.md` | prompts to use outside OpenCode (Antigravity, web chat) |
| `<Course>/esercizi/` | the code you write (input): the agent doesn't touch it |

To change the note style you edit only `.opencode/style.md`.

## The flow of a lesson

1. You create the note, with the date in the name: `2026-10-02 Automi a pila.md`. In the same folder you put the raw notes (`.txt`, one per lesson), the slides and, in `images/`, the images.
2. You write what you have in the note, with the `// ... //` placeholders where needed.
3. While working you can ask for word-level changes: the agent writes, updates the index and checks the structure. It doesn't call the reviewer.
4. When the lesson is finished you launch `/lesson`: it completes the note, writes the final summary, lets the reviewer run once and applies the corrections.

## Nothing is lost

The rule is rule 2 of `AGENTS.md`: everything in your notes, in the raw notes and in the slides stays in the note; the agent only removes words. A written rule, though, is not enough, because a model can make mistakes: that is why the check is done by a script.

1. before editing a note the agent saves a copy of it in `.opencode/originals/`;
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
/lesson "Primo semestre/Linguaggi/2026-10-02 Automi a pila.md"
/lesson "Primo semestre/Linguaggi/2026-10-02 Automi a pila.md" "Primo semestre/Linguaggi/automi.pdf"
```

It understands by itself which case it is in:
- the note already has text: it integrates it (placeholders, errors, missing parts) without rewriting it;
- the note is empty and there is a `.txt`: it writes it from the raw notes;
- the note is empty and there is only the material: it writes it from the slides.

**`/review`** has a note reviewed and applies the corrections: errors, missing parts, cuts. It is the command for trimming verbose notes: it removes words, not content, and has no length target to reach. On a folder it works one note at a time and stops after each one.

```
/review "Primo semestre/SO/2026-03-19 Semafori, Messaggi.md"
/review "Primo semestre/SO/2026-03-19 Semafori, Messaggi.md" report only     # modifies nothing
/review diff                                            # the notes modified and not yet committed
```

**`/audit`** runs the structural check and reports the result. It modifies nothing.

```
/audit                                  # the whole vault
/audit "Primo semestre/Linguaggi"       # a course
```

It finds: broken links, missing images, unclosed formulas and code blocks, unbalanced `<div>`, wrong callouts, unresolved placeholders, lessons missing from the index, file name without a date, missing final summary, frontmatter and tags, titles that break the conventions, typical AI phrases, open `[!todo]`, very long paragraphs.

**`/slide`** shows the text of a page of the material, so you can check it with your own eyes.

```
/slide "Primo semestre/Linguaggi/automi.pdf" 28
/slide "Primo semestre/Linguaggi/automi.pdf" 19-21
/slide "Primo semestre/Linguaggi/automi.pptx" --search "pila vuota"
```

**`/split`** splits a single notes file into one note per lesson. It is needed only once, for the notes written so far.

```
/split "Primo semestre/SO/Appunti teoria SO.md"
/split "Primo semestre/SO/Appunti teoria SO.md" --per-section
```

It shows the plan first and only writes after your confirmation. See below.

Paths with spaces must always be quoted.

## Converting old notes to the new format

1. `/split "path/Notes course.md"`. The script cuts the file on the `###` headings, derives the date of each section from the name of its first image and puts consecutive sections with the same date into the same note. The text is copied identically, it doesn't go through the model.
2. Check the plan. The dates are those of the screenshots, so they are approximate. The first sections usually have no images and stay dateless: the date has to be added by hand to the file name.
3. Confirm: it creates the notes and the index in the same folder. The single file stays intact: archive it or delete it yourself when you have checked.
4. If a date or a title is wrong, rename the file from Obsidian: the index links update by themselves.
5. `/review` on one note at a time. Every pass trims, adds the final summary and reports the word count before and after.

## What to write in the notes

**Placeholders.** Outside code blocks, `// ... //` is an instruction for the agent, to be carried out at that point:

```
// slide 28 //                         bring here the content of slide 28
// def automa a pila //                look for the definition in the material
// approfondire con un esempio //      any other request
```

The placeholder disappears once it has been carried out. If the agent can't, it replaces it with a `[!todo]`.

**Images.** After the image you indicate the layout:

```
![[x.png]]                        no placeholder: the agent asks (resized to 300 if you don't care)
![[x.png]] // adatta //           fitted to the width of the page
![[x.png]] // sotto: testo //     with a caption underneath
![[x.png]] // lato: testo //      with text alongside
![[x.png]] // lato //             the paragraph that follows goes alongside
```

If you don't write a placeholder, the agent asks you which layout to use, one question per image. The text for the caption or for the text alongside comes from the OCR or the agent asks you for it, and if you don't write it, it falls back to a resize.

Inside a callout the image stays `![[x.png|300]]`. The model cannot see the images: it never describes what they show unless your text or the OCR does.

**Todo.** `> [!todo] cosa va rivisto` marks a point to check. The agent tries to close them on every pass and leaves new ones when it is not sure about something. `/audit` lists them all.

**Sintesi.** Every note ends with `> [!info] Sintesi:`, 3 to 6 points. It is written by the agent with `/lesson` and `/review`.

**Code.** The snippet that serves the theory stays in the note, in a ```` ``` ```` block. The exercises and the complete solutions live in `esercizi/`, with the name you choose: the note keeps only the relevant piece with the wikilink `[[esercizi/es3.py|es3]]`. The files in `esercizi/` are yours: the agent never opens them for writing, and if you ask for an exercise it gives it to you in the answer and you save it.

## What OpenCode can and can't do

- It writes only `.md` files. It cannot modify `AGENTS.md`, the files in `.opencode/` or anything in `esercizi/`.
- It doesn't create notes: you create them and it fills them. It can only create the course index. The only exception is `/split`, which asks for confirmation.
- It doesn't touch `.txt`, PDFs, slides, images and the files in `esercizi/`. It doesn't run code.
- It doesn't leave the vault.
- In the terminal it can only run the four scripts, `ls`, `grep`, `rg`, `wc`, `pdfinfo`, `pdftotext` and the read-only git commands. For `pdftoppm` (which creates images) it asks for confirmation.
- It can search the web.
- It doesn't commit or push: those stay with you.

## The scripts, by hand too

```bash
python3 .opencode/scripts/read-slides.py FILE              # page list
python3 .opencode/scripts/read-slides.py FILE 28           # one page
python3 .opencode/scripts/read-slides.py FILE --search "x" # where x appears
python3 .opencode/scripts/vault-audit.py "Primo semestre/Linguaggi"
python3 .opencode/scripts/vault-audit.py --short           # only ERROR and WARN
python3 .opencode/scripts/check-losses.py NOTE --save      # copy before editing
python3 .opencode/scripts/check-losses.py NOTE             # what was lost compared to the copy
python3 .opencode/scripts/check-losses.py NOTE --with SOURCE   # compared to a .txt or the slides
python3 .opencode/scripts/split-notes.py FILE             # split plan
python3 .opencode/scripts/split-notes.py FILE --write     # creates the notes
```

`read-slides.py` reads PDF, PPTX and PPT (the PPTs are converted with LibreOffice into a temporary folder). If a file is made only of images it says so: in that case the content has to be read by hand.

## The opencode-parser plugin

It adds the `parse` tool, which extracts the text from PDF, Word, PowerPoint and, with OCR, from images. It doesn't create or insert images. Here it is used for one thing only: reading the text inside a screenshot (`parse` with OCR in Italian). For slides and PDF the agent uses `read-slides.py`, because `parse` returns the document from the start and not a precise page.

## When something goes wrong

- **An agent or a command doesn't appear:** restart OpenCode.
- **OpenCode won't start because of a configuration error:** `OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode`, fix it and restart. To see the configuration OpenCode actually loaded: `opencode debug config`.
- **The agent wrote too much or ruined a note:** `git diff` shows what changed, `git restore "path"` brings the note back to the last commit. Without git, the previous version is in `.opencode/originals/`. It is worth committing before `/review` and `/split`.
- **An image inside a `<div>` is not visible:** check that the name in `src` is identical to the file's. If it is right and it still doesn't show, see `LEGGIMI.md`.
- **Vague requests:** "improve the note" produces a random rewrite. Better "the section on semaphores is too long, trim it" or a placeholder in the right spot.