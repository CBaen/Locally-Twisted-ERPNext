import { createEventBuilderPage } from "./shared-ui.js";
import { createBabylonRenderer } from "./render-babylon.js";

createEventBuilderPage({
  engine: "babylon",
  engineLabel: "Babylon.js",
  createRenderer: createBabylonRenderer
});
