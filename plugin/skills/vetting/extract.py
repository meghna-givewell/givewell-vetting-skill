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
    """Parse 'A1' or '$A$1' -> (row=1, col=1). Returns (row, col) 1-based."""
    ref = ref.replace('$', '')  # strip absolute-reference markers (COORD-1)
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
    """Returns list of (name, rId, state) tuples. state is 'visible', 'hidden', or 'veryHidden'."""
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
            state = s.get('state', 'visible')  # TABS-1: capture hidden/veryHidden state
            result.append((name, rid, state))
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
    parts = sheet_target.lstrip('/').rsplit('/', 1)  # HYPER-2: strip leading slash before split
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
            if ref:
                if rid and rid in hl_rels:
                    hyperlinks[ref] = hl_rels[rid]
                else:
                    # HYPER-1: internal anchor hyperlinks (e.g., #Sheet1!A1) use 'location' not rId
                    loc = hl.get('location', '')
                    if loc:
                        hyperlinks[ref] = '#' + loc
    return hyperlinks


def hyperlinks_to_text(hyperlinks, sheet_name):
    lines = [f"--- Hyperlinks: {sheet_name} ---"]
    # HYPER-3: sort by (row, col) position rather than alphabetically by ref string.
    # Alphabetical sort produces A10 < A2 which is wrong.
    for ref in sorted(hyperlinks.keys(), key=lambda r: parse_cell_ref(r)):
        lines.append(f"  {ref} → {hyperlinks[ref]}")
    return '\n'.join(lines) + '\n'


# SCAN-1: use a tuple so we can test with startswith() for trailing-context variants
_FORMULA_ERRORS = ('#REF!', '#VALUE!', '#DIV/0!', '#N/A', '#NAME?', '#NULL!', '#NUM!')
# SCAN-2: broadened to catch xcash, x-cash, ×cash, and numeric-prefixed forms
_X_CASH_PAT = re.compile(r'\b\d*[xX][-\s]?cash\b|\bxcash\b|\bx-cash\b|×\s*cash', re.IGNORECASE)
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
            val = cell.get('value', '') or ''
            # SCAN-1: use startswith to catch error strings with trailing context text
            if cell.get('type') == 'e' or any(val.startswith(e) for e in _FORMULA_ERRORS):
                results.append((sheet_name, cell['ref'], val or '#ERROR'))
    return results


def find_terminology(all_cells):
    """Return (sheet, ref, value, term) for x-cash and GiveDirectly instances."""
    # TERM-1: map term_key → display_tag; replaces hardcoded if/elif chains below.
    _TERM_DISPLAY_TAGS = {
        'x cash': '',                          # always a finding; no extra tag needed
        'GiveDirectly': ' [verify: may be source citation]',
    }
    # SCAN-5: cells may have None value if the cell is empty or formula-only;
    # coerce to '' before pattern matching.
    results = []
    for sheet_name, cells in all_cells.items():
        for (row, col), cell in sorted(cells.items()):
            val = cell.get('value', '') or ''
            frm = cell.get('formula', '') or ''  # SCAN-3: also check formula text
            text = val + ' ' + frm
            if _X_CASH_PAT.search(text):
                results.append((sheet_name, cell['ref'], val, 'x cash'))
            if _GD_PAT.search(text):
                results.append((sheet_name, cell['ref'], val, 'GiveDirectly'))
    return results, _TERM_DISPLAY_TAGS


def find_placeholders(all_cells):
    """Return (sheet, ref, value) for cells containing TBD / TODO / Placeholder."""
    results = []
    for sheet_name, cells in all_cells.items():
        for (row, col), cell in sorted(cells.items()):
            val = cell.get('value', '') or ''
            frm = cell.get('formula', '') or ''  # SCAN-4: also check formula text
            if _PLACEHOLDER_PAT.search(val) or _PLACEHOLDER_PAT.search(frm):
                results.append((sheet_name, cell['ref'], val))
    return results


def pre_findings_to_text(errors, terminology, term_display_tags, placeholders):
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
            # TERM-1: look up display tag from dict rather than hardcoded if/elif
            tag = term_display_tags.get(term, '')
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


def _col_to_num(col_str):
    """Convert 1–3 character column letters to 1-based index. Inverse of col_letter()."""
    n = 0
    for c in col_str.upper():
        n = n * 26 + (ord(c) - 64)
    return n


