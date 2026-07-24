#!/usr/bin/env python3
"""Rebillion content validator — implements docs/VALIDATION.md checks 1-6.

Python 3 stdlib only. PyYAML is used if importable; otherwise a small tolerant
YAML reader (below) parses the block+flow subset our content files use, so the
tool runs on a bare python3.

Usage:
    python3 tools/validate.py [--scope A-B] [--entry map_NNN] [--allow-missing] [paths...]

Exit 0 = pass, 1 = fail. See tools/README.md for the check<->code map.
"""
import os
import re
import sys

try:
    import yaml as _yaml
except Exception:
    _yaml = None

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# REGISTRY — every enum token list, with the owner doc that mints it. Change a
# token in exactly one place here when its owner doc changes.
# ---------------------------------------------------------------------------
def _s(*x):
    return set(x)


REGISTRY = {
    # owner: 10_systems/ELEMENTS.md (GLOSSARY Elements)
    "element": _s("neutral", "fire", "frost", "nature", "arcane", "shadow"),
    # owner: 10_systems/STATUS_EFFECTS.md (GLOSSARY Status effects + cleanse tags)
    "status": _s("burn", "poison", "chill", "freeze", "stun", "root", "silence",
                 "blind", "sunder", "weaken", "empower", "fortify", "swiftness",
                 "regen", "clarity", "veil", "burn_type", "poison_type",
                 "chill_type", "control_type", "sense_type", "curse_type"),
    # owner: 10_systems/AI_BEHAVIOR.md (GLOSSARY AI profiles)
    "ai_profile": _s("passive_wanderer", "timid_grazer", "aggressive_charger",
                     "territorial_guard", "ambush_lurker", "ranged_skirmisher",
                     "aerial_swooper", "pack_hunter", "support_caller",
                     "kamikaze_burster", "stationary_turret", "boss_scripted"),
    # owner: 20_schemas/monster.schema.md (GLOSSARY Entity tiers)
    "monster_tier": _s("normal", "elite", "boss"),
    # owner: 10_systems/ITEMS.md (GLOSSARY Rarity)
    "rarity": _s("common", "uncommon", "rare", "epic", "legendary"),
    # owner: 40_assets/ART_BIBLE.yaml sizing.size_classes (GLOSSARY Size classes)
    "size_class": _s("tiny", "small", "medium", "large", "boss"),
    # owner: 10_systems/SKILL_EFFECTS.md (GLOSSARY Skill effect ops) — all 14
    "op": _s("deal_damage", "apply_status", "cleanse_status", "heal",
             "restore_essence", "grant_shield", "knockback", "pull", "dash",
             "leap", "taunt", "summon_entity", "passive_stat_bonus", "on_hit_proc"),
    # owner: item.schema.md restriction of the op registry (use rows only)
    "use_op": _s("heal", "restore_essence", "cleanse_status", "apply_status"),
    # owner: 10_systems/SKILL_SYSTEM.md (GLOSSARY Skill targeting)
    "targeting": _s("melee_arc", "line", "projectile", "aoe_circle", "self", "party"),
    # owner: 40_assets/ANIMATION_STATES.md (GLOSSARY Animation states)
    "animation_state": _s("idle", "walk", "jump", "fall", "climb", "attack", "cast",
                          "hit", "die", "telegraph", "phase_shift", "spawn"),
    # owner: 15_maps_system/MAPS_SYSTEM.md (GLOSSARY Map types)
    "map_type": _s("field", "dungeon", "town", "interior", "arena", "secret"),
    # owner: 10_systems/ITEMS.md (GLOSSARY Equipment slots)
    "slot": _s("weapon", "head", "body", "legs", "boots", "gloves", "cape", "ring", "amulet"),
    # owner: 10_systems/ITEMS.md (GLOSSARY Weapon types)
    "weapon_type": _s("blade", "bow", "staff", "dirk"),
    # owner: 10_systems/JOBS.md (GLOSSARY Job lines) — no novice weapon line
    "weapon_line": _s("bulwark", "keeneye", "weaver", "flicker"),
    # owner: 10_systems/JOBS.md (GLOSSARY Job lines) + novice
    "skill_line": _s("bulwark", "keeneye", "weaver", "flicker", "novice"),
    # owner: 10_systems/JOBS.md job bands
    "skill_tier": _s("novice", "first", "second", "third"),
    # owner: docs/WORLD_PLAN.md (GLOSSARY Region slugs)
    "region": _s("emberfoot", "millbrook", "verdant", "tidewatch", "gloomwood",
                 "ashfall", "sunken", "clockwork", "frostpeak", "arcane_reach", "voidshore"),
    # owner: map.schema.md / MAP_INTERACTABLES.md / MAP_CONNECTIONS.md
    "portal_kind": _s("edge", "door", "coach", "longship"),
    # owner: 15_maps_system/MAP_INTERACTABLES.md (portal/loot_drop excluded here)
    "interactable_type": _s("climbable", "reactor", "sign", "lore_marker", "inn_bed",
                            "storage_chest", "coach_station", "quest_object"),
    # owner: 15_maps_system/MAP_TRAVERSAL.md hazard tiers
    "hazard_tier": _s("minor", "standard", "severe"),
    # owner: map.schema.md
    "layers_preset": _s("standard"),
    # owner: item.schema.md category token set
    "category": _s("equip", "use", "etc"),
    # owner: skill.schema.md
    "skill_kind": _s("active", "passive"),
    # owner: npc.schema.md role enum
    "role": _s("merchant", "innkeeper", "blacksmith", "enchanter", "banker",
               "quest_giver", "coach_clerk", "pier_officer", "guide", "handler", "flavor"),
    # owner: npc.schema.md services enum
    "service": _s("inn_rest", "storage", "enhance", "coach", "longship"),
    # owner: quest.schema.md
    "quest_type": _s("main", "side"),
    # owner: quest.schema.md step types
    "step_type": _s("kill", "collect", "talk", "reach"),
    # owner: 10_systems/DROPS.md chance buckets (a raw float in [0,1] is also legal)
    "chance": _s("guaranteed", "common", "uncommon", "rare", "epic", "legendary"),
    # owner: drop_table.schema.md
    "rarity_source": _s("elite", "boss", "raid"),
}

