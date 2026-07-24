#!/usr/bin/env python3
"""Rebillion wiki generator — a hiddenstreet-style static reference site.

Reads every YAML file under docs/50_content/ and emits a cross-linked static
HTML wiki: one page per monster / map / NPC / quest, index pages per kind and
per region, an item catalog, and per-line skill pages. Everything is derived
from the minted content files — this tool asserts nothing of its own (CLAUDE.md
law 2); if a fact is wrong in the wiki, fix the content file, not this script.

Python 3 stdlib only; PyYAML is used when importable, otherwise the tolerant
reader in tools/validate.py handles the block+flow subset our content uses.

Usage:
    python3 tools/wiki_gen.py [--out DIR]     # default DIR = <repo>/wiki

Exit 0 on success. The output directory is disposable build output (gitignored);
regenerate at will.
"""
import argparse
import os
import shutil
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import load_yaml  # PyYAML if present, tolerant fallback otherwise

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = os.path.join(REPO, "docs", "50_content")
# Sprite frames exported per the ART_BIBLE export_contract frame naming —
# "{entity_id}_{state}_{NN}.png" — dropped anywhere under assets/sprites/ are
# auto-embedded (monster portrait = idle frame 00; one preview frame per state).
SPRITES = os.path.join(REPO, "assets", "sprites")

# Region display order + names come from the minted map files themselves (each
# map carries `region`); this list only fixes presentation order per WORLD_PLAN.
REGION_ORDER = ["emberfoot", "millbrook", "verdant", "tidewatch", "gloomwood",
                "ashfall", "sunken", "clockwork", "frostpeak", "arcane_reach",
                "voidshore"]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_dir(*parts):
    """Yield (filename, parsed_dict) for every .yaml in a content subdir."""
    d = os.path.join(CONTENT, *parts)
    if not os.path.isdir(d):
        return
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".yaml"):
            continue
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            data = load_yaml(f.read())
        if isinstance(data, dict):
            yield fn, data


def load_all():
    world = {
        "monsters": {}, "maps": {}, "npcs": {}, "quests": {},
        "drop_tables": {}, "pools": {}, "items": {}, "skills": {},
    }
    for _, m in load_dir("monsters"):
        world["monsters"][m["id"]] = m
    for _, m in load_dir("maps"):
        world["maps"][m["id"]] = m
    for _, n in load_dir("npcs"):
        world["npcs"][n["id"]] = n
    for _, q in load_dir("quests"):
        world["quests"][q["id"]] = q
    for _, t in load_dir("drop_tables"):
        if "pools" in t:
            for p in t.get("pools") or []:
                world["pools"][p.get("id")] = p
        else:
            world["drop_tables"][t["id"]] = t
    # item batch tables live at three depths; flatten to one id -> row index
    for sub in ("equip", "use", "etc"):
        for fn, tab in load_dir("items", sub):
            for row in tab.get("items") or []:
                row["_table"] = "%s/%s" % (sub, fn)
                world["items"][row["id"]] = row
    skills_root = os.path.join(CONTENT, "skills")
    if os.path.isdir(skills_root):
        for line in sorted(os.listdir(skills_root)):
            for _, s in load_dir("skills", line):
                s["_line_dir"] = line
                world["skills"][s["id"]] = s
    return world


# ---------------------------------------------------------------------------
# Cross-link indexes
# ---------------------------------------------------------------------------
def find_sprites():
    """Index every exported sprite frame: '{entity_id}_{state}_{NN}' -> path."""
    idx = {}
    for root, _, files in os.walk(SPRITES):
        for f in sorted(files):
            if f.endswith(".png"):
                idx[f[:-4]] = os.path.join(root, f)
    return idx


def png_width(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">I", head[16:20])[0]


def sprite_img(ix, out, key, cls="", scale=3):
    """Copy a sprite frame into the wiki and return an <img> tag ('' if absent)."""
    path = ix["sprites"].get(key)
    if not path:
        return ""
    dst_dir = os.path.join(out, "sprites")
    os.makedirs(dst_dir, exist_ok=True)
    shutil.copyfile(path, os.path.join(dst_dir, os.path.basename(path)))
    w = png_width(path)
    wattr = ' width="%d"' % (w * scale) if w else ""
    return '<img class="sprite %s" src="../sprites/%s" alt="%s"%s>' % (
        cls, os.path.basename(path), esc(key), wattr)