def adjust_formula_refs(formula, delta_row, delta_col):
    """Adjust relative cell references in a shared formula for a dependent cell.

    CELL-3: Shared formulas in XLSX store the master cell's formula unchanged for
    all dependents. Without adjustment, every dependent cell appears to reference
    the master cell's rows/columns, making copy-paste reference errors invisible.

    delta_row = dependent_row - master_row
    delta_col = dependent_col - master_col

    Absolute axes ($-prefixed) are not adjusted; relative axes are shifted by delta.
    """
    if delta_row == 0 and delta_col == 0:
        return formula

    def _adjust(m):
        col_lock, col_str, row_lock, row_str = m.group(1), m.group(2), m.group(3), m.group(4)
        new_col = col_letter(max(1, _col_to_num(col_str) + (0 if col_lock else delta_col)))
        new_row = str(max(1, int(row_str) + (0 if row_lock else delta_row)))
        return f"{col_lock}{new_col}{row_lock}{new_row}"

    # Match: optional-$ + 1–3 uppercase column letters + optional-$ + 1–7 row digits.
    # Negative lookbehind prevents matching inside function names or word identifiers.
    return re.sub(r'(?<![A-Za-z])(\$?)([A-Z]{1,3})(\$?)(\d{1,7})', _adjust, formula)


def load_named_ranges(zf):
    """NAME-1: Parse <definedNames> from workbook.xml.
    Returns list of (name, refers_to) tuples so agents can resolve named-range references."""
    try:
        with zf.open('xl/workbook.xml') as f:
            tree = ET.parse(f)
    except KeyError:
        return []
    root = tree.getroot()
    defined_names_el = root.find('ss:definedNames', NS)
    if defined_names_el is None:
        return []
    results = []
    for dn in defined_names_el.findall('ss:definedName', NS):
        name = dn.get('name', '')
        refers_to = dn.text or ''
        results.append((name, refers_to))
    return results


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
    # CELL-3: store (formula_text, master_row, master_col) so dependents can adjust refs
    shared_formulas = {}  # si index -> (master_formula, master_row, master_col)
    # PERF-1: find sheetData element directly then iterate rows/cells via iter() for
    # more robust parsing rather than searching the whole tree.
    sheet_data = root.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData')
    row_iter = sheet_data.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row') if sheet_data is not None else []
    for row_el in row_iter:
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
            # Dependent cells carry si=N but no formula text — look up and adjust the master.
            formula = None
            if f_el is not None:
                si = f_el.get('si')
                f_type = f_el.get('t', '')
                if f_el.text:
                    formula = f_el.text
                    # FORM-2/extract: annotate array (CSE) formulas
                    if f_type == 'array':
                        formula = '{' + formula + '}'
                    if f_type == 'shared' and si is not None:
                        shared_formulas[si] = (formula, row, col)
                elif f_type == 'shared' and si is not None:
                    master_entry = shared_formulas.get(si)
                    if master_entry is not None:
                        master_fml, master_row, master_col = master_entry
                        # CELL-3: adjust relative refs for this dependent cell
                        formula = adjust_formula_refs(master_fml, row - master_row, col - master_col)
                    # CELL-4: if master not yet seen (malformed XLSX), formula stays None

            if t == 's' and raw_val is not None:
                try:
                    display = shared_strings[int(raw_val)]
                except (IndexError, ValueError):
                    display = raw_val
            elif t == 'b':
                display = 'TRUE' if raw_val == '1' else 'FALSE'
            elif t == 'e':
                # CELL-1: error cells — always emit the error string, never blank
                display = raw_val or '#ERROR'
            elif t == 'd':
                # CELL-2: date cells — tag with [date:] to avoid ambiguous serial numbers
                display = f'[date:{raw_val}]' if raw_val else '[date]'
            elif t == 'str' and formula:
                # Calculated string — value is in v
                display = raw_val or ''
            elif t == 'str':
                # FORM-3: t=str with no formula — calculated string whose formula was not
                # stored; use cached value.
                display = raw_val or ''
            elif t == 'inlineStr':
                is_el = c.find('ss:is', NS)
                if is_el is not None:
                    # CELL-5/6: use iter() to collect all <t> runs in rich-text inline strings
                    t_texts = [el.text or '' for el in is_el.iter(
                        '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'
                    )]
                    display = ''.join(t_texts)
                else:
                    display = raw_val or ''
            else:
                display = raw_val or ''

            cells[(row, col)] = {
                'value': display,
                'formula': formula,
                'type': t,
                'ref': ref,
            }

    # MERGE-1: parse <mergeCells> and propagate the top-left cell's value to all
    # other cells in each merge range that are currently empty, appending "(merged)".
    merge_cells_el = root.find(
        '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}mergeCells'
    )
    if merge_cells_el is not None:
        for mc in merge_cells_el:
            mc_ref = mc.get('ref', '')
            if not mc_ref or ':' not in mc_ref:
                continue
            top_left_ref, bottom_right_ref = mc_ref.split(':', 1)
            tl_row, tl_col = parse_cell_ref(top_left_ref)
            br_row, br_col = parse_cell_ref(bottom_right_ref)
            tl_cell = cells.get((tl_row, tl_col))
            if tl_cell is None:
                continue
            tl_value = (tl_cell.get('value') or '').strip()
            if not tl_value:
                continue  # empty merged range — nothing to propagate
            for mr in range(tl_row, br_row + 1):
                for mc_col in range(tl_col, br_col + 1):
                    if (mr, mc_col) == (tl_row, tl_col):
                        continue  # skip the top-left cell itself
                    existing = cells.get((mr, mc_col))
                    # Propagate when cell is absent OR has no value (style-only empty cells
                    # are written by Excel as <c r="..." s="N"/> — present but valueless)
                    if existing is None or not (existing.get('value') or '').strip():
                        synthetic_ref = col_letter(mc_col) + str(mr)
                        merged_val = (tl_cell.get('value') or '') + ' (merged)'
                        cells[(mr, mc_col)] = {
                            'value': merged_val,
                            'formula': None,
                            'type': tl_cell.get('type', ''),
                            'ref': synthetic_ref,
                        }

    return cells

