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