def build_indexes(w):
    ix = {"mob_maps": {}, "npc_maps": {}, "mob_quests": {}, "npc_quests": {},
          "item_sources": {}, "map_region": {}, "mob_region": {},
          "sprites": find_sprites()}
    for mid, mp in w["maps"].items():
        ix["map_region"][mid] = mp.get("region", "")
        for zone in mp.get("spawn_zones") or []:
            for row in zone.get("mobs") or []:
                mob = row.get("mob")
                if mob:
                    ix["mob_maps"].setdefault(mob, []).append((mid, row.get("count")))
        ac = mp.get("arena_config") or {}
        if ac.get("boss_mob_id"):
            ix["mob_maps"].setdefault(ac["boss_mob_id"], []).append((mid, "boss arena"))
        for npc in mp.get("npcs") or []:
            ix["npc_maps"].setdefault(npc, []).append(mid)
    for mob, entries in ix["mob_maps"].items():
        regions = [ix["map_region"].get(mid, "") for mid, _ in entries]
        if regions:
            ix["mob_region"][mob] = max(set(regions), key=regions.count)
    for qid, q in w["quests"].items():
        for step in q.get("steps") or []:
            tgt = step.get("target", "")
            if isinstance(tgt, str) and tgt.startswith("mob_"):
                ix["mob_quests"].setdefault(tgt, []).append(qid)
            if isinstance(tgt, str) and tgt.startswith("npc_"):
                ix["npc_quests"].setdefault(tgt, []).append(qid)
    for tid, tab in w["drop_tables"].items():
        owner = tab.get("owner", "")
        for row in tab.get("rows") or []:
            ref = row.get("ref", "")
            if isinstance(ref, str) and ref.startswith("item_"):
                ix["item_sources"].setdefault(ref, []).append(owner)
    return ix


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
CSS = """
:root { --bg:#f6f3ea; --panel:#fffdf6; --ink:#241726; --line:#d8cfc0;
        --accent:#8f2d1b; --dim:#6b6270; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#1d1620; --panel:#241726; --ink:#e8e2d8; --line:#3a2b40;
          --accent:#eb7a2c; --dim:#9a92a0; } }
* { box-sizing:border-box; }
body { margin:0; font:15px/1.5 Georgia,'Times New Roman',serif;
       background:var(--bg); color:var(--ink); }
nav { background:var(--panel); border-bottom:2px solid var(--accent);
      padding:.5em 1em; }
nav a { margin-right:1em; color:var(--accent); text-decoration:none;
        font-weight:bold; }
main { max-width:900px; margin:0 auto; padding:1em; }
h1 { border-bottom:2px solid var(--accent); padding-bottom:.2em; }
h1 small, h2 small { color:var(--dim); font-size:.55em; font-weight:normal; }
table { border-collapse:collapse; width:100%; margin:.6em 0 1.2em;
        background:var(--panel); }
th, td { border:1px solid var(--line); padding:.3em .6em; text-align:left;
         vertical-align:top; }
th { background:var(--bg); }
a { color:var(--accent); }
.tag { display:inline-block; border:1px solid var(--line); border-radius:.6em;
       padding:0 .55em; font-size:.85em; background:var(--panel);
       margin-right:.3em; }
.flavor { font-style:italic; color:var(--dim); border-left:3px solid
          var(--accent); padding-left:.8em; margin:1em 0; }
.wrap { overflow-x:auto; }
img.sprite { image-rendering:pixelated; height:auto; }
img.portrait { float:right; margin:0 0 .5em 1em; }
footer { color:var(--dim); font-size:.8em; text-align:center; padding:1em; }
"""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def page(out_path, title, body, depth):
    root = "../" * depth
    nav = "".join('<a href="%s%s">%s</a>' % (root, href, label) for href, label in [
        ("index.html", "Home"), ("monsters/index.html", "Monsters"),
        ("maps/index.html", "Maps"), ("npcs/index.html", "NPCs"),
        ("quests/index.html", "Quests"), ("items/index.html", "Items"),
        ("skills/index.html", "Skills")])
    html = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>%s — Rebillion Wiki</title><style>%s</style></head><body>"
            "<nav>%s</nav><main>%s</main>"
            "<footer>Generated by tools/wiki_gen.py from docs/50_content — "
            "do not edit by hand.</footer></body></html>"
            % (esc(title), CSS, nav, body))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


def link(kind, eid, label, depth):
    return '<a href="%s%s/%s.html">%s</a>' % ("../" * depth, kind, eid, esc(label))


def item_ref(w, ref, depth):
    """Render a drop-row / shop ref: item link, pool link, or plain token."""
    if ref in w["items"]:
        return '<a href="%sitems/index.html#%s">%s</a>' % (
            "../" * depth, ref, esc(w["items"][ref].get("name", ref)))
    if ref in w["pools"]:
        return '<a href="%sitems/index.html#%s">%s</a>' % ("../" * depth, ref, esc(ref))
    return esc(ref)


