---
name: note-quality
description: Quality checklist to apply to every note before closing the work
license: MIT
compatibility: opencode
metadata:
  audience: note-writing
  workflow: write-review
---

# note-quality — note quality checklist

Apply this checklist to every note before considering it concluded. Every item must be verified against the teacher's material and the raw notes.

## Content

- [ ] All definitions of the material are present in the note, with the teacher's notation.
- [ ] All theorems, propositions and lemmas are present, with complete statement.
- [ ] All formulas of the material are reported, without unauthorized conversions or simplifications.
- [ ] All algorithms and procedural steps are present, in the teacher's order.
- [ ] All examples of the teacher are reported (none skipped as "secondary").
- [ ] All list items of the material are present.
- [ ] All numbers and special cases of the material are present.
- [ ] Observations and verbal clarifications by the teacher are reported.

## Style (style.md + no-ai-slop + i-have-adhd)

- [ ] No forbidden words from `no-ai-slop`.
- [ ] No empty formulas to cut.
- [ ] No introductions ("In this lesson we will see") or closings ("In conclusion").
- [ ] No forbidden sections: "Introduction", "Conclusion", "Key concepts", "Summary", "Recap".
- [ ] Titles do not have Every Word Capitalized, are not bold, have no emojis, are not numbered.
- [ ] There is only one `#` title at the head of the note.
- [ ] Subtopics use bold labels at the start of the paragraph, not `###` titles unless really needed.
- [ ] There is `> [!info] Summary:` at the end of the note, with 3-6 points, one line each.
- [ ] No frontmatter `---`.
- [ ] No tags `#`.
- [ ] No date in the file name or in the note.
- [ ] Images have the correct layout (`[[x.png]]`, `[[x.png|300]]`, text below/beside).
- [ ] Wikilinks point to existing notes and use the format `[[File name|text]]`.
- [ ] Code that serves theory remains in the note; complete exercises stay in `esercizi/`.

## Placeholders and todos

- [ ] All placeholders `// ... //` are resolved or replaced with `[!todo]`.
- [ ] Every `[!todo]` is concrete and says what is missing.
- [ ] Open `[!todo]` at the end are listed in the summary.

## Automatic verification

- [ ] `python3 .opencode/scripts/vault-audit.py <note>` → zero ERROR, zero WARN depending on you.
- [ ] `python3 .opencode/scripts/check-losses.py <note>` → zero loss entries compared to sources.
