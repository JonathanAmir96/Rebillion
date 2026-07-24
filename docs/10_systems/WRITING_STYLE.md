# WRITING_STYLE.md — Dialog & Quest Text Bible

References: docs/00_vision/PILLARS.md, docs/40_assets/ART_BIBLE.yaml, docs/WORLD_PLAN.md,
docs/10_systems/WORLD_LORE.md, docs/10_systems/QUESTS.md, docs/20_schemas/npc.schema.md,
docs/20_schemas/quest.schema.md, docs/00_vision/GLOSSARY.md, docs/VALIDATION.md

Owner doc for the words players read: NPC dialog/flavor, quest flavor/offer/complete text,
item flavor. One voice across the 120-NPC cast and 120 quests
(`docs/60_agents/roles/ROLE_NARRATIVE_WRITER.md`). Never restates length limits or lore
facts — cites their owners.

## 1. Tone
Cozy-heroic, slightly whimsical (`00_vision/PILLARS.md` P2; `40_assets/ART_BIBLE.yaml`
`identity.mood`). Warm even when the subject is dangerous; competent, not cynical; funny in
asides, never mocking the player. A line should sound like someone who has lived in this
world their whole life, not a narrator describing it from outside.

| Do | Don't |
|---|---|
| "Cindermaw's been snoring in that kiln since before I had my own teeth. Time someone woke it for good." | "A LEGENDARY BEAST OF ANCIENT FIRE AWAITS YOUR CHALLENGE." |
| "Mind the cinders on your way out." | "Beware, traveler, for peril lurks beyond!" |
| "Bring me its claw and I'll vouch for you at the gate." | "Slay 8 Cinderpups to prove your worth to the guild." |
| "Cold to the touch — good." | "You have defeated the darkness within your soul." |

## 2. Voice by context
- **Town NPC** (`merchant`/`innkeeper`/`banker`/etc. roles, `npc.schema.md` Enums): brisk,
  local, a little dry. They have a job and a life outside the player's quest.
- **Instructor:** warmer authority, a mentor's patience; speaks like they remember being a
  novice themselves. Never lectures past its `dialog` field's own sentence cap.
- **Quest body** (`flavor`/`offer_text`/`complete_text`): plain-spoken stakes, told in the
  giver's or turn-in NPC's own voice, not an omniscient narrator's —
  `quest.schema.md`'s field notes tie `offer_text`/`complete_text` to that NPC's dialog voice
  for exactly this reason.
- **Item flavor:** a single evocative image or aside, never a rules restatement (mechanics
  live in `10_systems/ITEMS.md`, not the flavor string).
- **System/UI text:** plainest voice of all — button labels, tooltips, log lines. No jokes,
  no flourish; clarity beats voice here (`00_vision/PILLARS.md` P1's "a player who dies
  should know why").

## 3. Naming conventions
Extracted from the seeded cast (`docs/WORLD_PLAN.md` Job instructors table, Region
sections):
- **People:** short, one or two syllables, faintly Old-World-cozy — *Bram, Saela, Yewna,
  Mira*. A nickname in quotes reads as a title standing in for a surname — *"Whisper" Vex*.
- **Places:** compound-plain, landscape word + settlement suffix — *Rosen Harbor, Mossmere,
  Cindershelf, Tidewatch Port, Emberfoot Village*. Do not invent suffixes outside this
  pattern (no "-opolis," "-heim," "-gard").
- **Monsters/bosses:** a plain descriptor, or a proper name plus at most one epithet for
  uniques — *Cindermaw, Mother Gloam, Karnothal the Stoker, The Drowned Warden, The
  Custodian* (`docs/WORLD_PLAN.md` Region sections). Title-case; no epithet longer than
  "the + noun."
- **Items:** functional-plain — material or slot plus one flavor word; no invented
  pseudo-Latin or invented mythology.

## 4. Forbidden clichés
No chosen-one prophecies; no "it's dangerous to go alone, take this" pastiches; no grimdark
edge (torture-for-shock, nihilism, gore-for-gore); no fourth-wall breaks or meme references;
no "ancient evil awakens" stock phrasing; no rhyming/monologuing villain taunts; no restating
stat math in prose (e.g. "your +12 might impresses me").

## 5. Length limits (schema owns the cap; this table only maps them)
| Field | Cap | Owner |
|---|---|---|
| `npc.dialog.greeting`/`idle`/`farewell` | ≤2 sentences each | `20_schemas/npc.schema.md` Fields + Validation rule 8 |
| `npc.flavor` | ≤2 sentences | `20_schemas/npc.schema.md` Fields |
| `quest.flavor` | ≤2 sentences | `20_schemas/quest.schema.md` Fields + Validation rule 13 |
| `quest.offer_text` | ≤2 sentences | `20_schemas/quest.schema.md` Fields + Validation rule 13 |
| `quest.complete_text` | ≤2 sentences | `20_schemas/quest.schema.md` Fields + Validation rule 13 |

The same "≤2 sentences per field" norm is echoed at `10_systems/QUESTS.md` §8's log
display — cited here, not restated. Item flavor has no dedicated item schema in this doc's
reading list; treat it under the same ≤2-sentence house norm until an item schema owner
fixes it explicitly (see Open Questions).

## 6. Mechanics in player-facing text
Any mechanic named in dialog/flavor must use its exact `00_vision/GLOSSARY.md` token (stat,
status, element, resource, currency) — no synonyms, no legacy-genre terms
(`docs/VALIDATION.md` §1's banned list). US spelling everywhere (`CLAUDE.md` law 6). Prefer
describing an effect in-world ("it'll slow you to a crawl") over naming the token in prose;
when a token must appear verbatim (e.g. a tooltip), spell it exactly as GLOSSARY.md does.

## 7. Proposing new lore
A writer may not invent a world fact — origin, history, causal "why" — inside dialog or
quest text. If a line needs a fact `10_systems/WORLD_LORE.md`/`docs/WORLD_PLAN.md` doesn't
cover, flag it in that doc's own `## Open Questions` and write around the gap (an in-world
shrug: "no one rightly knows") until an owner resolves it
(`docs/60_agents/roles/ROLE_NARRATIVE_WRITER.md` — "Never: invent world facts").

## Open Questions
- Item flavor has no schema-fixed length cap yet (no `item.schema.md` was in this doc's
  reading list); §5 assumes the same ≤2-sentence norm by house style until an item schema
  owner confirms or overrides it.
- Whether portrait-less NPCs (`npc.schema.md`'s own Open Question on the `portrait` token's
  ownership) need a written physical-description convention for artless flavor text is
  unresolved; default for now is no explicit physical description in `flavor` unless
  plot-relevant.