def label(token):
    """'aoe_circle' -> 'Aoe Circle'; used for statuses/stats/tokens in prose."""
    return str(token).replace("_", " ").title()


def pct(x):
    try:
        return "%d%%" % round(float(x) * 100)
    except (TypeError, ValueError):
        return esc(x)


def fmt_targeting(t):
    """Render a targeting token/map as player-readable prose (SKILL_SYSTEM §6).
    Tile figures convert at the locked 16 px grid."""
    if not isinstance(t, dict):
        names = {"melee_arc": "Melee arc", "line": "Straight line",
                 "projectile": "Projectile", "aoe_circle": "Area circle",
                 "self": "Self", "party": "Whole party"}
        return esc(names.get(t, label(t)))
    shape = t.get("shape")
    if shape == "melee_arc":
        return esc("Melee arc — %s° swing, %s-tile reach"
                   % (t.get("arc_degrees", 120), t.get("radius", "?")))
    if shape == "line":
        return esc("Straight line ahead — %s tiles long × %s tall"
                   % (t.get("length", "?"), t.get("width", "?")))
    if shape == "projectile":
        bits = []
        if t.get("range") is not None:
            bits.append("%s-tile range" % t["range"])
        if t.get("speed") is not None:
            bits.append("%s tiles/s" % t["speed"])
        if t.get("gravity"):
            bits.append("arcing")
        if t.get("impact_radius"):
            bits.append("bursts in a %s-tile circle on impact" % t["impact_radius"])
        return esc("Projectile" + (" — " + ", ".join(bits) if bits else ""))
    if shape == "aoe_circle":
        origin = {"self": "around itself", "reticle": "at a targeted spot",
                  "impact": "on impact"}.get(t.get("origin"), "")
        return esc(("%s-tile circle %s" % (t.get("radius", "?"), origin)).strip())
    if shape == "self":
        return "Self"
    if shape == "party":
        return esc("Whole party within %s tiles" % t.get("radius", 8))
    return esc(t)


def fmt_effect(e):
    """One effect op -> one player-readable sentence (SKILL_EFFECTS ops)."""
    if not isinstance(e, dict):
        return esc(e)
    op = e.get("op")
    chance = "" if e.get("chance") in (None, 1, 1.0) \
        else "%s chance to " % pct(e["chance"])
    if op == "deal_damage":
        elem = e.get("element", "neutral")
        mult = e.get("mult")
        return esc("Deals %s damage%s" % (elem, " (×%s)" % mult if mult else ""))
    if op == "apply_status":
        dur = " for %s s" % e["dur"] if e.get("dur") is not None else ""
        stacks = " (%s stacks)" % e["stacks"] if e.get("stacks") else ""
        verb = "inflict" if chance else "Inflicts"
        return esc("%s%s %s%s%s" % (chance, verb, label(e.get("status")),
                                    dur, stacks))
    if op == "cleanse_status":
        return esc("Cleanses %s" % label(e.get("status", e.get("tag", "effects"))))
    if op == "heal":
        return esc("Restores life" + (" (×%s)" % e["mult"] if e.get("mult") else ""))
    if op == "restore_essence":
        return "Restores essence"
    if op == "grant_shield":
        dur = " for %s s" % e["dur"] if e.get("dur") is not None else ""
        return esc("Grants a shield%s" % dur)
    if op == "knockback":
        return esc("Knocks the target back %s tiles" % e.get("distance", "?"))
    if op == "pull":
        return esc("Pulls the target %s tiles closer" % e.get("distance", "?"))
    if op in ("dash", "leap"):
        return esc("%s %s tiles" % (label(op), e.get("distance", "?")))
    if op == "taunt":
        return "Forces enemies to attack the caster"
    if op == "summon_entity":
        n = e.get("count", 1)
        who = e.get("entity", e.get("template", "minions"))
        return esc("Summons %s× %s" % (n, label(who)))
    if op == "passive_stat_bonus":
        return esc("Passive: +%s %s" % (e.get("amount", "?"),
                                        label(e.get("stat", "?"))))
    if op == "on_hit_proc":
        return esc("%s an on-hit effect"
                   % ("%strigger" % chance if chance else "Triggers"))
    bits = ", ".join("%s %s" % (k, v) for k, v in e.items() if k != "op")
    return esc("%s (%s)" % (label(op), bits))


def fmt_effects(effects):
    return "<br>".join(fmt_effect(e) for e in effects or [])


