import * as pc from "playcanvas";
import { CLASSIC_CAMERA, createClassicRenderObjects } from "./classic-scene.js";

export function createClassicPlayCanvasRenderer(canvas) {
  const app = new pc.Application(canvas, {
    graphicsDeviceOptions: {
      alpha: false,
      antialias: true,
      preserveDrawingBuffer: true
    }
  });

  app.start();
  app.scene.ambientLight = new pc.Color(0.62, 0.66, 0.65);

  const camera = new pc.Entity("fixed-isometric-camera");
  camera.addComponent("camera", {
    projection: pc.PROJECTION_ORTHOGRAPHIC,
    orthoHeight: 17.6,
    nearClip: 0.1,
    farClip: 100,
    clearColor: new pc.Color(0.84, 0.88, 0.86)
  });
  camera.setPosition(CLASSIC_CAMERA.position.x, CLASSIC_CAMERA.position.y, CLASSIC_CAMERA.position.z);
  camera.lookAt(CLASSIC_CAMERA.target.x, CLASSIC_CAMERA.target.y, CLASSIC_CAMERA.target.z);
  app.root.addChild(camera);

  const keyLight = new pc.Entity("key-light");
  keyLight.addComponent("light", {
    type: "directional",
    color: new pc.Color(1, 0.94, 0.82),
    intensity: 1.7,
    castShadows: false
  });
  keyLight.setEulerAngles(52, 34, 0);
  app.root.addChild(keyLight);

  const fillLight = new pc.Entity("fill-light");
  fillLight.addComponent("light", {
    type: "directional",
    color: new pc.Color(0.66, 0.78, 0.88),
    intensity: 0.55,
    castShadows: false
  });
  fillLight.setEulerAngles(24, -140, 0);
  app.root.addChild(fillLight);

  const root = new pc.Entity("classic-stage-root");
  app.root.addChild(root);
  const materialCache = new Map();

  function resize() {
    const width = Math.max(1, Math.floor(canvas.clientWidth));
    const height = Math.max(1, Math.floor(canvas.clientHeight));
    app.graphicsDevice.resizeCanvas(width, height);
  }

  function materialFor(hex, type) {
    const key = `${hex}:${type}`;
    if (materialCache.has(key)) {
      return materialCache.get(key);
    }
    const material = new pc.StandardMaterial();
    const color = toPcColor(hex);
    material.diffuse = color;
    material.emissive = new pc.Color(color.r * 0.05, color.g * 0.05, color.b * 0.05);
    material.specular = type === "balloon" ? new pc.Color(0.8, 0.76, 0.68) : new pc.Color(0.24, 0.24, 0.24);
    material.shininess = type === "balloon" ? 56 : 18;
    material.update();
    materialCache.set(key, material);
    return material;
  }

  function clearRoot() {
    for (const child of [...root.children]) {
      child.destroy();
    }
  }

  function addObject(object) {
    const entity = new pc.Entity(object.id);
    entity.setPosition(object.position.x, object.position.y, object.position.z);
    entity.setEulerAngles(0, object.rotation_y_deg ?? 0, 0);

    if (object.type === "balloon") {
      addBalloonObject(entity, object);
      root.addChild(entity);
      return;
    }

    entity.setLocalScale(object.scale.x, object.scale.y, object.scale.z);
    entity.addComponent("render", {
      type: object.type === "box" ? "box" : "sphere"
    });
    entity.render.material = materialFor(object.color, object.type);
    root.addChild(entity);
  }

  function addBalloonObject(parent, object) {
    addBalloonPart(parent, {
      name: `${object.id}-body`,
      position: [0, 0, 0],
      scale: [object.scale.x * 0.98, object.scale.y * 1.08, object.scale.z * 0.98],
      color: object.color
    });
    addBalloonPart(parent, {
      name: `${object.id}-neck`,
      position: [0, -object.scale.y * 0.56, 0],
      scale: [object.scale.x * 0.15, object.scale.y * 0.24, object.scale.z * 0.15],
      color: object.color
    });
  }

  function addBalloonPart(parent, { name, position, scale, color }) {
    const part = new pc.Entity(name);
    part.setLocalPosition(position[0], position[1], position[2]);
    part.setLocalScale(scale[0], scale[1], scale[2]);
    part.addComponent("render", { type: "sphere" });
    part.render.material = materialFor(color, "balloon");
    parent.addChild(part);
  }

  function render(state) {
    resize();
    clearRoot();
    for (const object of createClassicRenderObjects(state)) {
      addObject(object);
    }
    app.render();
  }

  return { render };
}

function toPcColor(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return new pc.Color(((value >> 16) & 0xff) / 255, ((value >> 8) & 0xff) / 255, (value & 0xff) / 255);
}