# §1 banned tokens (docs/VALIDATION.md §1). Case-sensitive whole words. Only
# docs/VALIDATION.md may spell them.
BANNED = ["STR", "DEX", "INT", "LUK", "HP", "MP", "meso", "mesos"]
BANNED_RE = re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(BANNED) + r")(?![A-Za-z0-9_])")

# ---------------------------------------------------------------------------
# ID_REGISTRY.md v3 ranges + mob tier layout.
# ---------------------------------------------------------------------------
# Map region blocks: (slug, lo, hi)
MAP_BLOCKS = [
    ("emberfoot", 1, 16), ("millbrook", 17, 42), ("verdant", 43, 70),
    ("tidewatch", 71, 97), ("gloomwood", 98, 124), ("ashfall", 125, 151),
    ("sunken", 152, 176), ("clockwork", 177, 200), ("frostpeak", 201, 244),
    ("arcane_reach", 245, 284), ("voidshore", 285, 324),
]
# Raid bonus rooms (10_systems/social/RAID.md §6.E) — one per raid, each belonging to its
# raid's region but placed in an appended extension range, because every region block above
# is contiguous and full (CLAUDE.md Law 3: extend ranges, never renumber).
MAP_EXT_BLOCKS = [
    ("millbrook", 325, 325), ("clockwork", 326, 326),
    ("frostpeak", 327, 327), ("voidshore", 328, 328),
]
# Mob region blocks: (slug, normal_lo, normal_hi, elite_lo, elite_hi, boss)
MOB_BLOCKS = [
    ("emberfoot", 1, 10, 11, 11, 12), ("millbrook", 13, 24, 25, 26, 27),
    ("verdant", 28, 43, 44, 46, 47), ("tidewatch", 48, 63, 64, 66, 67),
    ("gloomwood", 68, 83, 84, 86, 87), ("ashfall", 88, 103, 104, 106, 107),
    ("sunken", 108, 123, 124, 127, 128), ("clockwork", 129, 144, 145, 149, 150),
    ("frostpeak", 151, 170, 171, 177, 178), ("arcane_reach", 179, 198, 199, 205, 206),
    ("voidshore", 207, 226, 227, 233, 234),
]
# Category overall numeric ranges (prefix -> (lo, hi, digit_width))
ID_RANGES = {
    "map": (1, 328, 3), "mob": (1, 234, 3), "drop_mob": (1, 234, 3),
    "npc": (1, 120, 3), "quest": (1, 120, 3),
    "item_equip": (1, 300, 4), "item_use": (1, 60, 4), "item_etc": (1, 200, 4),
    "skill": (1, 60, 3),  # per line; novice caps at 10 but 1-60 is the block
    "pool_equip": (1, 11, 2),
}

# Reference-scan regex: any content ID token that must resolve (§2).
REF_RE = re.compile(
    r"\b("
    r"mob_\d{3}|map_\d{3}|npc_\d{3}|quest_\d{3}|drop_mob_\d{3}"
    r"|item_(?:equip|use|etc)_\d{4}"
    r"|skill_(?:bulwark|keeneye|weaver|flicker|novice)_\d{3}"
    r"|pool_equip_r\d{2}"
    r")\b"
)

SCHEMA_BY_PATH = {
    "20_schemas/monster.schema.md": "monster",
    "20_schemas/map.schema.md": "map",
    "20_schemas/item.schema.md": "item",
    "20_schemas/skill.schema.md": "skill",
    "20_schemas/npc.schema.md": "npc",
    "20_schemas/quest.schema.md": "quest",
    "20_schemas/drop_table.schema.md": "drop_table",
}