def cells_to_text(cells, sheet_name):
    """Render cells as a readable text table."""
    if not cells:
        return f"[Sheet '{sheet_name}' is empty]\n"
    rows = sorted(set(r for r, c in cells))
    # OUT-1: Column range spans min to max populated column — may appear wide for sparse
    # sheets with isolated notes/references.
    cols = sorted(set(c for r, c in cells))
    lines = [f"=== Sheet: {sheet_name} ==="]
    # OUT-4: include cell count in sheet header line
    lines.append(f"Rows: {min(rows)}–{max(rows)}, Cols: {col_letter(min(cols))}–{col_letter(max(cols))}, Cells: {len(cells)}")
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
        # ZIP-1: open ZipFile inside a with block so the file handle is always closed,
        # even if an exception fires before any explicit close.
        zf_handle = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        sys.exit(f"Error: '{path}' is not a valid ZIP/XLSX file.")

    os.makedirs('output', exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join('output', f'extracted_{base}.txt')

    all_cells = {}
    with zf_handle as zf:
        shared_strings = load_shared_strings(zf)
        sheet_names = load_sheet_names(zf)
        rels = load_sheet_rels(zf)
        # NAME-1: load named ranges so agents can resolve named-range references in formulas
        named_ranges = load_named_ranges(zf)

        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(f"Workbook: {os.path.basename(path)}\n")
            out.write(f"Sheets: {', '.join(n for n, _, _s in sheet_names)}\n")
            out.write("=" * 80 + "\n\n")

            # NAME-1: write Named ranges section before sheet content
            if named_ranges:
                out.write("=== Named ranges ===\n")
                for nr_name, nr_ref in named_ranges:
                    out.write(f"  {nr_name} = {nr_ref}\n")
                out.write("\n" + "=" * 80 + "\n\n")

            all_hyperlinks = {}
            # TABS-1: load_sheet_names now returns 3-tuples; annotate hidden/veryHidden sheets
            for name, rid, state in sheet_names:
                target = rels.get(rid, '')
                # Build display name with visibility annotation for agents
                if state == 'hidden':
                    display_name = f"{name} [HIDDEN]"
                elif state == 'veryHidden':
                    display_name = f"{name} [VERY HIDDEN]"
                else:
                    display_name = name
                if not target:
                    warning_msg = f"Warning: rId '{rid}' for sheet '{display_name}' not found in workbook rels — sheet skipped."
                    # TABS-2: print to stdout so the warning appears in terminal output,
                    # not only in the output file.
                    print(warning_msg)
                    out.write(f"[Could not find sheet target for '{display_name}']\n")
                    all_cells[name] = {}
                    all_hyperlinks[name] = {}
                    continue
                cells = extract_sheet(zf, target, shared_strings)
                all_cells[name] = cells
                out.write(cells_to_text(cells, display_name))
                hl_rels = load_hyperlink_rels(zf, target)
                hyperlinks = extract_hyperlinks(zf, target, hl_rels)
                all_hyperlinks[name] = hyperlinks
                if hyperlinks:
                    out.write(hyperlinks_to_text(hyperlinks, display_name))
                out.write("\n" + "=" * 80 + "\n\n")

    errors = find_formula_errors(all_cells)
    terminology, term_display_tags = find_terminology(all_cells)
    placeholders = find_placeholders(all_cells)
    with open(out_path, 'a', encoding='utf-8') as out:
        out.write(pre_findings_to_text(errors, terminology, term_display_tags, placeholders))

    print(f"Extracted to: {out_path}")
    # Print summary from already-built cells dict
    for name, rid, state in sheet_names:
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
