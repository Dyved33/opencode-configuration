# Prompt to use outside OpenCode

The style is not repeated here: it lives only in `.opencode/style.md`, so there are no two versions to keep in sync.

## Antigravity (or another agent that can see the vault)

Check of a note, without changes:

```
Read AGENTS.md, .opencode/style.md and .opencode/rules.md and follow them.
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
Read AGENTS.md, .opencode/style.md and .opencode/rules.md and follow them.
Work on the note [PATH]. Carry out the // ... // placeholders, fix the errors and add what is missing using the teacher's material in the same folder. The text that is already correct and clear stays as it is and no information is removed. Close the note with the callout [!info] Summary. Don't create other files.
Before editing run python3 .opencode/scripts/check-losses.py "[PATH]" --save. At the end run the same command without --save, put back what results as lost, then run python3 .opencode/scripts/vault-audit.py "[PATH]" and close with a summary of at most 5 lines.
```

## Web chat (ChatGPT, Claude, Gemini)

Attach `.opencode/style.md`, the notes and the teacher's material, then paste:

```
You are helping me take notes from a university lecture. Read the attached style file and follow it exactly.

Here is the note I wrote:
[ATTACHED NOTE]

Here is the teacher's material:
[ATTACHED MATERIAL]

Check the note against the material and return a list, one item per line, from most to least serious:
[ERROR] wrong or imprecise content, with the page of the material
[MISSING] definitions, theorems, steps, examples, list items, numbers of the material absent from the note
[CUT] words that carry no information (never my content, not even if it looks secondary)
[STYLE] what violates the style file

Don't rewrite the note, don't add content that isn't in the material, don't comment on the length. No preamble.
```

To have the note rewritten instead of checked:

```
Rewrite the note following the attached style file. Keep every piece of information from the teacher and from me: you may remove only the words that carry no information. Carry out the // ... // placeholders. Don't create new files. Return the whole note.
```
