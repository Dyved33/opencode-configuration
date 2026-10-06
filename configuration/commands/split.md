---
description: Splits a single notes file into one file per lesson. Usage - /split "path/Notes course.md" (add --per-section for one file per section)
agent: notes
---

This is the plan to split the file into one note per lesson. The script has not written anything yet:

!`python3 .opencode/scripts/split-notes.py $ARGUMENTS`

Procedure:

1. Show the plan as it is and ask for confirmation. The dates come from the image names and are approximate: point out the files without a date and the ones with the date taken from the previous section.
2. After the confirmation run the same command with `--write` at the end. The script copies the text: don't rewrite or copy the notes yourself.
3. Run `python3 .opencode/scripts/vault-audit.py --short` on the folder and report only the counts.
4. Don't trim the notes now. Close by saying that the next step is `/review` on one note at a time, and that the starting file must be archived or deleted by the user.