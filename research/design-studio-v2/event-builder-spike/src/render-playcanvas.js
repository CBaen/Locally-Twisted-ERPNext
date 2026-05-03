import * as pc from "playcanvas";
import { createSceneObjects } from "./scene-spec.js";

export function createPlayCanvasRenderer(canvas) {
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
    clearColor: new pc.Color(0.81, 0.88, 0.86)
  });
  camera.setPosition(16.5, 15.2, 16.5);
  camera.lookAt(0, 3.5, 0);
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

  const root = new pc.Entity("event-builder-scene-root");
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
    entity.setLocalScale(object.scale.x, object.scale.y, object.scale.z);
    entity.addComponent("render", {
      type: object.type === "box" ? "box" : "sphere"
    });
    entity.render.material = materialFor(object.color, object.type);
    root.addChild(entity);
  }

  function render(state) {
    resize();
    clearRoot();
    for (const object of createSceneObjects(state)) {
      addObject(object);
    }
    app.render();
  }

  return {
    render
  };
}

function toPcColor(hex) {
  const value = Number.parseInt(hex.slice(1), 16);
  return new pc.Color(((value >> 16) & 0xff) / 255, ((value >> 8) & 0xff) / 255, (value & 0xff) / 255);
}
