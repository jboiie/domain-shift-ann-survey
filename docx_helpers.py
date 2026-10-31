import re
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

FONT = "Times New Roman"
J, C, L = WD_ALIGN_PARAGRAPH.JUSTIFY, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT


def _font(style_or_run, size=None, bold=None, italic=None, name=FONT):
    f = style_or_run.font
    f.name = name
    f.color.rgb = RGBColor(0, 0, 0)
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    rpr = style_or_run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]


def new_document():
    doc = Document()
    s = doc.sections[0]
    s.page_width, s.page_height = Inches(8.27), Inches(11.69)  # A4
    s.left_margin = s.right_margin = Inches(1)
    s.top_margin = s.bottom_margin = Inches(1)
    n = doc.styles["Normal"]
    _font(n, 12)
    pf = n.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)
    n.paragraph_format.alignment = J
    h1 = doc.styles["Heading 1"]
    _font(h1, 16, True, False)
    h1.paragraph_format.alignment = C
    h1.paragraph_format.page_break_before = True
    h1.paragraph_format.space_before = Pt(0)
    h1.paragraph_format.space_after = Pt(18)
    h1.paragraph_format.line_spacing = 1.15
    h1.paragraph_format.keep_with_next = True
    h2 = doc.styles["Heading 2"]
    _font(h2, 14, True, False)
    h2.paragraph_format.alignment = L
    h2.paragraph_format.space_before = Pt(12)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.line_spacing = 1.15
    h2.paragraph_format.keep_with_next = True
    h3 = doc.styles["Heading 3"]
    _font(h3, 12, True, False)
    h3.paragraph_format.alignment = L
    h3.paragraph_format.space_before = Pt(8)
    h3.paragraph_format.space_after = Pt(4)
    h3.paragraph_format.line_spacing = 1.15
    h3.paragraph_format.keep_with_next = True
    return doc


def _runs(p, text, size=None, italic=None, bold=None):
    # **bold** and *italic* inline markup
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**"):
            part, b = part[2:-2], True
        elif part.startswith("*"):
            part, i = part[1:-1], True
        r = p.add_run(part)
        _font(r, size, b, i)


def para(doc, text, align=J, size=None, italic=None, bold=None, spacing=None, after=None, keep_next=False):
    p = doc.add_paragraph()
    p.alignment = align
    if spacing:
        p.paragraph_format.line_spacing = spacing
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.keep_with_next = keep_next
    _runs(p, text, size, italic, bold)
    return p


def chapter(doc, label, title):
    p = doc.add_paragraph(style="Heading 1")
    r = p.add_run(label)
    _font(r, 16, True)
    if title:
        r.add_break()
        r2 = p.add_run(title)
        _font(r2, 16, True)
    return p


def h2(doc, text):
    p = doc.add_paragraph(style="Heading 2")
    _font(p.add_run(text), 14, True)
    return p


def h3(doc, text):
    p = doc.add_paragraph(style="Heading 3")
    _font(p.add_run(text), 12, True)
    return p


def bullets(doc, items, size=None):
    for t in items:
        p = doc.add_paragraph()
        p.alignment = J
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(3)
        _runs(p, "•\t" + t, size)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))


def numbered(doc, items, size=None):
    for k, t in enumerate(items, 1):
        p = doc.add_paragraph()
        p.alignment = J
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.3)
        p.paragraph_format.space_after = Pt(3)
        _runs(p, f"{k}.\t" + t, size)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))


def figure(doc, path, caption, width=6.0):
    p = doc.add_paragraph()
    p.alignment = C
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Inches(width))
    c = doc.add_paragraph()
    c.alignment = C
    c.paragraph_format.space_after = Pt(12)
    _runs(c, caption, 11, bold=True)


def _shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), color)
    tcPr.append(sh)


def table(doc, caption, header, rows, widths, size=10, bold_first_col=False):
    cp = doc.add_paragraph()
    cp.alignment = C
    cp.paragraph_format.keep_with_next = True
    cp.paragraph_format.space_after = Pt(4)
    _runs(cp, caption, 11, bold=True)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        _fill(c, h, size, True)
        _shade(c, "D9D9D9")
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    th.set(qn("w:val"), "true")
    trPr.append(th)
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            _fill(cells[i], str(v), size, bold_first_col and i == 0)
    for row in t.rows:
        cs = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(cs)
        for i, w in enumerate(widths):
            row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t


def _fill(cell, text, size, bold):
    p = cell.paragraphs[0]
    p.alignment = L
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    _runs(p, text, size, bold=bold)


def code(doc, text, size=8.5):
    for line in text.strip("\n").split("\n"):
        p = doc.add_paragraph()
        p.alignment = L
        pf = p.paragraph_format
        pf.line_spacing = 1.0
        pf.space_after = Pt(0)
        pf.left_indent = Inches(0.2)
        r = p.add_run(line if line else " ")
        _font(r, size, name="Courier New")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def _field(run, instr):
    for kind, txt in (("begin", None), (None, instr), ("separate", None), ("text", "1"), ("end", None)):
        if kind in ("begin", "separate", "end"):
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), kind)
        elif kind is None:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        else:
            e = OxmlElement("w:t")
            e.text = txt
        run._r.append(e)


def toc(doc):
    p = doc.add_paragraph()
    p.alignment = L
    _field(p.add_run(), 'TOC \\o "1-2" \\h \\z \\u')
    return p


def page_number_footer(section, start=1):
    section.footer.is_linked_to_previous = False
    p = section.footer.paragraphs[0]
    p.alignment = C
    r = p.add_run()
    _font(r, 12)
    _field(r, "PAGE")
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:start"), str(start))
    section._sectPr.append(pg)


def new_section(doc):
    return doc.add_section(WD_SECTION.NEW_PAGE)
