---
description: Reads a textbook in books/. Usage - /book elenco | /book "libri/Introduzione IA.pdf" indice | /book FILE pagina 28 | /book FILE cerca "testo"
---

These are the textbooks of the vault and/or the requested text:

!`python3 .opencode/scripts/books.py $ARGUMENTS`

If the user only asked to read or search, return the output as-is, without summarizing and without modifying files. If the output is an error, explain in one line how to correct the command. Remember rule 11 of `AGENTS.md`: the book is a complement, not a default source, and nothing is taken from it without the user's consent.
