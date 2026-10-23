---
description: Runs the reviewer on a note (correctness, completeness, verbosity) without modifying anything. Callable skill, report-only
agent: reviewer
---

Review: $ARGUMENTS

- The first argument is the note. Any other paths are the teacher's material; if there are none, look for them in the same folder.
- The reviewer does not modify any file: it returns a list of corrections, from the most serious to the least serious, one item per line: [ERROR], [MISSING], [CUT], [STYLE], [SHAPE].
- Close with a single verdict line: `Note correct` / `To correct: N errors` and the estimate of how much can be trimmed.
- Do not apply the corrections: it is up to the user to do so, or via /review, or by asking the notes agent.
