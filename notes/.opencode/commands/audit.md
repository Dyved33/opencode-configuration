---
description: Structural check of a note, a course, or the whole vault (links, images, LaTeX, callouts, placeholders, todo). Does not modify anything
---

This is the result of the structural check on: $ARGUMENTS (if empty, the whole vault).

!`python3 .opencode/scripts/vault-audit.py $ARGUMENTS --breve`

Do not modify any file. Report the result as follows:

1. ERRORs, grouped by file, with the line.
2. WARNs, grouped by type, with how many times they appear and in which files.
3. INFOs in one line: how many open todos and how many long paragraphs.

Close saying which problems you can fix if the user asks you to, and which require the user (e.g. missing images).
