import pymupdf

from app.ingestion.table_extractor import TableExtractor


def _ruled_table(page, x0, y0, rows, col_w=150, row_h=20):
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            rect = pymupdf.Rect(x0 + c * col_w, y0 + r * row_h, x0 + (c + 1) * col_w, y0 + (r + 1) * row_h)
            page.draw_rect(rect, width=0.7)
            page.insert_text((rect.x0 + 4, rect.y0 + 14), value, fontsize=9)


def test_table_running_onto_next_page_stays_one_table(tmp_path):
    rows = [["Milestone", "Due Date", "Amount"]] + [[f"M{i}", f"Day {i * 10}", str(i * 1000)] for i in range(1, 40)]
    doc = pymupdf.open()
    _ruled_table(doc.new_page(), 50, 60, rows[:36])
    _ruled_table(doc.new_page(), 50, 60, rows[36:])
    path = tmp_path / "split.pdf"
    doc.save(path)

    tables = TableExtractor().extract_tables(path)

    assert len(tables) == 1
    assert tables[0].headers == ["Milestone", "Due Date", "Amount"]
    assert len(tables[0].rows) == 39 and tables[0].rows[-1][0] == "M39"


def test_separate_tables_on_consecutive_pages_are_not_merged(tmp_path):
    doc = pymupdf.open()
    _ruled_table(doc.new_page(), 50, 100, [["Tier", "Fee"], ["Basic", "5,000"]])
    _ruled_table(doc.new_page(), 50, 100, [["Party", "Address"], ["Acme", "Pune"]])
    path = tmp_path / "two.pdf"
    doc.save(path)

    assert len(TableExtractor().extract_tables(path)) == 2


def test_heading_that_only_contains_for_is_not_a_signature_block():
    extractor = TableExtractor()
    assert extractor._classify_table(["Payment for services", "Amount"]) != "signature_block"
    assert extractor._classify_table(["For Lumenfield Ltd", "For Cobaltrix Inc"]) == "signature_block"
