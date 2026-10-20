# Note style

Single source for the style. It applies to every lesson note. If a rule here and a note written by the user say different things, the user's note wins.

## Principle

These are notes from a student who understood the lesson, not a handout. They are meant for studying for the exam, where what the teacher said has to be reproduced.

That is why content is never lost: everything in the user's notes, in the raw notes and in the teacher's material stays in the note — definitions, theorems, proofs, formulas, code, images, examples, complete lists, numbers, edge cases, observations and clarifications made out loud. You don't decide what is secondary: your job is to fix the shape, correct mistakes and add what is missing.

Only words that carry no information are removed: if dropping a sentence loses even a single detail, the sentence stays and at most gets shortened. When in doubt, keep it.

Length has no limit: the content decides it. A long lesson or a difficult concept produce a long note, and that is right. What matters is density:

- the same information is written once, where it is needed: if it is repeated identically in two points keep the more complete version;
- a difficult concept deserves all the explanation needed to understand it; a simple one gets a line;
- the teacher's examples and the user's examples all stay; you add at most one of your own per concept, and only if it helps;
- if a paragraph can be said in half the words without losing information, it must be said in half the words.

Three kinds of text, and only these:

- **Bare definition**: one sentence, formal, using the teacher's notation.
- **Discursive explanation**: says *why* or *how* a step works, in simple words and even in the first person ("if I find myself in $q_0$ and read $a$..."). It does not restate the definition in other words.
- **Callout**: examples, notes, warnings. They sit outside the flow of the text.

## What not to write

- Introductions and closings: "In this lesson we will see", "In conclusion", "As we have seen".
- Sections called "Introduction", "Conclusions", "Key concepts", "Summary".
- Empty emphasis: "it is important to note that", "fundamental", "crucial", "extremely", "strictly".
- Fancy titles ("The Engine of Infinity"): the title states the topic and nothing else.
- Every Word Capitalised in titles and labels.
- Bold everywhere: it goes only on the term being defined, the first time.
- Lists where every item is "**Label:** generic sentence". A list is for when the elements really are parallel.
- Callouts with titles like "Note from the Prof", "Further reading", "Historical context".
- The same thing said twice. The only summary allowed is the Summary at the end of the note.

## Note structure

```markdown
# Title of the lesson

## Main topic
Text.

**Sub-topic:** text that continues on the same line.

> [!info] Summary:
> - key point
> - key point
```

- A single `#`, with the title. The date is written neither in the file name nor in the note. No frontmatter, no tags.
- `##` for the topics of the lesson. `###` only when a topic is really long. Never `####`.
- Inside a section, to separate sub-topics use the bold label at the start of the paragraph (`**Graph of an automaton:**`), not a heading.
- Titles without numbers, without bold, without emoji, capitalised only at the first letter.
- No `---` lines between sections and no navigation section at the end.
- The note always ends with a `> [!info] Summary:` callout: 3 to 6 points, one line each, with what should be remembered from the lesson. No new sentences and no long formulas. It is the last thing in the note and there is only one.

## Labels

In italics, at the start of the paragraph, followed by a colon:

`*Definition:*` `*Theorem:*` `*Lemma:*` `*Proposition:*` `*Proof:*` `*Observation:*` `*Advantages:*` `*Disadvantages:*`

Other habits to keep:

- Lists with `-`. Numbered lists only for steps in sequence.
- The gloss with ` = ` after a formal term: `$Q$ is the set of states = all the configurations the device can take`.
- `<u>...</u>` for the key sentence of a paragraph. At most one per section.
- Italics for English terms and for the quoted technical term (*busy-waiting*, *semWait*).
- Arrows, dots and symbols are free: `->`, `=>`, `→`, `…` are all fine.

## Callouts

Only these types, always in lowercase:

| Type | Use |
|---|---|
| `[!example]` | example, worked exercise, image of a concrete case. Usually without a title. |
| `[!info]` | plain-word explanation of a formal step (`In other words:`, `N.B.`) and the final summary of the note (`Summary:`) |
| `[!important]` | the thing you cannot get wrong in the exam. Rare. |
| `[!warning]` | typical mistake, edge case. Typical title: `Careful:` |
| `[!tip]` | reminder. Typical title: `Remember` |
| `[!todo]` | a point to revisit. See below. |

A callout does not repeat the text preceding it. `[!info] Summary:` is reserved for the closing of the note; to explain a difficult formal step in words use `[!info] In other words:`, in a few lines.

## Formulas and code

