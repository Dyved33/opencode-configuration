---
description: Reviews a note (correctness, completeness, verbosity) and applies corrections. With "solo report" it does not modify anything
agent: notes
---

Review: $ARGUMENTS

- If the argument is a note or a folder, work on those notes. If it is `diff`, work on notes modified according to `git status` and `git diff`. If empty, ask what to review.
- If there are multiple notes, work on one note at a time and stop after each one with the summary, asking whether to continue with the next.

Procedure:

1. Save a copy of the note: `python3 .opencode/scripts/check-losses.py "note" --save`. Then call the subagent `reviewer` on the note and on the teacher's material found in the same folder.
2. If the arguments contain `solo report`, stop here and return its list without modifying anything.
3. Otherwise apply the corrections: first [ERROR] and [MISSING], then [CUT] and [STYLE]. Condense according to case D: remove words, never information. If something is missing, add the final summary.
4. Run `python3 .opencode/scripts/check-losses.py "note"`. For each reported voice, reread the saved copy: if information is missing in the note, put it back.
5. Run `python3 .opencode/scripts/vault-audit.py` on the note and fix what depends on you.
6. Summary in at most 5 lines: words before and after, what you removed and why, loss check result.
