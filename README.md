# After Hours Arcade

A playable first version of an after-closing 1987 arcade. The room is modeled in Blender and exported as glTF. Its first cabinet opens into **Brickstorm Arena**, a first-person, ten-level brick breaker built with Three.js and WebXR.

## Run

Node.js 22.12+ is recommended for the pinned Vite version.

```sh
npm ci
npm run dev
```

Open the localhost URL printed by Vite. Choose **Brickstorm Arena** for direct play, or **Enter the arcade** to explore. `npm run build` creates the static deployment in `dist/`; `npm run preview` previews it. Deploy `dist/` to an HTTPS static host to use a headset from another device. The LAN HTTP address is suitable for desktop viewing but does not enable immersive WebXR on a remote headset.

## Controls

| Mode | Controls |
| --- | --- |
| Arcade, desktop | WASD to move; drag to look; approach the center cabinet and press E; Esc returns to the lobby |
| Brickstorm, desktop | Mouse / touch moves paddle; click or Space serves; P pauses; Esc banks the run and returns |
| Arcade, VR | Left stick moves; right stick snap-turns; squeeze near the gold token to hold it; bring it to the coin slot; lean toward the CRT |
| Brickstorm, VR | Move and tilt controller paddle; trigger serves or resumes; both triggers held two seconds return to arcade |
| Optional second paddle | Enable in the lobby’s How to play dialog before entering VR |

Angle shots with paddle-edge hits. Gold bonuses arrive every five destroyed bricks: slow ball, extra life, and wide paddle. Clear the bottom support row to collapse the remaining blocks in slow motion. Clearing all ten levels awards a trophy at the prize counter. Each 100 points earns one ticket. Returning early banks the current run.

High scores, tickets, and trophy state are **local to this browser/device**, stored under `afterhours-v1`; this is not an online competitive leaderboard. Storage failures fall back to session-only scores. Audio is opt-in through the lobby’s Sound button.

## Assets and implementation

- `source/blender/after-hours.blend`: editable Blender room with cabinets, CRTs, controls, signage, carpet, stools, and prize counter.
- `scripts/model_arcade.py`: deterministic Blender modeling/export script. Rebuild with `Blender -b --python scripts/model_arcade.py` from this folder.
- `public/assets/arcade.glb`: exported room used by the game. Static geometry is merged by material at runtime for fewer draw calls.
- `public/assets/brickstorm.png`: original AI-generated cabinet and poster artwork, also used on the portal card.
- `src/main.js`: rendering, portal, input, game state, effects, physics and WebXR integration.
- `src/rules.js`: level formations, shot calculations, and defensive saved-data loading.
- `docs/art-direction.md`: artwork provenance and exact generation prompt.
- `docs/validation.md`: verification completed and remaining headset checks.

Blender MCP was not exposed in the authoring session. The room was actually generated with the installed Blender 4.5.12 Python interface in background mode. The project does not claim to have used an MCP connection.

WebXR follows the official [Three.js VR guide](https://threejs.org/manual/en/webxr-basics.html) and [VRButton API](https://threejs.org/docs/pages/VRButton.html). Desktop uses bloom postprocessing; VR renders directly for stereo compatibility and performance. A headset, secure origin, tracked controllers, and compatible WebXR browser are required. No hand-tracking implementation is included.

## Checks

```sh
npm test
npm run build
git diff --check
```

This is a playable prototype. Ten levels and the win path are implemented; a full ten-level human playthrough and headset performance/comfort validation have not yet been completed. Other cabinets are decorative expansion slots in this version.
