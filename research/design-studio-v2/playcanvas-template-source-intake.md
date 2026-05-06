# PlayCanvas Template And Physics Source Intake

Date: 2026-05-06

Purpose: record the code sources and engine patterns used to reset the balloon builder prototype after the first material-model pass used the wrong contact behavior.

## Sources Checked

- Official PlayCanvas scaffold: <https://github.com/playcanvas/create-playcanvas>
  - Current templates: `vanilla-ts` and `react-ts`.
  - Useful command pattern: `npm create playcanvas@latest my-game -- -t vanilla-ts`.
  - Decision: use the vanilla/engine pattern for this game slice. React can wait until the game loop, picking, camera, and stage hierarchy are stable.

- Official PlayCanvas engine repo: <https://github.com/playcanvas/engine>
  - The engine is the primary source for examples, scripts, and current API behavior.
  - Current examples live under `examples/src/examples/`.

- Official camera controls script: <https://github.com/playcanvas/engine/blob/main/scripts/esm/camera-controls.mjs>
  - Adopted for the v2 route instead of custom orbit math.
  - It supports orbit/fly/focus modes, mouse, multi-touch, gamepad, damping, pitch/yaw ranges, and zoom range.

- Official physics examples: <https://github.com/playcanvas/engine/tree/main/examples/src/examples/physics>
  - Relevant examples include `compound-collision`, `falling-shapes`, `offset-collision`, `raycast`, and `vehicle`.
  - Useful pattern: graphics and collision can be separate; compound collision supports a rigid parent entity with child collision shapes.

- Official picker/raycast examples: <https://github.com/playcanvas/engine/tree/main/examples/src/examples/physics>
  - `raycast.example.mjs` is the correct family for selecting entities from screen input when physics is available.
  - The v2 route currently uses `pc.Picker` against rendered mesh instances for a lightweight first pass.

- PlayCanvas physics basics: <https://developer.playcanvas.com/user-manual/physics/physics-basics/>
  - PlayCanvas uses Ammo.js/Bullet through rigidbody and collision components.
  - Important engine rule: physics units are interpreted as meters by default. This project currently renders in feet, so a production physics layer needs an explicit feet-to-meter conversion.
  - Important design rule: collision shape does not have to match rendered shape. That is a good fit for balloon bodies where visual latex and physical contact proxy should be different systems.

- Calling Ammo.js from PlayCanvas: <https://developer.playcanvas.com/user-manual/physics/calling-ammo/>
  - PlayCanvas does not expose every Ammo/Bullet capability through components.
  - Constraints, soft bodies, cloth, vehicles, and some advanced behaviors require direct Ammo API use.
  - Decision: the production balloon-contact path should not pretend a visual patch is physics. It should either use a custom balloon packing/deformation solver or direct Ammo soft-body/constraint work after a contained proof.

- Ammo.js repo: <https://github.com/kripken/ammo.js>
  - Ammo is a JavaScript/WASM port of Bullet and includes demos for cubes, soft-body rope, cloth, volume, heightmap, and vehicle.
  - Relevant for future soft-body balloon experiments, but not yet adopted into the v2 route.

## Root Cause From The Failed Lab

The rejected material-model pass drew a flattened patch on the balloon surface when contacts existed. That made multi-balloon clusters look sliced instead of mutually displaced. The right first behavior for classic clusters is not "cut"; it is "push back until the balloon centers reach a valid packed distance," with deformation handled as a later visual layer.

## V2 Rebuild Decisions

- Use `classic-playcanvas-v2.html` in the stable `event-builder-spike` package.
- Keep `stageRoot` as the single parent for the stage and every placed piece.
- Keep every decor object under its own piece root.
- Use official `CameraControls` for view/orbit UX.
- Put the default camera on the audience side of the stage.
- Replace the solid backdrop wall with an open stage frame so rotating the stage does not hide the design behind a giant wall.
- Remove contact cut patches. Use an iterative push-apart packing solver for classic quad balloon centers.
- Keep this slice classic-only. Organic balloon work still needs a separate solver for mixed sizes, density, filler balloons, and support mechanics.

## Next Physics Work

1. Create a physics-scale adapter: feet for business payload, meters for PlayCanvas/Ammo simulation.
2. Add a pure test suite for the packing solver so no pair of classic balloons ends closer than the contact distance.
3. Prototype Ammo rigidbody/collision proxies for balloon clusters.
4. Separately prototype soft-body or shader/bone deformation for latex contact. Do not draw contact patches as proof of physics.
5. Only promote a physics layer after browser screenshots prove the visual result at desktop and mobile sizes.
