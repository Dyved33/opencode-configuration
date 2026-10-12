---
description: Reads a textbook in books/. Usage - /book list | /book "books/Introduction to AI.pdf" toc | /book FILE page 28 | /book FILE search "text"
---

These are the textbooks of the vault and/or the text requested:

!`python3 .opencode/scripts/books.py $ARGUMENTS`

If the user only asked to read or to search, report the output as it is, without summarising it and without modifying files. If the output is an error, explain in one line how to fix the command. A book is a complement, not a default source: nothing is taken from it without the user's consent.
