---
description: Opens the project in a browser with Playwright and reports how it renders. Usage - /preview [url or route, default "/"]
---

Open and look at: $ARGUMENTS (if empty, the root route).

Procedure:

1. Find out how the project runs: read the `dev`/`start` script in `package.json` and any port in the config. If a dev server is already answering on that port, use it; if not, start it in the background (`nohup npm run dev > /tmp/opencode-dev.log 2>&1 &`) and wait for it to be ready by reading the log. Say which command you started.
2. With the Playwright MCP tools open the page (the `$ARGUMENTS` route, or `/` if empty), take a screenshot and read the browser console.
3. Report, without modifying any file:
   - what loads and what doesn't (failed requests, 404, wrong port);
   - console errors and warnings;
   - rendering problems: layout broken, overlap, text unreadable, image missing, mobile width wrong;
   - obvious accessibility problems you can see: focus not visible, contrast, unlabelled control.
4. Close in at most 5 lines. If the server was started by you, say so and give the command to stop it: don't kill it yourself unless the user asks.
