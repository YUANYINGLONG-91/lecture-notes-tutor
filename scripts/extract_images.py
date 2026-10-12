#!/usr/bin/env python3
"""Extract images from a .pptx, mapped to their slides — for illustrated explanations.

Pure standard library. Reads each slide's relationship file so images are
attributed to the correct page, writes them to the output directory named
like slide03_img1.png, and prints the mapping for referencing in notes.

Usage:
    python -I extract_images.py <courseware.pptx> <output_dir>

The output directory receives:
    slide01_img1.png  -> first image on slide 1
    slide03_img2.jpg  -> ...
stdout lists slide -> file mappings for citation in the explanation document.
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"


def slide_num(name):
    m = re.search(r"slide(\d+)\.xml$", name)
    return int(m.group(1)) if m else 0


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 3:
        print(__doc__.strip())
        sys.exit(1)

    pptx_path, out_dir = sys.argv[1], Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        zf = zipfile.ZipFile(pptx_path)
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        print(f"Error: cannot open file: {e}")
        sys.exit(1)

    names = set(zf.namelist())
    slides = sorted(
        (n for n in names if re.match(r"ppt/slides/slide\d+\.xml$", n)),
        key=slide_num,
    )

    total = 0
    for slide_path in slides:
        idx = slide_num(slide_path)
        rels_path = f"ppt/slides/_rels/slide{idx}.xml.rels"
        if rels_path not in names:
            continue

        # rId -> media filename mapping
        rels_root = ET.fromstring(zf.read(rels_path))
        rid_to_media = {}
        for rel in rels_root.iter(f"{{{NS_REL}}}Relationship"):
            target = rel.get("Target", "")
            if "/media/" in target:
                rid_to_media[rel.get("Id")] = target.split("/media/")[-1]

        # rIds in order of appearance on the slide
        slide_root = ET.fromstring(zf.read(slide_path))
        ordered_rids = [
            blip.get(f"{{{NS_R}}}embed")
            for blip in slide_root.iter(f"{{{NS_A}}}blip")
        ]

        count = 0
        for rid in ordered_rids:
            media = rid_to_media.get(rid)
            if not media:
                continue
            src = f"ppt/media/{media}"
            if src not in names:
                continue
            count += 1
            ext = Path(media).suffix or ".png"
            dest = out_dir / f"slide{idx:02d}_img{count}{ext}"
            with zf.open(src) as fsrc, open(dest, "wb") as fdst:
                shutil.copyfileobj(fsrc, fdst)
            print(f"Slide {idx:>3} -> {dest.name}")
            total += 1

    print(f"\nExtracted {total} image(s) to {out_dir}")
    if total == 0:
        print("(no embedded images found — slides may use vector shapes or chart objects)")


if __name__ == "__main__":
    main()
