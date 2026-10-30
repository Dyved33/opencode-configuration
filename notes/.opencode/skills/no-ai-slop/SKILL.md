---
name: no-ai-slop
description: Ban on AI-style words and empty formulas in note writing
license: MIT
compatibility: opencode
metadata:
  audience: note-writing
  workflow: write-review
---

# no-ai-slop — no filler text

## Forbidden words (never use)

delve, foster, leverage, utilize, facilitate, empower, streamline,
robust, cutting-edge, paradigm shift, game changer, tapestry, realm, beacon, multifaceted,
meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness,
ever-evolving.

## Empty formulas (cut)

"it is important to note", "it is worth noting", "in conclusion",
"in summary", "in today's world", "at its core", "the reality is", "in terms of",
"as for", "we will see", "experts agree", "studies suggest"
→ name the source or cut.

## Patterns to eliminate

- reveal phrases: "The part that works: ..." → write it as a simple sentence
- binary contrasts: "It is not X, it is Y" → "It is Y"
- negative lists: "It is not X. It is not Y. It is Z" → "It is Z"
- puffiness: "pivotal", "vital", "crucial", "game changer", "serves as a" → concrete facts
- meta-discourse: "it is the key point", "as we will see", "it is worth remembering" → cut
- final summaries if the text is already complete

## Positive rules

- active verbs
- one sentence = one point
- names, numbers, mechanisms instead of abstractions
- no cyclic synonyms
- no sentences fired off rapidly
- do not repeat the same information with different words
- if content is uncertain: `[!todo]`, do not invent
