"""Exporta informe Markdown a Word y PDF, conservando la fuente y cifras.

Requiere python-docx y pypdf; los archivos de datos permanecen sin cambios.
"""
import re
import sys
import textwrap
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
import matplotlib
matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from pypdf import PdfReader

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
SOURCE = BASE / "informe_A_G.md"
DEST = ROOT / "outputs" / "informe"
MEMO = ROOT / "outputs" / "G4" / "memorando_ejecutivo_G4.md"
DECLARACION = BASE / "declaracion_uso_ia.md"


def clean(text):
    return text.replace("**", "").replace("`", "")


def blocks(path):
    result = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text or text == "---":
            continue
        match = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", text)
        if match:
            image = (path.parent / match.group(2)).resolve()
            if not image.is_file():
                raise FileNotFoundError(image)
            result.append(("image", (image, match.group(1))))
        elif text.startswith("# "):
            result.append(("title", clean(text[2:])))
        elif text.startswith("## "):
            result.append(("heading", clean(text[3:])))
        else:
            result.append(("text", clean(text)))
    return result


def docx_export(main, memo, declaracion):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = section.bottom_margin = Inches(.6)
    section.left_margin = section.right_margin = Inches(.7)
    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(10)
    style.paragraph_format.space_after = Pt(4)
    for kind, content in main + [("page", "")] + memo + [("page", "")] + declaracion:
        if kind == "page":
            doc.add_page_break()
        elif kind == "image":
            image, caption = content
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.add_run().add_picture(str(image), width=Inches(5.6))
            paragraph = doc.add_paragraph(caption)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif kind in ("title", "heading"):
            doc.add_heading(content, 0 if kind == "title" else 2)
        else:
            doc.add_paragraph(content)
    doc.save(DEST / "informe_A_G.docx")


def pdf_export(main, memo, declaracion):
    with PdfPages(DEST / "informe_A_G.pdf") as pdf:
        fig = None
        ypos = 0
        pages = 0

        def new_page():
            nonlocal fig, ypos, pages
            if fig is not None:
                pdf.savefig(fig)
                plt.close(fig)
            fig = plt.figure(figsize=(8.5, 11), facecolor="white")
            pages += 1
            ypos = .95
            fig.text(.5, .027, str(pages), ha="center", fontsize=8, color="#444444")

        def add_lines(lines, size=9, bold=False):
            nonlocal ypos
            for line in lines:
                if ypos < .065:
                    new_page()
                fig.text(.075, ypos, line, fontsize=size, va="top", fontweight="bold" if bold else "normal", family="DejaVu Sans")
                ypos -= .0146 if size <= 9 else .020

        def render(group):
            nonlocal ypos
            for kind, content in group:
                if kind == "image":
                    path, caption = content
                    if ypos < .30:
                        new_page()
                    axis = fig.add_axes([.13, ypos - .225, .74, .215])
                    axis.imshow(mpimg.imread(path))
                    axis.axis("off")
                    ypos -= .235
                    add_lines([caption], 8)
                    ypos -= .008
                else:
                    width = 85 if kind == "title" else 103
                    lines = textwrap.wrap(content, width=width, break_long_words=False, break_on_hyphens=False) or [""]
                    if kind in ("title", "heading") and ypos < .15:
                        new_page()
                    add_lines(lines, 13 if kind == "title" else 11 if kind == "heading" else 9, kind in ("title", "heading"))
                    ypos -= .008

        new_page()
        render(main)
        main_pages = pages
        new_page()
        render(memo)
        memo_pages = pages - main_pages
        new_page()
        render(declaracion)
        pdf.savefig(fig)
        plt.close(fig)
    total = len(PdfReader(DEST / "informe_A_G.pdf").pages)
    if main_pages > 14:
        raise ValueError(f"El cuerpo supera 14 páginas: {main_pages}")
    if memo_pages != 1:
        raise ValueError(f"El memorando ocupa {memo_pages} páginas, se requiere una")
    print(f"PDF: {main_pages} páginas de cuerpo, {memo_pages} página de memorando y {total - main_pages - memo_pages} de declaración")


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    source = blocks(SOURCE)
    memo = blocks(MEMO)
    declaracion = blocks(DECLARACION)
    docx_export(source, memo, declaracion)
    pdf_export(source, memo, declaracion)
    reopened = Document(DEST / "informe_A_G.docx")
    print(f"DOCX: {len(reopened.paragraphs)} párrafos, {len(reopened.inline_shapes)} imágenes")


if __name__ == "__main__":
    main()
