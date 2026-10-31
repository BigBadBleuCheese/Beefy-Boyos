# Beefy Boyos

A script mod for The Sims 4 that gives randomly generated male Sims real builds, using LAVAMANAMADE's and Golyhawhaw's body sliders alongside EA's own.

Out of the box, the game almost never touches custom sliders when it makes townies. At most they get a tiny nudge too small to see, and most of them get nothing at all. Beefy Boyos steps in as each Sim is generated and gives him a build that makes use of them.

## What it does

Every generated male Sim, teen through elder, rolls two independent tiers:

| Beef | Chance | | Chub | Chance |
|---|---|---|---|---|
| Normal (the game's own build) | 40% | | Normal | 70% |
| Well built | 50% | | Chubby | 22.5% |
| Chad | 10% | | Big bear | 7.5% |

- **Beefed Sims** get high muscle and EA's arm, forearm, thigh, calf, shoulder, torso and foot sliders raised first. LAVAMANAMADE's sliders then add on top, so the custom sliders build on EA's shape instead of fighting it. Golyhawhaw's neck and foot width follow along.
- **Chubby Sims** get more fat and EA's belly, with LAVAMANAMADE's beer gut on top.
- **Butts:** everyone gets at least a little. Beef and chub each add more, and only Sims who roll both end up with the really big ones.
- **Everyone else** gets an occasional random Golyhawhaw neck and foot width.

Sims you make in CAS, premade Sims and Gallery Sims are never changed.

## Requirements

- The Sims 4 with script mods enabled.
- For the full look: LAVAMANAMADE's Male Sliders, plus Golyhawhaw's Expanded Foot Size Sliders and Extra Neck Width Slider.

Any of the slider mods can be missing. Beefy Boyos checks which ones are installed and only uses those. EA's sliders, muscle and fat work with none of them.

## Installing

Put `beefy_boyos.ts4script` in your Mods folder, either at the top level or one folder down. The first time the game loads it, it writes `BeefyBoyos.ini` next to itself.

## Settings

`BeefyBoyos.ini` controls everything: tier chances and strengths, how hard each slider is pushed, and the butt, belly and feet amounts. Every setting has a comment explaining it. A few common changes:

- **Tone everyone down:** set `beef strength` and/or `chub strength` under `[Overall]` below 1.0, for example 0.8. LAVAMANAMADE's sliders are reduced first, then EA's.
- **More or fewer chads:** change the chances under `[Beef Tiers]`. They're relative weights, so they don't need to add up to anything.
- **Turn it off without uninstalling:** set `enabled = false` under `[General]`.

Changes apply to Sims generated after the file is read. That happens at game load, or any time you enter `beefyboyos.reload` in the cheat console. If a value can't be read, Beefy Boyos uses the default for that setting and notes it in `BeefyBoyos.log`, next to the script.

## Compatibility

- Beefy Boyos only raises EA's sliders, never lowers them, so mods that shape random Sims with CAS presets still have their say.
- It changes Sims as the game generates them and doesn't override any tuning.
- If a game update changes the part of the game it hooks into, Beefy Boyos stays inactive (and says so in its log) instead of breaking Sim generation.

## Building

```
py -3.7 build.py
```

This writes `dist/beefy_boyos.ts4script`. The game only accepts scripts compiled with Python 3.7.
