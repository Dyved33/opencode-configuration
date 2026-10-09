# AGENTS.md

Obsidian vault of university notes. One note = one lesson.

## Structure

```
Primo semestre/
  <Course>/                     a course (or <Course>/<Module>/ if the course has several modules)
    00 Index - <Course>.md     index: one line per lesson, with date and title
    YYYY-MM-DD Title.md         one note per lesson, created by the user
    *.txt                      raw notes, one per lesson (input)
    *.pdf, *.ppt, *.pptx       teacher's material (input)
    images/                    note images (input)
    esercizi/                  code written by the user (input), subfolders too
```

## Rules that always apply

1. **Style.** The writing rules are in `.opencode/style.md`. OpenCode loads them by itself; with other tools read them before writing.
2. **Nothing is lost.** Every piece of information in the user's notes, in the raw notes or in the teacher's material must be in the final note: in the exam what the teacher said has to be reproduced. You may fix the style, reorder, correct and add. You may remove only words: fillers and repetitions of the same information. When in doubt, keep it.
3. **The user's text rules.** In an existing note touch only what is wrong, unclear, missing or indicated by a placeholder. Don't rewrite what works.
4. **Don't create files.** The user creates the lesson notes, you fill them: neither notes nor code. The only exceptions are the course index, if it is missing, and the slide photos the user asked for (Tools table). If you are asked to write an exercise, the code goes in the answer, in a block labelled with the language, together with the `esercizi/` path to save it to: never open those files for writing.
5. **Inputs are not touched.** Never modify, rename, move or delete `.txt`, PDFs, slides, images and the files in `esercizi/`.
6. **No frontmatter and no tags.** The date lives only in the file name.
7. **Sources.** First the teacher's material, then the web to complete. If they contradict each other, the teacher wins and you leave a `[!todo]`.
8. **Git in read-only.** Commits and pushes are up to the user.
9. **Final summary.** Close every job with at most 5 lines: files touched, what you added, corrected and removed, the `[!todo]` you left.
10. **Stop on loops.** If the same action fails three times or brings no progress, stop and ask the user instead of retrying. Another attempt adds cost, not certainty.

## Tools

| What | How |
|---|---|
| Read slides and PDFs | `python3 .opencode/scripts/read-slides.py FILE [pages]` |
| Photo of a slide | ask the user whether to take it (`pdftoppm*` asks for confirmation); if yes: `pdftoppm -png -r 150 -f N -l N "FILE" "images/slide"` and read the description with `tesseract "images/slide-NN.png" stdout -l it`; if no: move on |
| Structural check | `python3 .opencode/scripts/vault-audit.py [path]` |
| Check that nothing was lost | `python3 .opencode/scripts/check-losses.py NOTE [--save] [--with SOURCE]` |
| Split a single file into lessons | `python3 .opencode/scripts/split-notes.py FILE` |
| Write and integrate notes | agent `notes` |
| Correctness and style check | agent `reviewer`: modifies nothing, one pass at the end of a lesson |