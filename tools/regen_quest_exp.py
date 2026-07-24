#!/usr/bin/env python3
"""regen_quest_exp.py — mechanical regen of quest `exp` rewards against LEVELING.md §1.

Owner handoff: QUESTS.md §4 + the "stale exp" Open Questions in QUESTS.md / LEVELING.md
(pacing retune 2026-07-24). Contract:

  * each quest's authored `pct` is PRESERVED — parsed from the `exp:` line's inline
    comment (explicit `pct=`, `round(pct * V)`, or derived as exp/V_old) and round-trip
    verified against the OLD curve value stored in the same comment;
  * new `exp` = round(pct * exp_to_next_new(L)) with the ratified curve
    kills_per_level(L) = round(20 + 6.6*L + 0.20*L^2)  (LEVELING.md §1);
    the old value it replaces was built on kills_per_level_old(L) = round(20 + 0.20*L^2);
    exp_per_kill_normal(L) = round(4 * L^1.3) is shared by both (unchanged by the retune);
  * every stale number inside the comment (round() argument, exp_to_next(L)=V, arrow
    arithmetic, factor breakdowns, embedded old formula) is refreshed in place — all
    other comment text is preserved verbatim;
  * pct bands (QUESTS.md §4: main 15-30%, side 5-10%) are NOT enforced — out-of-band
    pcts are flagged, never clamped;
  * only the `exp:` reward line of docs/50_content/quests/*.yaml is touched; `shards`
    rewards and monster `stats.exp` are explicitly out of scope (not stale);
  * anything unparseable is flagged and left untouched (fix-or-flag, VALIDATION.md).

Usage:  python3 tools/regen_quest_exp.py [--apply] [--table-out PATH]
        (default is a dry run: prints the before/after table, FTUE check, and flags)
"""

import argparse
import math
import re
import sys
from pathlib import Path

QUEST_DIR = Path(__file__).resolve().parent.parent / "docs" / "50_content" / "quests"

# ---------------------------------------------------------------- curve math

def rnd(x: float) -> int:
    """round-half-up (the tree's tables use this; see self-test)."""
    return math.floor(x + 0.5)

def exp_per_kill(level: int) -> int:
    return rnd(4 * level ** 1.3)

def kills_old(level: int) -> int:
    return rnd(20 + 0.20 * level * level)

def kills_new(level: int) -> int:
    return rnd(20 + 6.6 * level + 0.20 * level * level)

def exp_to_next_old(level: int) -> int:
    return exp_per_kill(level) * kills_old(level)

def exp_to_next_new(level: int) -> int:
    return exp_per_kill(level) * kills_new(level)

# LEVELING.md §1 table rows + QUESTS.md §4 rows (90, 99) — the script refuses to run
# if its arithmetic does not reproduce the ratified tables exactly.
LEVELING_TABLE = {
    1: 108, 2: 340, 3: 714, 4: 1200, 5: 1856, 6: 2747, 7: 3800, 8: 5160,
    9: 6720, 10: 8480, 15: 22140, 20: 45704, 25: 81530, 30: 132534,
    35: 201872, 40: 292336, 45: 407208, 50: 549950, 55: 723216, 60: 931520,
    65: 1177540, 70: 1464924, 75: 1797440, 80: 2177148,
    90: 3103026, 99: 4140648,
}
CUMULATIVE_TO_8 = 10765  # LEVELING §1 cumulative_total @ Lv 8 (exp to go 1 -> 8)
FTUE_SHORTFALL = 3800    # ONBOARDING_FTUE §2: the ~10-min Lv 7->8 gap the grants must cover

def self_test() -> None:
    bad = {lv: (exp_to_next_new(lv), want) for lv, want in LEVELING_TABLE.items()
           if exp_to_next_new(lv) != want}
    if bad:
        sys.exit(f"self-test FAILED vs LEVELING.md §1 / QUESTS.md §4 tables: {bad}")

# ---------------------------------------------------------------- parsing

# inverse index of the old curve so files whose comment names no level still resolve
OLD_V_TO_LEVEL = {}
for _lv in range(1, 101):
    OLD_V_TO_LEVEL.setdefault(exp_to_next_old(_lv), _lv)

EXP_LINE = re.compile(r"^(\s*)exp:\s*(\d+)(\s*)#(.*)$")
NUM = r"[\d][\d,]*"

class ParseFail(Exception):
    pass

def strip_commas(s: str) -> int:
    return int(s.replace(",", ""))