def fmt_cost(c):
    if isinstance(c, dict):
        return esc(" + ".join("%s %s" % (v, k) for k, v in c.items()))
    return esc(c)


def tags(vals):
    return "".join('<span class="tag">%s</span>' % esc(v) for v in vals or [])


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def monster_page(w, ix, mob, out):
    m = w["monsters"][mob]
    s = m.get("stats") or {}
    rows = [("Level", m.get("level")), ("Tier", m.get("tier")),
            ("Element", m.get("element")), ("Size", m.get("size_class")),
            ("HP (life)", s.get("life")), ("EXP", s.get("exp")),
            ("Power", s.get("power")), ("Spellpower", s.get("spellpower")),
            ("Armor", s.get("armor")), ("Warding", s.get("warding")),
            ("Precision", s.get("precision")),
            ("Dodge (evasion %)", s.get("evasion")),
            ("AI profile", m.get("ai_profile"))]
    body = ["<h1>%s <small>%s</small></h1>" % (esc(m.get("name", mob)), mob)]
    portrait = sprite_img(ix, out, "%s_idle_00" % mob, cls="portrait", scale=3)
    if portrait:
        body.append(portrait)
    if m.get("flavor"):
        body.append('<div class="flavor">%s</div>' % esc(m["flavor"]))
    body.append("<h2>Stats</h2><div class='wrap'><table>")
    for k, v in rows:
        if v is not None:
            body.append("<tr><th>%s</th><td>%s</td></tr>" % (esc(k), esc(v)))
    if m.get("weak_to"):
        body.append("<tr><th>Weak to (&times;1.5)</th><td>%s</td></tr>" % tags(m["weak_to"]))
    if m.get("resists"):
        body.append("<tr><th>Resists (&times;0.5)</th><td>%s</td></tr>" % tags(m["resists"]))
    if m.get("immune_to"):
        body.append("<tr><th>Immune to</th><td>%s</td></tr>" % tags(m["immune_to"]))
    body.append("</table></div>")

    if m.get("abilities"):
        body.append("<h2>Abilities</h2><div class='wrap'><table>"
                    "<tr><th>Ability</th><th>Hits</th><th>Cooldown</th>"
                    "<th>Wind-up</th><th>Effects</th></tr>")
        for a in m["abilities"]:
            body.append("<tr><td><b>%s</b>%s</td><td>%s</td><td>%s s</td>"
                        "<td>%s s</td><td>%s</td></tr>" % (
                            esc(a.get("name", a.get("id", "?"))),
                            "<br><i>%s</i>" % esc(a["animation_note"])
                            if a.get("animation_note") else "",
                            fmt_targeting(a.get("targeting")), esc(a.get("cooldown")),
                            esc(a.get("telegraph_s")), fmt_effects(a.get("effects"))))
        body.append("</table></div>")

    if m.get("phases"):
        body.append("<h2>Boss phases</h2><div class='wrap'><table>"
                    "<tr><th>Phase</th><th>At life %</th><th>Behavior</th>"
                    "<th>Adds abilities</th></tr>")
        for p in m["phases"]:
            body.append("<tr><td>%s</td><td>%s%%</td><td>%s</td><td>%s</td></tr>" % (
                esc(p.get("phase_id")), esc(p.get("life_threshold_pct")),
                esc(p.get("base_profile", "(inherits)")),
                esc(", ".join(p.get("added_abilities") or []) or "—")))
        body.append("</table></div>")

    body.append("<h2>Animations</h2>")
    notes = m.get("animation_notes") or {}
    has_frames = any(ix["sprites"].get("%s_%s_00" % (mob, st))
                     for st in m.get("animation_states") or [])
    body.append("<div class='wrap'><table><tr><th>State</th>%s<th>Description</th></tr>"
                % ("<th>Frame</th>" if has_frames else ""))
    for st in m.get("animation_states") or []:
        frame = ("<td>%s</td>" % (sprite_img(ix, out, "%s_%s_00" % (mob, st), scale=2)
                                  or "—")) if has_frames else ""
        body.append("<tr><td><code>%s</code></td>%s<td>%s</td></tr>"
                    % (esc(st), frame, esc(notes.get(st, "—"))))
    body.append("</table></div>")

    tab = w["drop_tables"].get(m.get("drop_table", ""), {})
    if tab.get("rows"):
        body.append("<h2>Drops</h2><div class='wrap'><table>"
                    "<tr><th>Drop</th><th>Chance</th><th>Qty</th></tr>")
        for r in tab["rows"]:
            extra = " <span class='tag'>first clear</span>" if r.get("first_clear_guaranteed") else ""
            body.append("<tr><td>%s%s</td><td>%s</td><td>%s–%s</td></tr>" % (
                item_ref(w, r.get("ref", "?"), 1), extra, esc(r.get("chance")),
                esc(r.get("qty_min")), esc(r.get("qty_max"))))
        body.append("</table></div>")

    locs = ix["mob_maps"].get(mob) or []
    if locs:
        body.append("<h2>Found in</h2><ul>")
        for mid, count in locs:
            mp = w["maps"].get(mid, {})
            body.append("<li>%s <small>(%s)</small></li>" % (
                link("maps", mid, mp.get("name", mid), 1), esc(count)))
        body.append("</ul>")
    if ix["mob_quests"].get(mob):
        body.append("<h2>Quest target of</h2><ul>%s</ul>" % "".join(
            "<li>%s</li>" % link("quests", q, w["quests"][q].get("name", q), 1)
            for q in ix["mob_quests"][mob]))
    page(os.path.join(out, "monsters", mob + ".html"),
         m.get("name", mob), "".join(body), 1)


