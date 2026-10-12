#!/usr/bin/env python3
"""Convert .ppt / .pptx to PDF using the locally installed Microsoft PowerPoint.

The resulting PDF can be read back page by page with the Read tool to see
layouts, charts and pictures — ideal for figure-heavy slides. Also handles
the legacy binary .ppt format.

Usage:
    python ppt_to_pdf.py <courseware.ppt|.pptx> <output.pdf>
"""

import os
import sys


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 3:
        print(__doc__.strip())
        sys.exit(1)

    src = os.path.abspath(sys.argv[1])
    dst = os.path.abspath(sys.argv[2])
    if not os.path.isfile(src):
        print(f"Error: file not found: {src}")
        sys.exit(1)

    try:
        import win32com.client
    except ImportError:
        print("Error: pywin32 required (pip install pywin32), plus a local PowerPoint install.")
        sys.exit(1)

    pp_save_as_pdf = 32  # ppSaveAsPDF
    app = None
    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
        deck = app.Presentations.Open(src, WithWindow=False)
        deck.SaveAs(dst, pp_save_as_pdf)
        deck.Close()
        print(f"Converted: {dst}")
    except Exception as e:
        print(f"Error: conversion failed: {e}")
        sys.exit(1)
    finally:
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass


if __name__ == "__main__":
    main()
