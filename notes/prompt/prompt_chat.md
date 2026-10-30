# Prompts for working outside OpenCode

Style is not repeated here: it is only in `.opencode/style.md`, so there are no two versions to keep aligned.

## Antigravity (or another agent that sees the vault)

Check a note, without modifying it:

```
Read AGENTS.md and .opencode/style.md and apply them.
Check the note [PATH] comparing it with the teacher's material found in the same folder. Do not modify any file.
Return a list, from most to least severe, one item per line:
[ERROR] incorrect or imprecise content, with reference to the material page
[MISSING] definitions, theorems, passages, examples, list items, numbers from the material missing in the note
[CUT] words that carry no information (never teacher's or my content, even if it seems secondary)
[STYLE] what violates .opencode/style.md
Do not propose rewriting what is correct and clear. No preambles.
```

Work on a note:

```
Read AGENTS.md and .opencode/style.md and apply them.
Work on note [PATH]. Execute the placeholders // ... //, correct errors and add what is missing using the teacher's material in the same folder. Correct and clear text remains as is and no information is removed. Close the note with the callout [!info] Summary. Do not create other files.
Before modifying run python3 .opencode/scripts/check-losses.py "[PATH]" --save. At the end run the same command without --save, put back what resulted lost, then run python3 .opencode/scripts/vault-audit.py "[PATH]" and close with a summary of at most 5 lines.
```

## Web chat (ChatGPT, Claude, Gemini)

Attach `.opencode/style.md`, your notes and the teacher's material, then paste:

```
In attachment you find style.md, my notes and the teacher's material.

Task: [choose one]
- integrate my notes: execute the placeholders // ... //, correct errors and add what is missing compared to the material. Correct and clear text remains as is, word for word.
- write the note from scratch from the teacher's material: student notes, not a handout. Every content slide must be covered in full: definitions, theorems, algorithms, all examples, all list items.
- condense this note removing only words: no information is removed.

Rules:
- follow style.md to the letter; if my notes and style.md say different things, my notes prevail;
- for the exam I must report what the teacher said: everything in my notes and in the material must remain in the note. You can fix the form, correct and add; you can remove only words that do not carry information. In doubt, keep;
- if you are not sure about content do not invent: leave > [!todo] with what is missing;
- image file names must be copied identically;
- code that serves theory remains in the note in a block; an exercise or complete solution goes in a separate block with the esercizi/ path where to save it.

Answer only with the note in a markdown block, followed by a summary of at most 5 lines: what you added, corrected, removed, and todos left.

Lesson title: [TITLE]
```
