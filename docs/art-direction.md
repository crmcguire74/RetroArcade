# Art direction and provenance

The arcade combines midnight plum enamel and carpet, amber signage, cyan CRT light, and rose wall trim. The lobby uses warm condensed typography over the actual rendered Blender room. Brickstorm switches to a cosmic grid arena with saturated formations and restrained bloom. These are original assets without licensed arcade brands or music.

The artwork was generated with the **built-in image generation tool**, using the imagegen skill. The resulting image was inspected and copied into `public/assets/brickstorm.png`; it is used by the running game. It has chrome BRICKSTORM ARENA lettering, a colorful brick pyramid, and an energy ball on a cosmic background.

Exact generation prompt:

> Use case: stylized-concept. Asset type: original arcade cabinet screen artwork and in-game wall poster. Create a beautiful 1987 airbrushed arcade game illustration: a luminous cyan energy orb smashing a towering geometric rainbow brick pyramid floating over a dark cosmic grid, fragments in hot pink and amber, electric blue trails, rich midnight violet background, dramatic cinematic depth, analog printed grain, premium vintage arcade art. Portrait composition, centered pyramid with generous dark edges. Text at top exactly 'BRICKSTORM' with small 'ARENA' below in chrome retro lettering. No cabinet frame, no mockup, no watermark. This will be used as a texture inside a WebXR arcade.

No image-generation CLI or API-key fallback was used. Blender geometry is procedural and editable; generated artwork is a runtime texture.
