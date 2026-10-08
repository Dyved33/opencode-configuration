#!/usr/bin/env python3
"""Structural check of the notes. Modifies nothing.

Usage:
  vault-audit.py                 the whole vault
  vault-audit.py PATH ...        only those files or folders
  vault-audit.py --short ...     only ERROR and WARN

ERROR  the note is broken (link, image, LaTeX, unclosed block)
WARN   it violates the conventions of .opencode/style.md
INFO   worth keeping an eye on (open todos, long paragraphs)
"""
import os
import re
import sys

ALLOWED_CALLOUTS = {"example", "info", "important", "warning", "tip", "todo"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
EXCLUDED_DIRS = {".git", ".obsidian", ".opencode", ".trash", "node_modules", "images", "esercizi"}
EXCLUDED_FILES = {"AGENTS.md", "Opencode_Guide.md", "chat_prompt.md", "README.md", "LEGGIMI.md"}
LONG_PARAGRAPH = 150  # words

AI_PHRASES = [
    "in questa lezione", "in questa nota", "in questa sezione", "in questa guida",
    "esploreremo", "approfondiremo", "andremo a vedere",
    "è importante notare", "è importante sottolineare", "è fondamentale notare",
    "è fondamentale sottolineare", "è essenziale notare", "è bene ricordare che",
    "vale la pena", "in conclusione", "in definitiva", "per riassumere", "ricapitolando",
    "nel panorama", "gioca un ruolo", "svolge un ruolo", "riveste un ruolo",
    "nota del prof",
]
FORBIDDEN_TITLES = {"conclusioni", "conclusione", "concetti chiave", "riepilogo", "riassunto", "introduzione"}

RE_DATE = re.compile(r"\b(\d{1,2}[/.\-_]\d{1,2}[/.\-_]\d{2,4}|\d{4}[/.\-_]\d{1,2}[/.\-_]\d{1,2})\b")
RE_WIKILINK = re.compile(r"(!?)\[\[([^\]\|#\n]*)(#[^\]\|\n]*)?(\|[^\]\n]*)?\]\]")
RE_IMG_HTML = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*[\"']([^\"']+)[\"']", re.I)
RE_CALLOUT = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+)?(?:>\s*)+\[!([^\]]*)\]")
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
RE_PLACEHOLDER = re.compile(r"(?<![:/\w])//[^/\n]{1,200}?//(?!/)")
RE_TAG = re.compile(r"(?:^|\s)#([A-Za-zÀ-ÿ][\w/\-]*)")
RE_URL = re.compile(r"https?://\S+")


def find_root():
    d = os.getcwd()
    while True:
        if os.path.exists(os.path.join(d, "opencode.json")) or os.path.isdir(os.path.join(d, ".obsidian")):
            return d
        up = os.path.dirname(d)
        if up == d:
            return os.getcwd()
        d = up


def scan(root):
    """All the vault files: lowercase basename -> list of paths."""
    by_name = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", ".obsidian", ".trash", "node_modules"}]
        for f in files:
            by_name.setdefault(f.lower(), []).append(os.path.join(base, f))
    return by_name


def notes_to_check(paths):
    out = []
    for p in paths:
        if os.path.isfile(p):
            if p.lower().endswith(".md"):
                out.append(p)
            continue
        if not os.path.isdir(p):
            print(f"ERROR {p}: path does not exist")
            continue
        for base, dirs, files in os.walk(p):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_DIRS)
            for f in sorted(files):
                if f.lower().endswith(".md") and f not in EXCLUDED_FILES:
                    out.append(os.path.join(base, f))
    return out


def is_index(path):
    return os.path.basename(path).startswith("00")


