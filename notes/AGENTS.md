# AGENTS.md

Obsidian vault of university notes. One note = one lesson.

## Structure

```
books/                          textbooks, one PDF per course (input)
<Semester>/                     a folder that groups the courses
  <Course>/                     a course (or <Course>/<Module>/ if the course has modules)
    00 Index - <Course>.md     index: one line per lesson, with the title
    Lesson N - Title.md        one note per lesson, created by the user
    *.txt                      raw notes, one per lesson (input)
    *.pdf, *.ppt, *.pptx       teacher's material (input)
    images/                    note images (input)
    esercizi/                  code written by the user (input), subfolders too
```

The courses are the folders that contain the lessons: search, grep and index them,
not the rest of the vault. The name of the semester folder is yours: the agent finds
the courses by looking for the folders that hold a `00 Index - ....md` file.

The textbooks live in `books/` (the name is configurable with the `BOOKS_DIR`
environment variable, default `books`).

## Rules that always apply

1. **Style.** The writing rules are in `.opencode/style.md`, the writing discipline in `.opencode/rules.md`. OpenCode loads both by itself; with other tools or other models read them before writing. They apply to every model, even a small one or one chosen automatically.
2. **Nothing is lost.** Every piece of information in the user's notes, in the raw notes or in the teacher's material must be in the final note: in the exam what the teacher said has to be reproduced. You may fix the style, reorder, correct and add. You may remove only words: fillers and repetitions of the same information. When in doubt, keep it.
3. **The user's text rules.** In an existing note touch only what is wrong, unclear, missing or indicated by a placeholder. Don't rewrite what works.
4. **Don't create files.** The user creates the lesson notes, you fill them: neither notes nor code. The only exceptions are the course index, if it is missing, and the slide photos the user asked for (Tools table). If you are asked to write an exercise, the code goes in the answer, in a block labelled with the language, together with the `esercizi/` path to save it to: never open those files for writing.
5. **Inputs are not touched.** Never modify, rename, move or delete `.txt`, PDFs, slides, images, the books in `books/` and the files in `esercizi/`.
6. **No frontmatter and no tags.** The date is written neither in the file name nor in the note.
7. **Sources.** First the teacher's material, then the web to complete. If they contradict each other, the teacher wins and you leave a `[!todo]`.
8. **Git in read-only.** Commits and pushes are up to the user.
9. **Final summary.** Close every job with at most 5 lines: files touched, what you added, corrected and removed, the `[!todo]` you left.
10. **Stop on loops.** If the same action fails after two consecutive attempts (even with different inputs) or brings no progress or after a timeout, stop and ask the user instead of retrying. Another attempt adds cost, not certainty. No parallel tesseract.
11. **Textbooks.** The books live in `books/<Course name>.pdf`, one per course, and are read with `python3 .opencode/scripts/books.py` (command `/book`). A note is complete without the book: it is a complement, not a default source. Take nothing from the book without the user's consent: when the lesson is over ask once, with the `question` tool, whether to integrate it as a complement; if they say no, the book stays out. When you use it, rules 2 and 7 apply.

## Tools

| What | How |
|---|---|
| Read slides and PDFs | `python3 .opencode/scripts/read-slides.py FILE [pages]` (image pages are read with Docling/OCR) |
| Read a textbook | `python3 .opencode/scripts/books.py` with `list`, `info FILE`, `toc FILE`, `page FILE 28`, `search FILE "text"` (command `/book`) |
| Search a lesson by topic | MCP server `obsidian-search` (tool `search`), or `python3 .opencode/scripts/vault-audit.py` for the structure |
| Photo of a slide | ask the user whether to take it (`pdftoppm*` asks for confirmation); if yes: `pdftoppm -png -r 150 -f N -l N "FILE" "images/slide"` and read the description with `tesseract "images/slide-NN.png" stdout -l <lang>` (`<lang>` is the language of the notes, `it` for Italian); if no: move on |
| Structural check | `python3 .opencode/scripts/vault-audit.py [path]` |
| Check that nothing was lost | `python3 .opencode/scripts/check-losses.py NOTE [--save] [--with SOURCE]` |
| Split a single file into lessons | `python3 .opencode/scripts/split-notes.py FILE` |
| Write and integrate notes | agent `notes` |
| Correctness and style check | agent `reviewer`: modifies nothing, one pass at the end of a lesson |
