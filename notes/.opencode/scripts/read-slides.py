#!/usr/bin/env python3
"""Reads the text of the teacher's material (PDF, PPTX, PPT) one page at a time.

Usage:
  read-slides.py FILE                  page list with the first line of each
  read-slides.py FILE 28               text of page 28
  read-slides.py FILE 19-21            text of pages 19 to 21
  read-slides.py FILE all              text of the whole file
  read-slides.py FILE --search "text"  pages in which the text appears

It writes nothing in the vault. The .ppt files are converted into a temporary folder.
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


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def pdf_pages(path):
    if not shutil.which("pdftotext"):
        fail("pdftotext not installed (poppler-utils package)")
    r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True)
    if r.returncode != 0:
        fail(f"pdftotext cannot read the file: {r.stderr.decode(errors='replace').strip()}")
    pages = r.stdout.decode("utf-8", errors="replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def pptx_pages(path):
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        order = []
        try:
            pres = ET.fromstring(z.read("ppt/presentation.xml"))
            rels = ET.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
            mapping = {r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", NS)}
            for sld in pres.findall("p:sldIdLst/p:sldId", NS):
                target = mapping.get(sld.get(f"{{{NS['r']}}}id"), "")
                name = "ppt/" + target.lstrip("/").removeprefix("ppt/")
                if name in names:
                    order.append(name)
        except (KeyError, ET.ParseError):
            pass
        if not order:
            order = sorted(
                (n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()),
            )
        pages = []
        for name in order:
            root = ET.fromstring(z.read(name))
            lines = []
            for par in root.iter(f"{{{NS['a']}}}p"):
                text = "".join(t.text or "" for t in par.iter(f"{{{NS['a']}}}t")).strip()
                if text:
                    lines.append(text)
            pages.append("\n".join(lines))
        return pages


def ppt_pages(path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        fail(".ppt files require LibreOffice: convert it to PDF by hand")
    st = os.stat(path)
    key = hashlib.sha1(f"{os.path.abspath(path)}{st.st_mtime}{st.st_size}".encode()).hexdigest()[:16]
    cache = os.path.join(tempfile.gettempdir(), "read-slides-cache")
    os.makedirs(cache, exist_ok=True)
    pdf = os.path.join(cache, key + ".pdf")
    if not os.path.exists(pdf):
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, path],
                capture_output=True,
            )
            produced = [f for f in os.listdir(tmp) if f.endswith(".pdf")]
            if r.returncode != 0 or not produced:
                fail(".ppt conversion failed: convert it to PDF by hand")
            shutil.move(os.path.join(tmp, produced[0]), pdf)
    return pdf_pages(pdf)


def load(path):
    if not os.path.isfile(path):
        fail(f"file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return pdf_pages(path)
    if ext == ".pptx":
        return pptx_pages(path)
    if ext == ".ppt":
        return ppt_pages(path)
    fail(f"unsupported format: {ext} (allowed: .pdf, .pptx, .ppt)")


def normalize(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def first_line(text):
    for line in text.splitlines():
        if line.strip():
            return " ".join(line.split())[:80]
    return "(image only, no text)"


def print_pages(pages, a, b):
    total = len(pages)
    for n in range(a, b + 1):
        print(f"=== page {n}/{total} ===")
        text = pages[n - 1].strip("\n")
        print(text if text.strip() else "(image only, no text: look at it by hand)")
        print()


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return
    path = args[0]
    pages = load(path)
    total = len(pages)
    if total == 0:
        fail("no page read")
    empty = sum(1 for p in pages if not p.strip())

    if len(args) == 1:
        print(f"{os.path.basename(path)}: {total} pages")
        for i, p in enumerate(pages, 1):
            print(f"{i:>4}  {first_line(p)}")
    elif args[1] == "--search":
        if len(args) < 3:
            fail('missing text to search: --search "text"')
        needle = normalize(" ".join(args[2:]))
        found = 0
        for i, p in enumerate(pages, 1):
            for line in p.splitlines():
                if needle in normalize(line):
                    print(f"p. {i}: {' '.join(line.split())[:140]}")
                    found += 1
                    if found >= 40:
                        print("... (more results omitted: narrow the search)")
                        return
        if not found:
            print(f'"{" ".join(args[2:])}" does not appear on any page')
    elif args[1] == "all":
        print_pages(pages, 1, total)
    else:
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", args[1])
        if not m:
            fail(f"invalid page: {args[1]} (use 28, 19-21 or all)")
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if a < 1 or b > total or a > b:
            fail(f"range outside the file: the file has {total} pages")
        print_pages(pages, a, b)

    if empty > total / 2:
        print(f"WARNING: {empty} pages out of {total} have no text. The file is made of images: the content has to be read by hand.")


if __name__ == "__main__":
    main()