def map_page(w, ix, mid, out):
    m = w["maps"][mid]
    lb = m.get("level_band") or {}
    body = ["<h1>%s <small>%s</small></h1>" % (esc(m.get("name", mid)), mid)]
    if m.get("flavor"):
        body.append('<div class="flavor">%s</div>' % esc(m["flavor"]))
    body.append("<div class='wrap'><table>")
    for k, v in [("Region", m.get("region")), ("Type", m.get("map_type")),
                 ("Level band", "%s–%s" % (lb.get("min"), lb.get("max"))),
                 ("Biome / tileset", "%s / %s" % (m.get("biome"), m.get("tileset"))),
                 ("Size (tiles)", "%s × %s" % ((m.get("size_tiles") or {}).get("w"),
                                               (m.get("size_tiles") or {}).get("h"))),
                 ("BGM", m.get("bgm"))]:
        body.append("<tr><th>%s</th><td>%s</td></tr>" % (esc(k), esc(v)))
    body.append("</table></div>")

    if m.get("portals"):
        body.append("<h2>Portals</h2><div class='wrap'><table>"
                    "<tr><th>Portal</th><th>Kind</th><th>Leads to</th></tr>")
        for p in m["portals"]:
            tgt = p.get("target_map", "")
            tname = w["maps"].get(tgt, {}).get("name", tgt)
            body.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                esc(p.get("id")), esc(p.get("kind")),
                link("maps", tgt, tname, 1) if tgt in w["maps"] else esc(tgt)))
        body.append("</table></div>")

    zone_rows = []
    for z in m.get("spawn_zones") or []:
        for r in z.get("mobs") or []:
            zone_rows.append((z.get("id"), r.get("mob"), r.get("count")))
    ac = m.get("arena_config") or {}
    if ac.get("boss_mob_id"):
        zone_rows.append(("arena", ac["boss_mob_id"], "boss"))
    if zone_rows:
        body.append("<h2>Monsters here</h2><div class='wrap'><table>"
                    "<tr><th>Zone</th><th>Monster</th><th>Lv</th><th>Count</th></tr>")
        for zid, mob, count in zone_rows:
            mm = w["monsters"].get(mob, {})
            body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                esc(zid), link("monsters", mob, mm.get("name", mob), 1)
                if mob in w["monsters"] else esc(mob),
                esc(mm.get("level", "?")), esc(count)))
        body.append("</table></div>")

    if m.get("npcs"):
        body.append("<h2>NPCs</h2><ul>%s</ul>" % "".join(
            "<li>%s <small>(%s)</small></li>" % (
                link("npcs", n, w["npcs"].get(n, {}).get("name", n), 1),
                esc(w["npcs"].get(n, {}).get("role", "?")))
            for n in m["npcs"]))
    if m.get("interactables"):
        body.append("<h2>Interactables</h2><ul>%s</ul>" % "".join(
            "<li><code>%s</code> %s</li>" % (esc(i.get("type")), esc(i.get("id")))
            for i in m["interactables"]))
    if m.get("platform_brief"):
        body.append("<h2>Layout brief</h2><p>%s</p>" % esc(m["platform_brief"]))
    page(os.path.join(out, "maps", mid + ".html"), m.get("name", mid),
         "".join(body), 1)


