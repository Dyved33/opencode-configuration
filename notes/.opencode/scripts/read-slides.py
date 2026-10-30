#!/usr/bin/env python3
"""Reads the teacher's material text (PDF, PPTX, PPT) one page at a time.

Usage:
  read-slides.py FILE                  list of pages with the first line of each
  read-slides.py FILE 28               text of page 28
  read-slides.py FILE 19-21            text of pages 19 to 21
  read-slides.py FILE all              text of the whole file
  read-slides.py FILE --search "text"  pages where the text appears

Writes nothing in the vault. .ppt files are converted in a temporary folder.

If a PDF or PPTX has no extractable text (image pages), text is read with Docling (OCR),
when the file is not too long. To force Docling on long files:
READ_SLIDES_DOCLING_FORZA=1. To change the page threshold: READ_SLIDES_DOCLING_LIMITE=N (default 60).
"""
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def exit_with(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def pdf_pages(path):
    if not shutil.which("pdftotext"):
        exit_with("pdftotext not installed (poppler-utils package)")
    r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True)
    if r.returncode != 0:
        exit_with(f"pdftotext cannot read the file: {r.stderr.decode(errors='replace').strip()}")
    pages = r.stdout.decode("utf-8", errors="replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pptx_pages(path):
    with zipfile.ZipFile(path) as z:
        nomi = set(z.namelist())
        ordine = []
        try:
            pres = ET.fromstring(z.read("ppt/presentation.xml"))
            rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
            mappa = {r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", NS)}
            for sld in pres.findall("p:sldIdLst/p:sldId", NS):
                target = mappa.get(sld.get(f"{{{NS['r']}}}id"), "")
                nome = "ppt/" + target.lstrip("/").removeprefix("ppt/")
                if nome in nomi:
                    ordine.append(nome)
        except (KeyError, ET.ParseError):
            pass
        if not ordine:
            ordine = sorted(
                (n for n in nomi if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()),
            )
        pagine = []
        for nome in ordine:
            radice = ET.fromstring(z.read(nome))
            righe = []
            for par in radice.iter(f"{{{NS['a']}}}p"):
                testo = "".join(t.text or "" for t in par.iter(f"{{{NS['a']}}}t")).strip()
                if testo:
                    righe.append(testo)
            pagine.append("\n".join(righe))
        return pagine


def ppt_pages(path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        exit_with(".ppt files require LibreOffice: convert to PDF manually")
    st = os.stat(path)
    chiave = hashlib.sha1(f"{os.path.abspath(path)}{st.st_mtime}{st.st_size}".encode()).hexdigest()[:16]
    cache = os.path.join(tempfile.gettempdir(), "read-slides-cache")
    os.makedirs(cache, exist_ok=True)
    pdf = os.path.join(cache, chiave + ".pdf")
    if not os.path.exists(pdf):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, path],
                capture_output=True,
            )
            prodotti = [f for f in os.listdir(tmp) if f.endswith(".pdf")]
            if r.returncode != 0 or not prodotti:
                exit_with(".ppt conversion failed: convert to PDF manually")
            shutil.move(os.path.join(tmp, prodotti[0]), pdf)
    return pdf_pages(pdf)


LIMITE_DOCLING = int(os.environ.get("READ_SLIDES_DOCLING_LIMITE", "60"))


def docling_pages(path):
    try:
        from docling.document_converter import DocumentConverter
    except ImportError:
        print(
            "docling not installed: run 'pip install --user --break-system-packages docling'",
            file=sys.stderr,
        )
        return None
    doc = DocumentConverter().convert(path).document
    per_pagina = {}
    for voce in doc.iterate_items():
        item = voce[0] if isinstance(voce, tuple) else voce
        prov = getattr(item, "prov", None)
        if not prov:
            continue
        testo = getattr(item, "text", "") or ""
        if not testo and hasattr(item, "export_to_markdown"):
            try:
                testo = item.export_to_markdown()
            except Exception:
                testo = ""
        if testo.strip():
            per_pagina.setdefault(prov[0].page_no, []).append(testo.strip())
    tot = doc.num_pages() if hasattr(doc, "num_pages") else (max(per_pagina) if per_pagina else 0)
    return ["\n\n".join(per_pagina.get(n, [])) for n in range(1, tot + 1)]


def maggior_parte_vuota(pagine):
    return not pagine or sum(1 for p in pagine if not p.strip()) > len(pagine) / 2


def carica(path):
    if not os.path.isfile(path):
        exit_with(f"file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        pagine = pdf_pages(path)
    elif ext == ".pptx":
        pagine = pptx_pages(path)
    elif ext == ".ppt":
        return ppt_pages(path)
    else:
        exit_with(f"unsupported format: {ext} (allowed: .pdf, .pptx, .ppt)")

    if maggior_parte_vuota(pagine):
        if len(pagine) <= LIMITE_DOCLING or os.environ.get("READ_SLIDES_DOCLING_FORZA") == "1":
            print(
                f"[{os.path.basename(path)}] text not extractable: trying Docling, may take time...",
                file=sys.stderr,
            )
            alternativo = docling_pages(path)
            if alternativo and not maggior_parte_vuota(alternativo):
                return alternativo
        else:
            print(
                f"[{os.path.basename(path)}] {len(pagine)} pages without text: Docling skipped (long file). "
                "Use slide photo or force with READ_SLIDES_DOCLING_FORZA=1.",
                file=sys.stderr,
            )
    return pagine


def normalizza(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def prima_riga(testo):
    for riga in testo.splitlines():
        if riga.strip():
            return " ".join(riga.split())[:80]
    return "(image only, no text)"


def stampa(pagine, a, b):
    tot = len(pagine)
    for n in range(a, b + 1):
        print(f"=== page {n}/{tot} ===")
        testo = pagine[n - 1].strip("\n")
        print(testo if testo.strip() else "(image only, no text: check manually)")
        print()


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return
    path = args[0]
    pagine = carica(path)
    tot = len(pagine)
    if tot == 0:
        exit_with("no pages read")
    vuote = sum(1 for p in pagine if not p.strip())

    if len(args) == 1:
        print(f"{os.path.basename(path)}: {tot} pages")
        for i, p in enumerate(pagine, 1):
            print(f"{i:>4}  {prima_riga(p)}")
    elif args[1] == "--search":
        if len(args) < 3:
            exit_with('missing search text: --search "text"')
        ago = normalizza(" ".join(args[2:]))
        trovate = 0
        for i, p in enumerate(pagine, 1):
            for riga in p.splitlines():
                if ago in normalizza(riga):
                    print(f"p. {i}: {' '.join(riga.split())[:140]}")
                    trovate += 1
                    if trovate >= 40:
                        print("... (other results omitted: narrow search)")
                        return
        if not trovate:
            print(f'"{" ".join(args[2:])}" does not appear on any page')
    elif args[1] == "all":
        stampa(pagine, 1, tot)
    else:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", args[1])
        if not m:
            exit_with(f"invalid page: {args[1]} (use 28, 19-21 or all)")
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if a < 1 or b > tot or a > b:
            exit_with(f"range out of file: file has {tot} pages")
        stampa(pagine, a, b)

    if vuote > tot / 2:
        print(f"WARNING: {vuote} pages out of {tot} have no text. File is image-based: content must be read manually.")

if __name__ == "__main__":
    main()