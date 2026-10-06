# Note style

Single source for the style. It applies to every lesson note. If a rule here and a note written by the user say different things, the user's note wins.

## Principle

These are notes from a student who understood the lesson, not a handout. They are meant for studying for the exam, where what the teacher said has to be reproduced.

That is why content is never lost. Everything in the user's notes, in the raw notes and in the teacher's material stays in the note: definitions, theorems, proofs, formulas, code, images, but also examples, complete lists, numbers, edge cases, observations and clarifications made out loud. You don't decide what is secondary. Your job is to fix the shape, correct mistakes and add what is missing.

Only words that carry no information are removed. If dropping a sentence loses no information, the sentence goes; if even a single detail is lost, the sentence stays and at most gets shortened. When in doubt, keep it.

Length has no limit: the content decides it. A long lesson or a difficult concept produce a long note, and that is right. What matters is density:

- the same information is written once, where it is needed: if it is repeated identically in two places keep the most complete version;
- a difficult concept deserves all the explanation needed to understand it; a simple one gets a line;
- the teacher's examples and the user's examples all stay; you add at most one of your own per concept, and only if it helps;
- if a paragraph can be said in half the words without losing information, it must be said in half the words.

To shorten, you remove words, never content.

Three kinds of text, and only these:

- **Bare definition**: one sentence, formal, using the teacher's notation.
- **Discursive explanation**: says *why* or *how* a step works, in simple words and even in the first person ("se mi trovo in $q_0$ e leggo $a$..."). It does not restate the definition in other words.
- **Callout**: examples, notes, warnings. They sit outside the flow of the text.

## What not to write

- Introductions and closings: "In questa lezione vedremo", "In conclusione", "Come abbiamo visto".
- Sections called "Introduzione", "Conclusioni", "Concetti chiave", "Riepilogo".
- Empty emphasis: "è importante notare che", "fondamentale", "cruciale", "estremamente", "strettamente".
- Fancy titles ("Il motore dell'infinito"): the title states the topic and nothing else.
- Every Word Capitalised in titles and labels.
- Bold everywhere: it goes only on the term being defined, the first time.
- Lists where every item is "**Label:** generic sentence". A list is for when the items really are parallel.
- Callouts with titles like "Nota del Prof", "Approfondimento", "Contesto storico".
- The same thing said twice. The only summary allowed is the Sintesi at the end of the note.

## Note structure

```markdown
# Titolo della lezione

## Argomento principale
Testo.

**Sotto-argomento:** testo che continua sulla stessa riga.

> [!info] Sintesi:
> - punto chiave
> - punto chiave
```

- A single `#`, with the title. The date lives only in the file name (`2026-05-07 Automi a pila.md`), never in the text. No frontmatter, no tags.
- `##` for the topics of the lesson. `###` only when a topic is really long. Never `####`.
- Inside a section, to separate subtopics use the bold label at the start of the paragraph (`**Grafo di un automa:**`), not a heading.
- Titles without numbers, without bold, without emoji, capitalised only at the first letter.
- No `---` lines between sections and no navigation section at the end.
- The note always ends with a `> [!info] Sintesi:` callout: 3 to 6 points, one line each, with what should be remembered from the lesson. No new sentences and no long formulas. It is the last thing in the note and there is only one.

## Labels

In italics, at the start of the paragraph, followed by a colon:

`*Definizione:*` `*Teorema:*` `*Lemma:*` `*Proposizione:*` `*Dimostrazione:*` `*Osservazione:*` `*Vantaggi:*` `*Svantaggi:*`

Other habits to keep:

- Lists with `-`. Numbered lists only for steps in sequence.
- The gloss with ` = ` after a formal term: `$Q$ è l'insieme degli stati = tutte le configurazioni che il dispositivo può assumere`.
- `<u>...</u>` for the key sentence of a paragraph. At most one per section.
- Italics for English terms and for the quoted technical term (*busy-waiting*, *semWait*).
- Arrows, dots and symbols are free: `->`, `=>`, `→`, `…` are all fine.

## Callouts

Only these types, always in lowercase:

| Type | Use |
|---|---|
| `[!example]` | example, worked exercise, image of a concrete case. Usually without a title. |
| `[!info]` | plain-word explanation of a formal step (`In altre parole:`, `N.B.`) and the final summary of the note (`Sintesi:`) |
| `[!important]` | the thing you cannot get wrong in the exam. Rare. |
| `[!warning]` | typical mistake, edge case. Typical title: `Attenzione:` |
| `[!tip]` | reminder. Typical title: `Ricorda` |
| `[!todo]` | a point to revisit. See below. |

A callout does not repeat the text preceding it. `[!info] Sintesi:` is reserved for the closing of the note; to explain a difficult formal step in words use `[!info] In altre parole:`, in a few lines.

## Formulas and code

