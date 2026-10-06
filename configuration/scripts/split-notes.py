#!/usr/bin/env python3
"""Splits a single notes file into one file per lesson. The text is never modified.

Usage:
  split-notes.py FILE                    shows the plan, writes nothing
  split-notes.py FILE --write            creates the files in FILE's folder
  split-notes.py FILE --write --dest FOLDER
  split-notes.py FILE --per-section      one file per section instead of per date

How it reasons: every top-level heading of the file is a section. The date of a
section is the one of its first image (the names "Screenshot From 2026-03-05 ..." and
"Pasted image 20260305..." contain it). Sections without images take the date of the
previous section. Consecutive sections with the same date form a lesson.

The starting file is not touched. No existing file is overwritten.
"""
import os
import re
import sys

RE_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
RE_DATA_IMG = re.compile(r"(?:Screenshot From (\d{4})-(\d{2})-(\d{2})|Pasted image (\d{4})(\d{2})(\d{2}))")
RE_WIKILINK = re.compile(r"\[\[([^\]\|#\n]*)")
FORBIDDEN = r'[\\/:*?"<>|#^\[\]]'


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def clean_title(t):
    t = re.sub(r"[*_`]", "", t).strip().rstrip(":").strip()
    return re.sub(r"\s+", " ", t)


def file_name(title):
    return re.sub(r"\s+", " ", re.sub(FORBIDDEN, " ", title)).strip()


