# Rebuilt edition validation

## Automated

`npm test` exercises the actual gameplay engine separately from rendering:

- Serve, brick hit, scoring, miss, life decrement, and pause state.
- Returning paddle-plane collision fires once and redirects the ball forward.
- All ten levels completed through real physics using a deterministic perfect test paddle: **23,619 simulation frames, 65 paddle returns, 59,600 points**. No score injection or direct level-skipping is used. This verifies reachability of the completion path, not human balance or headset comfort.
- Power-up collection, slow-ball speed, effect expiry, and extra life.
- VR return assistance projects shots into a standing reach region.
- Ten distinct bounded formations, reflection calculations, and malformed saved-data recovery.

## Browser

Verified the rebuilt interface in the local browser at 1280 × 720:

- All three replacement Blender exports load; cabinets show shaped profiles and illustrated side panels, and the arena shows modeled arches and generated cosmic artwork.
- A prominent Play Brickstorm button opens the arena directly.
- The first-serve panel has an explicit Launch ball button.
- Launch starts gameplay. A brick hit changed score from 0 to 100 and brick count from 45 to 44.
- Pause displayed Game paused and Resume game; Resume returned to the appropriate serving state.
- A pointer drag to screen coordinate (880, 360) placed the rendered paddle at that position.
- Visual review caught and corrected inverted CRT texture mapping, an opaque paddle obscuring play, excessive bloom, and an instruction panel blocking the center of the arena.

The earlier build’s local score persistence was verified across reload. The revised build retains the same storage key; further real-device testing remains appropriate.

## Remaining hardware validation

No physical headset is available in this session. WebXR session entry, controller grip orientation, physical token insertion, two-paddle coordination, standing reach comfort, headset performance, and mobile device behavior require actual device testing. No award, certification, or production-readiness claim is made.

Final packaged browser check: the model loader reported 348 arcade meshes (98,712 triangles), 73 arena meshes (44,378 triangles), and six brick-prop meshes (936 triangles) before runtime merging. The generated backdrop was loaded from the Blender arena GLB. The browser error log was empty after loading and entering the final first-serve screen.


## Bayou Crossing integration — September 13, 2026

- **23 automated tests pass**, including keyboard/stick debouncing, pause, frame-rate-independent platform carry, mid-hop vehicle collisions, diving turtles, timeouts, occupied homes, round progression and isolated persistent storage.
- `node scripts/check_bayou_routes.mjs` searched legal inputs and replayed them through the public hop/update methods. All **15 homes / 3 rounds** completed with **289 hops, 12,902 points and all 3 lives**. This is an automated reachability check, not a human playtest.
- Blender produced the environment, four reusable props and second cabinet. The geometry audit matched all 33 layout instances and found zero non-manifold edges in the five audited substrate/boundary meshes.
- All **15 GLB hashes and sizes** match the export manifest. The reduced game package totals **6,195,064 bytes**. Sampled visible geometry across three rounds peaks at **214,137 triangles**, under the 250,000 triangle budget. Shadow and postprocessing passes redraw geometry and are counted separately.
- The actual browser loaded the new cabinet and five game GLBs. The old VECTOR cabinet was excluded, leaving one new cabinet in its place.
- Desktop walkthrough: choose Bayou → Play → Start; first forward hop completed and score became 10; pause/resume preserved a hop; frog-eye camera worked; Arcade returned correctly; a 10-point score survived reload alongside existing Brickstorm scores.
- Arcade guided navigation reached the new cabinet and exposed its own Play Bayou Crossing action.
- At a 390 × 844 CSS viewport, the direction-pad right button moved the frog from x=0 to x=1.3. This checks responsive UI and pointer activation, not a physical touchscreen.
- Brickstorm still started and served after returning from Bayou.
- Final local preview snapshot: **60 FPS, 90 draw calls, 196,358 scene triangles**, with 390,746 triangles including shadow and postprocessing work. This is one desktop snapshot, not a cross-device benchmark.
- No JavaScript errors were captured. An old Three.js PCFSoftShadowMap warning was corrected by using PCFShadowMap.
- Browser screenshots of the cabinet, start screen, frog-eye view and responsive layout were inspected inline in the task conversation. The final playable start screen was left open.

### Deliberate limits

WebXR code is implemented, including cabinet selection, stick debouncing, frog-height camera, in-world instructions and comfort fade, but no physical headset was tested. Browser play is validated locally; this revision has not been deployed to the existing public site. The runtime lighting uses manifest-driven real-time approximations of the Blender area lights, with no baked lightmap. Accordingly the plugin's full Runtime/deployment gate is not marked approved. Human Function and Form approvals are recorded. Paid Meshy requirements were explicitly replaced by the user-approved Blender-only route; the unmodified provider-specific validator still reports its three pricing/budget requirements.