- `$...$` in the text. `$$...$$` on their own lines for long formulas or ones that deserve emphasis.
- In formulas follow the notation already used in the note and by the teacher. Do not convert existing formulas.
- Code and pseudocode always in a ``` ``` ``` block. The label after the three backticks is whatever the user put: the language (`c`, `java`) or a name (`Algoritmo_di_Dekker`). Don't change it. In new blocks put the language if it is real code, otherwise a name without spaces.
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
| `![[x.png]] // adatta //` | fitted to the width of the page |
| `![[x.png]] // sotto: testo //` | with a caption underneath |
| `![[x.png]] // lato: testo //` | with text alongside. With `// lato //` and no text, the paragraph that follows goes alongside |

If the image has no placeholder, before writing the HTML ask the user which layout to use with the `question` tool, one question per image, in the order the images appear:

- resized to 300
- fitted to the width of the page
- with a caption underneath
- with text alongside
- leave it as it is

For "with a caption underneath" and "with text alongside" the text comes from the OCR when it gives something usable (`parse` with `extractImages: true` on an image of `images/`, `tesseract` on a slide photo). If the OCR gives nothing, ask the user to write the text in the same question; if they don't, fall back to a resize. Never invent what the image shows.

Ask the same question for a photo you take yourself with `pdftoppm`, before inserting it: the layout is chosen then, with the same options.

No question for images inside a callout and for images already inside a `<div>`: their layout is already decided (see below).

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
  <img src="x.png" alt="Immagine" />
  <p>Testo</p>
</div>
```

With text alongside:

```html
<div style="display: flex; align-items: flex-start; gap: 20px;">
  <div style="flex: 1;">
    <img src="x.png" style="width: 100%; border-radius: 8px;">
  </div>
  <div style="flex: 1.5;">
  Testo
  </div>
</div>
```

Inside a `<div>` Markdown doesn't work: italics with `<i>`, bold with `<b>`, no `$...$`. If the text alongside has formulas, use the resized layout and put the text underneath, outside the div.

Inside a callout the image stays `![[x.png|300]]`. Images already inside a `<div>` are left alone.

## User placeholders

Outside code blocks, `// ... //` is an instruction for you, to be carried out at that point:

| Placeholder | What to do |
|---|---|
| `// slide 28 //`, `// slide 19-21 //` | read those pages of the material and integrate the content here |
| `// def X //`, `// tabella X //`, `// passaggi X //` | look for X in the material and bring it here |
| any other text | it is a request: go deeper, correct, add an example, etc. |

The placeholder disappears only once it has been carried out. If you can't carry it out, replace it with a `[!todo]` saying what is missing.

## Todo

```markdown
> [!todo] slide 28 non trovata in automi.pdf
```

Leave a `[!todo]` when: a placeholder can't be resolved, the material and the notes contradict each other and you don't know who is right, a step looks wrong but you can't verify it. One line, concrete. On every pass try to close the `[!todo]` already there.

## Links

Link with a wikilink the lessons of the same course when a concept is explained in another note: `[[File name|text]]`, or `[[File name#Section|text]]`. Only towards notes that exist (check first), only at the first occurrence in the section, and without changing the text to make room for the link.

## Example

Not like this:

```markdown
### **Il Time-Sharing: Una Rivoluzione Interattiva**
Il **Time-sharing** (condivisione del tempo) è un paradigma fondamentale sviluppato per supportare la gestione di più lavori interattivi. È importante notare che:
* **Condivisione fluida:** Il processore viene condiviso in modo fluido tra tutti gli utenti attivi.
* **Accesso simultaneo:** L'accesso avviene simultaneamente attraverso l'uso di terminali.

> [!NOTE] Nota del Prof
> Il time-sharing permette quindi a più utenti di usare contemporaneamente la stessa macchina.
```

Like this:

```markdown
## Time-sharing
Il processore viene condiviso fra più utenti collegati da terminale: il SO assegna a turno a ogni programma un *quanto di elaborazione*. L'obiettivo non è più massimizzare l'uso della CPU (multiprogrammazione) ma minimizzare il tempo di risposta.
```

And this is the right register for definition, explanation and callout together:

```markdown
## Semafori
Meccanismo per sincronizzare l'accesso alle sezioni critiche. Un semaforo è formato da una variabile intera, una coda e tre operazioni:
- Inizializzazione a un valore non negativo
- *semWait:* decrementa il valore. Se diventa negativo, il processo è sospeso e messo in coda
- *semSignal:* incrementa il valore. Se non diventa positivo, uno dei processi in coda è riattivato

> [!info] In altre parole:
> Quando il valore è positivo dice quanti processi possono ancora entrare, quando è negativo dice quanti sono in coda.

*Osservazione:* il processo non può sapere in anticipo se con *semWait* sarà sospeso.
```
