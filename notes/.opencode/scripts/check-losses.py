#!/usr/bin/env python3
"""Checks that no information has been lost in a note compared to the source.

Usage:
  check-losses.py NOTE --save         saves a copy of the note BEFORE modifying it
  check-losses.py NOTE                compares the note with the saved copy
                                      (if missing, with the last git commit)
  check-losses.py NOTE --with FILE    compares the note with raw notes (.txt, .md)
                                      or with the teacher's material (.pdf, .pptx, .ppt)

What it looks for in the source and no longer finds in the note: formulas, code lines,
images, numbers, and lines (or slides) it no longer finds.

Text files linked from the note via a wikilink (e.g. code in esercizi/) are read and
counted as if they were inside the note: an exercise moved to a file does not show as lost.

It is a word-based check, not meaning-based: every item is "to check", not a certain
error. A sentence rewritten with other words may be flagged; a flagged sentence must
be reread in the source and, if the information is truly missing, put back in the note.
Saved copies are in .opencode/originali/.
"""
import os
import re
import subprocess
import sys
import unicodedata

QUI = os.path.dirname(os.path.abspath(__file__))
ORIGINALI = os.path.join(os.path.dirname(QUI), "originali")
SOGLIA_RIGA = 0.6     # below this ratio of words found in the same spot, the line is reported
SOGLIA_SLIDE = 0.4
MAX_VOCI = 60

STOP = set("""
a alla alle allo agli anche ancora avere aveva base bene caso come cosa cose cosi cioe con cui
dalla dalle dallo dagli degli della delle dello dentro deve devono dopo dove dunque ecco
essa esse essere esso fare fatto fino formato fra hanno infatti inoltre loro meno mentre
molto nella nelle nello negli ogni oppure ossia parte perche pero piu poi possono prima
proprio puo quale quali quando quanto quella quelle quelli quello questa queste questi
questo quindi sara sempre senza sia sono solo sopra sotto stata stato stessa stesso sua
sue sugli sulla sulle sullo suo suoi tale tali tanto tipo tra tutta tutte tutti tutto
una uno viene vengono verso volta
""".split())


