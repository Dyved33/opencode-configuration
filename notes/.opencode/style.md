# Notes style

Single source for style. Applies to every lesson note. If a rule here and a note written by the user say different things, the user's note prevails.

## Principle

These are notes from a student who understood the lesson, not a handout. They serve to study for the exam, where what the teacher said must be reported.

For this reason content is never lost: the note keeps everything that is in the user's notes, in the raw notes and in the teacher's material — definitions, theorems, proofs, formulas, code, images, examples, complete lists, numbers, special cases, observations and clarifications made verbally. You do not decide what is secondary: your job is to fix the form, correct errors and add what is missing.

Only words that carry no information are removed: if removing a sentence loses even a single detail, the sentence remains and at most is shortened. In doubt, keep it.

Length has no limit: content decides it. A long lesson or a difficult concept produces a long note, and that is fine. What matters is density:

- the same information is written once, in the place where it serves: if repeated identically in two places, keep the more complete version;
- a difficult concept deserves all the explanation needed to understand it; a simple one one line;
- the teacher's and user's examples all remain; add at most one per concept, and only if it helps;
- if a paragraph can be said in half the words without losing information, say it in half the words.

Three types of text, and only these:

- **Dry definition**: one sentence, formal, with the teacher's notation.
- **Discursive explanation**: says *why* or *how* a passage works, with simple words and even in first person ("if I am in $q_0$ and read $a$..."). It does not repeat the definition with other words.
- **Callout**: examples, notes, warnings. They are outside the flow of the text.

## What not to write

- Introductions and closings: "In this lesson we will see", "In conclusion", "As we have seen".
- Sections "Introduction", "Conclusion", "Key concepts", "Summary".
- Empty emphasis: "it is important to note that", "fundamental", "crucial", "extremely", "strictly".
- Catchy titles ("The engine of infinity"): the title says the topic and nothing else.
- Every Word Capitalized in titles and labels.
- Bold overload: only on the term being defined, the first time.
- Lists where every point is "**Label:** generic sentence". A list serves when elements are truly parallel.
- Callouts with titles like "Teacher's Note", "In-depth", "Historical context".
- The same thing said twice. The only summary allowed is the synthesis at the end of the note.

## Note structure

```markdown
# Lesson title

## Main topic
Text.

**Sub-topic:** text continuing on the same line.

> [!info] Summary:
> - key point
> - key point
```

- A single `#`, with the title. No frontmatter, no tags.
- `##` for the lesson's topics. `###` only if a topic is really long. Never `####`.
- Inside a section, to separate subtopics use the bold label at the start of the paragraph (`**Graph of an automaton:**`), not a title.
- Titles without numbers, without bold, without emojis, with only the first letter capitalized.
- No `---` lines between sections and no navigation section at the bottom.
- The note always closes with a callout `> [!info] Summary:`: 3 to 6 points, one line each, with what from the lesson must be remembered. No new sentences and no long formulas. It is the last thing in the note and there is only one.

## Labels

In italics, at the start of the paragraph, followed by a colon:

`*Definition:*` `*Theorem:*` `*Lemma:*` `*Proposition:*` `*Proof:*` `*Observation:*` `*Advantages:*` `*Disadvantages:*`

Other habits to keep:

- Lists with `-`. Numbered lists only for sequential steps.
- The glossary with ` = ` after a formal term: `$Q$ is the set of states = all configurations the device can assume`.
- `<u>...</u>` for the key sentence of a paragraph. At most one per section.
- Italics for English terms and for the cited technical term (*busy-waiting*, *semWait*).
- Arrows, dots and symbols are free: `->`, `=>`, `→`, `…` all fine.

## Callouts

Only these types, always lowercase:

| Type | Use |
|---|---|
| `[!example]` | example, solved exercise, image of a concrete case. Usually without title. |
| `[!info]` | explanation in words of a formal passage (`In other words:`, `N.B.`) and final note summary (`Summary:`) |
| `[!important]` | the thing that cannot be wrong at the exam. Rare. |
| `[!warning]` | typical error, edge case. Typical title: `Attention:` |
| `[!tip]` | reminder. Typical title: `Remember` |
| `[!todo]` | point to review. See below. |

A callout does not repeat the text preceding it. `[!info] Summary:` is reserved for closing the note; to explain in words a difficult formal passage use `[!info] In other words:`, in a few lines.

## Formulas and code

