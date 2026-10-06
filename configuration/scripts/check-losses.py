#!/usr/bin/env python3
"""Checks that a note has not lost information compared to the source.

Usage:
  check-losses.py NOTE --save         saves a copy of the note BEFORE editing it
  check-losses.py NOTE                compares the note against the saved copy
                                      (if missing, against the last git commit)
  check-losses.py NOTE --with FILE    compares the note against raw notes (.txt, .md)
                                      or against the teacher's material (.pdf, .pptx, .ppt)

What it looks for in the source and no longer finds in the note: formulas, lines of
code, images, numbers, and the lines (or slides) it can't find.

It is a check on words, not on meaning: every item is "to check", not a certain error.
A sentence rewritten in other words can be reported; a reported sentence must be
reread in the source and, if the information really is missing, put back in the note.
The saved copies live in .opencode/originals/.
"""
import os
import re
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ORIGINALS = os.path.join(os.path.dirname(HERE), "originals")
LINE_THRESHOLD = 0.6   # below this share of words found again at the same spot the line is reported
SLIDE_THRESHOLD = 0.4
MAX_ITEMS = 60

STOP = set("""
alla alle allo agli anche ancora avere aveva base bene caso come cosa cose cosi cioe con cui
dalla dalle dallo dagli degli della delle dello dentro deve devono dopo dove dunque ecco
essa esse essere esso fare fatto fino formato fra hanno infatti inoltre loro meno mentre
molto nella nelle nello negli ogni oppure ossia parte perche pero piu poi possono prima
proprio puo quale quali quando quanto quella quelle quelli quello questa queste questi
questo quindi sara sempre senza sia sono solo sopra sotto stata stato stessa stesso sua
sue sugli sulla sulle sullo suo suoi tale tali tanto tipo tra tutta tutte tutti tutto
una uno viene vengono verso volta
""".split())


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def strip_accents(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def words(text):
    """Content words, reduced to the first 5 letters to absorb plurals and conjugations."""
    out = set()
    for p in re.findall(r"[a-z]{4,}", strip_accents(text)):
        if p not in STOP:
            out.add(p[:5])
    return out


def numbers(text):
    return set(re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?(?![\w])", text))


def formulas(text):
    out = set()
    for f in re.findall(r"\$\$(.+?)\$\$", text, re.S) + re.findall(r"(?<!\$)\$([^$\n]+)\$(?!\$)", text):
        f = re.sub(r"\s+", "", f)
        if len(f) > 2:
            out.add(f)
    return out


def code_blocks(lines):
    """Lines inside ``` blocks; returns (code lines, lines outside the code)."""
    code, outside = [], []
    inside = False
    for n, line in enumerate(lines, 1):
        bare = re.sub(r"^\s*(?:>\s*)+", "", line)
        if re.match(r"^\s*(```|~~~)", bare):
            inside = not inside
            continue
        (code if inside else outside).append((n, line))
    return code, outside


def images(text):
    names = set(re.findall(r"!\[\[([^\]\|#\n]+)", text))
    names |= set(re.findall(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", text, re.I))
    return {os.path.basename(n.strip()).lower() for n in names}


def clean_markdown(line):
    line = re.sub(r"<[^>]+>", " ", line)
    line = re.sub(r"!?\[\[([^\]\|]*\|)?([^\]]*)\]\]", r"\2", line)
    line = re.sub(r"^\s*(?:>\s*)+(\[![^\]]*\])?", "", line)
    return re.sub(r"[*_`#|]", " ", line)


def key(note):
    return os.path.relpath(os.path.abspath(note)).replace(os.sep, "__")


def git_version(note):
    try:
        rel = os.path.basename(note)
        r = subprocess.run(["git", "show", f"HEAD:./{rel}"], capture_output=True,
                           cwd=os.path.dirname(os.path.abspath(note)) or ".")
        if r.returncode == 0:
            return r.stdout.decode("utf-8", errors="replace")
    except OSError:
        pass
    return None


def material_pages(path):
    r = subprocess.run([sys.executable, os.path.join(HERE, "read-slides.py"), path, "all"],
                       capture_output=True)
    text = r.stdout.decode("utf-8", errors="replace")
    if text.startswith("ERROR"):
        fail(text.strip()[8:])
    pages = []
    for block in re.split(r"^=== page (\d+)/\d+ ===$", text, flags=re.M)[1:]:
        pages.append(block)
    return [(int(pages[i]), pages[i + 1]) for i in range(0, len(pages) - 1, 2)]


def show(title, items):
    if not items:
        return 0
    print(f"\n{title} ({len(items)})")
    for v in items[:MAX_ITEMS]:
        print(f"  {v}")
    if len(items) > MAX_ITEMS:
        print(f"  ... and {len(items) - MAX_ITEMS} more")
    return len(items)


def compare_text(source, note_text, label):
    source_lines = source.split("\n")
    note_lines = note_text.split("\n")
    code_src, outside_src = code_blocks(source_lines)
    code_note, _ = code_blocks(note_lines)
    note_numbers = numbers(note_text)
    # every source line must be found again at a precise spot of the note (window of 3 lines),
    # not in the vocabulary of the whole note: this way a removed line shows even if its
    # words appear somewhere else
    per_line = [words(clean_markdown(r)) for r in note_lines]
    windows = [per_line[i] | (per_line[i + 1] if i + 1 < len(per_line) else set())
               | (per_line[i + 2] if i + 2 < len(per_line) else set()) for i in range(len(per_line))]
    total = 0

    lost = sorted(formulas(source) - formulas(note_text), key=len, reverse=True)
    total += show("Formulas I can no longer find", [f"${f[:110]}$" for f in lost])

    code_in_note = {re.sub(r"\s+", "", r) for _n, r in code_note}
    lost = [f"line {n}: {r.strip()[:110]}" for n, r in code_src
            if len(re.sub(r"\s+", "", r)) > 3 and re.sub(r"\s+", "", r) not in code_in_note]
    total += show("Lines of code I can no longer find", lost)

    lost = sorted(images(source) - images(note_text))
    total += show("Images I can no longer find", lost)

    number_items, line_items = [], []
    for n, line in outside_src:
        cleaned = clean_markdown(line)
        no_formulas = re.sub(r"\$[^$]*\$", " ", cleaned)
        missing = sorted(numbers(no_formulas) - note_numbers)
        if missing:
            number_items.append(f"line {n}: {', '.join(missing)}  <- {cleaned.strip()[:90]}")
        p = words(no_formulas)
        if len(p) >= 3:
            ratio = max((len(p & w) / len(p) for w in windows), default=0)
            if ratio < LINE_THRESHOLD:
                line_items.append(f"line {n} ({int(ratio * 100)}% found again): {cleaned.strip()[:120]}")
    total += show("Numbers I can no longer find", number_items)
    total += show(f"Lines of {label} I can't find in the note", line_items)
    return total


def compare_slides(pages, note_text):
    note_words = words(clean_markdown(note_text))
    note_numbers = numbers(note_text)
    items, number_items, empty = [], [], 0
    for n, text in pages:
        p = words(text)
        if len(p) < 4:
            empty += 1
            continue
        ratio = len(p & note_words) / len(p)
        first = next((" ".join(r.split()) for r in text.splitlines() if r.strip()), "")
        if ratio < SLIDE_THRESHOLD:
            items.append(f"page {n} ({int(ratio * 100)}% found again): {first[:100]}")
        missing = sorted(x for x in numbers(text) - note_numbers if len(x) > 1)
        if missing and ratio >= SLIDE_THRESHOLD:
            number_items.append(f"page {n}: {', '.join(missing[:12])}")
    total = show("Material pages barely or not at all present in the note", items)
    total += show("Material numbers I can't find in the note", number_items)
    if empty:
        print(f"\n{empty} pages with little or no text (titles, images): cannot be checked, look at them by hand.")
    return total


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__.strip())
        return
    with_source = None
    if "--with" in args:
        i = args.index("--with")
        if i + 1 >= len(args):
            fail("missing file after --with")
        with_source = args[i + 1]
        del args[i: i + 2]
    save = "--save" in args
    positional = [a for a in args if not a.startswith("--")]
    if len(positional) != 1:
        fail("indicate a single note")
    note = positional[0]
    if not os.path.isfile(note):
        fail(f"note not found: {note}")
    with open(note, encoding="utf-8") as f:
        note_text = f.read()
    copy = os.path.join(ORIGINALS, key(note))

    if save:
        os.makedirs(ORIGINALS, exist_ok=True)
        with open(copy, "w", encoding="utf-8") as f:
            f.write(note_text)
        print(f"Copy saved: {len(note_text.split())} words, {note_text.count(chr(10)) + 1} lines.")
        return

    if with_source:
        if not os.path.isfile(with_source):
            fail(f"file not found: {with_source}")
        ext = os.path.splitext(with_source)[1].lower()
        print(f"Comparison: {os.path.basename(note)}  <-  {os.path.basename(with_source)}")
        if ext in (".pdf", ".pptx", ".ppt"):
            total = compare_slides(material_pages(with_source), note_text)
        else:
            with open(with_source, encoding="utf-8", errors="replace") as f:
                total = compare_text(f.read(), note_text, "raw notes")
    else:
        if os.path.isfile(copy):
            with open(copy, encoding="utf-8") as f:
                source = f.read()
            origin = "copy saved before the edit"
        else:
            source = git_version(note)
            origin = "last git commit"
            if source is None:
                fail("there is neither a saved copy nor a git commit of this note: "
                     "before editing run the script with --save")
        before, after = len(source.split()), len(note_text.split())
        print(f"Comparison: {os.path.basename(note)}  <-  {origin}")
        print(f"Words: {before} -> {after} ({(after - before) / max(before, 1) * 100:+.0f}%)")
        total = compare_text(source, note_text, "text")

    if total == 0:
        print("\nNo loss detected.")
    else:
        print(f"\n{total} items to check. For each one: reread the source; if the information is "
              "missing from the note, put it back. If it is there in other words, that's fine.")


if __name__ == "__main__":
    main()