def mask(lines):
    """Returns the lines with code and formulas replaced by spaces, plus the closure problems."""
    problems = []
    text_only = []      # without code, with formulas
    no_formulas = []    # without code and without formulas
    in_fence = False
    fence_line = 0
    in_math_block = False
    math_line = 0
    for n, line in enumerate(lines, 1):
        clean = re.sub(r"^\s*(?:>\s*)+", "", line)
        if re.match(r"^\s*(```|~~~)", clean):
            if not in_fence:
                in_fence, fence_line = True, n
            else:
                in_fence = False
            text_only.append("")
            no_formulas.append("")
            continue
        if in_fence:
            text_only.append("")
            no_formulas.append("")
            continue
        t = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group()), line)
        text_only.append(t)

        t = t.replace("\\$", "  ")
        parts = t.split("$$")
        rebuilt = []
        for i, part in enumerate(parts):
            if i > 0:
                in_math_block = not in_math_block
                if in_math_block:
                    math_line = n
            rebuilt.append(" " * len(part) if in_math_block else part)
        t = "  ".join(rebuilt)
        if not in_math_block and t.count("$") % 2 == 1:
            problems.append(("ERROR", n, "unclosed formula $...$ on the line"))
        t = re.sub(r"\$[^$\n]*\$", lambda m: " " * len(m.group()), t)
        no_formulas.append(t)
    if in_fence:
        problems.append(("ERROR", fence_line, "unclosed code block ```"))
    if in_math_block:
        problems.append(("ERROR", math_line, "unclosed formula $$...$$"))
    return text_only, no_formulas, problems


def title_case(text):
    words = [p for p in re.split(r"[\s/]+", re.sub(r"[*_`$():,]", " ", text)) if p]
    if len(words) < 4:
        return False
    caps = [p for p in words[1:] if len(p) > 3 and p[0].isupper() and not p.isupper()]
    return len(caps) >= 3 and len(caps) >= len(words[1:]) / 2


def resolve_note(target, by_name, folder, root):
    target = target.strip()
    if not target:
        return True
    name = os.path.basename(target)
    if not os.path.splitext(name)[1]:
        name += ".md"
    candidates = by_name.get(name.lower(), [])
    if "/" in target:
        suff = (target if target.lower().endswith(".md") else target + ".md").lower()
        candidates = [c for c in candidates if c.lower().replace(os.sep, "/").endswith(suff)]
    return candidates[0] if candidates else None


def resolve_file(src, by_name, folder, root):
    src = src.strip()
    if re.match(r"^(https?:|data:|app:|file:)", src):
        return True
    src = re.sub(r"%20", " ", src)
    for base in (folder, root, os.path.join(folder, "images")):
        if os.path.isfile(os.path.join(base, src)):
            return True
    return bool(by_name.get(os.path.basename(src).lower()))


def headings(path, cache={}):
    if path not in cache:
        try:
            with open(path, encoding="utf-8") as f:
                cache[path] = {
                    re.sub(r"[*_`]", "", m.group(2)).strip().lower()
                    for m in (RE_HEADING.match(r) for r in f) if m
                }
        except OSError:
            cache[path] = set()
    return cache[path]