def exit_with(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def senza_accenti(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def parole(testo):
    """Content words, reduced to first 5 letters to handle plurals and conjugations."""
    out = set()
    for p in re.findall(r"[a-z]{4,}", senza_accenti(testo)):
        if p not in STOP:
            out.add(p[:5])
    return out


def numeri(testo):
    return set(re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])", testo))


def formule(testo):
    out = set()
    for f in re.findall(r"\$\$(.+?)\$\$", testo, re.S) + re.findall(r"(?<!\$)\$([^$\n]+)\$(?!\$)", testo):
        f = re.sub(r"\s+", "", f)
        if len(f) > 2:
            out.add(f)
    return out


def blocchi_codice(righe):
    """Lines inside ``` blocks; returns (code lines, non-code lines)."""
    codice, fuori = [], []
    dentro = False
    for n, riga in enumerate(righe, 1):
        nuda = re.sub(r"^\s*(?:>\s*)+", "", riga)
        if re.match(r"^\s*(```|~~~)", nuda):
            dentro = not dentro
            continue
        (codice if dentro else fuori).append((n, riga))
    return codice, fuori


def immagini(testo):
    nomi = set(re.findall(r"!\[\[([^\]\|#\n]+)", testo))
    nomi |= set(re.findall(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", testo, re.I))
    return {os.path.basename(n.strip()).lower() for n in nomi}


RE_LINK_FILE = re.compile(r"(?<!\!)\[\[([^\]\|#\n]+\.[A-Za-z0-9]+)(?:#[^\]\|\n]*)?(?:\|[^\]\n]*)?\]\]")
ESTENSIONI_TESTO = {
    ".py", ".c", ".h", ".cpp", ".cc", ".java", ".js", ".ts", ".html", ".css", ".sql",
    ".sh", ".r", ".tex", ".xml", ".json", ".yml", ".yaml", ".php", ".rb", ".go", ".rs",
    ".kt", ".swift", ".hs", ".ml", ".scala", ".asm", ".pl", ".txt",
}


def allegati(nota_testo, cartella):
    """Text of files linked from the note (code in esercizi/): counts as part of the note."""
    pezzi = []
    for target in RE_LINK_FILE.findall(nota_testo):
        if os.path.splitext(target)[1].lower() not in ESTENSIONI_TESTO:
            continue
        percorso = os.path.join(cartella, target.strip())
        if not os.path.isfile(percorso):
            continue
        try:
            with open(percorso, encoding="utf-8") as f:
                pezzi.append(f.read())
        except (OSError, UnicodeDecodeError):
            continue
    return "".join(f"\n```\n{p}\n```\n" for p in pezzi)


def pulisci_markdown(riga):
    riga = re.sub(r"<[^>]+>", " ", riga)
    riga = re.sub(r"!?\[\[([^\]\|]*\|)?([^\]]*)\]\]", r"\2", riga)
    riga = re.sub(r"^\s*(?:>\s*)+(\[![^\]]*\])?", "", riga)
    return re.sub(r"[*_`#|]", " ", riga)


def chiave(nota):
    return os.path.relpath(os.path.abspath(nota)).replace(os.sep, "__")


def versione_git(nota):
    try:
        rel = os.path.basename(nota)
        r = subprocess.run(["git", "show", f"HEAD:./{rel}"], capture_output=True,
                           cwd=os.path.dirname(os.path.abspath(nota)) or ".")
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace")
    except OSError:
        pass
    return None


def pagine_materiale(path):
    r = subprocess.run([sys.executable, os.path.join(QUI, "read-slides.py"), path, "all"],
                       capture_output=True)
    testo = r.stdout.decode("utf-8", errors="replace")
    if testo.startswith("ERRORE"):
        exit_with(testo.strip()[8:])
    pagine = []
    for blocco in re.split(r"^=== pagina (\d+)/\d+ ===$", testo, flags=re.M)[1:]:
        pagine.append(blocco)
    return [(int(pagine[i]), pagine[i + 1]) for i in range(0, len(pagine) - 1, 2)]


def mostra(titolo, voci):
    if not voci:
        return 0
    print(f"\n{titolo} ({len(voci)})")
    for v in voci[:MAX_VOCI]:
        print(f"  {v}")
    if len(voci) > MAX_VOCI:
        print(f"  ... and {len(voci) - MAX_VOCI} more")
    return len(voci)


def confronta_testo(fonte, nota_testo, etichetta):
    righe_fonte = fonte.split("\n")
    righe_nota = nota_testo.split("\n")
    codice_f, fuori_f = blocchi_codice(righe_fonte)
    codice_n, _ = blocchi_codice(righe_nota)
    numeri_nota = numeri(nota_testo)
    # every source line must be found in a precise spot of the note (3-line window),
    # not in the whole note vocabulary: so a removed line is visible even if its words
    # appear elsewhere
    per_riga = [parole(pulisci_markdown(r)) for r in righe_nota]
    finestre = [per_riga[i] | (per_riga[i + 1] if i + 1 < len(per_riga) else set())
                | (per_riga[i + 2] if i + 2 < len(per_riga) else set()) for i in range(len(per_riga))]
    tot = 0

    perse = sorted(formule(fonte) - formule(nota_testo), key=len, reverse=True)
    tot += mostra("Formulas no longer found", [f"${f[:110]}$" for f in perse])

    codice_nota = {re.sub(r"\s+", "", r) for _n, r in codice_n}
    perse = [f"line {n}: {r.strip()[:110]}" for n, r in codice_f
             if len(re.sub(r"\s+", "", r)) > 3 and re.sub(r"\s+", "", r) not in codice_nota]
    tot += mostra("Code lines no longer found", perse)

    perse = sorted(immagini(fonte) - immagini(nota_testo))
    tot += mostra("Images no longer found", perse)

    voci_numeri, voci_righe = [], []
    for n, riga in fuori_f:
        pulita = pulisci_markdown(riga)
        senza_formule = re.sub(r"\$[^$]*\$", " ", pulita)
        mancanti = sorted(numeri(senza_formule) - numeri_nota)
        if mancanti:
            voci_numeri.append(f"line {n}: {', '.join(mancanti)}  <- {pulita.strip()[:90]}")
        p = parole(senza_formule)
        if len(p) >= 3:
            quota = max((len(p & f) / len(p) for f in finestre), default=0)
            if quota < SOGLIA_RIGA:
                voci_righe.append(f"line {n} ({int(quota * 100)}% found): {pulita.strip()[:120]}")
    tot += mostra("Numbers no longer found", voci_numeri)
    tot += mostra(f"Lines of {etichetta} not found in the note", voci_righe)
    return tot


def confronta_slide(pagine, nota_testo):
    parole_nota = parole(pulisci_markdown(nota_testo))
    numeri_nota = numeri(nota_testo)
    voci, voci_numeri, vuote = [], [], 0
    for n, testo in pagine:
        p = parole(testo)
        if len(p) < 4:
            vuote += 1
            continue
        quota = len(p & parole_nota) / len(p)
        prima = next((" ".join(r.split()) for r in testo.splitlines() if r.strip()), "")
        if quota < SOGLIA_SLIDE:
            voci.append(f"page {n} ({int(quota * 100)}% found): {prima[:100]}")
        mancanti = sorted(x for x in numeri(testo) - numeri_nota if len(x) > 1)
        if mancanti and quota >= SOGLIA_SLIDE:
            voci_numeri.append(f"page {n}: {', '.join(mancanti[:12])}")
    tot = mostra("Material pages little or not at all present in the note", voci)
    tot += mostra("Material numbers not found in the note", voci_numeri)
    if vuote:
        print(f"\n{vuote} pages with little or no text (titles, images): not checkable, check manually.")
    return tot


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__.strip())
        return
    con = None
    if "--with" in args:
        i = args.index("--with")
        if i + 1 >= len(args):
            exit_with("missing file after --with")
        con = args[i + 1]
        del args[i: i + 2]
    salva = "--save" in args
    posizionali = [a for a in args if not a.startswith("--")]
    if len(posizionali) != 1:
        exit_with("specify a single note")
    nota = posizionali[0]
    if not os.path.isfile(nota):
        exit_with(f"note not found: {nota}")
    with open(nota, encoding="utf-8") as f:
        nota_testo = f.read()
    copia = os.path.join(ORIGINALI, chiave(nota))

    if salva:
        os.makedirs(ORIGINALI, exist_ok=True)
        with open(copia, "w", encoding="utf-8") as f:
            f.write(nota_testo)
        print(f"Copy saved: {len(nota_testo.split())} words, {nota_testo.count(chr(10)) + 1} lines.")
        return

    estesa = nota_testo + allegati(nota_testo, os.path.dirname(os.path.abspath(nota)) or ".")

    if con:
        if not os.path.isfile(con):
            exit_with(f"file not found: {con}")
        est = os.path.splitext(con)[1].lower()
        print(f"Comparison: {os.path.basename(nota)}  <-  {os.path.basename(con)}")
        if est in (".pdf", ".pptx", ".ppt"):
            tot = confronta_slide(pagine_materiale(con), estesa)
        else:
            with open(con, encoding="utf-8", errors="replace") as f:
                tot = confronta_testo(f.read(), estesa, "raw notes")
    else:
        if os.path.isfile(copia):
            with open(copia, encoding="utf-8") as f:
                fonte = f.read()
            origine = "saved copy before modification"
        else:
            fonte = versione_git(nota)
            origine = "last git commit"
            if fonte is None:
                exit_with("no saved copy nor git commit for this note: "
                          "before modifying run the script with --save")
        prima, dopo = len(fonte.split()), len(nota_testo.split())
        print(f"Comparison: {os.path.basename(nota)}  <-  {origine}")
        print(f"Words: {prima} -> {dopo} ({(dopo - prima) / max(prima, 1) * 100:+.0f}%)")
        tot = confronta_testo(fonte, estesa, "text")

    if tot == 0:
        print("\nNo loss detected.")
    else:
        print(f"\n{tot} items to check. For each: reread the source; if the information is truly "
              "missing in the note, put it back. If it is there with other words, it's fine.")

if __name__ == "__main__":
    main()