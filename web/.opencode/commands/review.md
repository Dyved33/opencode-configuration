---
description: Has changed or given code reviewed (correctness, accessibility, SEO, security, style) and applies the corrections. With "report only" it modifies nothing
agent: webdev
---

Review: $ARGUMENTS

- If the argument is a file or a folder, work on those. If it is `diff`, work on what `git status` and `git diff` show. If it is empty, ask what to review.
- If there are several files or folders, work one at a time and stop after each one with the summary, asking whether to continue with the next.

Procedure:

1. Call the `reviewer` subagent on the code to review: pass the paths and one line saying what the change was supposed to do.
2. If the arguments contain `report only`, stop here and report its list without modifying anything.
3. Otherwise apply the corrections: first `[ERROR]` and `[SECURITY]`, then `[A11Y]` and `[SEO]`, then `[STYLE]` and `[SCOPE]`. Fix, don't rewrite: the change stays as small as it was. Nothing that is already correct gets touched.
4. Run the lint/build script if the project has one, and fix what the change broke (never an unrelated pre-existing failure: report it instead).
5. Summary in at most 5 lines: files touched, what you corrected and why, checks run and their result.
