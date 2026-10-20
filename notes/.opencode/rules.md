# Writing rules

The only source for the anti-slop and layout rules. It applies to every note you
write, with any model: the note style is in `.opencode/style.md`, these are the
writing rules. If a rule here and a rule in `style.md` say different things,
`style.md` wins.

They are inside the configuration on purpose: they must work on every machine,
without installing anything.

## no-ai-slop

**Forbidden words** (never): delve, foster, leverage, utilize, facilitate, empower, streamline,
robust, cutting-edge, paradigm shift, game changer, tapestry, realm, beacon, multifaceted,
meticulous, intricate, paramount, transformative, elevate, embark, supercharge, harness,
ever-evolving.

**Empty formulas** (cut): "it's worth noting", "it's important to note", "in conclusion",
"in summary", "in today's world", "at its core", "the reality is", "in terms of",
"with regard to", "we'll see how", "experts agree", "studies suggest"
→ name the source or cut it.

**Patterns to remove**:
- reveal sentences: "The part that works: ..." → write it as a plain sentence
- binary contrasts: "It's not X, it's Y" → "It's Y"
- negative lists: "It's not X. It's not Y. It's Z." → "It's Z"
- puffiness: "pivotal", "vital", "crucial", "game changer", "serves as a" → concrete facts
- meta-talk: "the key point is", "as we'll see", "it's worth remembering" → cut it
- closing summaries when the text is already complete

**Positive rules**: active verbs, one point per sentence, names/numbers/mechanisms instead of
abstractions, no cyclic synonyms, no sentences broken in a rush, don't repeat the same
information with different words. If a piece of content isn't certain: `[!todo]`, don't invent.

## i-have-adhd

1. **First line = the next action**, not the context.
2. **More than one step → numbered list**, one step per line, no repeated "and then".
3. **End with ONE concrete action** (less than 2 minutes). No "hope this helps".
4. **No digressions**: finish the first point, then ask about the second.
5. **Restate the state every turn**: "Step 3 of 5: done X. Now Y".
6. **Concrete times**: "about 15 minutes if the tests are there", never "a bit of work".
7. **Make the result visible** instead of narrating it.
