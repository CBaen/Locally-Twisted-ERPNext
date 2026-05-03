import { createEventBuilderPage } from "./shared-ui.js";
import { createPlayCanvasRenderer } from "./render-playcanvas.js";

createEventBuilderPage({
  engine: "playcanvas",
  engineLabel: "PlayCanvas",
  createRenderer: createPlayCanvasRenderer
});
