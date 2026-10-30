---
description: Close a note: loss check, structure check and reviewer in a single flow. Report-only, modifies nothing.
agent: notes
---

Close note: $ARGUMENTS

- The first argument is the note to close. Any additional paths are the teacher's material; if none are provided, look for them in the same folder.
- This command does not modify any files: it returns a unified report. To apply corrections, use `/review` afterwards.

Procedure:

1. Save a backup copy: `python3 .opencode/scripts/check-losses.py "note" --save`
2. Run `python3 .opencode/scripts/check-losses.py "note"` and report missing items (formulas, code lines, images, numbers, source lines not found in the note).
3. Run `python3 .opencode/scripts/vault-audit.py "note" --breve` and report ERROR and WARN.
4. Call the subagent `reviewer` on the note and material, and report its [ERROR], [MISSING], [CUT], [STYLE], [FORM] list.
5. Close with a judgment line: `Note correct` / `To correct: N errors` / `To complete: N missing items`, and state whether the note is ready to be closed.
