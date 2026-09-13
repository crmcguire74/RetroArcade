# After Hours Arcade — two playable worlds

A modeled 1987 arcade with two playable worlds: Brickstorm Arena and Bayou Crossing, a Frogger-inspired road-and-river crossing game.

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

## Bayou Crossing

Choose **02 · Bayou Crossing → Play Bayou Crossing → Start crossing**. Alternatively, use **Look around the arcade → Next view** to visit the green cabinet in the right-hand bay and play from there.

- Arrow keys, WASD, or the on-screen direction pad: one hop per press.
- Cross five traffic lanes, pause on the safe median, then ride logs and turtles through five river lanes.
- Turtles bob before diving. Reach all five empty lily-pad homes to advance; complete three rounds to win.
- **Frog-eye view** switches the desktop camera. **Pause / Resume** and **Arcade** remain visible.
- Runs save on leaving or finishing. Separate browser storage (`afterhours-bayou-v1`) preserves Brickstorm scores. A full win earns a golden frog behind the prize counter.
- In VR, trigger starts/resumes and the left stick hops; return the stick to center between hops. Flick the stick left/right in the arcade to switch cabinets. Hold both triggers to return. Hops use a brief comfort fade; hardware comfort is unverified.

The new environment, frog, truck, log, turtle and cabinet are **native Blender-authored geometry exported to GLB**. Generated artwork supplies the cabinet illustration, detailed ground albedo and distant woodland cyclorama. Near scenery and all gameplay objects are actual meshes. Blender procedural micro-normal detail is baked into normal textures.

Native sources are in `design/bayou-crossing/meshes/`; browser assets are in `public/assets/bayou/`. Function and Form approvals are recorded in `design/bayou-crossing/milestone-reviews.json`. Open `/design/bayou-crossing/form-review.html` on the development server for the reviewed Blender renders.

Normal, high, and reduced geometry tiers are preserved. Coarse-pointer devices load reduced geometry and texture tiers (6.2 MB total). Desktop uses the standard tier (12.0 MB for the game world and four movable assets). A shared lighting manifest maps Blender fixture positions into the runtime; area lights are approximated for WebXR, with real-time shadows rather than baked lightmaps.

Blender MCP was unavailable. The user approved direct local Blender authoring with no paid Meshy generation. Game Development Studio's `game-dev` CLI was also unavailable; its CLI workflow was not run. The room-building skill's paid-Meshy validator assumptions are documented as exceptions, not fabricated provider receipts.

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

The older assets remain in the repository for reference; the application loads the three replacement `premium` GLBs plus the new Bayou exports. The old VECTOR cabinet is omitted from the merged arcade and replaced by the new modeled cabinet. Blender MCP is not exposed in this session, so Blender 4.5.12’s background Python interface produced the models. Runtime geometry is merged by material, preserving embedded artwork textures.

## VR

Use **Play with a VR headset** on a compatible headset browser over HTTPS. Trigger starts the game and serves; move the controller paddle to catch the ball. Optional two-paddle play is available under Controls. Hold both triggers for 1.5 seconds to return. Physical token pickup/insertion remains an optional route at the center cabinet, with direct trigger entry always available. Returning VR shots are assisted into a standing player’s reachable area.

WebXR/controller code is implemented, but real headset comfort, device compatibility, and frame-rate validation remain outstanding. There is no claim of completed headset testing. The ordinary LAN HTTP URL does not enable immersive WebXR on another device; host `dist/` over HTTPS for headset access.

## Build and checks

```sh
npm test
npm run build
git diff --check
node scripts/check_bayou_routes.mjs
node scripts/check_bayou_assets.mjs
```

Node 22.12+ is recommended. Vite produces `dist/` for static hosting. See `docs/validation.md` for verification evidence and `docs/art-direction.md` for image-generation provenance and prompts.
