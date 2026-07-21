Owner Agent-3 (extends ART_BIBLE). Defines the original "framed-box" interface identity (bordered
dialog boxes, blocky bitmap font, ornate slot frames, composable guild crests) — same family as
classic 2D MMOs, NOT a copy. Binds to HUD.md and Godot Theme + NinePatchRect + FontFile.

**Prime rules:** everything framed is a 9-slice (no stretched bitmaps); pixel-perfect (integer
scale, nearest, whole-pixel positions); ONE Godot `Theme` resource holds all fonts/frames/colors;
palette-locked to ART_BIBLE; readability over ornament.

**9-slice frames:** 3x3, `base_tile_px: 8`, `corner_px: 8`, `patch_margins {8,8,8,8}`, edges TILE
(not stretch), center flat fill (no gradient). Variants share geometry, differ by trim:
`frame_window` (panels, bone fill, ornate corners), `frame_dialog` (NPC box, earth trim),
`frame_quest` (ribbon corner tab, arcane accent), `frame_system` (thin, stone), `frame_tooltip`
(thin dark), `frame_input` (sunken/inset), `frame_button` (raised, states), `frame_slot`
(inset square, rarity ring). Standard panel = title bar strip + 8px-inset content + footer buttons.

**Font (the blocky "rectangle" look):** original bitmap font "GameSans-Pixel", FontFile hinting
off / Nearest / mipmaps off, integer scale only, rectangular even letterforms, hard 1px shadow.
Styles: `ui_title` 16 bold, `ui_body` 12, `ui_small` 10, `ui_number` 12 bold **tabular** (live
stats don't jitter), `dmg_number` 14 bold 2px outline (elemental ramp color, crit larger+tinted),
`name_tag` 10 bold 1px outline. Effects: shadow/outline `#241726`, default `#fbf7ef`, link
`#54b0c6`, emphasis `#f6c34b`. Inline color tags in dialog/quest: item=emphasis, npc=link,
warn=`#c8461f`, good=`#3f9a45`.

**Windows:** NPC dialog (bottom-center, portrait slot, clickable keyword links, ▼ more-text
blinker); quest window+tracker (ribbon tab, objectives checklist, reward icons; compact top-right
tracker); text input (sunken, 1px caret, tide-dark selection); system toast (color-coded left
edge); tooltip (dark, item layout: name in rarity color→type/req→stat lines→flavor); confirm modal
(screen dimmer). Buttons: normal/hover(emphasis+glow)/pressed(sunken,+1px)/disabled(flat,desat);
sizes 64/96/128; icon-only squares 20/24/28 for HUD/skill bar.

**Slots & icons:** one inset-square construction, states empty/filled/selected/locked/cooldown;
rarity ring from rarity_code; cooldown wipe + ui_number seconds; quantity badge bottom-right;
empty equip-slot glyph shows slot type. Icons on 16/24/32 grids, 1px ink outline, single motif,
readable at 16px; categories item/skill/buff_debuff/currency/quest/map_marker/emote. Buff/debuff
icons get a duration ring (buff=verdant edge, debuff=red edge).

**Tags/bubbles:** name tags on semi-transparent ink chip (player=white, npc=link, monster=ash /
elite=ember.light); player second line `[Guild] + 12px emblem`. Chat bubbles: rounded pixel bubble
with tail, channel tint (normal/party/guild/whisper). Boss: wide framed boss_bar, name in
ui_title, life in ember ramp, phase pips.

**Guild crest (composable — data, not an image):** `shield_shape + symbol + 2 palette colors`.
5 shapes (heater/round/banner/diamond/crest_ornate) × ~24 symbols (sword/shield/wing/flame/leaf/
wave/star/moon/skull/crown/anvil/bow/book/gem/wolf/dragon/anchor/key/eye/fist/tower/rune/bell/paw)
× palette. Symbol centered, 1px outline (readable at 12px). Render sizes 12/24/32/64. Stored per
guild (server-owned): `{shape, symbol, primary, accent}`; composited in-engine at any size.

**Cursor/minimap:** pixel cursor states (arrow/hand/attack/deny/loading); minimap in frame_system
top-right with marker icon set; map-name card on entry (frame_system, fades).

**Godot contract:** one `theme.tres` registering every FontFile, StyleBoxTexture (from 9-patch
PNGs, edges tile), color; Controls pick frames via `theme_type_variation`; guild crest = small
compositor scene stacking shape+symbol layers with palette `modulate`; all UI under a CanvasLayer
on an integer-scaled viewport.

**Export:** PNG RGBA palette-locked; 9-patch with marked 8px margins (document patch rect per
asset); UI atlas by category (frames/icons/crest_parts/cursor); Nearest/mipmaps off. Naming:
`ui_frame_{variant}`, `ui_button_{state}`, `ui_slot_{state}`, `ui_icon_{category}_{name}`,
`ui_crest_shape_{id}` / `ui_crest_symbol_{id}`, `ui_font_{style}`. PixelLab UI briefs inherit
ART_BIBLE defaults and inject only variant/motif, ramp accent, size, patch margins (if frame).

**Open Questions:** original vs licensed pixel font (check shipping license); lock guild
shape/symbol counts; window title-bar draggable vs fixed; which HUD elements always-on vs toggle.