def npc_page(w, ix, nid, out):
    n = w["npcs"][nid]
    body = ["<h1>%s <small>%s</small></h1>" % (esc(n.get("name", nid)), nid)]
    if n.get("flavor"):
        body.append('<div class="flavor">%s</div>' % esc(n["flavor"]))
    home = n.get("map", "")
    body.append("<div class='wrap'><table>")
    body.append("<tr><th>Role</th><td>%s</td></tr>" % esc(n.get("role")))
    body.append("<tr><th>Region</th><td>%s</td></tr>" % esc(n.get("region")))
    body.append("<tr><th>Location</th><td>%s</td></tr>" % (
        link("maps", home, w["maps"].get(home, {}).get("name", home), 1)
        if home in w["maps"] else esc(home)))
    if n.get("services"):
        body.append("<tr><th>Services</th><td>%s</td></tr>" % tags(n["services"]))
    body.append("</table></div>")
    shop = (n.get("shop") or {}).get("items") or []
    if shop:
        body.append("<h2>Shop</h2><ul>%s</ul>" % "".join(
            "<li>%s</li>" % item_ref(w, i, 1) for i in shop))
    dlg = n.get("dialog") or {}
    if dlg:
        body.append("<h2>Dialog</h2><div class='wrap'><table>%s</table></div>" % "".join(
            "<tr><th>%s</th><td>%s</td></tr>" % (esc(k), esc(v))
            for k, v in dlg.items()))
    if ix["npc_quests"].get(nid):
        body.append("<h2>Involved in quests</h2><ul>%s</ul>" % "".join(
            "<li>%s</li>" % link("quests", q, w["quests"][q].get("name", q), 1)
            for q in ix["npc_quests"][nid]))
    page(os.path.join(out, "npcs", nid + ".html"), n.get("name", nid),
         "".join(body), 1)


def quest_page(w, ix, qid, out):
    q = w["quests"][qid]
    body = ["<h1>%s <small>%s</small></h1>" % (esc(q.get("name", qid)), qid)]
    if q.get("flavor"):
        body.append('<div class="flavor">%s</div>' % esc(q["flavor"]))
    giver = q.get("giver_npc", "")
    body.append("<div class='wrap'><table>")
    for k, v in [("Region", esc(q.get("region"))), ("Type", esc(q.get("quest_type"))),
                 ("Giver", link("npcs", giver, w["npcs"].get(giver, {}).get("name", giver), 1)
                  if giver in w["npcs"] else esc(giver)),
                 ("Level requirement", esc(q.get("level_requirement"))),
                 ("Recommended level", esc(q.get("recommended_level")))]:
        body.append("<tr><th>%s</th><td>%s</td></tr>" % (k, v))
    body.append("</table></div>")
    body.append("<h2>Steps</h2><ol>")
    for s in q.get("steps") or []:
        tgt = s.get("target", "")
        if isinstance(tgt, str) and tgt.startswith("mob_") and tgt in w["monsters"]:
            tgt_html = link("monsters", tgt, w["monsters"][tgt].get("name", tgt), 1)
        elif isinstance(tgt, str) and tgt.startswith("npc_") and tgt in w["npcs"]:
            tgt_html = link("npcs", tgt, w["npcs"][tgt].get("name", tgt), 1)
        elif isinstance(tgt, str) and tgt.startswith("item_"):
            tgt_html = item_ref(w, tgt, 1)
        elif isinstance(tgt, str) and tgt.startswith("map_") and tgt in w["maps"]:
            tgt_html = link("maps", tgt, w["maps"][tgt].get("name", tgt), 1)
        else:
            tgt_html = esc(tgt)
        body.append("<li><b>%s</b> %s &times;%s</li>" % (
            esc(s.get("type")), tgt_html, esc(s.get("count", 1))))
    body.append("</ol>")
    rw = q.get("rewards") or {}
    body.append("<h2>Rewards</h2><ul>")
    if rw.get("exp") is not None:
        body.append("<li>EXP: %s</li>" % esc(rw["exp"]))
    if rw.get("shards") is not None:
        body.append("<li>Shards: %s</li>" % esc(rw["shards"]))
    for it in rw.get("items") or []:
        body.append("<li>%s &times;%s</li>" % (
            item_ref(w, it.get("id", "?"), 1), esc(it.get("qty", 1))))
    for sk in rw.get("skills") or []:
        body.append("<li>Skill: %s</li>" % esc(sk))
    body.append("</ul>")
    page(os.path.join(out, "quests", qid + ".html"), q.get("name", qid),
         "".join(body), 1)


# ---------------------------------------------------------------------------
# Index pages
# ---------------------------------------------------------------------------
def by_region(ids, region_of):
    groups = {}
    for i in ids:
        groups.setdefault(region_of(i) or "other", []).append(i)
    order = [r for r in REGION_ORDER if r in groups]
    order += sorted(r for r in groups if r not in REGION_ORDER)
    return [(r, groups[r]) for r in order]


