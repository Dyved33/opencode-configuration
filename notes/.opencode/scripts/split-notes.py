#!/usr/bin/env python3
"""Splits a single raw notes file into one file per lesson. Text is not modified.

Usage:
  split-notes.py FILE                    shows the plan, writes nothing
  split-notes.py FILE --write            creates files in FILE's folder
  split-notes.py FILE --write --dest FOLDER
  split-notes.py FILE --per-section      one file per section instead of per group

How it works: every top-level heading of the file is a section. To group sections
into a lesson it uses the hidden date in image names ("Screenshot From
2026-03-05 ..." and "Pasted image 20260305..." contain it): sections without images
take the date of the previous section, and consecutive sections with the same date
form a lesson. The date never ends up in the file name nor in the index.

The source file is not touched. No existing file is overwritten.
"""
import os
import re
import sys

RE_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
RE_DATA_IMG = re.compile(r"(?:Screenshot From (\d{4})-(\d{2})-(\d{2})|Pasted image (\d{4})(\d{2})(\d{2}))")
RE_WIKILINK = re.compile(r"\[\[([^\]\|#\n]*)")
VIETATI = r'[\\/:*?"<>|#^\[\]]'


def exit_with(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def pulisci_titolo(t):
    t = re.sub(r"[*_`]", "", t).strip().rstrip(":").strip()
    return re.sub(r"\s+", " ", t)


def nome_file(titolo):
    return re.sub(r"\s+", " ", re.sub(VIETATI, " ", titolo)).strip()


def leggi_sezioni(righe):
    """Splits the file on the topmost heading level present, ignoring code blocks."""
    in_fence = False
    titoli = []
    for i, riga in enumerate(righe):
        if re.match(r"^\s*(?:>\s*)*(```|~~~)", riga):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = RE_HEADING.match(riga)
        if m:
            titoli.append((i, len(m.group(1)), m.group(2)))
    if not titoli:
        exit_with("file has no headings: I don't know where to split it")
    livello = min(l for _i, l, _t in titoli)
    inizi = [(i, t) for i, l, t in titoli if l == livello]
    sezioni = []
    if "".join(righe[: inizi[0][0]]).strip():
        sezioni.append({"titolo": "Preamble", "inizio": 0, "fine": inizi[0][0], "corpo_da": 0})
    for n, (i, t) in enumerate(inizi):
        fine = inizi[n + 1][0] if n + 1 < len(inizi) else len(righe)
        sezioni.append({"titolo": pulisci_titolo(t), "inizio": i, "fine": fine, "corpo_da": i + 1})
    annidati = {i: l for i, l, _t in titoli if l > livello}
    return sezioni, livello, annidati


def assegna_date(sezioni, righe):
    precedente = None
    for s in sezioni:
        s["dedotta"] = False
        s["data"] = None
        for riga in righe[s["inizio"]: s["fine"]]:
            m = RE_DATA_IMG.search(riga)
            if m:
                g = [x for x in m.groups() if x]
                s["data"] = "-".join(g)
                break
        if s["data"] is None and precedente:
            s["data"], s["dedotta"] = precedente, True
        precedente = s["data"] or precedente


def raggruppa(sezioni, per_sezione):
    lezioni = []
    for s in sezioni:
        if (not per_sezione and lezioni and s["data"] is not None
                and lezioni[-1]["data"] == s["data"]):
            lezioni[-1]["sezioni"].append(s)
        else:
            lezioni.append({"data": s["data"], "sezioni": [s]})
    for lez in lezioni:
        titoli = [s["titolo"] for s in lez["sezioni"]]
        titolo = ", ".join(titoli[:3]) + (" etc" if len(titoli) > 3 else "")
        lez["titolo"] = titolo
        base = nome_file(titolo)
        lez["file"] = base + ".md"
        lez["righe"] = sum(s["fine"] - s["inizio"] for s in lez["sezioni"])
        lez["dedotta"] = all(s["dedotta"] for s in lez["sezioni"])
    visti = {}
    for lez in lezioni:
        chiave = lez["file"].lower()
        visti[chiave] = visti.get(chiave, 0) + 1
        if visti[chiave] > 1:
            lez["file"] = lez["file"][:-3] + f" ({visti[chiave]}).md"
    return lezioni


def componi(lez, righe, livello, annidati):
    """Note text: # title, then sections. Nested headings scale accordingly."""
    singola = len(lez["sezioni"]) == 1
    out = [f"# {lez['titolo']}\n", "\n"]
    for s in lez["sezioni"]:
        if not singola:
            out.append(f"## {s['titolo']}\n")
        for i in range(s["corpo_da"], s["fine"]):
            riga = righe[i]
            if i in annidati:
                m = RE_HEADING.match(riga)
                nuovo = min(annidati[i] - livello + (1 if singola else 2), 6)
                riga = f"{'#' * nuovo} {m.group(2)}\n"
            out.append(riga)
        if out and out[-1].strip():
            out.append("\n")
    testo = "".join(out)
    return testo if testo.endswith("\n") else testo + "\n"


def riga_indice(lez):
    nome = lez["file"][:-3]
    return f"- [[{nome}|{lez['titolo']}]]\n"


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__.strip())
        return
    scrivi = "--write" in args
    per_sezione = "--per-section" in args
    dest = None
    if "--dest" in args:
        i = args.index("--dest")
        if i + 1 >= len(args):
            exit_with("missing folder after --dest")
        dest = args[i + 1]
        del args[i: i + 2]
    posizionali = [a for a in args if not a.startswith("--")]
    if len(posizionali) != 1:
        exit_with("specify a single file to split")
    sorgente = posizionali[0]
    if not os.path.isfile(sorgente):
        exit_with(f"file not found: {sorgente}")
    dest = dest or os.path.dirname(sorgente) or "."

    with open(sorgente, encoding="utf-8") as f:
        righe = f.readlines()
    sezioni, livello, annidati = leggi_sezioni(righe)
    assegna_date(sezioni, righe)
    lezioni = raggruppa(sezioni, per_sezione)

    print(f"{os.path.basename(sorgente)}: {len(righe)} lines, {len(sezioni)} sections -> {len(lezioni)} files in {dest}/\n")
    for lez in lezioni:
        nota = ""
        if lez["data"] is None:
            nota = "   <- no image: separate group, merge manually if needed"
        elif lez["dedotta"]:
            nota = "   <- grouped with previous section"
        print(f"{lez['righe']:>5} lines  {lez['file']}{nota}")

    esistenti = [lez["file"] for lez in lezioni if os.path.exists(os.path.join(dest, lez["file"]))]
    if not scrivi:
        print("\nI wrote nothing. Groups follow images in each section: check them.")
        if esistenti:
            print(f"WARNING: {len(esistenti)} of these files already exist: with --write I would stop without creating anything.")
        print("To create files: add --write. For one file per section: --per-section.")
        return

    if esistenti:
        exit_with("these files already exist, I overwrite nothing: " + "; ".join(esistenti))
    os.makedirs(dest, exist_ok=True)
    for lez in lezioni:
        with open(os.path.join(dest, lez["file"]), "x", encoding="utf-8") as f:
            f.write(componi(lez, righe, livello, annidati))

    cartella = os.path.basename(os.path.abspath(dest))
    indici = sorted(f for f in os.listdir(dest) if f.startswith("00") and f.lower().endswith(".md"))
    if indici:
        indice = os.path.join(dest, indici[0])
        with open(indice, encoding="utf-8") as f:
            contenuto = f.read()
        presenti = {os.path.basename(t.strip()).lower() for t in RE_WIKILINK.findall(contenuto)}
        nuove = [riga_indice(l) for l in lezioni if l["file"][:-3].lower() not in presenti]
        if nuove:
            with open(indice, "a", encoding="utf-8") as f:
                f.write(("" if contenuto.endswith("\n") else "\n") + "".join(nuove))
        print(f"\nIndex updated: {indici[0]} (+{len(nuove)} lines)")
    else:
        indice = os.path.join(dest, f"00 Index - {cartella}.md")
        with open(indice, "x", encoding="utf-8") as f:
            f.write(f"# Index - {cartella}\n\n" + "".join(riga_indice(l) for l in lezioni))
        print(f"\nIndex created: {os.path.basename(indice)}")

    print(f"Created {len(lezioni)} files. Source file is intact: after checking, archive or delete it yourself.")
    print("If a title or name does not suit you, rename the file from Obsidian: index links update automatically.")


if __name__ == "__main__":
    main()