def read_sections(lines):
    """Splits the file on the headings of the highest level present, ignoring code blocks."""
    in_fence = False
    headings = []
    for i, line in enumerate(lines):
        if re.match(r"^\s*(?:>\s*)*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = RE_HEADING.match(line)
        if m:
            headings.append((i, len(m.group(1)), m.group(2)))
    if not headings:
        fail("the file has no headings: I don't know where to split it")
    level = min(l for _i, l, _t in headings)
    starts = [(i, t) for i, l, t in headings if l == level]
    sections = []
    if "".join(lines[: starts[0][0]]).strip():
        sections.append({"title": "Preface", "start": 0, "end": starts[0][0], "body_from": 0})
    for n, (i, t) in enumerate(starts):
        end = starts[n + 1][0] if n + 1 < len(starts) else len(lines)
        sections.append({"title": clean_title(t), "start": i, "end": end, "body_from": i + 1})
    nested = {i: l for i, l, _t in headings if l > level}
    return sections, level, nested


def assign_dates(sections, lines):
    previous = None
    for s in sections:
        s["derived"] = False
        s["date"] = None
        for line in lines[s["start"]: s["end"]]:
            m = RE_DATA_IMG.search(line)
            if m:
                g = [x for x in m.groups() if x]
                s["date"] = "-".join(g)
                break
        if s["date"] is None and previous:
            s["date"], s["derived"] = previous, True
        previous = s["date"] or previous


def group(sections, per_section):
    lessons = []
    for s in sections:
        if (not per_section and lessons and s["date"] is not None
                and lessons[-1]["date"] == s["date"]):
            lessons[-1]["sections"].append(s)
        else:
            lessons.append({"date": s["date"], "sections": [s]})
    for lez in lessons:
        titles = [s["title"] for s in lez["sections"]]
        title = ", ".join(titles[:3]) + (" etc" if len(titles) > 3 else "")
        lez["title"] = title
        base = file_name(title)
        lez["file"] = (f"{lez['date']} {base}" if lez["date"] else base) + ".md"
        lez["lines"] = sum(s["end"] - s["start"] for s in lez["sections"])
        lez["derived"] = all(s["derived"] for s in lez["sections"])
    seen = {}
    for lez in lessons:
        key = lez["file"].lower()
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > 1:
            lez["file"] = lez["file"][:-3] + f" ({seen[key]}).md"
    return lessons


def compose(lez, lines, level, nested):
    """Text of the note: # title, then the sections. Nested headings shift accordingly."""
    single = len(lez["sections"]) == 1
    out = [f"# {lez['title']}\n", "\n"]
    for s in lez["sections"]:
        if not single:
            out.append(f"## {s['title']}\n")
        for i in range(s["body_from"], s["end"]):
            line = lines[i]
            if i in nested:
                m = RE_HEADING.match(line)
                new = min(nested[i] - level + (1 if single else 2), 6)
                line = f"{'#' * new} {m.group(2)}\n"
            out.append(line)
        if out and out[-1].strip():
            out.append("\n")
    text = "".join(out)
    return text if text.endswith("\n") else text + "\n"


def short_date(d):
    y, m, d_ = d.split("-")
    return f"{d_}/{m}/{y}"


def index_line(lez):
    name = lez["file"][:-3]
    date = short_date(lez["date"]) if lez["date"] else "date to insert"
    return f"- {date} - [[{name}|{lez['title']}]]\n"


def main():
    args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print(__doc__.strip())
        return
    write = "--write" in args
    per_section = "--per-section" in args
    dest = None
    if "--dest" in args:
        i = args.index("--dest")
        if i + 1 >= len(args):
            fail("missing folder after --dest")
        dest = args[i + 1]
        del args[i: i + 2]
    positional = [a for a in args if not a.startswith("--")]
    if len(positional) != 1:
        fail("indicate a single file to split")
    source = positional[0]
    if not os.path.isfile(source):
        fail(f"file not found: {source}")
    dest = dest or os.path.dirname(source) or "."

    with open(source, encoding="utf-8") as f:
        lines = f.readlines()
    sections, level, nested = read_sections(lines)
    assign_dates(sections, lines)
    lessons = group(sections, per_section)

    print(f"{os.path.basename(source)}: {len(lines)} lines, {len(sections)} sections -> {len(lessons)} files in {dest}/\n")
    for lez in lessons:
        note = ""
        if lez["date"] is None:
            note = "   <- NO DATE: add it to the file name"
        elif lez["derived"]:
            note = "   <- date taken from the previous section"
        print(f"{lez['lines']:>5} lines  {lez['file']}{note}")

    existing = [lez["file"] for lez in lessons if os.path.exists(os.path.join(dest, lez["file"]))]
    if not write:
        print("\nI wrote nothing. The dates come from the image names: they are approximate.")
        if existing:
            print(f"WARNING: {len(existing)} of these files already exist: with --write I would stop without creating anything.")
        print("To create the files: add --write. For one file per section: --per-section.")
        return

    if existing:
        fail("these files already exist, I overwrite nothing: " + "; ".join(existing))
    os.makedirs(dest, exist_ok=True)
    for lez in lessons:
        with open(os.path.join(dest, lez["file"]), "x", encoding="utf-8") as f:
            f.write(compose(lez, lines, level, nested))

    folder = os.path.basename(os.path.abspath(dest))
    indexes = sorted(f for f in os.listdir(dest) if f.startswith("00") and f.lower().endswith(".md"))
    if indexes:
        index = os.path.join(dest, indexes[0])
        with open(index, encoding="utf-8") as f:
            content = f.read()
        present = {os.path.basename(t.strip()).lower() for t in RE_WIKILINK.findall(content)}
        new = [index_line(l) for l in lessons if l["file"][:-3].lower() not in present]
        if new:
            with open(index, "a", encoding="utf-8") as f:
                f.write(("" if content.endswith("\n") else "\n") + "".join(new))
        print(f"\nIndex updated: {indexes[0]} (+{len(new)} lines)")
    else:
        index = os.path.join(dest, f"00 Index - {folder}.md")
        with open(index, "x", encoding="utf-8") as f:
            f.write(f"# Index - {folder}\n\n" + "".join(index_line(l) for l in lessons))
        print(f"\nIndex created: {os.path.basename(index)}")

    print(f"Created {len(lessons)} files. The starting file is intact: when you have checked, archive it or delete it yourself.")
    print("If a date is wrong, rename the file from Obsidian: the index links update by themselves.")


if __name__ == "__main__":
    main()