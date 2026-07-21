# CHAT.md — Channel Chat & Speech Bubbles (Stub)

References: 00_vision/GLOSSARY.md, 00_vision/PILLARS.md, 10_systems/social/PARTY.md,
10_systems/social/GUILD.md, 10_systems/HUD.md, 10_systems/CONTROLS.md, 10_systems/PERSISTENCE.md

**Purpose.** Real-time text between players: a local/map channel, the two roster-scoped channels
(party, guild), and 1:1 whispers, plus above-character speech bubbles so a conversation reads
without opening a log (`00_vision/PILLARS.md` P1).

## Planned scope
- Four channels: `normal` (broadcast to the sender's current `map_NNN`), `party`
  (`10_systems/social/PARTY.md` roster), `guild` (`10_systems/social/GUILD.md` roster), `whisper`
  (1:1, not map-scoped).
- **Speech bubbles** render only on `normal`-channel messages, above the sender's character;
  `party`/`guild`/`whisper` are log-only.
- Dock position/collapse state is already fixed (`10_systems/HUD.md` §10, bottom-left); focus key
  is already fixed (`Enter`, `10_systems/CONTROLS.md` §1) — this doc owns channels/history/
  moderation only, not placement or input.
- Client-side scrollback log per channel with timestamps; mute/block/report hooks (moderation
  surface only, no policy authored here).

## Dependencies
Relay and presence come from `10_systems/social/PARTY.md`, `10_systems/social/GUILD.md`, and the
live server (`10_systems/PERSISTENCE.md`); dock rendering and the focus key are already reserved
by `10_systems/HUD.md` / `10_systems/CONTROLS.md`.

## Reserved vocabulary
Channel tokens `normal`/`party`/`guild`/`whisper` — proposed for `00_vision/GLOSSARY.md`
Provisional, not yet promoted.

## Data sketch
```yaml
channel: guild          # normal | party | guild | whisper
sender: player_ref
recipient: player_ref    # whisper only
map_id: map_029           # normal channel scoping only
body: "..."
ts: <server timestamp>
bubble: true              # normal channel only
```

## Server Dependency
Message content/delivery is `authority: server` (`10_systems/PERSISTENCE.md` §1); the dock's
collapse/position preference is `authority: client` (§3). **The interim solo build ships chat
present but dormant**: a player can type (local echo only) but no other character exists to
receive it.

## Open Questions
- Bubble duration/truncation, scrollback size, and spam/rate limits are unset — owner
  `10_systems/HUD.md` jointly with this doc.
- Moderation policy and whether `party`/`guild` history persists across relogin
  (`10_systems/PERSISTENCE.md`) are undecided.
- Gamepad chat entry is undecided, inherited from `10_systems/CONTROLS.md`'s own open item.
