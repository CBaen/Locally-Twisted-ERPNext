import * as BABYLON from "@babylonjs/core";
import { createSceneObjects } from "./scene-spec.js";

export function createBabylonRenderer(canvas) {
  const engine = new BABYLON.Engine(
    canvas,
    true,
    {
      antialias: true,
      preserveDrawingBuffer: true,
      stencil: true
    },
    true
  );
  const scene = new BABYLON.Scene(engine);
  scene.clearColor = BABYLON.Color4.FromHexString("#cfdfdcff");
  scene.ambientColor = new BABYLON.Color3(0.62, 0.66, 0.65);

  const camera = new BABYLON.FreeCamera("fixed-isometric-camera", new BABYLON.Vector3(16.5, 15.2, 16.5), scene);
  camera.mode = BABYLON.Camera.ORTHOGRAPHIC_CAMERA;
  camera.setTarget(new BABYLON.Vector3(0, 3.5, 0));
  camera.minZ = 0.1;
  camera.maxZ = 100;
  fitCamera(camera, canvas);

  const keyLight = new BABYLON.DirectionalLight("key-light", new BABYLON.Vector3(-0.6, -1, -0.55), scene);
  keyLight.intensity = 1.35;
  keyLight.diffuse = new BABYLON.Color3(1, 0.94, 0.82);

  const fillLight = new BABYLON.DirectionalLight("fill-light", new BABYLON.Vector3(0.55, -0.5, 0.7), scene);
  fillLight.intensity = 0.45;
  fillLight.diffuse = new BABYLON.Color3(0.66, 0.78, 0.88);

  const materialCache = new Map();
  let activeMeshes = [];

  function materialFor(hex, type) {
    const key = `${hex}:${type}`;
    if (materialCache.has(key)) {
      return materialCache.get(key);
    }
    const material = new BABYLON.StandardMaterial(key, scene);
    const color = BABYLON.Color3.FromHexString(hex);
    material.diffuseColor = color;
    material.emissiveColor = color.scale(type === "balloon" ? 0.035 : 0.015);
    material.specularColor = type === "balloon" ? new BABYLON.Color3(0.8, 0.76, 0.68) : new BABYLON.Color3(0.2, 0.2, 0.2);
    material.specularPower = type === "balloon" ? 72 : 24;
    materialCache.set(key, material);
    return material;
  }

  function clearMeshes() {
    for (const mesh of activeMeshes) {
      mesh.dispose(false, true);
    }
    activeMeshes = [];
  }

  function addObject(object) {
    const mesh =
      object.type === "box"
        ? BABYLON.MeshBuilder.CreateBox(object.id, { size: 1 }, scene)
        : BABYLON.MeshBuilder.CreateSphere(object.id, { diameter: 1, segments: object.type === "knot" ? 8 : 16 }, scene);
    mesh.position = new BABYLON.Vector3(object.position.x, object.position.y, object.position.z);
    mesh.scaling = new BABYLON.Vector3(object.scale.x, object.scale.y, object.scale.z);
    mesh.material = materialFor(object.color, object.type);
    activeMeshes.push(mesh);
  }

  function render(state) {
    engine.resize();
    fitCamera(camera, canvas);
    clearMeshes();
    for (const object of createSceneObjects(state)) {
      addObject(object);
    }
    scene.render();
  }

  engine.runRenderLoop(() => {
    scene.render();
  });

  window.addEventListener("resize", () => {
    engine.resize();
    fitCamera(camera, canvas);
  });

  return {
    render
  };
}

function fitCamera(camera, canvas) {
  const width = Math.max(1, canvas.clientWidth);
  const height = Math.max(1, canvas.clientHeight);
  const aspect = width / height;
  const vertical = 17.6;
  camera.orthoTop = vertical / 2;
  camera.orthoBottom = -vertical / 2;
  camera.orthoRight = (vertical * aspect) / 2;
  camera.orthoLeft = -(vertical * aspect) / 2;
}
