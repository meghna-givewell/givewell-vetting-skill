"""
extract.py — stdlib-only XLSX extractor for spreadsheet vetting.
Usage: python3 extract.py <path_to_file.xlsx>
Outputs: output/extracted_<filename>.txt
"""
import sys
import os
import re
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
    """Returns list of (name, rId) tuples."""
    try:
        with zf.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
    except KeyError:
        print("Warning: 'xl/workbook.xml' not found in ZIP — cannot read sheet names.")
        return []
    root = tree.getroot()
    sheets_el = root.find('ss:sheets', NS)
    result = []
    if sheets_el is not None:
        for s in sheets_el.findall('ss:sheet', NS):
            name = s.get('name', '')
            rid = s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', '')
            result.append((name, rid))
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

HYPERLINK_REL_TYPE = (
    'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink'
)


def load_hyperlink_rels(zf, sheet_target):
    """Return rId → URL for all hyperlinks declared in a sheet's _rels file."""
    parts = sheet_target.rsplit('/', 1)
    if len(parts) == 2:
        rels_path = f"xl/{parts[0]}/_rels/{parts[1]}.rels"
    else:
        rels_path = f"xl/_rels/{sheet_target}.rels"
    try:
        with zf.open(rels_path) as f:
            tree = ET.parse(f)
    except KeyError:
        return {}
    root = tree.getroot()
    rels = {}
    for rel in root.findall(
        '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship'
    ):
        if rel.get('Type') == HYPERLINK_REL_TYPE:
            rels[rel.get('Id', '')] = rel.get('Target', '')
    return rels


def extract_hyperlinks(zf, path, hl_rels):
    """Return cell ref → URL by matching <hyperlink> elements against hl_rels."""
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
    hyperlinks = {}
    hl_parent = root.find(
        '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}hyperlinks'
    )
    if hl_parent is not None:
        for hl in hl_parent:
            ref = hl.get('ref', '')
            rid = hl.get(
                '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id', ''
            )
            if ref and rid in hl_rels:
                hyperlinks[ref] = hl_rels[rid]
    return hyperlinks


def hyperlinks_to_text(hyperlinks, sheet_name):
    lines = [f"--- Hyperlinks: {sheet_name} ---"]
    for ref in sorted(hyperlinks.keys()):
        lines.append(f"  {ref} → {hyperlinks[ref]}")
    return '\n'.join(lines) + '\n'


_FORMULA_ERRORS = {'#REF!', '#VALUE!', '#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!'}
# Matches "x cash", "10x cash", "5.2x cash" etc. — any number (optional) followed by x cash.
_X_CASH_PAT = re.compile(r'\b\d+x\s+cash\b|\bx\s+cash\b', re.IGNORECASE)
_GD_PAT = re.compile(r'\bgivedirectly\b', re.IGNORECASE)
_PLACEHOLDER_PAT = re.compile(r'\b(TBD|TODO|Placeholder)\b', re.IGNORECASE)
_MAX_VAL_LEN = 100  # truncate long values in pre-findings display


def _truncate(s):
    return s if len(s) <= _MAX_VAL_LEN else s[:_MAX_VAL_LEN] + '…'


def find_formula_errors(all_cells):
    """Return (sheet, ref, value) for all error-type cells across all sheets."""
    results = []
    for sheet_name, cells in all_cells.items():
        for (row, col), cell in sorted(cells.items()):
            if cell.get('type') == 'e' or cell.get('value') in _FORMULA_ERRORS:
                results.append((sheet_name, cell['ref'], cell['value']))
    return results


def find_terminology(all_cells):
    """Return (sheet, ref, value, term) for x-cash and GiveDirectly instances."""
    results = []
    for sheet_name, cells in all_cells.items():
        for (row, col), cell in sorted(cells.items()):
            val = cell.get('value', '') or ''
            if _X_CASH_PAT.search(val):
                results.append((sheet_name, cell['ref'], val, 'x cash'))
            if _GD_PAT.search(val):
                results.append((sheet_name, cell['ref'], val, 'GiveDirectly'))
    return results


def find_placeholders(all_cells):
    """Return (sheet, ref, value) for cells containing TBD / TODO / Placeholder."""
    results = []
    for sheet_name, cells in all_cells.items():
        for (row, col), cell in sorted(cells.items()):
            val = cell.get('value', '') or ''
            if _PLACEHOLDER_PAT.search(val):
                results.append((sheet_name, cell['ref'], val))
    return results