# Required top-level fields per schema (front-matter + always-required content
# fields). Conditional fields (tier-gated, type-gated) are handled in code.
# Edit these lists here when a schema's required-field set changes.
REQUIRED = {
    "monster": ["id", "schema", "references", "name", "tier", "element", "level",
                "size_class", "stats", "ai_profile", "animation_states",
                "drop_table", "flavor"],
    "map": ["id", "schema", "references", "name", "region", "map_type",
            "level_band", "biome", "tileset", "size_tiles", "bgm",
            "layers_preset", "spawn_points", "platform_brief", "flavor"],
    "item": ["id", "schema", "references", "items"],
    "skill": ["id", "schema", "references", "name", "line", "tier", "kind",
              "targeting", "cost", "cooldown", "level_data", "flavor"],
    "npc": ["id", "schema", "references", "name", "region", "map", "role",
            "dialog", "flavor"],
    "quest": ["id", "schema", "references", "name", "region", "quest_type",
              "giver_npc", "level_requirement", "recommended_level", "steps",
              "rewards", "flavor", "offer_text", "complete_text"],
    # drop_table has two shapes; presence of 'pools' vs 'owner' distinguishes.
    "drop_table": ["id", "schema", "references"],
}
MONSTER_STATS_REQ = ["life", "power", "armor", "warding", "precision", "evasion", "exp"]

# Allowed top-level keys per schema (unknown top-level key = §3 fail).
ALLOWED = {
    "monster": set(REQUIRED["monster"]) | {
        "weak_to", "resists", "immune_to", "ai_params", "abilities", "phases",
        "respawn_override", "summon_owner", "animation_notes"},
    "map": set(REQUIRED["map"]) | {
        "water_physics", "ambience", "portals", "moving_platforms", "spawn_zones",
        "interactables", "npcs", "arena_config"},
    "item": set(REQUIRED["item"]),
    "skill": set(REQUIRED["skill"]) | {"max_level", "prerequisites", "animation"},
    "npc": set(REQUIRED["npc"]) | {"shop", "services", "portrait"},
    "quest": set(REQUIRED["quest"]) | {"turn_in_npc", "prereqs"},
    "drop_table": {"id", "schema", "references", "owner", "rows", "pools"},
}


# ---------------------------------------------------------------------------
# Tolerant YAML reader (used only when PyYAML is absent).
# ---------------------------------------------------------------------------
def _strip_comment(s):
    out, q, i = [], None, 0
    while i < len(s):
        c = s[i]
        if q:
            out.append(c)
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            out.append(c)
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _scalar(tok):
    tok = tok.strip()
    if tok == "" or tok in ("~", "null", "Null", "NULL"):
        return None
    if len(tok) >= 2 and tok[0] == tok[-1] and tok[0] in "\"'":
        return tok[1:-1]
    if tok in ("true", "True", "false", "False"):
        return tok.lower() == "true"
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        pass
    return tok


