#!/usr/bin/env python3
"""Extract per-slide text and speaker notes from a .pptx file, printed as markdown.

Pure standard library (zipfile + xml) — no dependencies to install.

Usage:
    python -I extract_pptx.py <courseware.pptx>

Output format:
    # Slide 1
    <all text on the slide, one paragraph per line>
    > Notes: <speaker notes, if any>
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

# DrawingML namespaces
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def slide_sort_key(name):
    """Sort by slide number (slide1, slide2, ... slide10)."""
    m = re.search(r"slide(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def extract_paragraphs(xml_bytes):
    """Pull paragraph text out of slide/notes XML.

    One <a:p> paragraph per entry; <a:t> runs inside are concatenated.
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []

    paragraphs = []
    for para in root.iter("{%s}p" % NS["a"]):
        runs = [node.text or "" for node in para.iter("{%s}t" % NS["a"])]
        text = "".join(runs).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2:
        print(__doc__.strip())
        sys.exit(1)

    path = sys.argv[1]
    if not path.lower().endswith(".pptx"):
        print("Error: only .pptx is supported. Re-save legacy .ppt as .pptx or PDF first.")
        sys.exit(1)

    try:
        zf = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        print(f"Error: cannot open file: {e}")
        sys.exit(1)

    names = zf.namelist()

    slides = sorted(
        (n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=slide_sort_key,
    )
    # notesSlideN.xml pairs with slideN.xml by number
    notes = {
        slide_sort_key(n): n
        for n in names
        if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", n)
    }

    if not slides:
        print("Error: no slides found in this file.")
        sys.exit(1)

    for slide_path in slides:
        idx = slide_sort_key(slide_path)
        print(f"\n# Slide {idx}\n")

        paragraphs = extract_paragraphs(zf.read(slide_path))
        if paragraphs:
            for p in paragraphs:
                print(p)
        else:
            print("(no extractable text — likely an image-only slide)")

        note_path = notes.get(idx)
        if note_path:
            note_paras = extract_paragraphs(zf.read(note_path))
            # notes XML also contains placeholder text like the slide number; drop pure digits
            note_paras = [p for p in note_paras if not p.isdigit()]
            if note_paras:
                print()
                for p in note_paras:
                    print(f"> Notes: {p}")

    print(f"\n\n---\nTotal: {len(slides)} slides.")


if __name__ == "__main__":
    main()