def parse_comment(comment: str, stored_exp: int):
    """Return (pct, level, v_old, warns) or raise ParseFail with a reason.

    Two recoverable Phase-D authoring slips are accepted with a warn instead of a fail —
    in both, pct and level are unambiguously authored and the ratified curve is authoritative:
      A. explicit pct + on-curve old V, but the stored integer was mis-computed from them;
      B. explicit pct + explicit level marker, but the stored old V itself is off-curve
         (author slip in exp_per_kill) while stored integer matches round(pct * stored V).
    """
    # --- candidate old exp_to_next values -------------------------------
    v_candidates = []
    lvl_marked = None
    m = re.search(r"exp_to_next\((\d+)\)", comment)  # the L marker, whatever follows the call
    if m:
        lvl_marked = int(m.group(1))
    m = re.search(r"exp_to_next\((\d+)\)\s*=\s*(" + NUM + ")", comment)
    if m:
        v_candidates.append(strip_commas(m.group(2)))
    m = re.search(r"round\(\s*(0?\.\d+)\s*\*\s*(" + NUM + r")\s*\)", comment)
    pct_explicit = None
    if m:
        pct_explicit = float(m.group(1))
        v_candidates.append(strip_commas(m.group(2)))
    m = re.search(r"round\(\s*(0?\.\d+)\s*\*\s*exp_to_next\((\d+)\)\s*=\s*(" + NUM + r")\s*\)", comment)
    if m:
        pct_explicit = float(m.group(1))
        lvl_marked = int(m.group(2))
        v_candidates.append(strip_commas(m.group(3)))
    m = re.search(r"pct\s*=\s*(0?\.\d+)", comment)
    if m:
        pct_explicit = float(m.group(1))
    if lvl_marked is None:
        m = re.search(r"(?:at\s+)?Lv\s*(\d+)", comment)
        if m:
            lvl_marked = int(m.group(1))
    # last resort: any comma-grouped number in the comment that IS an old-curve value
    if not v_candidates:
        for tok in re.findall(NUM, comment):
            v = strip_commas(tok)
            if v in OLD_V_TO_LEVEL:
                v_candidates.append(v)
                break
    if not v_candidates:
        raise ParseFail("no old exp_to_next value found in comment")
    v_old = v_candidates[0]
    if any(v != v_old for v in v_candidates):
        raise ParseFail(f"comment carries conflicting old values {sorted(set(v_candidates))}")
    warns = []
    # --- level -----------------------------------------------------------
    lvl_derived = OLD_V_TO_LEVEL.get(v_old)
    if lvl_derived is None and lvl_marked is None:
        raise ParseFail(f"stored value {v_old} is not exp_to_next_old(L) for any L in 1..100 and no level marker")
    if lvl_derived is not None and lvl_marked is not None and lvl_marked != lvl_derived:
        raise ParseFail(f"comment says Lv {lvl_marked} but {v_old} = exp_to_next_old({lvl_derived})")
    level = lvl_derived if lvl_derived is not None else lvl_marked
    if v_old != exp_to_next_old(level):  # off-curve stored V (slip case B)
        if pct_explicit is not None and rnd(pct_explicit * v_old) == stored_exp:
            warns.append(f"stored old V {v_old:,} is off-curve (true exp_to_next_old({level}) = "
                         f"{exp_to_next_old(level):,}; author slip) — authored pct/level kept, true curve used")
        else:
            raise ParseFail(f"off-curve stored V {v_old} and no internally-consistent explicit pct")
    # --- pct ---------------------------------------------------------------
    pct = pct_explicit if pct_explicit is not None else round(stored_exp / v_old, 4)
    if rnd(pct * v_old) != stored_exp:
        if pct_explicit is not None and v_old == exp_to_next_old(level):  # slip case A
            warns.append(f"stored integer {stored_exp:,} was mis-computed from its own comment "
                         f"(round({pct} * {v_old:,}) = {rnd(pct * v_old):,}) — authored pct kept, regen heals it")
        else:
            raise ParseFail(f"round-trip failed: round({pct} * {v_old}) = {rnd(pct * v_old)} != stored {stored_exp}")
    return pct, level, v_old, warns

def fmt_like(value: int, template_token: str) -> str:
    """format value with thousands-commas iff the token it replaces had them."""
    return f"{value:,}" if "," in template_token else str(value)

def rewrite_comment(comment: str, v_old: int, level: int, pct: float, new_exp: int) -> str:
    v_new = exp_to_next_new(level)
    out = comment
    # 1) every occurrence of the old value (comma or plain form), longest-first
    for tok in (f"{v_old:,}", str(v_old)):
        if tok in out:
            out = out.replace(tok, fmt_like(v_new, tok))
    # 2) arrow arithmetic:  "= 148.5 -> 149"
    def arrow_sub(m):
        exact = pct * v_new
        return f"= {exact:.10g} -> {new_exp}"
    out = re.sub(r"=\s*[\d,]+(?:\.\d+)?\s*->\s*\d+", arrow_sub, out)
    # 3) embedded old formula  round(20+0.2*54^2) -> ratified formula
    out = re.sub(r"round\(20\s*\+\s*0\.2\s*\*\s*(\d+)\s*\^\s*2\)",
                 lambda m: f"round(20+6.6*{m.group(1)}+0.2*{m.group(1)}^2)", out)
    # 4) factor breakdowns  =716*603  where the product was the old value
    def factor_sub(m):
        a, b = int(m.group(1)), int(m.group(2))
        if a * b == v_old:
            return f"={exp_per_kill(level)}*{kills_new(level)}"
        return m.group(0)
    out = re.sub(r"=(\d+)\*(\d+)", factor_sub, out)
    return out

