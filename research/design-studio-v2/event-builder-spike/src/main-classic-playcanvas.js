import { createClassicBuilderPage } from "./classic-builder-ui.js";
import { createClassicPlayCanvasRenderer } from "./render-classic-playcanvas.js";

createClassicBuilderPage({
  createRenderer: createClassicPlayCanvasRenderer
});
