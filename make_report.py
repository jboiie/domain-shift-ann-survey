import sys
import build_report as B
from build_report import *
from report_sprints import ch3, ch4, ch5, ch6
from report_end import ch7, ch8, ch9, ch10, screenshots


def body(doc, figs, tabs):
    ch1(doc)
    ch2(doc)
    ch3(doc)
    ch4(doc, figs)
    ch5(doc, tabs)
    ch6(doc)
    ch7(doc)
    ch8(doc)
    ch9(doc)
    ch10(doc)
    screenshots(doc)


def main(out="Domain_Shift_Survey_Report.docx"):
    # Pass 1 collects every figure and table so the list chapters (4, 5) can precede the chapters that contain them
    tmp = new_document()
    body(tmp, [], [])
    figs, tabs = list(B.FIGS), list(B.TABS)
    B.FIGS.clear()
    B.TABS.clear()

    doc = new_document()
    front_matter(doc)
    sec = new_section(doc)
    page_number_footer(sec, 1)
    abstract(doc)
    body(doc, figs, tabs)
    doc.core_properties.title = TITLE_CASE
    doc.core_properties.author = ", ".join(n for n, _ in AUTHORS)
    doc.save(out)
    print("saved", out, len(figs), "figures", len(tabs), "tables")


if __name__ == "__main__":
    main(*sys.argv[1:])
