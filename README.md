# After Hours Arcade — rebuilt edition

An immersive first-person brick breaker inside a modeled 1987 arcade. This revision replaces the initial prototype’s navigation, paddle mapping, cabinet models, and arena.

## Start playing

```sh
npm ci
npm run dev
```

Open the localhost URL. Select **Play Brickstorm**, then **Launch ball**. Move your mouse or finger to move the paddle. No walking, coin insertion, hidden cabinet selection, or headset is required for desktop play.

- Move the paddle under the returning ball. The gold ring shows its projected return position.
- Hit near paddle edges to angle shots. Destroy the lowest support row to collapse the formation.
- Gold bonuses give a wider paddle, slow ball, or extra life.
- Use the visible **Pause / Resume** controls, or Esc. Space serves or resumes. Arrow keys move the paddle too.
- **Arcade** returns to the home screen and saves the run. **Look around the arcade** offers guided camera views without free-roaming movement.

There are ten formations, four starting lives, local high scores, earned tickets, and a trophy for clearing all levels. Scores are stored on this browser/device under `afterhours-v1`, not on a global online leaderboard.

## What was rebuilt

**Real Blender geometry:** sculpted cabinet profiles, rounded T molding, curved CRT glass, side-panel illustrations, recessed coin mechanisms, screws, speaker vents, detailed buttons, joysticks, stools, a prize counter, fluted walls, and a stepped arena with repeated metal arches. Blender exports the room, arena, and beveled game bricks into GLB files loaded by the application.

**Generated artwork:** the original Brickstorm illustration is embedded on cabinet side panels and wall posters. A newly generated cosmic panorama is embedded on the Blender arena’s cyclorama. The Blender source files pack their textures. Runtime CRT attract screens animate separately so instructions remain sharp and readable.

**Reliable play:** the cursor is projected onto the actual paddle plane. The previous arbitrary screen-to-world mapping, hidden focus pause, and mandatory free-roaming cabinet approach are removed. Pause always exposes a Resume action. The pure game engine is independently tested through all ten levels.

## Blender source and rebuilding

- `source/blender/arcade-premium.blend` → `public/assets/arcade-premium.glb`
- `source/blender/arena-premium.blend` → `public/assets/arena-premium.glb`
- `source/blender/brick-premium.blend` → `public/assets/brick-premium.glb`
- `scripts/model_premium.py`: deterministic modeling and export script.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python scripts/model_premium.py
```

The older assets remain in the repository for reference; the application loads the three replacement `premium` GLBs. Blender MCP is not exposed in this session, so Blender 4.5.12’s background Python interface produced the models. Runtime geometry is merged by material, preserving embedded artwork textures.

## VR

Use **Play with a VR headset** on a compatible headset browser over HTTPS. Trigger starts the game and serves; move the controller paddle to catch the ball. Optional two-paddle play is available under Controls. Hold both triggers for 1.5 seconds to return. Physical token pickup/insertion remains an optional route at the center cabinet, with direct trigger entry always available. Returning VR shots are assisted into a standing player’s reachable area.

WebXR/controller code is implemented, but real headset comfort, device compatibility, and frame-rate validation remain outstanding. There is no claim of completed headset testing. The ordinary LAN HTTP URL does not enable immersive WebXR on another device; host `dist/` over HTTPS for headset access.

## Build and checks

```sh
npm test
npm run build
git diff --check
```

Node 22.12+ is recommended. Vite produces `dist/` for static hosting. See `docs/validation.md` for verification evidence and `docs/art-direction.md` for image-generation provenance and prompts.