- `$...$` in text. `$$...$$` on their own lines for long formulas or those deserving emphasis.
- In formulas follow the notation already used in the note and by the teacher. Do not convert existing formulas.
- Code and pseudocode always in a ` ``` ` block. The label after the three backticks is the one the user sets: the language (`c`, `java`) or a name (`Algorithm_of_Dekker`). Do not change it. In new blocks put the language if it is real code, otherwise a name without spaces.
- The snippet that serves theory remains in the note. The whole exercise or complete solution does not: they are in `esercizi/<name>.<ext>`, in the course folder, and in the note only the relevant piece remains, with the wikilink `[[esercizi/es3.py|es3]]`.
- Function and variable names in text in single quotes: `` `fork()` ``.
- Tables only for comparisons with at least two columns of data.

## Images

Images are inserted by the user and are in the `images/` folder next to the note. Do not rename, move, or invent them. In `src` goes only the file name, copied identically to how the user wrote it, without `images/` in front.

You cannot see images: do not describe what they show unless the user's text says so.

Exception: when the photo is taken by the agent with `pdftoppm` from a page of the material, the description is written from the text returned by OCR (`tesseract`). In `src` goes only the file name, example `slide-06.png`, without `images/` in front. Only what OCR reads is reported: no invented details.

Outside callouts each image uses one of these layouts. Which one to use is decided by the placeholder the user writes after the image; without placeholder, the decision is the question below:

| User writes | Layout |
|---|---|
| `![[x.png]]` (no placeholder) | first ask, see below; resized to 300 if the user does not choose another layout |
| `![[x.png]] // adatta //` | adapted to page width |
| `![[x.png]] // sotto: testo //` | with text below |
| `![[x.png]] // lato: testo //` | with text beside. With `// lato //` without text, beside goes the following paragraph |

If the image has no placeholder — or if you are inserting it yourself with `pdftoppm` — ask which layout to use with the `question` tool: one question listing all images, in the order they appear, each with layout choices. No question for images inside a callout and for images already in a `<div>`: their layout is already decided (see below).

- resized to 300
- adapted to page width
- with text below
- with text beside
- leave as is

For "with text below" and "with text beside" the text comes from OCR when it returns something useful (`parse` with `extractImages: true` on an image in `images/`, `tesseract` on a slide photo). If OCR returns nothing, ask the user to write the text in the same question; if they don't, fall back to resizing. Never invent what the image shows.

Resized:

```html
<div style="display: flex; justify-content: center;">
  <img src="x.png" width="300">
</div>
```

Adapted to page:

```html
<div style="display: flex; justify-content: center;">
  <img src="x.png" style="width: 100%;">
</div>
```

With text below:

```html
<div style="text-align: center;">
  <img src="x.png" alt="Image" />
  <p>Text</p>
</div>
```

With text beside:

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

Inside a `<div>` Markdown does not work: italics with `<i>`, bold with `<b>`, no `$...$`. If the text beside has formulas, use the resized layout and put the text below, outside the div.

Inside a callout the image remains `![[x.png|300]]`.

## User placeholders

Outside code blocks, `// ... //` is an instruction for you, to execute at that point:

| Placeholder | What to do |
|---|---|
| `// slide 28 //`, `// slide 19-21 //` | read those pages of the material and integrate the content here |
| `// def X //`, `// tabella X //`, `// passaggi X //` | search X in the material and report it here |
| any other text | it is a request: deepen, correct, add an example, etc. |

The placeholder disappears only when it has been executed. If you cannot execute it, replace it with a `[!todo]` that says what is missing.

## Todo

```markdown
> [!todo] slide 28 not found in automi.pdf
```

Leave a `[!todo]` when: a placeholder does not resolve, material and raw notes contradict and you don't know who is right, a passage seems wrong but you cannot verify it. One line, concrete. At every pass try to close existing `[!todo]`.

## Links

Link with a wikilink lessons of the same course when a concept is explained in another note: `[[File name|text]]`, or `[[File name#Section|text]]`. Only toward existing notes (check first), only at the first occurrence in the section, and without changing the text to make room for the link.

## Example

So no:

```markdown
### **Il Time-Sharing: Una Rivoluzione Interattiva**
Il **Time-sharing** (condivisione del tempo) è un paradigma fondamentale sviluppato per supportare la gestione di più lavori interattivi. È importante notare che:
* **Condivisione fluida:** Il processore viene condiviso in modo fluido tra tutti gli utenti attivi.
* **Accesso simultaneo:** L'accesso avviene simultaneamente attraverso l'uso di terminali.

> [!NOTE] Nota del Prof
> Il time-sharing permette quindi a più utenti di usare contemporaneamente la stessa macchina.
```

So yes:

```markdown
## Time-sharing
The processor is shared among more users connected by terminal: the OS assigns in turn to each program a *quantum of processing*. The goal is no longer to maximize CPU usage (multiprogramming) but to minimize response time.
```

And this is the right register for definition, explanation and callout together:

```markdown
## Semaphores
Mechanism to synchronize access to critical sections. A semaphore consists of an integer variable, a queue and three operations:
- Initialization to a non-negative value
- *semWait:* decrements the value. If it becomes negative, the process is suspended and put in queue
- *semSignal:* increments the value. If it does not become positive, one of the processes in queue is reactivated

> [!info] In other words:
> When the value is positive it says how many processes can still enter, when negative it says how many are in queue.

*Observation:* the process cannot know in advance if with *semWait* it will be suspended.
```
