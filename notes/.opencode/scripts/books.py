#!/usr/bin/env python3
"""Textbook management in books/.

A book is in books/<Course name>.pdf. Usage:
  books.py list                     present books and associated course
  books.py info FILE                title, pages, course of the book
  books.py index FILE               PDF summary (from bookmarks)
  books.py page FILE 28             text of page 28 (or 19-21)
  books.py search FILE "text"       pages where the text appears

Pages are read with the same engine as read-slides.py (pdftotext, with
Docling fallback on image pages). Writes nothing in the vault.
"""
import importlib.util
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
LIBRI = os.path.join(RADICE, "libri")
CORSI = os.path.join(RADICE, "first semester")


def _carica_read_slides():
    percorso = os.path.join(QUI, "read-slides.py")
    spec = importlib.util.spec_from_file_location("read_slides", percorso)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def exit_with(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def normalizza(s):
    return " ".join(s.split()).lower()


def libri_presenti():
    if not os.path.isdir(LIBRI):
        return []
    return sorted(f for f in os.listdir(LIBRI) if f.lower().endswith(".pdf"))


def corsi_presenti():
    if not os.path.isdir(CORSI):
        return []
    return sorted(
        x for x in os.listdir(CORSI)
        if os.path.isdir(os.path.join(CORSI, x)) and not x.startswith(".")
    )


def corso_del_libro(nome_file):
    base = normalizza(os.path.splitext(nome_file)[0])
    for corso in corsi_presenti():
        if normalizza(corso) == base:
            return corso
    return None


def risolvi(argomento):
    if os.sep in argomento or os.path.isfile(argomento):
        percorso = argomento
        if not os.path.isfile(percorso):
            exit_with(f"file not found: {argomento}")
        return percorso
    candidato = os.path.join(LIBRI, argomento)
    if os.path.isfile(candidato):
        return candidato
    if not candidato.lower().endswith(".pdf") and os.path.isfile(candidato + ".pdf"):
        return candidato + ".pdf"
    exit_with(f"book not found: {argomento} (look in books/)")


def comando_elenco():
    libri = libri_presenti()
    if not libri:
        print(f"no books in {os.path.relpath(LIBRI, RADICE)}/")
        return
    print(f"Books in {os.path.relpath(LIBRI, RADICE)}/:")
    for nome in libri:
        corso = corso_del_libro(nome)
        stato = f"course: {corso}" if corso else "NO MATCHING COURSE"
        print(f"  {nome}  ->  {stato}")
    orfani = [
        c for c in corsi_presenti()
        if normalizza(c) not in {normalizza(os.path.splitext(n)[0]) for n in libri}
    ]
    if orfani:
        print("Courses without book:")
        for c in orfani:
            print(f"  {c}")


def comando_info(percorso):
    from pypdf import PdfReader
    r = PdfReader(percorso)
    nome = os.path.basename(percorso)
    corso = corso_del_libro(nome) or "none"
    titolo = (r.metadata.title if r.metadata else None) or "(no title)"
    print(f"File:    {nome}")
    print(f"Title:   {titolo}")
    print(f"Pages:   {len(r.pages)}")
    print(f"Course:  {corso}")
    print(f"Bookmarks: {_conta_segnalibri(r.outline) if r.outline else 0}")


def _conta_segnalibri(items):
    n = 0
    for it in items:
        if isinstance(it, list):
            n += _conta_segnalibri(it)
        else:
            n += 1
    return n


def comando_indice(percorso):
    from pypdf import PdfReader
    r = PdfReader(percorso)
    if not r.outline:
        print("This PDF has no summary (bookmarks). Use 'page FILE N' or 'search FILE \"text\"'.")
        return
    print(f"Summary of {os.path.basename(percorso)}:")

    def cammina(items, livello):
        for it in items:
            if isinstance(it, list):
                cammina(it, livello + 1)
                continue
            titolo = (getattr(it, "title", "") or "").strip().replace("\n", " ")
            try:
                pagina = r.get_destination_page_number(it) + 1
            except Exception:
                pagina = "?"
            print(f"{'  ' * livello}{titolo}  (p. {pagina})")

    cammina(r.outline, 0)


def comando_pagina(percorso, argomento):
    import re
    leggi = _carica_read_slides()
    pagine = leggi.carica(percorso)
    tot = len(pagine)
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", argomento)
    if not m:
        exit_with(f"invalid page: {argomento} (use 28 or 19-21)")
    a = int(m.group(1))
    b = int(m.group(2) or a)
    if a < 1 or b > tot or a > b:
        exit_with(f"range out of book: book has {tot} pages")
    leggi.stampa(pagine, a, b)
    vuote = sum(1 for p in pagine if not p.strip())
    if vuote > tot / 2:
        print(f"WARNING: {vuote} pages out of {tot} have no text. If the file is image-based, Docling fallback reads it manually.")


def comando_cerca(percorso, ago):
    leggi = _carica_read_slides()
    pagine = leggi.carica(percorso)
    ago_norm = leggi.normalizza(ago)
    trovate = 0
    for i, pagina in enumerate(pagine, 1):
        for riga in pagina.splitlines():
            if ago_norm in leggi.normalizza(riga):
                print(f"p. {i}: {' '.join(riga.split())[:140]}")
                trovate += 1
                if trovate >= 40:
                    print("... (other results omitted: narrow search)")
                    return
    if not trovate:
        print(f'"{ago}" does not appear on any page')


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return
    comando = args[0]
    if comando == "list":
        comando_elenco()
    elif comando == "info":
        if len(args) < 2:
            exit_with("missing book: info FILE")
        comando_info(risolvi(args[1]))
    elif comando == "index":
        if len(args) < 2:
            exit_with("missing book: index FILE")
        comando_indice(risolvi(args[1]))
    elif comando == "page":
        if len(args) < 3:
            exit_with('missing page: page FILE 28')
        comando_pagina(risolvi(args[1]), args[2])
    elif comando == "search":
        if len(args) < 3:
            exit_with('missing search text: search FILE "text"')
        comando_cerca(risolvi(args[1]), " ".join(args[2:]))
    else:
        exit_with(f"unknown command: {comando} (list, info, index, page, search)")


if __name__ == "__main__":
    main()