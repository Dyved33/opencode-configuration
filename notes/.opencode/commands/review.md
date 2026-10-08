---
description: Has a note reviewed (correctness, completeness, verbosity) and applies the corrections. With "report only" it modifies nothing
agent: notes
---

Review: $ARGUMENTS

- If the argument is a note or a folder, work on those notes. If it is `diff`, work on the notes modified according to `git status` and `git diff`. If it is empty, ask what to review.
- If there are several notes, work one at a time and stop after each one with the summary, asking whether to continue with the next.

Procedure:

1. Save a copy of the note: `python3 .opencode/scripts/check-losses.py "note" --save`. Then call the `reviewer` subagent on the note and on the teacher's material you find in the same folder.
2. If the arguments contain `report only`, stop here and report its list without modifying anything.
3. Otherwise apply the corrections: first the `[ERROR]` and the `[MISSING]`, then the `[CUT]` and the `[STYLE]`. Trim according to your case D: words are removed, never information. If it is missing, add the final summary.
4. Run `python3 .opencode/scripts/check-losses.py "note"`. For every item reported reread the saved copy: if the information is missing from the note, put it back.
5. Run `python3 .opencode/scripts/vault-audit.py` on the note and fix what depends on you.
6. Summary in at most 5 lines: words before and after, what you removed and why, the outcome of the loss check.