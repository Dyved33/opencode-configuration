---
description: Launches the reviewer on a note (correctness, completeness, verbosity) without modifying anything. Skill callable, report-only
agent: reviewer
---

Review: $ARGUMENTS

- The first argument is the note. Any additional paths are the teacher's material; if none, look for them in the same folder.
- The reviewer does not modify any file: it returns a list of corrections, from most to least severe, one per line: [ERROR], [MISSING], [CUT], [STYLE], [FORM].
- Close with a judgment line: `Note correct` / `To correct: N errors` and an estimate of how much can be cut.
- Do not apply corrections: it is up to the user to do so, via `/review`, or by asking the `notes` agent.
