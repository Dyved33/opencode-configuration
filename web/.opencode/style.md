# Code style

Single source for how code is written in this project. It applies to every change. If a rule here and the code already in the project say different things, the project wins: the first job is to read the files around the one you touch and do what they do.

The stack can change over time (C# + React today, something else tomorrow). Nothing here is tied to one framework: where a rule names a framework, it applies only while that framework is in the project.

## Principle

This is code for a portal that people use and that someone has to maintain: readable, small, predictable. Prefer the boring solution that fits the project over the clever one.

- Read before writing: `package.json`, the neighbouring files, the routing, the existing components. Copy their naming, their structure and their imports.
- One idea per file. A file that does two things gets split only when the project already does it that way.
- No new dependencies, no new folders, no new configuration unless the user asks for it.
- No dead code: no commented-out blocks, no unused imports, no variables that are never read.
- Small, focused changes: touch what the task needs and nothing else.

## Frontend

- Function components with hooks. One component per file, the file named after it (`EventCard.tsx` -> `EventCard`).
- Props destructured in the signature. Types declared next to the component when TypeScript is in the project, otherwise plain JavaScript.
- State is kept as low as it can be: local `useState` first, lifting only when a sibling really needs it.
- Lists need a stable `key`. Event handlers are named `handleX`, effects explain in one comment why they exist.
- Fetching goes through the project's existing layer (functions, hooks, client) if there is one; never `fetch` scattered inside components when a helper exists.
- Rendering branches early: return the empty/loading/error case first, then the content. No nested ternaries.

## Styling

- Whatever the project uses (Tailwind, CSS modules, plain CSS, a framework): use it, don't add another one.
- Reuse the existing spacing, colour and typography tokens. No magic pixel values for things the project already defines.
- Class names follow the project (`kebab-case` for CSS, the framework's convention for the rest).

## Accessibility

Non-negotiable for a portal:

- Every `<img>` has an `alt`; decorative images get `alt=""`.
- Every input has a `<label>` (or `aria-label` when a visible label is impossible); errors are announced with `aria-describedby`.
- One `<h1>` per page and a heading hierarchy without skips; landmarks (`header`, `nav`, `main`, `footer`) where the project uses them.
- Everything reachable and operable with the keyboard; visible focus; no focus trap in dialogs.
- Text against its background meets normal contrast; colour is never the only signal.
- Icons used as buttons carry an accessible name.

## SEO

- One unique `<title>` and one meta description per page; `lang` on `<html>`; canonical when the page can be reached at more than one URL.
- Semantic HTML before ARIA: real links `<a href>`, real buttons, no `<div onClick>`.
- Headings say what the page is about; images below the fold lazy-load; nothing important lives only inside JavaScript if the page must be indexed.
- Internal links between the pages of the portal, with meaningful text.

## Backend

- Follow the project's layering (controllers, services, routes, data access) exactly as it is written today; don't invent a new one.
- Same naming as the surrounding code; async all the way where the project is async.
- Input validated at the boundary, errors returned through the project's error mechanism, never swallowed.
- No secrets in the code: configuration comes from environment variables or the project's config files, and `.env` files are read-only.
- Queries parameterised, output encoded for the context it is printed in.

## Hygiene

- No `console.log`, `debugger`, `print` or equivalent left behind in committed code.
- No `TODO` without a name or an issue behind it: either do it now or write `TODO(user): what is missing`.
- Comments only where the code cannot explain itself, in the language the project already uses for comments.
- Handle the failure case: a missing image, an empty list, a request that fails. A portal shows something, it does not crash.

## UI language

The text the user sees stays in the language of the existing interface. Don't translate labels, don't switch language in the middle of a file.

## Git hygiene

- One change, one coherent diff: no reformatting of files you didn't need to touch, no whitespace noise.
- Never commit or push unless the user asked for it in that message.