def monsters_index(w, ix, out):
    body = ["<h1>Monsters <small>%d</small></h1>" % len(w["monsters"])]
    for region, ids in by_region(sorted(w["monsters"]),
                                 lambda m: ix["mob_region"].get(m)):
        body.append("<h2>%s</h2><div class='wrap'><table><tr><th>ID</th><th>Name</th>"
                    "<th>Lv</th><th>Tier</th><th>Element</th><th>HP</th>"
                    "<th>EXP</th><th>Dodge %%</th></tr>" % esc(region))
        for mob in sorted(ids, key=lambda x: w["monsters"][x].get("level", 0)):
            m = w["monsters"][mob]
            s = m.get("stats") or {}
            body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                        "<td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                            mob, link("monsters", mob, m.get("name", mob), 1),
                            esc(m.get("level")), esc(m.get("tier")),
                            esc(m.get("element")), esc(s.get("life")),
                            esc(s.get("exp")), esc(s.get("evasion"))))
        body.append("</table></div>")
    page(os.path.join(out, "monsters", "index.html"), "Monsters", "".join(body), 1)


def maps_index(w, out):
    body = ["<h1>Maps <small>%d</small></h1>" % len(w["maps"])]
    for region, ids in by_region(sorted(w["maps"]),
                                 lambda m: w["maps"][m].get("region")):
        body.append("<h2>%s</h2><div class='wrap'><table><tr><th>ID</th><th>Name</th>"
                    "<th>Type</th><th>Level band</th></tr>" % esc(region))
        for mid in ids:
            m = w["maps"][mid]
            lb = m.get("level_band") or {}
            body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s–%s</td></tr>" % (
                mid, link("maps", mid, m.get("name", mid), 1),
                esc(m.get("map_type")), esc(lb.get("min")), esc(lb.get("max"))))
        body.append("</table></div>")
    page(os.path.join(out, "maps", "index.html"), "Maps", "".join(body), 1)


def npcs_index(w, out):
    body = ["<h1>NPCs <small>%d</small></h1>" % len(w["npcs"]),
            "<div class='wrap'><table><tr><th>ID</th><th>Name</th><th>Role</th>"
            "<th>Region</th><th>Map</th></tr>"]
    for nid in sorted(w["npcs"]):
        n = w["npcs"][nid]
        home = n.get("map", "")
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            nid, link("npcs", nid, n.get("name", nid), 1), esc(n.get("role")),
            esc(n.get("region")),
            link("maps", home, w["maps"].get(home, {}).get("name", home), 1)
            if home in w["maps"] else esc(home)))
    body.append("</table></div>")
    page(os.path.join(out, "npcs", "index.html"), "NPCs", "".join(body), 1)


def quests_index(w, out):
    body = ["<h1>Quests <small>%d</small></h1>" % len(w["quests"]),
            "<div class='wrap'><table><tr><th>ID</th><th>Name</th><th>Type</th>"
            "<th>Region</th><th>Lv req</th><th>EXP</th></tr>"]
    for qid in sorted(w["quests"]):
        q = w["quests"][qid]
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                    "<td>%s</td><td>%s</td></tr>" % (
                        qid, link("quests", qid, q.get("name", qid), 1),
                        esc(q.get("quest_type")), esc(q.get("region")),
                        esc(q.get("level_requirement")),
                        esc((q.get("rewards") or {}).get("exp"))))
    body.append("</table></div>")
    page(os.path.join(out, "quests", "index.html"), "Quests", "".join(body), 1)


def items_index(w, ix, out):
    body = ["<h1>Items <small>%d</small></h1>" % len(w["items"])]
    cats = {}
    for iid, it in w["items"].items():
        cats.setdefault(it.get("category", it.get("_table", "other")), []).append(iid)
    for cat in sorted(cats):
        body.append("<h2>%s</h2><div class='wrap'><table><tr><th>ID</th><th>Name</th>"
                    "<th>Rarity</th><th>Req Lv</th><th>Buy</th><th>Sell</th>"
                    "<th>Dropped by</th></tr>" % esc(cat))
        for iid in sorted(cats[cat]):
            it = w["items"][iid]
            price = it.get("price") or {}
            srcs = ix["item_sources"].get(iid) or []
            src_html = ", ".join(
                link("monsters", s, w["monsters"].get(s, {}).get("name", s), 1)
                for s in sorted(set(srcs)) if s) or "—"
            body.append("<tr id='%s'><td>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                        "<td>%s</td><td>%s</td><td>%s</td></tr>" % (
                            iid, iid, esc(it.get("name", iid)), esc(it.get("rarity", "—")),
                            esc(it.get("req_level", "—")), esc(price.get("buy", "—")),
                            esc(price.get("sell", "—")), src_html))
        body.append("</table></div>")
    if w["pools"]:
        body.append("<h2>Equipment drop pools</h2>")
        for pid in sorted(w["pools"]):
            p = w["pools"][pid]
            entries = ", ".join(item_ref(w, e.get("item", "?"), 1)
                                for e in p.get("entries") or [])
            body.append("<h3 id='%s'>%s <small>%s</small></h3><p>%s</p>" % (
                pid, pid, esc(p.get("region", "")), entries))
    page(os.path.join(out, "items", "index.html"), "Items", "".join(body), 1)