def check(path, by_name, root):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except (OSError, UnicodeDecodeError) as e:
        return [("ERROR", 0, f"unreadable file: {e}")], 0
    folder = os.path.dirname(path)
    index = is_index(path)
    text_only, no_formulas, problems = mask(lines)
    out += problems

    if lines and lines[0].strip() == "---":
        out.append(("WARN", 1, "frontmatter present (notes don't use it)"))

    # headings
    h1 = []
    for n, line in enumerate(text_only, 1):
        m = RE_HEADING.match(line)
        if not m:
            continue
        level, text = len(m.group(1)), m.group(2)
        if level == 1:
            h1.append((n, text))
        if level > 3:
            out.append(("WARN", n, f"heading level {level}: stop at ###"))
        bare = re.sub(r"[*_`]", "", text).strip()
        if "**" in text:
            out.append(("WARN", n, "bold heading"))
        if re.match(r"^([IVX]+\.|\d+[.)])\s", bare):
            out.append(("WARN", n, "numbered heading"))
        if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", bare):
            out.append(("WARN", n, "emoji in the heading"))
        if bare.rstrip(":").lower() in FORBIDDEN_TITLES:
            out.append(("WARN", n, f'section "{bare}" is AI-style'))
        if level > 1 and title_case(bare):
            out.append(("WARN", n, "Title Case heading"))
    if not h1:
        out.append(("WARN", 1, "missing # heading at the top"))
    elif len(h1) > 1:
        out.append(("WARN", h1[1][0], "more than one # heading: only one allowed"))
    if not index and not RE_DATE.search(os.path.basename(path)):
        out.append(("WARN", 0, "the file name doesn't contain the lesson date (YYYY-MM-DD Title.md)"))

    # line by line
    open_divs = 0
    for n, (line, nofx) in enumerate(zip(text_only, no_formulas), 1):
        m = RE_CALLOUT.match(line)
        if m:
            ctype = m.group(1).rstrip("+-").strip()
            if ctype.lower() not in ALLOWED_CALLOUTS:
                out.append(("WARN", n, f"callout [!{ctype}] not allowed (allowed: {', '.join(sorted(ALLOWED_CALLOUTS))})"))
            elif ctype != ctype.lower():
                out.append(("WARN", n, f"callout [!{ctype}] must be lowercase"))
            if ctype.lower() == "todo":
                text = line.split("]", 1)[1].strip() or "(no text)"
                out.append(("INFO", n, f"open todo: {text[:90]}"))
        elif re.search(r"\[![A-Za-z]+\]", nofx):
            out.append(("ERROR", n, "malformed callout: [!type] must come right after >"))

        for emb, target, anchor, _alias in RE_WIKILINK.findall(nofx):
            ext = os.path.splitext(target.strip())[1].lower()
            if emb and ext in IMAGE_EXTS:
                if not resolve_file(target, by_name, folder, root):
                    out.append(("ERROR", n, f"missing image: {target.strip()}"))
            elif ext and ext != ".md":
                if not resolve_file(target, by_name, folder, root):
                    out.append(("ERROR", n, f"missing linked file: {target.strip()}"))
            else:
                dest = resolve_note(target, by_name, folder, root)
                if dest is None:
                    out.append(("ERROR", n, f"broken link: [[{target.strip()}]]"))
                elif anchor and not anchor.startswith("#^"):
                    file_dest = path if dest is True else dest
                    if anchor[1:].strip().lower() not in headings(file_dest):
                        out.append(("WARN", n, f"nonexistent section in the link: [[{target.strip()}{anchor}]]"))

        for src in RE_IMG_HTML.findall(line):
            if not resolve_file(src, by_name, folder, root):
                out.append(("ERROR", n, f"missing image: {src}"))
        open_divs += len(re.findall(r"<div\b", line, re.I)) - len(re.findall(r"</div>", line, re.I))

        no_url = RE_URL.sub("", nofx)
        for m in RE_PLACEHOLDER.finditer(no_url):
            out.append(("WARN", n, f"unresolved placeholder: {m.group().strip()[:70]}"))

        no_link = re.sub(r"<[^>]+>", " ", RE_WIKILINK.sub(" ", no_url))
        if not RE_HEADING.match(line):
            m = RE_TAG.search(no_link)
            if m:
                out.append(("WARN", n, f"tag #{m.group(1)} (notes don't use tags)"))

        low = nofx.lower()
        for phrase in AI_PHRASES:
            if phrase in low:
                out.append(("WARN", n, f'AI-style phrase: "{phrase}"'))
        if "—" in nofx:
            out.append(("INFO", n, "em dash —"))
        m = re.match(r"^\s*\*\*([^*]+)\*\*:?\s*$", line)
        if m and title_case(m.group(1)):
            out.append(("WARN", n, "Title Case label"))

        word_count = len(nofx.split())
        if word_count > LONG_PARAGRAPH and not line.lstrip().startswith("|"):
            out.append(("INFO", n, f"paragraph of {word_count} words: split or trim it"))

    if open_divs != 0:
        out.append(("ERROR", len(lines), f"<div> and </div> unbalanced (difference {open_divs})"))

    total_words = sum(len(r.split()) for r in text_only)
    if not index and total_words > 50:
        # the note must end with the [!info] Sintesi callout
        last = None
        for n, line in enumerate(text_only, 1):
            if RE_CALLOUT.match(line):
                last = n
        closes = False
        if last:
            head = text_only[last - 1]
            ctype = RE_CALLOUT.match(head).group(1).strip().lower()
            title = re.sub(r"[*_]", "", head.split("]", 1)[1]).strip().lower()
            rest = [r for r in text_only[last:] if r.strip() and not r.lstrip().startswith(">")]
            closes = ctype == "info" and title.startswith("sintesi") and not rest
        if not closes:
            out.append(("WARN", 0, "the note doesn't end with the [!info] Sintesi: callout"))
    return out, total_words


