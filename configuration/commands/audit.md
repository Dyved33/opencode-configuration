---
description: Structural check of a note, a course or the whole vault (links, images, LaTeX, callouts, placeholders, todo). Modifies nothing
---

This is the result of the structural check on: $ARGUMENTS (if empty, the whole vault).

!`python3 .opencode/scripts/vault-audit.py $ARGUMENTS`

Don't modify any file. Report the result like this:

1. The ERRORs, grouped by file, with the line.
2. The WARNs, grouped by type, with how many times they occur and in which files.
3. The INFOs in a single line: how many open todos and how many long paragraphs.

Close by saying which problems you can fix yourself if the user asks you to and which require them (for example the missing images).