- `$...$` in the text. `$$...$$` on their own lines for long formulas or ones that deserve emphasis.
- In formulas follow the notation already used in the note and by the teacher. Do not convert existing formulas.
- Code and pseudocode always in a ``` ``` ``` block. The label after the three backticks is whatever the user put: the language (`c`, `java`) or a name (`Algoritmo_di_Dekker`). Don't change it. In new blocks put the language if it is real code, otherwise a name without spaces.
- The snippet that serves the theory stays in the note. The whole exercise or the complete solution does not: they go in `esercizi/<name>.<ext>`, in the course folder, and the note keeps only the relevant piece with the wikilink `[[esercizi/es3.py|es3]]`.
- Function and variable names in the text in single backticks: `` `fork()` ``.
- Tables only for comparisons with at least two columns of data.

## Images

The images are inserted by the user and live in the `images/` folder next to the note. Don't rename them, don't move them, don't invent them. In `src` goes only the file name, copied exactly as the user wrote it, without `images/` in front.

You cannot see the images: don't describe what they show unless the user's text tells you.

Exception: when the agent takes the photo itself with `pdftoppm` from a page of the material, the description is written from the text the OCR (`tesseract`) returns. In `src` goes only the file name, e.g. `slide-06.png`, without `images/` in front. Only what the OCR reads is reported: no invented details.

Outside callouts every image uses one of these layouts. Which one to use is told by the placeholder the user writes after the image; without a placeholder it is the question below that decides:

| The user writes | Layout |
|---|---|
| `![[x.png]]` (no placeholder) | ask first, see below; resized to 300 unless the user picks another layout |
| `![[x.png]] // fit //` | fitted to the width of the page |
| `![[x.png]] // below: text //` | with a caption underneath |
| `![[x.png]] // side: text //` | with text alongside. With `// side //` and no text, the paragraph that follows goes alongside |

If the image has no placeholder — or if you are inserting it yourself with `pdftoppm` — ask which layout to use with the `question` tool: a single question listing all the images, in the order they appear, each with the layout choices. No question for images inside a callout and for images already inside a `<div>`: their layout is already decided (see below).

- resized to 300
- fitted to the width of the page
- with a caption underneath
- with text alongside
- leave it as it is

For "with a caption underneath" and "with text alongside" the text comes from the OCR when it gives something usable (`parse` with `extractImages: true` on an image of `images/`, `tesseract` on a slide photo). If the OCR gives nothing, ask the user to write the text in the same question; if they don't, fall back to a resize. Never invent what the image shows.

Resized:

```html
<div style="display: flex; justify-content: center;">
  <img src="x.png" width="300">
</div>
```

Fitted to the page:

```html
<div style="display: flex; justify-content: center;">
  <img src="x.png" style="width: 100%;">
</div>
```

With a caption underneath:

```html
<div style="text-align: center;">
  <img src="x.png" alt="Image" />
  <p>Text</p>
</div>
```

With text alongside:

```html
<div style="display: flex; align-items: flex-start; gap: 20px;">
  <div style="flex: 1;">
    <img src="x.png" style="width: 100%; border-radius: 8px;">
  </div>
  <div style="flex: 1.5;">
  Text
  </div>
</div>
```

Inside a `<div>` Markdown doesn't work: italics with `<i>`, bold with `<b>`, no `$...$`. If the text alongside has formulas, use the resized layout and put the text underneath, outside the div.

Inside a callout the image stays `![[x.png|300]]`.

## User placeholders

Outside code blocks, `// ... //` is an instruction for you, to be carried out at that point:

| Placeholder | What to do |
|---|---|
| `// slide 28 //`, `// slide 19-21 //` | read those pages of the material and integrate the content here |
| `// def X //`, `// table X //`, `// steps X //` | look for X in the material and bring it here |
| any other text | it is a request: go deeper, correct, add an example, etc. |

The placeholder disappears only once it has been carried out. If you can't carry it out, replace it with a `[!todo]` saying what is missing.

## Todo

```markdown
> [!todo] slide 28 not found in automi.pdf
```

Leave a `[!todo]` when: a placeholder can't be resolved, the material and the notes contradict each other and you don't know who is right, a step looks wrong but you can't verify it. One line, concrete. On every pass try to close the `[!todo]` already there.

## Links

Link with a wikilink the lessons of the same course when a concept is explained in another note: `[[File name|text]]`, or `[[File name#Section|text]]`. Only towards notes that exist (check first), only at the first occurrence in the section, and without changing the text to make room for the link.

## Example

Not like this:

```markdown
### **Time-Sharing: An Interactive Revolution**
**Time-sharing** (sharing the time) is a fundamental paradigm developed to support the management of multiple interactive jobs. It is important to note that:
* **Fluid sharing:** the processor is shared fluidly among all the active users.
* **Simultaneous access:** access happens simultaneously through the use of terminals.

> [!NOTE] Note from the Prof
> Time-sharing therefore allows several users to use the same machine at the same time.
```

Like this:

```markdown
## Time-sharing
The processor is shared among several users connected through terminals: the OS assigns each program a *time slice* in turn. The goal is no longer to maximise CPU utilisation (multiprogramming) but to minimise response time.
```

And this is the right register for definition, explanation and callout together:

```markdown
## Semaphores
Mechanism for synchronising access to the critical sections. A semaphore is made of an integer variable, a queue and three operations:
- Initialisation to a non-negative value
- *semWait:* decrements the value. If it becomes negative, the process is suspended and queued
- *semSignal:* increments the value. If it does not become positive, one of the queued processes is reactivated

> [!info] In other words:
> When the value is positive it tells how many processes can still enter, when it is negative it tells how many are in the queue.

*Observation:* the process cannot know in advance if it will be suspended by *semWait*.
```
