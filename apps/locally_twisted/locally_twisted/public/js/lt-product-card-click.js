(function () {
  "use strict";

  var CARD_SELECTOR = ".lt-shop__card, #products-grid-area .item-card";
  var INTERACTIVE_SELECTOR = [
    "a",
    "button",
    "input",
    "select",
    "textarea",
    "label",
    "summary",
    "[role='button']",
    "[contenteditable='true']",
    "[data-no-card-click]",
  ].join(",");

  function isProductHref(href) {
    if (!href) {
      return false;
    }

    try {
      var url = new URL(href, window.location.href);
      return url.origin === window.location.origin && url.pathname.indexOf("/shop-items/") === 0;
    } catch (error) {
      return false;
    }
  }

  function getCardLink(card) {
    var preferredSelectors = [
      ".lt-shop__card-image[href]",
      ".lt-shop__card-name a[href]",
      ".product-image a[href]",
      ".product-title a[href]",
      ".card-title a[href]",
      "a[href]",
    ];

    for (var i = 0; i < preferredSelectors.length; i += 1) {
      var link = card.querySelector(preferredSelectors[i]);
      if (link && isProductHref(link.getAttribute("href"))) {
        return link;
      }
    }

    return null;
  }

  function markCards(root) {
    var scope = root && root.querySelectorAll ? root : document;
    if (scope.matches && scope.matches(CARD_SELECTOR)) {
      scope.classList.toggle("lt-product-card-clickable", !!getCardLink(scope));
    }
    scope.querySelectorAll(CARD_SELECTOR).forEach(function (card) {
      card.classList.toggle("lt-product-card-clickable", !!getCardLink(card));
    });
  }

  function isModifiedClick(event) {
    return event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
  }

  function hasSelectedText() {
    var selection = window.getSelection && window.getSelection();
    return !!selection && selection.toString().trim().length > 0;
  }

  function handleCardClick(event) {
    if (event.defaultPrevented || isModifiedClick(event) || hasSelectedText()) {
      return;
    }

    var target = event.target;
    if (!(target instanceof Element)) {
      return;
    }

    var card = target.closest(CARD_SELECTOR);
    if (!card) {
      return;
    }

    var interactive = target.closest(INTERACTIVE_SELECTOR);
    if (interactive && card.contains(interactive)) {
      return;
    }

    var link = getCardLink(card);
    if (link) {
      window.location.href = link.href;
    }
  }

  function initProductCardClick() {
    markCards(document);
    document.addEventListener("click", handleCardClick);
    document.addEventListener("product_list_update", function () {
      markCards(document);
    });

    if (!document.body) {
      return;
    }

    var observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (node instanceof Element) {
            markCards(node);
          }
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initProductCardClick, { once: true });
  } else {
    initProductCardClick();
  }
})();
