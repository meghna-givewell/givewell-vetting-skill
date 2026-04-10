"""
extract.py — stdlib-only XLSX extractor for spreadsheet vetting.
Usage: python3 extract.py <path_to_file.xlsx>
Outputs: output/extracted_<filename>.txt
"""
import sys
import os
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

NS = {
    'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r':  'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'rel':'http://schemas.openxmlformats.org/package/2006/relationships',
}

def col_letter(n):
    """Convert 1-based column index to letter(s)."""
    result = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        result = chr(65 + r) + result
    return result

def parse_cell_ref(ref):
    """Parse 'A1' -> (row=1, col=1). Returns (row, col) 1-based."""
    col_str = ''
    row_str = ''
    for ch in ref:
        if ch.isalpha():
            col_str += ch
        else:
            row_str += ch
    col = 0
    for ch in col_str:
        col = col * 26 + (ord(ch) - 64)
    return int(row_str), col

def load_shared_strings(zf):
    try:
        with zf.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
    except KeyError:
        return []
    root = tree.getroot()
    strings = []
    for si in root.findall('ss:si', NS):
        # Collect all text nodes
        parts = []
        for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
            if t.text:
                parts.append(t.text)
        strings.append(''.join(parts))
    return strings

def load_sheet_names(zf):
    """Returns list of (name, sheet_id, rId) tuples."""
    with zf.open('xl/workbook.xml') as f:
        tree = ET.parse(f)
    root = tree.getroot()
    sheets_el = root.find('ss:sheets', NS)
    result = []
    if sheets_el is not None:
        for s in sheets_el.findall('ss:sheet', NS):
            name = s.get('name', '')
            sid = s.get('sheetId', '')
            rid = s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', '')
            result.append((name, sid, rid))
    return result

def load_sheet_rels(zf):
    """Map rId -> target path for sheets."""
    try:
        with zf.open('xl/_rels/workbook.xml.rels') as f:
            tree = ET.parse(f)
    except KeyError:
        return {}
    root = tree.getroot()
    rels = {}
    for rel in root.findall('{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'):
        rels[rel.get('Id')] = rel.get('Target')
    return rels

def extract_sheet(zf, path, shared_strings):
    """Extract cells from a sheet. Returns dict: (row, col) -> {value, formula, type}."""
    try:
        with zf.open('xl/' + path.lstrip('/')) as f:
            tree = ET.parse(f)
    except KeyError:
        try:
            with zf.open(path) as f:
                tree = ET.parse(f)
        except KeyError:
            return {}
    root = tree.getroot()
    cells = {}
    for row_el in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        for c in row_el.findall('ss:c', NS):
            ref = c.get('r', '')
            if not ref:
                continue
            row, col = parse_cell_ref(ref)
            t = c.get('t', '')  # cell type
            f_el = c.find('ss:f', NS)
            v_el = c.find('ss:v', NS)
            formula = f_el.text if f_el is not None and f_el.text else None
            raw_val = v_el.text if v_el is not None and v_el.text else None

            if t == 's' and raw_val is not None:
                try:
                    display = shared_strings[int(raw_val)]
                except (IndexError, ValueError):
                    display = raw_val
            elif t == 'b':
                display = 'TRUE' if raw_val == '1' else 'FALSE'
            elif t == 'str' and formula:
                # Calculated string — value is in v
                display = raw_val or ''
            else:
                display = raw_val or ''

            cells[(row, col)] = {
                'value': display,
                'formula': formula,
                'type': t,
                'ref': ref,
            }
    return cells

def cells_to_text(cells, sheet_name, max_col=None):
    """Render cells as a readable text table."""
    if not cells:
        return f"[Sheet '{sheet_name}' is empty]\n"
    rows = sorted(set(r for r, c in cells))
    cols = sorted(set(c for r, c in cells))
    if max_col:
        cols = [c for c in cols if c <= max_col]
    lines = [f"=== Sheet: {sheet_name} ==="]
    lines.append(f"Rows: {min(rows)}–{max(rows)}, Cols: {col_letter(min(cols))}–{col_letter(max(cols))}")
    lines.append("")
    for row in rows:
        row_cells = []
        for col in cols:
            cell = cells.get((row, col))
            if cell:
                ref = cell['ref']
                val = cell['value']
                frm = cell['formula']
                if frm:
                    row_cells.append(f"{ref}=[{frm}]({val})")
                else:
                    row_cells.append(f"{ref}={val!r}" if val else f"{ref}=''")
            # skip empty cells
        if row_cells:
            lines.append(f"  Row {row:4d}: " + "  |  ".join(row_cells))
    return "\n".join(lines) + "\n"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 extract.py <path_to_file.xlsx>")
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)

    os.makedirs('output', exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join('output', f'extracted_{base}.txt')

    with zipfile.ZipFile(path) as zf:
        shared_strings = load_shared_strings(zf)
        sheet_names = load_sheet_names(zf)
        rels = load_sheet_rels(zf)

        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(f"Workbook: {os.path.basename(path)}\n")
            out.write(f"Sheets: {', '.join(n for n,_,_ in sheet_names)}\n")
            out.write("=" * 80 + "\n\n")

            for name, sid, rid in sheet_names:
                target = rels.get(rid, '')
                if not target:
                    out.write(f"[Could not find sheet target for '{name}']\n")
                    continue
                cells = extract_sheet(zf, target, shared_strings)
                out.write(cells_to_text(cells, name))
                out.write("\n" + "=" * 80 + "\n\n")

    print(f"Extracted to: {out_path}")
    # Print summary
    with zipfile.ZipFile(path) as zf:
        sheet_names = load_sheet_names(zf)
        rels = load_sheet_rels(zf)
        for name, sid, rid in sheet_names:
            target = rels.get(rid, '')
            cells = extract_sheet(zf, target, shared_strings) if target else {}
            rows = sorted(set(r for r, c in cells)) if cells else []
            print(f"  {name}: {len(rows)} rows, {len(cells)} cells")

if __name__ == '__main__':
    main()
