---
description: Splits a single notes file into one file per lesson. Usage - /split "path/Notes course.md" (add --per-section for one file per section)
agent: notes
---

This is the plan to split the file into one note per lesson. The script has not written anything yet:

!`python3 .opencode/scripts/split-notes.py $ARGUMENTS`

Procedure:

1. Show the plan as-is and ask for confirmation. Image names are only used to group sections: the date does not appear in files nor in the index. Report groups without images, which remain separate.
2. After confirmation, run the same command with `--write` at the end. The text is copied by the script: do not rewrite and do not copy the notes yourself.
3. Run `python3 .opencode/scripts/vault-audit.py --breve` on the folder and report only the counts.
4. Do not condense the notes now. Close saying that the next step is `/review` one note at a time, and that the source file should be archived or deleted by the user.