def _parse_flow(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return None, i
    if s[i] == "{":
        d, i = {}, i + 1
        while i < len(s):
            while i < len(s) and s[i] in " ,":
                i += 1
            if i < len(s) and s[i] == "}":
                return d, i + 1
            k, i = _read_flow_key(s, i)
            while i < len(s) and s[i] in " :":
                i += 1
            v, i = _parse_flow(s, i)
            d[k] = v
        return d, i
    if s[i] == "[":
        a, i = [], i + 1
        while i < len(s):
            while i < len(s) and s[i] in " ,":
                i += 1
            if i < len(s) and s[i] == "]":
                return a, i + 1
            v, i = _parse_flow(s, i)
            a.append(v)
        return a, i
    # bare scalar until , } ] (respecting quotes)
    start, q = i, None
    while i < len(s):
        c = s[i]
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c in ",}]":
            break
        i += 1
    return _scalar(s[start:i]), i


def _read_flow_key(s, i):
    start, q = i, None
    while i < len(s):
        c = s[i]
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == ":":
            break
        i += 1
    return _scalar(s[start:i].strip()), i


def _split_kv(content):
    q = None
    for i, c in enumerate(content):
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == ":" and (i + 1 >= len(content) or content[i + 1] == " "):
            return content[:i].strip(), content[i + 1:].strip()
    if content.endswith(":"):
        return content[:-1].strip(), ""
    return content.strip(), None


def _fallback_load(text):
    raw = text.split("\n")
    cur = [0]

    def indent(line):
        return len(line) - len(line.lstrip(" "))

    def skip():
        while cur[0] < len(raw):
            if _strip_comment(raw[cur[0]]).strip() == "":
                cur[0] += 1
                continue
            return True
        return False

    def value_of(v, parent_indent):
        v = v.strip()
        if v == "":
            return parse_block(parent_indent + 1)
        if v[0] in "|>":
            return parse_block_scalar(parent_indent, v)
        if v[0] in "{[":
            return _parse_flow(v, 0)[0]
        return _scalar(v)

    def parse_block_scalar(parent_indent, marker):
        fold = marker[0] == ">"
        body, base = [], None
        while cur[0] < len(raw):
            line = raw[cur[0]]
            if line.strip() == "":
                body.append("")
                cur[0] += 1
                continue
            ci = indent(line)
            if ci <= parent_indent:
                break
            if base is None:
                base = ci
            body.append(line[base:])
            cur[0] += 1
        out = "\n".join(body).strip("\n")
        return out.replace("\n", " ") if fold else out

    def parse_block(min_indent):
        if not skip():
            return None
        line = raw[cur[0]]
        ind = indent(line)
        if ind < min_indent:
            return None
        content = _strip_comment(line)[ind:]
        if content.startswith("- ") or content.strip() == "-":
            return parse_seq(ind)
        return parse_map(ind)

    def parse_seq(ind):
        arr = []
        while skip():
            line = raw[cur[0]]
            if indent(line) != ind:
                break
            content = _strip_comment(line)[ind:]
            if not (content.startswith("- ") or content.strip() == "-"):
                break
            j = 1
            while j < len(content) and content[j] == " ":
                j += 1
            rest = content[j:]
            item_indent = ind + j
            if rest == "":
                cur[0] += 1
                arr.append(parse_block(ind + 1))
            elif _split_kv(rest)[1] is not None and rest[0] not in "{[\"'":
                k, v = _split_kv(rest)
                cur[0] += 1
                arr.append(parse_map(item_indent, seed=(k, value_of(v, item_indent))))
            else:
                cur[0] += 1
                arr.append(value_of(rest, ind))
        return arr

    def parse_map(ind, seed=None):
        d = {}
        if seed is not None:
            d[seed[0]] = seed[1]
        while skip():
            line = raw[cur[0]]
            if indent(line) != ind:
                break
            content = _strip_comment(line)[ind:]
            if content.startswith("- "):
                break
            k, v = _split_kv(content)
            if v is None:
                cur[0] += 1
                continue
            cur[0] += 1
            d[k] = value_of(v, ind)
        return d

    return parse_block(0)


def load_yaml(text):
    if _yaml is not None:
        return _yaml.safe_load(text)
    return _fallback_load(text)


# ---------------------------------------------------------------------------
# Violation collection.
# ---------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.items = []  # (check, sev, file, line, msg)

    def add(self, check, sev, path, line, msg):
        self.items.append((check, sev, path, line, msg))

    def fail(self, check, path, line, msg):
        self.add(check, "FAIL", path, line, msg)

    def warn(self, check, path, line, msg):
        self.add(check, "WARN", path, line, msg)

    def has_fail(self):
        return any(i[1] == "FAIL" for i in self.items)

    def render(self):
        titles = {
            1: "§1 Forbidden tokens", 2: "§2 Referential integrity",
            3: "§3 Schema conformance", 4: "§4 ID uniqueness & range",
            5: "§5 World-graph soundness", 6: "§6 Asset contract",
        }
        fails = sum(1 for i in self.items if i[1] == "FAIL")
        warns = sum(1 for i in self.items if i[1] == "WARN")
        for chk in sorted(titles):
            group = [i for i in self.items if i[0] == chk]
            if not group:
                continue
            print("\n== %s ==" % titles[chk])
            for _, sev, path, line, msg in sorted(group, key=lambda x: (x[2], x[3])):
                loc = "%s:%d" % (path, line) if line else path
                print("  [%s] %s — %s" % (sev, loc, msg))
        print("\n%d failure(s), %d warning(s)." % (fails, warns))


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------
def rel(path):
    try:
        return os.path.relpath(path, REPO)
    except ValueError:
        return path


def find_line(raw_lines, key):
    pat = re.compile(r"^\s*" + re.escape(key) + r"\s*:")
    for n, line in enumerate(raw_lines, 1):
        if pat.match(line):
            return n
    return 0


def mob_tier(n):
    for slug, nl, nh, el, eh, boss in MOB_BLOCKS:
        if nl <= n <= nh:
            return "normal"
        if el <= n <= eh:
            return "elite"
        if n == boss:
            return "boss"
    return None


def walk_strings(node):
    """Yield every string scalar in a parsed structure."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v)
    elif isinstance(node, (list, tuple)):
        for v in node:
            yield from walk_strings(v)


def enum_check(rep, path, line, field, value, key):
    allowed = REGISTRY[key]
    if value not in allowed:
        rep.fail(3, path, line, "%s: '%s' not in %s registry" % (field, value, key))


# ---------------------------------------------------------------------------
# §1 banned-token scan.
# ---------------------------------------------------------------------------
def scan_banned(rep, files):
    for path in files:
        if rel(path) == "docs/VALIDATION.md":
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.read().split("\n")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            for m in BANNED_RE.finditer(line):
                rep.fail(1, rel(path), n, "forbidden token '%s'" % m.group(1))


# ---------------------------------------------------------------------------
# Per-schema field / enum validation (§3, plus §4 tier, §6 assets).
# ---------------------------------------------------------------------------
def check_effects(rep, path, line, effects, op_key):
    if not isinstance(effects, list):
        return
    for eff in effects:
        if not isinstance(eff, dict):
            continue
        op = eff.get("op")
        if op is not None and op not in REGISTRY[op_key]:
            rep.fail(3, path, line, "effects op '%s' not in %s registry" % (op, op_key))
        if "element" in eff and eff["element"] is not None:
            enum_check(rep, path, line, "effects.element", eff["element"], "element")
        if "status" in eff and eff["status"] is not None:
            if eff["status"] not in REGISTRY["status"]:
                rep.fail(3, path, line, "effects status '%s' not in status registry" % eff["status"])


def targeting_shape(t):
    if isinstance(t, dict):
        return t.get("shape")
    return t


def validate_monster(rep, path, ln, data):
    idn = parse_id_num(data.get("id"))
    tier = data.get("tier")
    if tier is not None:
        enum_check(rep, path, ln, "tier", tier, "monster_tier")
    if data.get("element") is not None:
        enum_check(rep, path, ln, "element", data["element"], "element")
    for f in ("weak_to", "resists", "immune_to"):
        for e in data.get(f) or []:
            if e not in REGISTRY["element"]:
                rep.fail(3, path, ln, "%s: '%s' not an element" % (f, e))
    if data.get("size_class") is not None:
        enum_check(rep, path, ln, "size_class", data["size_class"], "size_class")
    if data.get("ai_profile") is not None:
        enum_check(rep, path, ln, "ai_profile", data["ai_profile"], "ai_profile")
    stats = data.get("stats")
    if isinstance(stats, dict):
        for s in MONSTER_STATS_REQ:
            if s not in stats:
                rep.fail(3, path, ln, "stats missing required '%s'" % s)
    elif "stats" in data:
        rep.fail(3, path, ln, "stats must be a map")
    # abilities gating (elite/boss iff present)
    ab = data.get("abilities")
    if tier in ("elite", "boss"):
        if not ab:
            rep.fail(3, path, ln, "tier %s requires >=1 abilities row" % tier)
    elif ab:
        rep.fail(3, path, ln, "abilities forbidden on tier normal")
    for a in ab or []:
        if isinstance(a, dict):
            t = targeting_shape(a.get("targeting"))
            if t is not None and t not in REGISTRY["targeting"]:
                rep.fail(3, path, ln, "abilities targeting '%s' not a shape token" % t)
            check_effects(rep, path, ln, a.get("effects"), "op")
    # phases iff boss_scripted
    if data.get("phases") and data.get("ai_profile") != "boss_scripted":
        rep.fail(3, path, ln, "phases present but ai_profile is not boss_scripted")
    for ph in data.get("phases") or []:
        if isinstance(ph, dict) and ph.get("base_profile"):
            enum_check(rep, path, ln, "phases.base_profile", ph["base_profile"], "ai_profile")
    # §4 tier <-> ID slot
    if idn is not None and tier is not None:
        expect = mob_tier(idn)
        if expect and expect != tier:
            rep.fail(4, path, ln, "mob_%03d is a %s slot but tier=%s" % (idn, expect, tier))
    # §6 asset contract
    states = data.get("animation_states") or []
    if isinstance(states, list):
        for st in states:
            if st not in REGISTRY["animation_state"]:
                rep.fail(6, path, ln, "animation_states: '%s' not an ANIMATION_STATES token" % st)
        if tier in ("elite", "boss") and "telegraph" not in states:
            rep.fail(6, path, ln, "elite/boss must declare 'telegraph' animation state")
    # §6 animation_notes keys ⊆ animation_states (monster.schema rule 11)
    notes = data.get("animation_notes")
    if notes is not None and not isinstance(notes, dict):
        rep.fail(6, path, ln, "animation_notes must be a map of state -> description")
    for k, v in (notes or {}).items():
        if k not in (states or []):
            rep.fail(6, path, ln,
                     "animation_notes key '%s' not in this file's animation_states" % k)
        if not isinstance(v, str) or not v.strip():
            rep.fail(6, path, ln, "animation_notes['%s'] must be a non-empty string" % k)


def validate_map(rep, path, ln, data):
    if data.get("region") is not None:
        enum_check(rep, path, ln, "region", data["region"], "region")
        n = parse_id_num(data.get("id"))
        if n is not None:
            blocks = [b for b in MAP_BLOCKS + MAP_EXT_BLOCKS if b[0] == data["region"]]
            if blocks and not any(lo <= n <= hi for _, lo, hi in blocks):
                rep.fail(4, path, ln, "map_%03d not in region %s block(s) %s"
                         % (n, data["region"],
                            ", ".join("[%d,%d]" % (lo, hi) for _, lo, hi in blocks)))
    if data.get("map_type") is not None:
        enum_check(rep, path, ln, "map_type", data["map_type"], "map_type")
    if data.get("layers_preset") is not None:
        enum_check(rep, path, ln, "layers_preset", data["layers_preset"], "layers_preset")
    for p in data.get("portals") or []:
        if isinstance(p, dict) and p.get("kind") is not None:
            enum_check(rep, path, ln, "portals.kind", p["kind"], "portal_kind")
    for it in data.get("interactables") or []:
        if isinstance(it, dict) and it.get("type") is not None:
            if it["type"] not in REGISTRY["interactable_type"]:
                rep.fail(3, path, ln, "interactables type '%s' invalid (portal/loot_drop excluded)" % it["type"])
    ac = data.get("arena_config")
    if data.get("map_type") == "arena" and not ac:
        rep.fail(3, path, ln, "map_type arena requires arena_config")
    if data.get("map_type") != "arena" and ac:
        rep.fail(3, path, ln, "arena_config forbidden on non-arena map")
    if isinstance(ac, dict):
        for hz in ac.get("hazards") or []:
            if isinstance(hz, dict) and hz.get("tier") is not None:
                enum_check(rep, path, ln, "hazards.tier", hz["tier"], "hazard_tier")


def validate_item(rep, path, ln, data):
    stem = os.path.basename(path).rsplit(".", 1)[0]
    rows = data.get("items")
    if not isinstance(rows, list):
        rep.fail(3, path, ln, "items must be a list")
        return
    for row in rows:
        if not isinstance(row, dict):
            continue
        cat = row.get("category")
        rid = row.get("id", "?")
        if cat is not None:
            enum_check(rep, path, ln, "items[%s].category" % rid, cat, "category")
        if row.get("rarity") is not None:
            enum_check(rep, path, ln, "items[%s].rarity" % rid, row["rarity"], "rarity")
        if row.get("slot") is not None:
            enum_check(rep, path, ln, "items[%s].slot" % rid, row["slot"], "slot")
        if row.get("weapon_type") is not None:
            enum_check(rep, path, ln, "items[%s].weapon_type" % rid, row["weapon_type"], "weapon_type")
        if row.get("line_hint") is not None:
            if row["line_hint"] not in REGISTRY["weapon_line"]:
                rep.fail(3, path, ln, "items[%s].line_hint '%s' not a job line" % (rid, row["line_hint"]))
        t = row.get("tier")
        if cat == "equip" and not (isinstance(t, int) and 1 <= t <= 12):
            # T1-T12 per ITEMS.md v3 §4 (arc 1 T1-T6, arc 2 T7-T12)
            rep.fail(3, path, ln, "items[%s].tier must be int 1-12" % rid)
        # required-by-category
        if cat == "equip":
            for f in ("slot", "tier", "stats", "enhance_max"):
                if f not in row:
                    rep.fail(3, path, ln, "equip row %s missing '%s'" % (rid, f))
        elif cat == "use":
            for f in ("effects", "use_cooldown", "stack"):
                if f not in row:
                    rep.fail(3, path, ln, "use row %s missing '%s'" % (rid, f))
            check_effects(rep, path, ln, row.get("effects"), "use_op")
        elif cat == "etc":
            for f in ("source_hint", "stack"):
                if f not in row:
                    rep.fail(3, path, ln, "etc row %s missing '%s'" % (rid, f))
        for f in ("id", "name", "rarity", "req_level", "price"):
            if f not in row:
                rep.fail(3, path, ln, "item row %s missing '%s'" % (rid, f))
        # §4 row id range/prefix
        check_id(rep, path, ln, row.get("id"))


def validate_skill(rep, path, ln, data):
    if data.get("line") is not None:
        if data["line"] not in REGISTRY["skill_line"]:
            rep.fail(3, path, ln, "line '%s' not a job line" % data["line"])
    if data.get("tier") is not None:
        enum_check(rep, path, ln, "tier", data["tier"], "skill_tier")
    if data.get("kind") is not None:
        enum_check(rep, path, ln, "kind", data["kind"], "skill_kind")
    t = targeting_shape(data.get("targeting"))
    if t is not None and t not in REGISTRY["targeting"]:
        rep.fail(3, path, ln, "targeting '%s' not a shape token" % t)
    if data.get("kind") == "active" and not data.get("animation"):
        rep.fail(6, path, ln, "active skill requires an animation id")
    for row in data.get("level_data") or []:
        if isinstance(row, dict):
            check_effects(rep, path, ln, row.get("effects"), "op")


def validate_npc(rep, path, ln, data):
    if data.get("region") is not None:
        enum_check(rep, path, ln, "region", data["region"], "region")
    if data.get("role") is not None:
        enum_check(rep, path, ln, "role", data["role"], "role")
    for s in data.get("services") or []:
        if s not in REGISTRY["service"]:
            rep.fail(3, path, ln, "services: '%s' not a service token" % s)
    dlg = data.get("dialog")
    if isinstance(dlg, dict) and "greeting" not in dlg:
        rep.fail(3, path, ln, "dialog missing required 'greeting'")


def validate_quest(rep, path, ln, data):
    if data.get("region") is not None:
        enum_check(rep, path, ln, "region", data["region"], "region")
    if data.get("quest_type") is not None:
        enum_check(rep, path, ln, "quest_type", data["quest_type"], "quest_type")
    for st in data.get("steps") or []:
        if isinstance(st, dict) and st.get("type") is not None:
            if st["type"] not in REGISTRY["step_type"]:
                rep.fail(3, path, ln, "steps type '%s' invalid" % st["type"])
    rw = data.get("rewards")
    if isinstance(rw, dict):
        if "shards" not in rw:
            rep.fail(3, path, ln, "rewards missing 'shards'")


def validate_drop_table(rep, path, ln, data):
    if "pools" in data:  # pools.yaml shape
        pools = data.get("pools")
        if data.get("id") != "drop_pools":
            rep.fail(3, path, ln, "pools file id must be 'drop_pools'")
        for pool in pools or []:
            if isinstance(pool, dict) and pool.get("region") is not None:
                enum_check(rep, path, ln, "pools.region", pool["region"], "region")
        return
    # drop_mob shape
    for f in ("owner", "rows"):
        if f not in data:
            rep.fail(3, path, ln, "drop table missing '%s'" % f)
    for row in data.get("rows") or []:
        if not isinstance(row, dict):
            continue
        ch = row.get("chance")
        if isinstance(ch, str):
            if ch not in REGISTRY["chance"]:
                rep.fail(3, path, ln, "rows chance '%s' not a bucket token" % ch)
        elif isinstance(ch, (int, float)):
            if not (0 <= ch <= 1):
                rep.fail(3, path, ln, "rows chance float %s out of [0,1]" % ch)
        rs = row.get("rarity_source")
        ispool = isinstance(row.get("ref"), str) and row["ref"].startswith("pool_equip_")
        if rs is not None:
            if rs not in REGISTRY["rarity_source"]:
                rep.fail(3, path, ln, "rows rarity_source '%s' invalid" % rs)
            if not ispool:
                rep.fail(3, path, ln, "rarity_source only allowed on pool-ref rows")
        elif ispool:
            rep.fail(3, path, ln, "pool-ref row missing rarity_source")


VALIDATORS = {
    "monster": validate_monster, "map": validate_map, "item": validate_item,
    "skill": validate_skill, "npc": validate_npc, "quest": validate_quest,
    "drop_table": validate_drop_table,
}


# ---------------------------------------------------------------------------
# §4 ID format / range.
# ---------------------------------------------------------------------------
def parse_id_num(idv):
    if not isinstance(idv, str):
        return None
    m = re.search(r"(\d+)$", idv)
    return int(m.group(1)) if m else None


def id_category(idv):
    if not isinstance(idv, str):
        return None
    for pref in ("drop_mob", "item_equip", "item_use", "item_etc", "pool_equip",
                 "map", "mob", "npc", "quest", "skill"):
        if idv.startswith(pref + "_") or (pref == "pool_equip" and idv.startswith("pool_equip_r")):
            return pref
    return None


def check_id(rep, path, ln, idv):
    if not isinstance(idv, str):
        return
    cat = id_category(idv)
    if cat is None:
        return
    lo, hi, width = ID_RANGES[cat]
    num = parse_id_num(idv)
    if num is None:
        rep.fail(4, path, ln, "id '%s' has no numeric suffix" % idv)
        return
    # width check
    suffix = re.search(r"(\d+)$", idv).group(1)
    if len(suffix) != width:
        rep.fail(4, path, ln, "id '%s' should be zero-padded to %d digits" % (idv, width))
    if not (lo <= num <= hi):
        rep.fail(4, path, ln, "id '%s' number %d out of range [%d,%d]" % (idv, num, lo, hi))


# ---------------------------------------------------------------------------
# §5 world-graph.
# ---------------------------------------------------------------------------
def check_world_graph(rep, maps, entry, scope, allow_missing=False):
    # maps: {map_id: (path, data)}
    def in_scope(mid):
        if scope is None:
            return True
        n = parse_id_num(mid)
        return n is not None and scope[0] <= n <= scope[1]

    present = {m: v for m, v in maps.items() if in_scope(m)}
    if not present:
        return
    spawns = {}  # map_id -> set of spawn ids
    for mid, (path, data) in present.items():
        sp = set()
        for s in data.get("spawn_points") or []:
            if isinstance(s, dict) and s.get("id") is not None:
                sp.add(s["id"])
        spawns[mid] = sp
    # portal target checks
    for mid, (path, data) in present.items():
        ln = find_line(open(path, encoding="utf-8").read().split("\n"), "id")
        for p in data.get("portals") or []:
            if not isinstance(p, dict):
                continue
            tm = p.get("target_map")
            ts = p.get("target_spawn")
            if tm and tm not in maps:
                if allow_missing:
                    rep.warn(5, rel(path), ln,
                             "portal '%s' targets not-yet-authored map %s (allow-missing)"
                             % (p.get("id"), tm))
                else:
                    rep.fail(5, rel(path), ln,
                             "portal '%s' targets missing map %s" % (p.get("id"), tm))
            elif tm and ts is not None:
                if tm in spawns and ts not in spawns[tm]:
                    rep.fail(5, rel(path), ln, "portal '%s' targets missing spawn '%s' on %s"
                             % (p.get("id"), ts, tm))
    # reachability from entry
    if entry not in present:
        rep.warn(5, "world-graph", 0, "entry %s not in checked map set; reachability skipped" % entry)
        return
    adj = {mid: [] for mid in present}
    for mid, (path, data) in present.items():
        for p in data.get("portals") or []:
            if isinstance(p, dict) and p.get("target_map") in present:
                adj[mid].append(p["target_map"])
    seen, stack = set(), [entry]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(adj.get(cur, []))
    for mid in present:
        if mid not in seen:
            rep.fail(5, rel(present[mid][0]), 0, "map %s unreachable from %s" % (mid, entry))


# ---------------------------------------------------------------------------
# File discovery.
# ---------------------------------------------------------------------------
def iter_files(paths, exts=None):
    for p in paths:
        if os.path.isfile(p):
            yield p
        elif os.path.isdir(p):
            for root, _, names in os.walk(p):
                if os.sep + ".git" in root:
                    continue
                for n in sorted(names):
                    if exts is None or n.rsplit(".", 1)[-1] in exts:
                        yield os.path.join(root, n)


def main(argv):
    scope = None
    entry = "map_001"
    allow_missing = False
    paths = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--scope":
            i += 1
            m = re.match(r"(\d+)-(\d+)$", argv[i])
            if not m:
                print("bad --scope (use A-B)")
                return 2
            scope = (int(m.group(1)), int(m.group(2)))
        elif a == "--entry":
            i += 1
            entry = argv[i]
        elif a == "--allow-missing":
            allow_missing = True
        elif a.startswith("--"):
            print("unknown flag %s" % a)
            return 2
        else:
            paths.append(a)
        i += 1

    if not paths:
        scan_paths = [os.path.join(REPO, "docs"),
                      os.path.join(REPO, "CLAUDE.md"),
                      os.path.join(REPO, "README.md")]
    else:
        scan_paths = [p if os.path.isabs(p) else os.path.join(os.getcwd(), p) for p in paths]

    rep = Report()

    # §1 over all text files in scan set.
    scan_banned(rep, list(iter_files(scan_paths)))

    # Content files: yaml with a resolvable known schema front-matter key.
    content = []  # (path, data, raw_lines)
    for f in iter_files(scan_paths, exts={"yaml", "yml"}):
        try:
            with open(f, "r", encoding="utf-8") as fh:
                text = fh.read()
            data = load_yaml(text)
        except Exception as e:
            continue
        if not isinstance(data, dict):
            continue
        sch = data.get("schema")
        if sch not in SCHEMA_BY_PATH:
            continue
        content.append((f, data, text.split("\n")))

    # Build defined-ID universe (§2/§4).
    defined = {}  # id -> path (first)
    for path, data, _ in content:
        kind = SCHEMA_BY_PATH[data["schema"]]
        ids = []
        if kind == "item":
            for row in data.get("items") or []:
                if isinstance(row, dict) and isinstance(row.get("id"), str):
                    ids.append(row["id"])
        elif kind == "drop_table" and "pools" in data:
            for pool in data.get("pools") or []:
                if isinstance(pool, dict) and isinstance(pool.get("id"), str):
                    ids.append(pool["id"])
        else:
            if isinstance(data.get("id"), str):
                ids.append(data["id"])
        for idv in ids:
            if idv in defined:
                rep.fail(4, rel(path), 0, "duplicate id '%s' (also in %s)" % (idv, rel(defined[idv])))
            else:
                defined[idv] = path

    # Per-file §3/§4/§6 validation.
    maps = {}
    for path, data, raw in content:
        kind = SCHEMA_BY_PATH[data["schema"]]
        rln = find_line(raw, "id") or 1
        rp = rel(path)
        # §3 front-matter + schema resolution
        sch = data["schema"]
        if not os.path.exists(os.path.join(REPO, "docs", sch)):
            rep.fail(3, rp, find_line(raw, "schema") or rln, "schema '%s' does not resolve" % sch)
        if "references" not in data:
            rep.fail(3, rp, rln, "missing front-matter 'references'")
        # §3 required fields
        for f in REQUIRED[kind]:
            if f not in data:
                rep.fail(3, rp, rln, "missing required field '%s'" % f)
        if kind == "drop_table" and "pools" not in data and "owner" not in data:
            rep.fail(3, rp, rln, "drop table must carry 'owner'+'rows' or 'pools'")
        # §3 unknown top-level fields
        for k in data:
            if k not in ALLOWED[kind]:
                rep.fail(3, rp, rln, "unknown top-level field '%s'" % k)
        # §4 id format/range (row ids handled inside item validator)
        if kind != "item":
            check_id(rep, rp, rln, data.get("id"))
        # schema-specific
        VALIDATORS[kind](rep, rp, rln, data)
        if kind == "map" and isinstance(data.get("id"), str):
            maps[data["id"]] = (path, data)

    # §2 referential integrity.
    for path, data, raw in content:
        rp = rel(path)
        rln = find_line(raw, "id") or 1
        refs = set()
        # walk everything except the doc-name 'references' list and 'schema'.
        scan = {k: v for k, v in data.items() if k not in ("references", "schema")}
        for s in walk_strings(scan):
            for m in REF_RE.finditer(s):
                refs.add(m.group(1))
        for r in sorted(refs):
            if r not in defined:
                if allow_missing:
                    rep.warn(2, rp, rln, "reference '%s' unresolved (allow-missing)" % r)
                else:
                    rep.fail(2, rp, rln, "reference '%s' does not resolve to a content file" % r)

    # §5 world-graph.
    if maps:
        check_world_graph(rep, maps, entry, scope, allow_missing)

    rep.render()
    return 1 if rep.has_fail() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
