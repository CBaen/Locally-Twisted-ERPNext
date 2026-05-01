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

  // Webshop renders #list / #image-view buttons asynchronously after page
  // load. A timeout-based re-apply has a race with axe-core (and any other
  // a11y check that runs before the timeout fires). MutationObserver applies
  // labels the instant the buttons appear in the DOM — no race window.
  const observer = new MutationObserver(function (mutations) {
    for (const m of mutations) {
      for (const node of m.addedNodes) {
        if (node.nodeType !== 1) continue;
        if (
          node.id === "list" ||
          node.id === "image-view" ||
          (node.querySelector && (node.querySelector("#list") || node.querySelector("#image-view")))
        ) {
          apply();
          return;
        }
      }
    }
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });

  // Disconnect after 5s — webshop's late renders are well over by then.
  setTimeout(function () { observer.disconnect(); }, 5000);
})();
