#!/usr/bin/env python3
"""Generate vetting-skill-slides.pptx using raw Open XML — no external deps."""
import zipfile

OUT = "/Users/mray/Desktop/spreadsheet-vetter/output/vetting-skill-slides.pptx"

CX = 12192000   # widescreen width  (13.33 in)
CY = 6858000    # widescreen height (7.50 in)

BLUE  = "1A5C8A"; DBLU  = "1A3A5C"; AMBER = "B8960C"
GREEN = "1A8A5A"; RED   = "A93226"; PURP  = "6C3483"
GRAY  = "888888"; WHITE = "FFFFFF"; LGRAY = "F0F4F8"
DKBL  = "1F4E79"

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

_id = [1]
def nid():  _id[0] += 1; return _id[0]
def reset(): _id[0] = 1

# ── Shape builders ────────────────────────────────────────────────────────────

def box(x, y, w, h, fill, border=None):
    i = nid()
    ln = (f'<a:ln w="9525"><a:solidFill><a:srgbClr val="{border}"/></a:solidFill></a:ln>'
          if border else '<a:ln><a:noFill/></a:ln>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="b{i}"/>'
            f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>{ln}</p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')

def txt(x, y, w, h, paras, anchor="t"):
    """paras = list of paragraph-lists; each para = list of run-dicts or [] for blank line.
       run keys: text, size(pt, default 14), bold, italic, color, align(l/c/r)"""
    i = nid()
    p_xml = ""
    for para in paras:
        if not para:
            p_xml += "<a:p/>"
            continue
        algn = {"l": "l", "c": "ctr", "r": "r"}.get(para[0].get("align","l"), "l")
        r_xml = "".join(
            f'<a:r><a:rPr lang="en-US" sz="{int(run.get("size",14)*100)}" '
            f'b="{"1" if run.get("bold") else "0"}" '
            f'i="{"1" if run.get("italic") else "0"}" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{run.get("color","333333")}"/></a:solidFill>'
            f'<a:latin typeface="Segoe UI"/></a:rPr>'
            f'<a:t>{esc(run["text"])}</a:t></a:r>'
            for run in para
        )
        p_xml += f'<a:p><a:pPr algn="{algn}"/>{r_xml}</a:p>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="t{i}"/>'
            f'<p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
            f'<a:noFill/><a:ln><a:noFill/></a:ln></p:spPr>'
            f'<p:txBody><a:bodyPr anchor="{anchor}" wrap="square" '
            f'lIns="91440" rIns="91440" tIns="45720" bIns="45720"/>'
            f'<a:lstStyle/>{p_xml}</p:txBody></p:sp>')

def R(text, size=14, bold=False, italic=False, color="333333", align="l"):
    return {"text": text, "size": size, "bold": bold, "italic": italic,
            "color": color, "align": align}

def hdr(label, title, sh):
    sh.append(box(0, 0, CX, 100000, BLUE))
    sh.append(txt(457200, 165000, CX-914400, 200000,
                  [[R(label.upper(), 9, bold=True, color=BLUE)]]))
    sh.append(txt(457200, 330000, CX-914400, 580000,
                  [[R(title, 28, bold=True, color=DBLU)]]))

def card(x, y, w, h, title, lines, accent=BLUE, bg=LGRAY):
    parts = [box(x, y, w, h, bg),
             box(x, y, 50000, h, accent),
             txt(x+100000, y+100000, w-160000, 220000,
                 [[R(title, 12, bold=True, color=DBLU)]]),
             txt(x+100000, y+300000, w-160000, h-340000,
                 [[R(l, 11, color="555555")] for l in lines])]
    return parts

# ── Slide XML wrapper ─────────────────────────────────────────────────────────

def wrap(shapes):
    sp = "\n".join(shapes)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
       xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
      <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {sp}
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE CONTENT
# ═══════════════════════════════════════════════════════════════════════════════

