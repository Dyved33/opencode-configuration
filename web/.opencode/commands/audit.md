---
description: Structural check of the project: lint and build, TODO, console.log, dead code, missing alt and meta, broken internal links. Modifies nothing
---

Check: $ARGUMENTS (if empty, the whole project).

Run these checks yourself, in this order, and only the ones that apply to the project:

Run the checks in batches: independent commands in one tool call, `rg -l` or `rg --count` first, and open only the files with a hit.

1. **Scripts.** Read `package.json`: if `lint`, `build` or `test` exist, run them (`npm run lint`, `npm run build`, `npm test`) and collect the failures. If a script needs a dev server or a database that isn't there, skip it and say so.
2. **Leftovers.** `rg` for `console.log`, `console.debug`, `debugger`, `TODO`, `FIXME`, commented-out blocks of code, and unused files the router no longer references.
3. **Frontend.** `<img` without `alt`, `<a href="#"` or empty, `<div onClick`/`<span onClick>` without a role, pages without `<title>` or meta description, more than one `<h1>` in a file, missing `lang=`, labels without a matching input.
4. **Backend and config.** Hard-coded secrets or URLs that look like keys, `.env` values copied into the code, routes without their auth check, unparameterised queries.
5. **Links.** Internal links to files or routes that don't exist in the project.

Don't modify any file. Report the result like this:

1. The errors, grouped by file, with the line.
2. The warnings, grouped by type, with how many times they occur and in which files.
3. The info in a single line: how many `TODO` are open and how many files were checked.

Close by saying which problems you can fix yourself if the user asks you to and which need a decision from them (missing content, secrets, broken build).
