#!/usr/bin/env python3
"""Export a review-notes markdown file to Word (.docx) or PDF.

Pipeline: markdown -> styled HTML (CJK-friendly typography) -> local Word
saves it as docx / pdf. Images are referenced by absolute file:// URLs in the
HTML, then unlinked inside Word so they get embedded into the document.

Usage:
    python export_doc.py <notes.md> <output.docx | output.pdf>

If Word is unavailable or conversion fails, a styled <name>.html is left next
to the output path — open it in a browser and Ctrl+P to save as PDF.
"""

import html as html_mod
import os
import re
import sys
from pathlib import Path

CSS = """
body { font-family: "Microsoft YaHei", "SimSun", sans-serif; font-size: 11pt;
       line-height: 1.7; max-width: 780px; margin: 40px auto; color: #222; }
h1 { font-size: 20pt; border-bottom: 2px solid #446; padding-bottom: 6px; }
h2 { font-size: 15pt; color: #234; margin-top: 28px; }
h3 { font-size: 12.5pt; color: #345; }
code { font-family: Consolas, monospace; background: #f2f2f2; padding: 1px 4px; }
pre { background: #f6f6f6; padding: 10px; border-left: 3px solid #446; }
pre code { background: none; padding: 0; }
blockquote { border-left: 3px solid #bbb; margin-left: 0; padding-left: 12px; color: #555; }
img { max-width: 100%; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #999; padding: 6px 10px; text-align: left; }
th { background: #eef0f4; }
hr { border: none; border-top: 1px solid #ccc; margin: 24px 0; }
"""


def inline(text):
    """Inline formatting: images, bold, italic, inline code."""
    text = html_mod.escape(text, quote=False)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}">', text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<em>\1</em>", text)
    return text


def md_to_html(md, img_dir):
    """Lightweight markdown parser for this skill's note format (not full CommonMark)."""
    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html_mod.escape("\n".join(buf)) + "</code></pre>")
            continue

        # pipe table
        if line.strip().startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in header) + "</tr>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue

        # heading / hr / quote / lists / paragraph
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
        elif re.match(r"^\s*---+\s*$", line):
            out.append("<hr>")
        elif line.strip().startswith(">"):
            out.append(f"<blockquote>{inline(line.strip()[1:].strip())}</blockquote>")
        elif re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i])); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        elif re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s+", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
        i += 1

    body = "\n".join(out)
    # relative image paths -> absolute file:// URLs so Word can find and embed them
    body = re.sub(
        r'<img src="(?!https?://|file://)([^"]+)"',
        lambda m: f'<img src="file:///{(img_dir / m.group(1)).as_posix()}"',
        body,
    )
    return (f'<html><head><meta charset="utf-8">'
            f"<style>{CSS}</style></head><body>{body}</body></html>")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 3:
        print(__doc__.strip())
        sys.exit(1)

    md_path = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2]).resolve()
    want_pdf = out_path.suffix.lower() == ".pdf"
    if out_path.suffix.lower() not in (".docx", ".pdf"):
        print("Error: output file must be .docx or .pdf")
        sys.exit(1)

    md = md_path.read_text(encoding="utf-8")
    html_text = md_to_html(md, md_path.parent)
    html_path = out_path.with_suffix(".html")
    html_path.write_text(html_text, encoding="utf-8")

    last_err = None
    for attempt in range(2):  # retry once: a previous Word instance may still be shutting down
        try:
            import win32com.client
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            word.DisplayAlerts = 0
            try:
                doc = word.Documents.Open(str(html_path))
                # Word opens HTML with images LINKED, not embedded — saving to docx
                # would lose them. Break every link so pictures are packaged inside.
                for collection in (doc.InlineShapes, doc.Shapes):
                    for i in range(1, collection.Count + 1):
                        try:
                            lf = collection(i).LinkFormat
                            if lf is not None:
                                lf.SavePictureWithDocument = True
                                lf.BreakLink()
                        except Exception:
                            pass
                if want_pdf:
                    doc.SaveAs2(str(out_path), FileFormat=17)  # wdFormatPDF
                else:
                    doc.SaveAs2(str(out_path), FileFormat=16)  # wdFormatDocumentDefault (.docx)
                doc.Close(False)
            finally:
                word.Quit()
            html_path.unlink(missing_ok=True)
            print(f"Exported: {out_path}")
            return
        except Exception as e:
            last_err = e
            if attempt == 0:
                import time
                time.sleep(3)

    print(f"Word conversion failed ({last_err}); kept the styled HTML: {html_path}")
    print("Open it in a browser and Ctrl+P to save as PDF.")
    sys.exit(1)


if __name__ == "__main__":
    main()
