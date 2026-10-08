---
description: Creates the skeleton of a page or component, wired into the project. Usage - /page "path or name" [what it is for]
agent: webdev
---

Create the skeleton for: $ARGUMENTS

The first argument is the path or the name of the page/component; everything after it describes what it is for. If it is empty or ambiguous, ask where it goes and what it must show before writing.

Procedure:

1. Read `package.json`, the router and the folder where the sibling pages/components live: the new file follows that framework, that naming and that layout system, nothing else.
2. Create the minimal file: component with the right signature, the route or menu entry wired in exactly where the other pages are, and the empty states (loading, error, no content) the project uses.
3. No content, no business logic, no new dependency: the skeleton only. Placeholders for the real sections are fine, marked `TODO(user): what this section needs`.
4. Run the lint/build script if the project has one and close with the summary: files created, where it was wired in, checks run.
