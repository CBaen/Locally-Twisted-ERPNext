/* lt-webshop-a11y.js
 * Patches webshop's default rendering to add aria-labels to icon-only
 * view-toggle buttons and inject a visually-hidden h1 on /all-products.
 * Idempotent; no-ops when targets are absent.
 */
(function () {
  "use strict";

  function apply() {
    const list = document.querySelector("#list");
    const grid = document.querySelector("#image-view");
    if (list && !list.hasAttribute("aria-label")) {
      list.setAttribute("aria-label", "List view");
    }
    if (grid && !grid.hasAttribute("aria-label")) {
      grid.setAttribute("aria-label", "Grid view");
    }

    if (window.location.pathname === "/all-products" && !document.querySelector("h1")) {
      const h1 = document.createElement("h1");
      h1.textContent = "All Products";
      h1.className = "visually-hidden";
      const target = document.querySelector("main") || document.body;
      target.insertBefore(h1, target.firstChild);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", apply);
  } else {
    apply();
  }
  // Webshop renders some elements asynchronously — re-apply after a couple of ticks.
  setTimeout(apply, 500);
  setTimeout(apply, 1500);
})();
