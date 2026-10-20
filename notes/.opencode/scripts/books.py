#!/usr/bin/env python3
"""Manages the textbooks in books/.

One book lives in books/<Course name>.pdf. Usage:
  books.py list                      books present and the matched course
  books.py info FILE                 title, pages, course of the book
  books.py toc FILE                  table of contents (PDF bookmarks)
  books.py page FILE 28              text of page 28 (or 19-21)
  books.py search FILE "text"        pages in which the text appears

The pages are read with the same engine as read-slides.py (pdftotext, with the
Docling fallback on the image pages). It writes nothing in the vault.

Environment:
  BOOKS_DIR    where the books are (default: books)
  COURSES_DIR  where the courses are (default: every first-level folder)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BOOKS = os.path.join(ROOT, os.environ.get("BOOKS_DIR", "books"))
COURSES_DIR = os.environ.get("COURSES_DIR", "")


def _load_read_slides():
    path = os.path.join(HERE, "read-slides.py")
    spec = importlib.util.spec_from_file_location("read_slides", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fail(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def is_index_file(name):
    return name.startswith("00") and name.lower().endswith(".md")


def find_courses(base, depth=3):
    """The course folders inside `base`.

    A folder is a course when it holds a course index: a file starting with 00
    whose name contains the name of the folder ("00 Index - Algebra.md" inside
    "Algebra"). A folder with a general index instead ("00 General Index.md")
    is a container: its subfolders are the courses.
    """
    found = []
    if depth <= 0 or not os.path.isdir(base):
        return found
    try:
        entries = os.listdir(base)
    except OSError:
        return found
    indexes = [f for f in entries if is_index_file(f)]
    subdirs = [d for d in entries
               if not d.startswith(".") and os.path.isdir(os.path.join(base, d))]
    if indexes:
        name = os.path.basename(base.rstrip(os.sep))
        if any(name.lower() in f.lower() for f in indexes):
            return [name]
        # a general index: the courses are the subfolders
        for d in subdirs:
            found.extend(find_courses(os.path.join(base, d), depth - 1))
        return found
    for d in subdirs:
        found.extend(find_courses(os.path.join(base, d), depth - 1))
    return found


def courses():
    """The course folders of the vault."""
    base = os.path.join(ROOT, COURSES_DIR) if COURSES_DIR else ROOT
    if not os.path.isdir(base):
        return []
    found = sorted(set(find_courses(base)))
    if found:
        return found
    # no index anywhere: fall back to the first-level folders
    return sorted(
        name for name in os.listdir(base)
        if not name.startswith(".") and name != os.path.basename(BOOKS)
        and os.path.isdir(os.path.join(base, name))
    )


def norm(s):
    return " ".join(s.split()).lower()


def books_present():
    if not os.path.isdir(BOOKS):
        return []
    return sorted(f for f in os.listdir(BOOKS) if f.lower().endswith(".pdf"))


def course_of(book_name):
    stem = norm(os.path.splitext(book_name)[0])
    for course in courses():
        if norm(course) == stem:
            return course
    return None


def resolve(arg):
    if os.sep in arg or os.path.isfile(arg):
        if os.path.isfile(arg):
            return arg
        fail(f"file not found: {arg}")
    candidate = os.path.join(BOOKS, arg)
    if os.path.isfile(candidate):
        return candidate
    if not candidate.lower().endswith(".pdf") and os.path.isfile(candidate + ".pdf"):
        return candidate + ".pdf"
    fail(f"book not found: {arg} (look in {os.path.relpath(BOOKS, ROOT)}/)")


def cmd_list():
    books = books_present()
    if not books:
        print(f"no books in {os.path.relpath(BOOKS, ROOT)}/")
        return
    print(f"Books in {os.path.relpath(BOOKS, ROOT)}/:")
    for name in books:
        course = course_of(name)
        state = f"course: {course}" if course else "NO MATCHING COURSE"
        print(f"  {name}  ->  {state}")
    orphans = [
        c for c in courses()
        if norm(c) not in {norm(os.path.splitext(n)[0]) for n in books}
    ]
    if orphans:
        print("Courses without a book:")
        for c in orphans:
            print(f"  {c}")


def cmd_info(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    name = os.path.basename(path)
    course = course_of(name) or "none"
    title = (r.metadata.title if r.metadata else None) or "(untitled)"
    print(f"File:      {name}")
    print(f"Title:     {title}")
    print(f"Pages:     {len(r.pages)}")
    print(f"Course:    {course}")
    print(f"Bookmarks: {_count_bookmarks(r.outline) if r.outline else 0}")


def _count_bookmarks(items):
    n = 0
    for it in items:
        if isinstance(it, list):
            n += _count_bookmarks(it)
        else:
            n += 1
    return n


def cmd_toc(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    if not r.outline:
        print("This PDF has no table of contents (bookmarks). Use 'page FILE N' or 'search FILE \"text\"'.")
        return
    print(f"Table of contents of {os.path.basename(path)}:")

    def walk(items, level):
        for it in items:
            if isinstance(it, list):
                walk(it, level + 1)
                continue
            title = (getattr(it, "title", "") or "").strip().replace("\n", " ")
            try:
                page = r.get_destination_page_number(it) + 1
            except Exception:
                page = "?"
            print(f"{'  ' * level}{title}  (p. {page})")

    walk(r.outline, 0)


def cmd_page(path, arg):
    import re
    slides = _load_read_slides()
    pages = slides.load(path)
    total = len(pages)
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", arg)
    if not m:
        fail(f"invalid page: {arg} (use 28 or 19-21)")
    a = int(m.group(1))
    b = int(m.group(2) or a)
    if a < 1 or b > total or a > b:
        fail(f"range outside the book: the book has {total} pages")
    slides.print_pages(pages, a, b)
    empty = sum(1 for p in pages if not p.strip())
    if empty > total / 2:
        print(f"WARNING: {empty} pages out of {total} have no text. The file is made of images: they have to be read by hand.")


def cmd_search(path, needle):
    slides = _load_read_slides()
    pages = slides.load(path)
    target = slides.normalize(needle)
    found = 0
    for i, page in enumerate(pages, 1):
        for line in page.splitlines():
            if target in slides.normalize(line):
                print(f"p. {i}: {' '.join(line.split())[:140]}")
                found += 1
                if found >= 40:
                    print("... (more results omitted: narrow the search)")
                    return
    if not found:
        print(f'"{needle}" does not appear on any page')


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return
    command = args[0]
    if command == "list":
        cmd_list()
    elif command == "info":
        if len(args) < 2:
            fail("missing the book: info FILE")
        cmd_info(resolve(args[1]))
    elif command == "toc":
        if len(args) < 2:
            fail("missing the book: toc FILE")
        cmd_toc(resolve(args[1]))
    elif command == "page":
        if len(args) < 3:
            fail("missing a page: page FILE 28")
        cmd_page(resolve(args[1]), args[2])
    elif command == "search":
        if len(args) < 3:
            fail('missing the text to search: search FILE "text"')
        cmd_search(resolve(args[1]), " ".join(args[2:]))
    else:
        fail(f"unknown command: {command} (list, info, toc, page, search)")


if __name__ == "__main__":
    main()