def skills_index(w, out):
    body = ["<h1>Skills <small>%d</small></h1>" % len(w["skills"])]
    lines = {}
    for sid, s in w["skills"].items():
        lines.setdefault(s.get("_line_dir", s.get("line", "other")), []).append(sid)
    for line in sorted(lines):
        body.append("<h2>%s</h2>" % esc(line))
        for sid in sorted(lines[line]):
            s = w["skills"][sid]
            body.append("<h3 id='%s'>%s <small>%s · %s · %s</small></h3>" % (
                sid, esc(s.get("name", sid)), sid, esc(s.get("tier")),
                esc(s.get("kind"))))
            if s.get("flavor"):
                body.append('<div class="flavor">%s</div>' % esc(s["flavor"]))
            body.append("<p>Hits: %s · Cost: %s · Cooldown: %s s</p>"
                        % (fmt_targeting(s.get("targeting")),
                           fmt_cost(s.get("cost")), esc(s.get("cooldown"))))
            ld = s.get("level_data") or []
            if ld:
                body.append("<div class='wrap'><table><tr><th>Rank Lv</th>"
                            "<th>Cost</th><th>CD</th><th>Effects</th></tr>")
                for row in ld:
                    body.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
                        esc(row.get("level")), esc(row.get("essence_cost")),
                        esc(row.get("cooldown")), fmt_effects(row.get("effects"))))
                body.append("</table></div>")
    page(os.path.join(out, "skills", "index.html"), "Skills", "".join(body), 1)


def home_index(w, ix, out):
    body = ["<h1>Rebillion Wiki</h1>",
            "<p>A generated reference for the Rebillion design tree — every number "
            "on these pages comes straight from the minted YAML in "
            "<code>docs/50_content/</code>.</p>",
            "<div class='wrap'><table><tr><th>Section</th><th>Entries</th></tr>"]
    for label, href, count in [
            ("Monsters", "monsters/index.html", len(w["monsters"])),
            ("Maps", "maps/index.html", len(w["maps"])),
            ("NPCs", "npcs/index.html", len(w["npcs"])),
            ("Quests", "quests/index.html", len(w["quests"])),
            ("Items", "items/index.html", len(w["items"])),
            ("Skills", "skills/index.html", len(w["skills"]))]:
        body.append("<tr><td><a href='%s'>%s</a></td><td>%s</td></tr>"
                    % (href, label, count))
    body.append("</table></div><h2>Regions</h2><div class='wrap'><table>"
                "<tr><th>Region</th><th>Maps</th><th>Monsters</th></tr>")
    for region, mids in by_region(sorted(w["maps"]),
                                  lambda m: w["maps"][m].get("region")):
        mobs = [m for m, r in ix["mob_region"].items() if r == region]
        body.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (esc(region), len(mids), len(mobs)))
    body.append("</table></div>")
    page(os.path.join(out, "index.html"), "Home", "".join(body), 0)


# ---------------------------------------------------------------------------
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=os.path.join(REPO, "wiki"))
    args = ap.parse_args(argv)
    w = load_all()
    ix = build_indexes(w)
    for mob in w["monsters"]:
        monster_page(w, ix, mob, args.out)
    for mid in w["maps"]:
        map_page(w, ix, mid, args.out)
    for nid in w["npcs"]:
        npc_page(w, ix, nid, args.out)
    for qid in w["quests"]:
        quest_page(w, ix, qid, args.out)
    monsters_index(w, ix, args.out)
    maps_index(w, args.out)
    npcs_index(w, args.out)
    quests_index(w, args.out)
    items_index(w, ix, args.out)
    skills_index(w, args.out)
    home_index(w, ix, args.out)
    n_pages = sum(len(files) for _, _, files in os.walk(args.out))
    print("wiki: %d pages -> %s" % (n_pages, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
