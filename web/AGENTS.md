# AGENTS.md

Web project: portals and websites. One change = one task.

The stack is read from the project itself, never assumed: today it can be a C#
backend with a React frontend, tomorrow something else. Before writing code, look
at `package.json`, the project folders and the files next to the one you touch.

## Structure

```
<project>/
  src/                  frontend code (components, pages, styles)
  public/               static assets
  <backend folder>/     backend code (C#, Node, PHP...)
  package.json          scripts: dev, build, lint, test
  AGENTS.md             these rules
  opencode.json         permissions
  Opencode_Guide.md     guide for the user
  .opencode/            style, agents, commands (not yours to edit)
```

The folders depend on the project: follow what is there.

## Rules that always apply

1. **Style.** The code conventions are in `.opencode/style.md`. OpenCode loads them by itself; with other tools read them before writing.
2. **Stay in this project.** Files outside the working directory are off limits: read, edit and run commands only inside this repo.
3. **Commit and push only on explicit request.** Never commit, push or stage on your own initiative: the user asks for it in that message, and then you do exactly that and nothing else.
4. **Never deploy, publish or release.** No `npm publish`, no deploy commands, no releases, no CI triggered by you. Building locally is fine.
5. **No destructive actions.** No deleting or overwriting the user's files without asking, no `git reset --hard`, no `git clean`, no force push, no rewriting history.
6. **The configuration is not yours.** Don't modify `AGENTS.md`, `opencode.json` or anything in `.opencode/`.
7. **The project decides.** Use the framework, the naming, the folder layout and the styling system already in the project. Don't introduce a new library, a new pattern or a new build tool unless the user asks for it.
8. **Sources.** First the code of the project, then the official docs, then the web. Keep external research short.
9. **Final summary.** Close every job with at most 5 lines: files touched, what changed, which checks you ran, what is left.

## Tools

| What | How |
|---|---|
| Write and change code | agent `webdev` |
| Review of a change | agent `reviewer`: modifies nothing, returns the list of corrections |
| Skeleton of a page or component | `/page "path or name" description` |
| Review and apply corrections | `/review path`, `/review diff`, `/review report only` |
| Project check | `/audit [path]` |
| See it in the browser | `/preview [url]` (Playwright MCP) |
