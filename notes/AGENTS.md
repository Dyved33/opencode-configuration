# AGENTS.md

Obsidian vault of university notes. One note = one lesson.

## Structure

```
books/                          textbooks, one PDF per course (input)
first semester/
  <Course>/                     a course (or <Course>/<Module>/ if the course has modules)
    00 Index - <Course>.md     index: one line per lesson, with title
    Title.md                    one note per lesson, created by the user
    *.txt                      raw notes, one per lesson (input)
    *.pdf, *.ppt, *.pptx       teacher's material (input)
    images/                    note images (input)
    esercizi/                  code written by the user (input), also in subfolders
rollback/                      old single files before lesson division: not notes
.review/                       review work: not notes
```

Notes are only inside `first semester/`: search, grep and index there, not in the rest of the vault.

## Rules that always apply

1. **Style.** The writing rules are in `.opencode/style.md`. OpenCode loads them automatically; with other tools or other models read them before writing, together with the skills `~/.agents/skills/no-ai-slop/SKILL.md` (no filler text) and `.opencode/skills/i-have-adhd/SKILL.md` (layout: one idea per block, answer first, lists instead of prose). They apply to every model, even small or automatically chosen ones.
2. **Nothing is lost.** Every piece of information that is in the user's notes, in the raw notes or in the teacher's material must be in the final note: for the exam what the teacher said must be reported. You can fix style, reorder, correct and add. You can remove only words: fillers and repetitions of the same information. In doubt, keep it.
3. **The user's text commands.** In an existing note modify only what is wrong, unclear, missing or indicated by a placeholder. Do not rewrite what works.
4. **Do not create files.** Lesson notes are created by the user, you fill them: neither notes nor code. The only exception is the course index, if missing, and the slide photos the user asked for (Tools table). If asked to write an exercise, the code goes in the answer, in a block with the language label, with the `esercizi/` path where to save it: do not open those files for writing.
5. **Inputs are not touched.** Never modify, rename, move or delete `.txt`, PDFs, slides, images, the books in `libri/` and the files in `esercizi/`.
6. **No frontmatter and no tags.**
7. **Sources.** First the teacher's material, then the web to complete. If they contradict each other, the teacher wins and leave a `[!todo]`.
8. **Git read-only.** Commits and pushes are done by the user.
9. **Stop on loops.** If the same action fails after two equivalent attempts (even with different input) or brings no progress or after a timeout, stop and ask the user instead of retrying. Another attempt adds cost, not certainty. No parallel tesseract.
10. **Final chapter from the book.** If a textbook exists for the course in `libri/` and there is relevant content to add on the lesson's topics, add a final chapter to the note with information from the book about the arguments covered. The note is complete without the book: it is a complement, not a default source.

## Tools

| What | How |
|---|---|
| Read slides and PDFs | `python3 .opencode/scripts/read-slides.py FILE [pages]` (image pages are read with Docling/OCR) |
| Search a lesson by topic | MCP server `obsidian-search` (tool `search`), or `python3 .opencode/scripts/vault-audit.py` for structure |
| Photo of a slide | ask the user whether to take it (`pdftoppm*` asks for confirmation); if yes: `pdftoppm -png -r 150 -f N -l N "FILE" "images/slide"` and read the description with `tesseract "images/slide-NN.png" stdout -l it`; if no: move on |
| Structural check | `python3 .opencode/scripts/vault-audit.py [path]` |
| Check that nothing was lost | `python3 .opencode/scripts/check-losses.py NOTE [--save] [--with SOURCE]` |
| Divide a single file into lessons | `python3 .opencode/scripts/split-notes.py FILE` |
| Write and integrate notes | agent `notes` |
| Correctness and style check | agent `reviewer` and command `/reviewer`: does not modify anything, report-only; one pass at lesson end |
