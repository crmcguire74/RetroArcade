# Art direction and provenance

The arcade combines midnight plum enamel and carpet, amber signage, cyan CRT light, and rose wall trim. The lobby uses warm condensed typography over the actual rendered Blender room. Brickstorm switches to a cosmic grid arena with saturated formations and restrained bloom. These are original assets without licensed arcade brands or music.

The artwork was generated with the **built-in image generation tool**, using the imagegen skill. The resulting image was inspected and copied into `public/assets/brickstorm.png`; it is used by the running game. It has chrome BRICKSTORM ARENA lettering, a colorful brick pyramid, and an energy ball on a cosmic background.

Exact generation prompt:

> Use case: stylized-concept. Asset type: original arcade cabinet screen artwork and in-game wall poster. Create a beautiful 1987 airbrushed arcade game illustration: a luminous cyan energy orb smashing a towering geometric rainbow brick pyramid floating over a dark cosmic grid, fragments in hot pink and amber, electric blue trails, rich midnight violet background, dramatic cinematic depth, analog printed grain, premium vintage arcade art. Portrait composition, centered pyramid with generous dark edges. Text at top exactly 'BRICKSTORM' with small 'ARENA' below in chrome retro lettering. No cabinet frame, no mockup, no watermark. This will be used as a texture inside a WebXR arcade.

No image-generation CLI or API-key fallback was used. Blender geometry is procedural and editable; generated artwork is a runtime texture.

## Rebuilt edition

The revision replaces the initial box cabinets with shaped Blender geometry, curved CRTs, sculpted trim, coin mechanisms, and embedded full-size illustrated side panels. The arena now uses stepped architecture, machined arches, and individually modeled beveled bricks. The palette is obsidian enamel, champagne brass, turquoise glass, dusty rose, and amber. Large generated imagery sits behind real geometry; it does not stand in for a 3D room.

New artwork: `public/assets/arena-nebula.png`. Generated with the **built-in image generation tool**, inspected, then packed into `source/blender/arena-premium.blend` and embedded in the exported GLB’s cyclorama material.

Exact new prompt:

> Use case: stylized-concept. Asset type: panoramic environmental texture for the rear cyclorama of a premium immersive VR brick-breaking game. Create a cinematic wide 3:2 cosmic vista, painterly photoreal quality with extraordinary fine detail: monumental eclipsed violet planet on the upper right, luminous turquoise nebula sweeping from lower left to upper right, tiny warm amber stars in velvet indigo space, subtle distant planetary rings and layered interstellar clouds. Dark lower quarter and dark center suitable for bright colorful 3D bricks in front, exquisite restrained color, atmospheric depth, sophisticated science-fiction film production design, believable light scattering and fine dust. No buildings, no interface, no words, no logos, no grid, no ball or bricks. This will be visibly integrated as a backdrop behind actual Blender-modeled arena architecture.

Code-generated CRT attract animations and procedural terrazzo microdetail complement the generated artwork. They do not replace it. The generated panorama is a flat distant background; cabinets, architecture, paddles, balls, and bricks are actual 3D geometry.