def pre_findings_to_text(errors, terminology, placeholders):
    """Render pre-findings scan results as a text section."""
    lines = ['=== Pre-findings scan ===', '']

    lines.append('--- Formula errors (cell type e) ---')
    if errors:
        for sheet, ref, val in errors:
            lines.append(f'  {sheet}!{ref}: {val}')
    else:
        lines.append('  (none found)')
    lines.append('')

    lines.append('--- Terminology: x cash / GiveDirectly ---')
    lines.append('    x cash → should be x benchmark (always a finding)')
    lines.append('    GiveDirectly → candidates; verify not a source citation before filing')
    if terminology:
        for sheet, ref, val, term in terminology:
            tag = '' if term == 'x cash' else ' [verify: may be source citation]'
            lines.append(f'  {sheet}!{ref} [{term}]: {_truncate(val)!r}{tag}')
    else:
        lines.append('  (none found)')
    lines.append('')

    lines.append('--- Placeholders: TBD / TODO / Placeholder ---')
    if placeholders:
        for sheet, ref, val in placeholders:
            lines.append(f'  {sheet}!{ref}: {_truncate(val)!r}')
    else:
        lines.append('  (none found)')
    lines.append('')

    return '\n'.join(lines)


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
    shared_formulas = {}  # si index -> master formula text
    for row_el in root.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row'):
        for c in row_el.findall('ss:c', NS):
            ref = c.get('r', '')
            if not ref:
                continue
            row, col = parse_cell_ref(ref)
            t = c.get('t', '')  # cell type
            f_el = c.find('ss:f', NS)
            v_el = c.find('ss:v', NS)
            raw_val = v_el.text if v_el is not None and v_el.text else None

            # Shared formulas: XLSX stores formula text only in the master cell.
            # Dependent cells carry si=N but no text — look up the master.
            formula = None
            if f_el is not None:
                si = f_el.get('si')
                f_type = f_el.get('t', '')
                if f_el.text:
                    formula = f_el.text
                    if f_type == 'shared' and si is not None:
                        shared_formulas[si] = formula
                elif f_type == 'shared' and si is not None:
                    master = shared_formulas.get(si)
                    if master is not None:
                        formula = f'shared:{master}'

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

def cells_to_text(cells, sheet_name):
    """Render cells as a readable text table."""
    if not cells:
        return f"[Sheet '{sheet_name}' is empty]\n"
    rows = sorted(set(r for r, c in cells))
    cols = sorted(set(c for r, c in cells))
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

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        sys.exit(f"Error: '{path}' is not a valid ZIP/XLSX file.")

    os.makedirs('output', exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join('output', f'extracted_{base}.txt')

    all_cells = {}
    with zf:
        shared_strings = load_shared_strings(zf)
        sheet_names = load_sheet_names(zf)
        rels = load_sheet_rels(zf)

        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(f"Workbook: {os.path.basename(path)}\n")
            out.write(f"Sheets: {', '.join(n for n,_ in sheet_names)}\n")
            out.write("=" * 80 + "\n\n")

            all_hyperlinks = {}
            for name, rid in sheet_names:
                target = rels.get(rid, '')
                if not target:
                    out.write(f"[Could not find sheet target for '{name}']\n")
                    all_cells[name] = {}
                    all_hyperlinks[name] = {}
                    continue
                cells = extract_sheet(zf, target, shared_strings)
                all_cells[name] = cells
                out.write(cells_to_text(cells, name))
                hl_rels = load_hyperlink_rels(zf, target)
                hyperlinks = extract_hyperlinks(zf, target, hl_rels)
                all_hyperlinks[name] = hyperlinks
                if hyperlinks:
                    out.write(hyperlinks_to_text(hyperlinks, name))
                out.write("\n" + "=" * 80 + "\n\n")

    errors = find_formula_errors(all_cells)
    terminology = find_terminology(all_cells)
    placeholders = find_placeholders(all_cells)
    with open(out_path, 'a', encoding='utf-8') as out:
        out.write(pre_findings_to_text(errors, terminology, placeholders))

    print(f"Extracted to: {out_path}")
    # Print summary from already-built cells dict
    for name, rid in sheet_names:
        cells = all_cells.get(name, {})
        rows = sorted(set(r for r, c in cells)) if cells else []
        hl_count = len(all_hyperlinks.get(name, {}))
        hl_str = f", {hl_count} hyperlinks" if hl_count else ""
        print(f"  {name}: {len(rows)} rows, {len(cells)} cells{hl_str}")
    total = len(errors) + len(terminology) + len(placeholders)
    if total:
        print(f"  Pre-findings: {len(errors)} formula error(s), {len(terminology)} terminology hit(s), {len(placeholders)} placeholder(s)")

if __name__ == '__main__':
    main()
