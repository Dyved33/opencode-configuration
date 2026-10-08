# OpenCode guide for this project

## Starting up

OpenCode must be started from the project folder, the one that contains `opencode.json`:

```bash
cd path/to/project
opencode
```

After any change to `opencode.json` or to a file in `.opencode/` it has to be restarted: the configuration is only read at startup.

## How it is organized

| File | What it is for |
|---|---|
| `AGENTS.md` | the few rules that always apply. It is read at every session |
| `.opencode/style.md` | how the code must be written. It is loaded at every session |
| `.opencode/agents/` | the 2 agents |
| `.opencode/commands/` | the 4 commands |
| `opencode.json` | permissions, MCP browser |
| `Opencode_Guide.md` | this guide |

To change the code conventions you edit only `.opencode/style.md`.

## The rules in one line

- It works only inside this folder: it cannot read or write files outside the project.
- It commits and pushes **only** when you ask for it in that message, and then nothing else.
- It never deploys, publishes or releases.
- It never deletes or overwrites your files without asking, and never rewrites git history.
- It doesn't touch `AGENTS.md`, `opencode.json` or `.opencode/`.
- The stack is whatever the project is: it reads `package.json` and the files around the change before writing anything.

## The flow of a change

1. You describe the change: a fix, a new page, a restyle.
2. The agent reads the project (structure, conventions, the file to change), makes the smallest change that does the job, then runs lint and build if the project has them and closes with a 5-line summary.
3. When the change is finished you launch `/review`: it lets the reviewer run once and applies the corrections.
4. `/preview` opens the result in a browser so you can see it with your own eyes.

## The agents

| Agent | What it does | How to use it |
|---|---|---|
| `webdev` | writes and changes the code. It is the one active at startup | just write the request |
| `reviewer` | checks a change (correctness, accessibility, SEO, security, style) and returns the list of corrections. It modifies nothing | runs by itself with `/review`; by hand with `@reviewer` |

## The commands

**`/page`** creates the skeleton of a page or component and wires it in where the other pages are. No content, no logic.

```
/page "src/pages/Events.tsx" listing of the portal's events
/page Contact
```

**`/review`** has code reviewed and applies the corrections: errors, security, accessibility, SEO, style. On a folder it works one file at a time and stops after each one.

```
/review src/components/Header.tsx
/review diff                    # what git status and git diff show
/review src/pages report only   # modifies nothing
```

**`/audit`** runs the project checks and reports the result. It modifies nothing.

```
/audit                # the whole project
/audit src/pages      # one folder
```

It runs lint/build/test if they exist in `package.json`, then looks for: `console.log` and `debugger` left in, open `TODO`, commented-out code, `<img>` without `alt`, links and clicks on `<div>`, pages without title and meta description, hard-coded secrets, internal links that don't exist.

**`/preview`** starts the dev server if needed, opens the page with Playwright and reports what loads, the console errors and the rendering problems.

```
/preview
/preview /events/42
```

Paths with spaces must always be quoted.

## What OpenCode can and can't do

- It can create and modify any file of the project. It cannot modify `AGENTS.md`, `opencode.json` or the files in `.opencode/`.
- It can run `npm`/`npx`/`node`, `pnpm`, `yarn`, `dotnet`, `git` and the usual command-line tools.
- `git commit` and `git push` ask for your confirmation, and the agent only attempts them when you asked for them.
- It cannot deploy, publish or release anything: those commands are blocked.
- Deleting files and git commands that could throw work away ask for confirmation.
- It cannot leave the project: no reading or editing outside this folder.
- It can search the web and open the page in a browser (Playwright MCP).

## The browser (Playwright MCP)

`/preview` and any request to "look at the page" use the `playwright` server configured in `opencode.json`. The first start downloads it with `npx`, so it needs the network once. If it doesn't start, check that `npx` works and restart OpenCode.

## When something goes wrong

- **An agent or a command doesn't appear:** restart OpenCode.
- **OpenCode won't start because of a configuration error:** `OPENCODE_DISABLE_PROJECT_CONFIG=1 opencode`, fix `opencode.json` and restart. To see the configuration OpenCode actually loaded: `opencode debug config`.
- **The change broke something:** `git diff` shows what changed, `git restore "path"` brings the file back to the last commit (it asks for confirmation).
- **A dev server left running:** it was started in the background, its log is in `/tmp/opencode-dev.log`; stop it with the command the agent reported in the summary.
- **Vague requests:** "improve the site" produces a random rewrite. Better "the events page is slow to scan, restructure the list" or a precise bug report.
