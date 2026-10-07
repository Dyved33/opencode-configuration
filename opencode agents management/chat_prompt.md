# Prompt to use outside OpenCode

The style is not repeated here: it lives only in `.opencode/style.md`, so there are no two versions to keep in sync.

## Antigravity (or another agent that can see the vault)

Check of a note, without changes:

```
Read AGENTS.md and .opencode/style.md and follow them.
Check the note [PATH] against the teacher's material you find in the same folder. Don't modify any file.
Return a list, from most to least serious, one item per line:
[ERROR] wrong or imprecise content, with the reference to the page of the material
[MISSING] definitions, theorems, steps, examples, list items, numbers of the material absent from the note
[CUT] words that carry no information (never content from the teacher or me, not even if it looks secondary)
[STYLE] what violates .opencode/style.md
Don't propose rewriting what is correct and clear. No preambles.
```

Work on a note:

```
Read AGENTS.md and .opencode/style.md and follow them.
Work on the note [PATH]. Carry out the // ... // placeholders, fix the errors and add what is missing using the teacher's material in the same folder. The text that is already correct and clear stays as it is and no information is removed. Close the note with the callout [!info] Sintesi. Don't create other files.
Before editing run python3 .opencode/scripts/check-losses.py "[PATH]" --save. At the end run the same command without --save, put back what results as lost, then run python3 .opencode/scripts/vault-audit.py "[PATH]" and close with a summary of at most 5 lines.
```

## Web chat (ChatGPT, Claude, Gemini)

Attach `.opencode/style.md`, the notes and the teacher's material, then paste:

```
In the attachments you will find style.md, my notes and the teacher's material.

Task: [pick one]
- integrate my notes: carry out the // ... // placeholders, fix the errors and add what is missing compared to the material. The text that is already correct and clear stays as it is, word for word.
- write the note from scratch from the teacher's material: notes from a student, not a handout. Every content slide must be covered in full: definitions, theorems, algorithms, all the examples, every list item.
- trim this note removing only words: no information may be lost.

Rules:
- follow style.md to the letter; if my notes and style.md say different things, my notes win;
- in the exam I have to reproduce what the teacher said: everything in my notes and in the material must stay in the note. You may fix the shape, correct and add; you may only remove words that carry no information. When in doubt, keep it;
- if you are not sure about some content don't invent it: leave > [!todo] with what is missing;
- the image file names must be copied identically;
- code that serves the theory stays in the note in a block; an exercise or a complete solution goes in a separate block with the esercizi/ path to save it to.

Reply only with the note in a markdown block, followed by a summary of at most 5 lines: what you added, corrected, removed, and the todos you left.

Lesson title: [TITLE]
```