# ---------------------------------------------------------------- main pass

def load_quest_fields(text: str):
    fields = {}
    for key in ("id", "region", "quest_type", "level_requirement", "recommended_level"):
        m = re.search(rf"^{key}:\s*([A-Za-z0-9_]+)", text, re.M)
        fields[key] = m.group(1) if m else None
    return fields

BANDS = {"main": (0.15, 0.30), "side": (0.05, 0.10)}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--table-out", help="also write the before/after markdown table here")
    args = ap.parse_args()

    self_test()

    rows, flags, info = [], [], []
    files = sorted(QUEST_DIR.glob("quest_*.yaml"))
    if len(files) != 120:
        flags.append(f"expected 120 quest files, found {len(files)}")

    for path in files:
        text = path.read_text(encoding="utf-8")
        fields = load_quest_fields(text)
        qid = fields["id"] or path.stem
        exp_lines = [(i, EXP_LINE.match(line)) for i, line in enumerate(text.splitlines())
                     if EXP_LINE.match(line)]
        if len(exp_lines) != 1:
            flags.append(f"{qid}: expected exactly 1 exp line, found {len(exp_lines)} — untouched")
            continue
        idx, m = exp_lines[0]
        indent, stored, gap, comment = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        try:
            pct, level, v_old, warns = parse_comment(comment, stored)
        except ParseFail as e:
            flags.append(f"{qid}: {e} — untouched")
            continue
        for w in warns:
            info.append(f"{qid}: {w}")

        qtype = fields["quest_type"]
        lo, hi = BANDS.get(qtype, (0.0, 1.0))
        if qtype not in BANDS:
            flags.append(f"{qid}: unknown quest_type {qtype!r} — regenerated, band unchecked")
        elif not (lo - 1e-9 <= pct <= hi + 1e-9):
            flags.append(f"{qid}: pct {pct} outside {qtype} band {lo:.0%}-{hi:.0%} — regenerated, NOT clamped (owner call)")
        for fld in ("level_requirement", "recommended_level"):
            if fields[fld] and fields[fld].isdigit() and int(fields[fld]) != level:
                info.append(f"{qid}: comment level {level} != {fld} {fields[fld]} (authored quest_level kept)")

        new_exp = rnd(pct * exp_to_next_new(level))
        new_comment = rewrite_comment(comment, v_old, level, pct, new_exp)
        lines = text.splitlines(keepends=True)
        eol = "\n" if lines[idx].endswith("\n") else ""
        lines[idx] = f"{indent}exp: {new_exp}{gap}#{new_comment}{eol}"
        rows.append((qid, fields["region"], qtype, level, pct, stored, new_exp))
        if args.apply:
            path.write_text("".join(lines), encoding="utf-8")

    # ------------------------------------------------------------ report
    header = ("| quest | region | type | Lv | pct | exp (old) | exp (new) |\n"
              "|---|---|---|---|---|---|---|\n")
    table = header + "\n".join(
        f"| {q} | {r} | {t} | {lv} | {pct:.4g} | {old:,} | {new:,} |"
        for q, r, t, lv, pct, old, new in rows)
    print(table)

    ember = [(q, pct, new) for q, r, t, lv, pct, old, new in rows if r == "emberfoot"]
    ember_sum = sum(n for _, _, n in ember)
    print(f"\nFTUE check (ONBOARDING_FTUE.md §2): emberfoot quests = {len(ember)}, "
          f"summed new exp = {ember_sum:,}")
    print(f"  vs Lv7->8 shortfall target >= {FTUE_SHORTFALL:,}: "
          f"{'CLOSES' if ember_sum >= FTUE_SHORTFALL else 'DOES NOT CLOSE'}")
    print(f"  vs cumulative exp Lv1->8 = {CUMULATIVE_TO_8:,}: quests cover "
          f"{ember_sum / CUMULATIVE_TO_8:.0%} (LEVELING §4 quest share target ~25%)")
    print(f"  emberfoot pcts: {[(q, f'{p:g}') for q, p, _ in ember]}")

    print(f"\n{len(rows)}/{len(files)} files regenerated; {len(flags)} flag(s); {len(info)} info note(s)")
    for f in flags:
        print(f"  FLAG: {f}")
    for n in info:
        print(f"  info: {n}")
    if args.table_out:
        Path(args.table_out).write_text(table + "\n", encoding="utf-8")
    if not args.apply:
        print("\n(dry run — re-run with --apply to write)")
    return 1 if flags and args.apply else 0

if __name__ == "__main__":
    sys.exit(main())