def check_indexes(notes, root):
    out = []
    per_folder = {}
    for p in notes:
        per_folder.setdefault(os.path.dirname(p) or ".", []).append(os.path.join(os.path.dirname(p) or ".", os.path.basename(p)))
    for folder, files in sorted(per_folder.items()):
        all_md = [os.path.join(folder, f) for f in sorted(os.listdir(folder))
                  if f.lower().endswith(".md") and f not in EXCLUDED_FILES]
        indexes = [f for f in all_md if is_index(f)]
        lessons = [f for f in all_md if not is_index(f)]
        if not indexes:
            if len(lessons) >= 2:
                out.append((folder, "INFO", 0, f"{len(lessons)} notes and no index (file starting with 00)"))
            continue
        try:
            with open(indexes[0], encoding="utf-8") as f:
                linked = {os.path.basename(t.strip()).lower().removesuffix(".md")
                          for _e, t, _a, _al in RE_WIKILINK.findall(f.read())}
        except OSError:
            continue
        for lesson in lessons:
            name = os.path.basename(lesson)[:-3]
            if name.lower() not in linked:
                out.append((indexes[0], "WARN", 0, f"lesson not listed in the index: {name}"))
    return out


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        print(__doc__.strip())
        return
    short = "--short" in args
    paths = [a for a in args if not a.startswith("--")] or ["."]
    root = find_root()
    by_name = scan(root)
    notes = notes_to_check(paths)
    if not notes:
        print("No .md note to check in the given paths.")
        return

    counts = {"ERROR": 0, "WARN": 0, "INFO": 0}
    results = []
    for p in notes:
        problems, words = check(p, by_name, root)
        results.append((p, problems, words))
    extra = {}
    for file, severity, n, msg in check_indexes(notes, root):
        extra.setdefault(file, []).append((severity, n, msg))
    for file, items in extra.items():
        for i, (p, problems, words) in enumerate(results):
            if os.path.abspath(p) == os.path.abspath(file):
                results[i] = (p, problems + items, words)
                break
        else:
            results.append((file, items, 0))

    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    if short:
        results = [(p, [x for x in pr if x[0] != "INFO"], w) for p, pr, w in results]
    for p, problems, words in results:
        for g, _n, _m in problems:
            counts[g] += 1
        if not problems:
            continue
        rel = os.path.relpath(p)
        print(f"\n{rel}" + (f"  ({words} words)" if words else ""))
        for severity, n, msg in sorted(problems, key=lambda x: (order[x[0]], x[1])):
            where = f"line {n}" if n else "-"
            print(f"  {severity:<5} {where:<9} {msg}")

    checked = {os.path.abspath(n) for n in notes}
    clean = len(notes) - sum(1 for p, pr, _w in results if pr and os.path.abspath(p) in checked)
    print(f"\n{len(notes)} notes checked, {clean} without findings: "
          f"{counts['ERROR']} ERROR, {counts['WARN']} WARN, {counts['INFO']} INFO")


if __name__ == "__main__":
    main()