def slide1():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    sh.append(box(0, 0, CX, 100000, BLUE))
    sh.append(txt(457200, 200000, int(CX*0.7), 200000,
                  [[R("GiveWell · Research Operations", 11, color=GRAY)]]))
    sh.append(txt(457200, 520000, int(CX*0.65), 1380000, [
        [R("Spreadsheet", 46, bold=True, color=DBLU)],
        [R("Vetting Skill", 46, bold=True, color=BLUE)],
    ]))
    sh.append(txt(457200, 2100000, int(CX*0.62), 900000, [
        [R("Using Claude Code to audit cost-effectiveness analysis spreadsheets —", 15, color=GRAY)],
        [R("catching formula errors, plausibility issues, and readability", 15, color=GRAY)],
        [R("problems before publication.", 15, color=GRAY)],
    ]))
    sh.append(box(457200, CY-470000, int(CX*0.5), 18000, "DDDDDD"))
    sh.append(txt(457200, CY-400000, int(CX*0.5), 280000,
                  [[R("April 2026  ·  Meghna Ray", 12, color="BBBBBB")]]))
    return wrap(sh)

def slide2():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Overview", "What the skill does", sh)
    cw = int((CX - 3*457200) // 2)
    x1, x2 = 457200, 457200 + cw + 457200
    y0 = 1020000
    for acc, ttl, lines in [
        (BLUE, "Input",
         ["A GiveWell CEA spreadsheet — a Google Sheet or Excel file",
          "modeling the cost-effectiveness of a grant."]),
        (GREEN, "Output 1 — Findings Sheet",
         ["Every issue flagged, tagged by severity (High/Medium/Low) and",
          "type (D/H/O). Includes exact cell references and recommended fixes."]),
        (RED, "Output 2 — Vetting Summary Doc",
         ["Human-readable summary: workbook structure, baseline CE figures,",
          "and key findings for the researcher to review."]),
    ]:
        for s in card(x1, y0, cw, 570000, ttl, lines, acc): sh.append(s)
        y0 += 650000
    y0 = 1020000
    for ttl, lines in [
        ("Formula Check", ["Hardcoded values, broken references, stale parameters,",
                           "cross-sheet inconsistencies."]),
        ("Plausibility", ["Adjustment magnitudes, multiplicative vs. additive",
                          "methods, VOI assumptions."]),
        ("Source Audit", ["Missing citations, stale data, unverifiable",
                          "'GW analysis' references, org mismatches."]),
        ("Readability", ["Label precision, vestigial rows, first-person notes,",
                         "parallel tab structure."]),
    ]:
        for s in card(x2, y0, cw, 430000, ttl, lines, AMBER): sh.append(s)
        y0 += 500000
    return wrap(sh)

def slide3():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Architecture", "How it works", sh)
    sh.append(txt(457200, 1010000, CX-914400, 240000, [
        [R("Invoked with /vetting <spreadsheet URL>  —  runs five specialized agents in sequence.", 13, color=GRAY)]
    ]))
    sh.append(box(457200, 1360000, 1900000, 420000, "E8F8F5", GREEN))
    sh.append(txt(570000, 1400000, 1680000, 340000, [
        [R("Orchestrator", 14, bold=True, color="1A5C3A")],
        [R("Steps 0–2 · SKILL.md", 10, color=GRAY)],
    ]))
    sh.append(txt(2500000, 1430000, 2800000, 300000, [
        [R("Reads spreadsheet, summarizes structure,", 12, color=GRAY)],
        [R("creates output files, then spawns agents", 12, color=GRAY)],
    ]))
    agents = [
        ("Formula\nCheck", "Steps 3–4"),
        ("Plausibility", "Step 5"),
        ("Source\nAudit", "Step 6"),
        ("Readability", "Steps 7–7b"),
        ("Sensitivity\n& Final Review", "Steps 8–10"),
    ]
    arw = 170000
    aw = int((CX - 2*457200 - (len(agents)-1)*arw) / len(agents))
    ah, ax, ay = 720000, 457200, 1910000
    for idx, (name, step) in enumerate(agents):
        sh.append(box(ax, ay, aw, ah, "FEF9E7", AMBER))
        nparas = [[R(line, 12, bold=True, color="7D6608")] for line in name.split("\n")]
        nparas.append([R(step, 10, color=GRAY)])
        sh.append(txt(ax+80000, ay+80000, aw-160000, ah-160000, nparas, anchor="ctr"))
        ax += aw
        if idx < len(agents)-1:
            sh.append(txt(ax, ay+ah//2-160000, arw, 320000,
                          [[R("→", 16, color=AMBER, align="c")]], anchor="ctr"))
            ax += arw
    nw = int((CX - 3*457200) // 2)
    for nx, acc, t, b in [
        (457200, BLUE, "Each agent reads prior findings first",
         "Agents run sequentially — each reads what previous agents wrote, avoiding duplicates and building on earlier context."),
        (457200+nw+457200, PURP, "Reference docs loaded on demand",
         "Vetting Guide, Moral Weights, CEA Consistency, VOI Template, and Legibility Guide load only when the relevant step begins."),
    ]:
        for s in card(nx, 2800000, nw, 620000, t, [b], acc): sh.append(s)
    return wrap(sh)

def slide4():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Evaluation", "How we tested it", sh)
    sh.append(txt(457200, 1010000, CX-914400, 260000, [
        [R("Each 'pre-vet' is a blind comparison: Claude vets first, then a human vets independently. We grade Claude against the human.", 13, color=GRAY)]
    ]))
    steps = [
        ("Claude vets\nthe spreadsheet", "Runs full skill,\nwrites findings"),
        ("Human vets\nindependently", "No prior knowledge\nof Claude's output"),
        ("Grade &\ncompare", "D/H/O recall\n+ precision"),
        ("Update\nthe skill", "Add checks for\neach miss"),
    ]
    bw, bh = 2000000, 900000
    total = len(steps)*bw + (len(steps)-1)*400000
    sx = (CX - total) // 2
    sy = 1420000
    for idx, (ttl, sub) in enumerate(steps):
        sh.append(box(sx, sy, bw, bh, "EDF4FB", BLUE))
        tp = [[R(l, 13, bold=True, color=DBLU)] for l in ttl.split("\n")]
        sp = [[R(l, 11, color=GRAY)] for l in sub.split("\n")]
        sh.append(txt(sx+100000, sy+100000, bw-200000, bh-200000,
                      tp+[[]]+sp, anchor="ctr"))
        sx += bw
        if idx < len(steps)-1:
            sh.append(txt(sx, sy+bh//2-180000, 400000, 360000,
                          [[R("→", 20, color=BLUE, align="c")]], anchor="ctr"))
            sx += 400000
    cw = int((CX - 3*457200) // 2)
    for cx2, acc, t, b in [
        (457200, GREEN, "What counts as a 'catch'",
         "Full credit: Claude named the same cell and issue as the human. Partial credit: Claude identified the right area but not the specific cell or question."),
        (457200+cw+457200, BLUE, "What counts as a false positive",
         "A finding Claude filed that the human reviewer considered invalid, not a real issue, or a misreading of the spreadsheet."),
    ]:
        for s in card(cx2, 2600000, cw, 700000, t, [b], acc): sh.append(s)
    return wrap(sh)

def slide5():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Evaluation", "The grading rubric", sh)
    tx, ty = 457200, 1000000
    tw = CX - 914400
    cols = [int(tw*0.20), int(tw*0.50), int(tw*0.30)]
    hx = tx
    for htxt, cw in zip(["Category", "What it covers", "Target recall"], cols):
        sh.append(box(hx, ty, cw, 370000, DKBL))
        sh.append(txt(hx+80000, ty+90000, cw-160000, 200000,
                      [[R(htxt, 12, bold=True, color=WHITE)]]))
        hx += cw
    rows = [
        ("D — Decision", "FFB3B3", "7B241C",
         "Formula bugs, stale parameters, wrong references that change the bottom-line CE by ≥5%. A miss here could affect a funding decision.",
         "≥ 90%", RED),
        ("H — Heads-up", "FFE5B3", "7D6608",
         "Structural or methodological questions the researcher should consider — questionable assumptions, modeling choices, undocumented parameters.",
         "≥ 80%", AMBER),
        ("O — Other", "B3D9B3", "1A5C3A",
         "Legibility issues, label precision, missing source notes, readability improvements. Important but not CE-critical.",
         "≥ 80%", GREEN),
    ]
    rh = 600000
    for ridx, (cat, chip_bg, chip_fg, desc, tgt, tgt_col) in enumerate(rows):
        ry = ty + 370000 + ridx*rh
        bg = "FAFAFA" if ridx % 2 == 0 else WHITE
        rx = tx
        sh.append(box(rx, ry, cols[0], rh, bg))
        sh.append(box(rx+80000, ry+rh//2-90000, cols[0]-160000, 180000, chip_bg))
        sh.append(txt(rx+120000, ry+rh//2-70000, cols[0]-200000, 160000,
                      [[R(cat, 11, bold=True, color=chip_fg)]]))
        rx += cols[0]
        sh.append(box(rx, ry, cols[1], rh, bg))
        sh.append(txt(rx+80000, ry+80000, cols[1]-160000, rh-160000,
                      [[R(desc, 11, color="444444")]]))
        rx += cols[1]
        sh.append(box(rx, ry, cols[2], rh, bg))
        sh.append(txt(rx+80000, ry+80000, cols[2]-160000, rh-160000,
                      [[R(tgt, 20, bold=True, color=tgt_col, align="c")]], anchor="ctr"))
    by = ty + 370000 + 3*rh + 160000
    mw = int((CX - 4*228600) // 3)
    for mx, acc, mt, mb in [
        (457200, GREEN, "Recall",
         "Of all findings the human identified, what share did Claude catch? Tracked separately for D, H, and O."),
        (457200+mw+228600, BLUE, "Overall Score",
         "Simple average of D-recall, H-recall, and O-recall. A single number to track improvement across vets."),
        (457200+2*mw+2*228600, AMBER, "Precision",
         "Of findings Claude filed, what share were valid? Measures signal-to-noise — how much review time Claude creates vs. saves."),
    ]:
        for s in card(mx, by, mw, 500000, mt, [mb], acc): sh.append(s)
    return wrap(sh)

def slide6():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Results", "Performance across 5 pre-vets", sh)
    tx, ty = 457200, 1000000
    tw = CX - 914400
    cols = [int(tw*0.34), int(tw*0.12), int(tw*0.12), int(tw*0.12), int(tw*0.16), int(tw*0.14)]
    headers = ["Spreadsheet", "D-recall", "H-recall", "O-recall", "Overall", "Precision"]
    hx = tx
    for htxt, cw in zip(headers, cols):
        sh.append(box(hx, ty, cw, 370000, DKBL))
        algn = "l" if htxt == "Spreadsheet" else "c"
        sh.append(txt(hx+80000, ty+90000, cw-160000, 200000,
                      [[R(htxt, 12, bold=True, color=WHITE, align=algn)]]))
        hx += cw
    def sc(v):
        if v == "N/A": return GRAY
        n = int(v.replace("%",""))
        return GREEN if n >= 80 else (AMBER if n >= 60 else RED)
    data = [
        ("UNFPA Supplies CEA",   "67%",  "33%",  "100%", "67%",  "96%"),
        ("PATH SAFEStart+ CEA",  "0%",   "100%", "0%",   "33%",  "100%"),
        ("GiveWell VAS CEA",     "N/A",  "0%",   "21%",  "11%",  "96%"),
        ("mSupply RCT CEA",      "63%",  "0%",   "33%",  "32%",  "87%"),
        ("HIV PrEP CEA",         "100%", "80%",  "100%", "93%",  "94%"),
    ]
    rh = 540000
    for ridx, row in enumerate(data):
        ry = ty + 370000 + ridx*rh
        bg = "EDF4FB" if row[0] == "HIV PrEP CEA" else ("FAFAFA" if ridx%2==0 else WHITE)
        rx = tx
        for j, (val, cw) in enumerate(zip(row, cols)):
            sh.append(box(rx, ry, cw, rh, bg))
            bold = j == 0
            color = DBLU if j == 0 else sc(val)
            algn = "l" if j == 0 else "c"
            sh.append(txt(rx+80000, ry+80000, cw-160000, rh-160000,
                          [[R(val, 13, bold=bold, color=color, align=algn)]], anchor="ctr"))
            rx += cw
    sh.append(txt(457200, ty+370000+5*rh+120000, CX-914400, 300000, [
        [R("Precision has stayed consistently high (≥87%) across all vets. Recall on D-findings reached 100% in vet 5 after targeted skill improvements.",
           11, italic=True, color="AAAAAA")]
    ]))
    return wrap(sh)

def slide7():
    reset(); sh = []
    sh.append(box(0, 0, CX, CY, WHITE))
    hdr("Iteration", "How the skill improves", sh)
    sh.append(txt(457200, 1010000, CX-914400, 260000, [
        [R("Every miss becomes a new check. After each vet, we analyze what Claude missed and add targeted instructions to the relevant agent file.", 13, color=GRAY)]
    ]))
    cw = int((CX - 3*457200) // 2)
    x1, x2 = 457200, 457200+cw+457200
    y0 = 1420000
    for acc, ttl, body in [
        (BLUE, "Vet 1 → plausibility.md",
         "Missed multiplicative vs. additive adjustment. Added: when adjustments chain multiplicatively, compute additive equivalent and flag if they differ by >10 pp."),
        (AMBER, "Vet 2 → formula-check.md",
         "Missed GW benchmark in row 22 (outside declared scope 'rows 1–15'). Added: always check benchmark and final CE row regardless of declared scope."),
        (GREEN, "Cross-vet pattern → all agents",
         "Agents named the right section but stopped short of the specific cell. Added 'name the cell before filing' rule to all 5 agent files."),
    ]:
        for s in card(x1, y0, cw, 680000, ttl, [body], acc): sh.append(s)
        y0 += 760000
    sh.append(box(x2, 1420000, cw, 2200000, LGRAY))
    sh.append(txt(x2+100000, 1490000, cw-200000, 280000,
                  [[R("5 vets → 20+ new checks added", 13, bold=True, color=DBLU)]]))
    checks = [
        "Multiplicative vs. additive adjustment",
        "Leverage benefit/cost allocation",
        "Benchmark row always checked",
        "Hardcoded literals inside formulas",
        "Vestigial pass-through rows",
        "Active org-mismatch scan",
        "Broken link protocol (http → https)",
        "Unverifiable 'GW analysis' sources",
        "Age-range label precision",
        "VOI parameter deviation check",
        "Complex formula walkthrough notes",
        "Aggregating-function as point estimate",
        "Structural row-parity for parallel tabs",
        "'Name the cell before filing'",
        "Cross-tab time-parameter sourcing",
    ]
    sh.append(txt(x2+100000, 1770000, cw-200000, 1860000,
                  [[R(f"\u2713  {c}", 11, color="555555")] for c in checks]))
    return wrap(sh)

# ── PPTX plumbing ─────────────────────────────────────────────────────────────

SLIDES = [slide1, slide2, slide3, slide4, slide5, slide6, slide7]
N = len(SLIDES)

def content_types():
    ov = "".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" '
        f'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>\n'
        for i in range(1, N+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{ov}  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

def prs_xml():
    sids = "\n".join(f'    <p:sldId id="{256+i}" r:id="rId{i}"/>' for i in range(1, N+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
                saveSubsetFonts="1">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId0"/></p:sldMasterIdLst>
  <p:sldIdLst>
{sids}
  </p:sldIdLst>
  <p:sldSz cx="{CX}" cy="{CY}" type="screen16x9"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>'''

def prs_rels():
    sr = "".join(
        f'  <Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>\n'
        for i in range(1, N+1))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId0" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
{sr}</Relationships>'''

MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:cSld><p:bg><p:bgRef idx="1001"><a:schemeClr val="bg1"/></p:bgRef></p:bg>
  <p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
      <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2"
            accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6"
            hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst>
    <p:sldLayoutId id="2147483649" r:id="rId1"/>
  </p:sldLayoutIdLst>
  <p:txStyles>
    <p:titleStyle><a:lvl1pPr><a:defRPr lang="en-US" sz="4000" b="1">
      <a:solidFill><a:srgbClr val="1A3A5C"/></a:solidFill>
    </a:defRPr></a:lvl1pPr></p:titleStyle>
    <p:bodyStyle><a:lvl1pPr><a:defRPr lang="en-US" sz="1800">
      <a:solidFill><a:srgbClr val="333333"/></a:solidFill>
    </a:defRPr></a:lvl1pPr></p:bodyStyle>
    <p:otherStyle><a:lvl1pPr><a:defRPr lang="en-US" sz="1800"/></a:lvl1pPr></p:otherStyle>
  </p:txStyles>
</p:sldMaster>'''

MASTER_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId99" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>'''

LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
             xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
             xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
             type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>
      <a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
  </p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''

LAYOUT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''

SLIDE_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>'''

THEME = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="GiveWell">
  <a:themeElements>
    <a:clrScheme name="GiveWell">
      <a:dk1><a:srgbClr val="1A3A5C"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="1A3A5C"/></a:dk2><a:lt2><a:srgbClr val="F5F8FC"/></a:lt2>
      <a:accent1><a:srgbClr val="1A5C8A"/></a:accent1>
      <a:accent2><a:srgbClr val="1A8A5A"/></a:accent2>
      <a:accent3><a:srgbClr val="B8960C"/></a:accent3>
      <a:accent4><a:srgbClr val="A93226"/></a:accent4>
      <a:accent5><a:srgbClr val="6C3483"/></a:accent5>
      <a:accent6><a:srgbClr val="888888"/></a:accent6>
      <a:hlink><a:srgbClr val="1A5C8A"/></a:hlink>
      <a:folHlink><a:srgbClr val="6C3483"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="GiveWell">
      <a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst>
          <a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="50000"/></a:schemeClr></a:gs>
          <a:gs pos="100000"><a:schemeClr val="phClr"/></a:gs>
        </a:gsLst></a:gradFill>
        <a:gradFill rotWithShape="1"><a:gsLst>
          <a:gs pos="0"><a:schemeClr val="phClr"/></a:gs>
          <a:gs pos="100000"><a:schemeClr val="phClr"/></a:gs>
        </a:gsLst></a:gradFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst>
          <a:outerShdw blurRad="40000" dist="23000" dir="5400000" rotWithShape="0">
            <a:srgbClr val="000000"><a:alpha val="35000"/></a:srgbClr>
          </a:outerShdw>
        </a:effectLst></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst>
          <a:gs pos="0"><a:schemeClr val="phClr"/></a:gs>
          <a:gs pos="100000"><a:schemeClr val="phClr"/></a:gs>
        </a:gsLst></a:gradFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>'''

CORE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
                   xmlns:dc="http://purl.org/dc/elements/1.1/"
                   xmlns:dcterms="http://purl.org/dc/terms/"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:creator>Meghna Ray</dc:creator>
  <dc:title>GiveWell Spreadsheet Vetting Skill</dc:title>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-04-08T00:00:00Z</dcterms:created>
</cp:coreProperties>'''

APP = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>Microsoft Office PowerPoint</Application>
  <Slides>{N}</Slides>
</Properties>'''

# ── Assemble ─────────────────────────────────────────────────────────────────

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", content_types())
    z.writestr("_rels/.rels", ROOT_RELS)
    z.writestr("ppt/presentation.xml", prs_xml())
    z.writestr("ppt/_rels/presentation.xml.rels", prs_rels())
    z.writestr("ppt/theme/theme1.xml", THEME)
    z.writestr("ppt/slideMasters/slideMaster1.xml", MASTER)
    z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", MASTER_RELS)
    z.writestr("ppt/slideLayouts/slideLayout1.xml", LAYOUT)
    z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", LAYOUT_RELS)
    z.writestr("docProps/core.xml", CORE)
    z.writestr("docProps/app.xml", APP)
    for i, fn in enumerate(SLIDES, 1):
        z.writestr(f"ppt/slides/slide{i}.xml", fn())
        z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels", SLIDE_RELS)

print(f"Written: {OUT}")
