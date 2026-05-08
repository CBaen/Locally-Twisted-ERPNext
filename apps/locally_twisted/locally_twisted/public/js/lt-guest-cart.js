/* Locally Twisted — guest cart engine.
 *
 * Webshop's stock cart is bound to a Quotation -> Customer -> User and
 * forces guests to /login before any cart action. GL's product rule:
 * sign-in is optional, never blocking. So we run a parallel cart in
 * localStorage that survives across product pages, /cart, and checkout.
 *
 * The server-side Quotation/Customer/Sales-Order is created ONCE at
 * checkout submit (see www/checkout.py submit_guest_order). Until then
 * the cart lives entirely in the browser.
 *
 * Public surface:
 *   LT_CART.getCart()        -> {items: [{item_code, qty}], updated_at}
 *   LT_CART.getCount()       -> total number of items (sum of qtys)
 *   LT_CART.add(code, qty)   -> add or increment a line
 *   LT_CART.update(code, q)  -> set qty to q (q<=0 removes the line)
 *   LT_CART.remove(code)     -> drop a line
 *   LT_CART.clear()          -> empty the cart (call after order submit)
 *   LT_CART.subscribe(fn)    -> register a listener; fn(cart) on every change
 *
 * Webshop overrides applied at load:
 *   - webshop.webshop.shopping_cart.update_cart -> route to LT_CART.add
 *   - capture-phase click handler on .btn-add-to-cart-list -> LT_CART.add,
 *     stops propagation so webshop's bubble-phase login redirect never fires
 */
(function () {
    "use strict";

    var STORAGE_KEY = "lt_cart";
    var SCHEMA_VERSION = 1;
    var MAX_QTY_PER_LINE = 99;
    var CHANGE_EVENT = "lt-cart-change";
    var ADD_TO_CART_FAILURE = "Tiny snag: we could not add that to your cart just now. Please try once more or call (801) 285-0860.";

    // In-memory fallback for when localStorage is unavailable
    // (Safari Private Mode, browsers with storage disabled). Cart persists
    // for the page session only — gone on next page load.
    var memoryCart = null;
    var storageAvailable = (function () {
        try {
            var t = "__lt_test__";
            window.localStorage.setItem(t, t);
            window.localStorage.removeItem(t);
            return true;
        } catch (err) {
            return false;
        }
    })();

    function nowIso() {
        return new Date().toISOString();
    }

    function emptyCart() {
        return { v: SCHEMA_VERSION, items: [], updated_at: nowIso() };
    }

    function readRaw() {
        if (!storageAvailable) {
            return memoryCart || emptyCart();
        }
        var raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) return emptyCart();
        try {
            var parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== "object") return emptyCart();
            if (parsed.v !== SCHEMA_VERSION) return emptyCart();
            if (!Array.isArray(parsed.items)) return emptyCart();
            // Drop malformed entries silently rather than discard the whole cart.
            var clean = [];
            for (var i = 0; i < parsed.items.length; i++) {
                var it = parsed.items[i];
                if (!it || typeof it.item_code !== "string" || !it.item_code) continue;
                var q = parseInt(it.qty, 10);
                if (!isFinite(q) || q < 1) continue;
                if (q > MAX_QTY_PER_LINE) q = MAX_QTY_PER_LINE;
                clean.push({ item_code: it.item_code, qty: q });
            }
            return { v: SCHEMA_VERSION, items: clean, updated_at: parsed.updated_at || nowIso() };
        } catch (err) {
            // Corrupted JSON. Reset; do not crash the page.
            console.warn("[lt-cart] corrupted storage, resetting:", err);
            return emptyCart();
        }
    }

    function writeRaw(cart) {
        cart.updated_at = nowIso();
        if (!storageAvailable) {
            memoryCart = cart;
        } else {
            try {
                window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
            } catch (err) {
                // Quota exceeded or other failure — fall back to memory.
                console.warn("[lt-cart] storage write failed, falling back to memory:", err);
                memoryCart = cart;
            }
        }
        notifyChange(cart);
    }

    var listeners = [];
    function notifyChange(cart) {
        // Same-tab listeners.
        for (var i = 0; i < listeners.length; i++) {
            try { listeners[i](cart); } catch (err) {
                console.error("[lt-cart] listener threw:", err);
            }
        }
        // Cross-document custom event (lets template inline scripts react).
        try {
            document.dispatchEvent(new CustomEvent(CHANGE_EVENT, { detail: cart }));
        } catch (err) { /* IE fallback unneeded — Frappe v15 ships modern only */ }
    }

    function findLine(cart, itemCode) {
        for (var i = 0; i < cart.items.length; i++) {
            if (cart.items[i].item_code === itemCode) return i;
        }
        return -1;
    }

    var LT_CART = {
        getCart: function () { return readRaw(); },

        getCount: function () {
            var cart = readRaw();
            var total = 0;
            for (var i = 0; i < cart.items.length; i++) total += cart.items[i].qty;
            return total;
        },

        add: function (itemCode, qty) {
            if (!itemCode || typeof itemCode !== "string") {
                throw new Error("LT_CART.add: item_code is required");
            }
            qty = parseInt(qty, 10);
            if (!isFinite(qty) || qty < 1) qty = 1;

            var cart = readRaw();
            var idx = findLine(cart, itemCode);
            if (idx >= 0) {
                cart.items[idx].qty = Math.min(cart.items[idx].qty + qty, MAX_QTY_PER_LINE);
            } else {
                cart.items.push({ item_code: itemCode, qty: Math.min(qty, MAX_QTY_PER_LINE) });
            }
            writeRaw(cart);
            return cart;
        },

        update: function (itemCode, qty) {
            qty = parseInt(qty, 10);
            var cart = readRaw();
            var idx = findLine(cart, itemCode);
            if (idx < 0) return cart;
            if (!isFinite(qty) || qty < 1) {
                cart.items.splice(idx, 1);
            } else {
                cart.items[idx].qty = Math.min(qty, MAX_QTY_PER_LINE);
            }
            writeRaw(cart);
            return cart;
        },

        remove: function (itemCode) {
            var cart = readRaw();
            var idx = findLine(cart, itemCode);
            if (idx < 0) return cart;
            cart.items.splice(idx, 1);
            writeRaw(cart);
            return cart;
        },

        clear: function () {
            var cart = emptyCart();
            writeRaw(cart);
            return cart;
        },

        subscribe: function (fn) {
            if (typeof fn !== "function") return function () {};
            listeners.push(fn);
            return function unsubscribe() {
                var i = listeners.indexOf(fn);
                if (i >= 0) listeners.splice(i, 1);
            };
        },

        _storageAvailable: storageAvailable,
    };

    // Expose globally and on the webshop namespace for any code that
    // already references it.
    window.LT_CART = LT_CART;

    // Cross-tab sync — Storage event fires on OTHER tabs when this tab
    // writes. We re-emit our same-tab change event so badges/views update.
    if (storageAvailable) {
        window.addEventListener("storage", function (ev) {
            if (ev.key !== STORAGE_KEY) return;
            notifyChange(readRaw());
        });
    }

    /* ── Webshop overrides ────────────────────────────────────────────
     *
     * Webshop bundles ship before our app's web_include_js. So at the
     * time our script runs, `webshop.webshop.shopping_cart` is already
     * defined. We patch the two functions that hard-redirect guests.
     *
     * If the namespace isn't there yet (e.g. our script loaded before
     * webshop's), we retry on a short interval until it shows up.
     * Capped at 5s so we don't run a forever-loop on pages where
     * webshop isn't loaded at all (which is fine — those pages don't
     * have webshop cart buttons).
     */
    function patchWebshopUpdateCart() {
        var ns = window.webshop && window.webshop.webshop && window.webshop.webshop.shopping_cart;
        if (!ns) return false;

        // Replace update_cart with our localStorage-based add.
        ns.update_cart = function (opts) {
            opts = opts || {};
            if (!opts.item_code) return;
            try {
                LT_CART.add(opts.item_code, opts.qty || 1);
                if (typeof opts.callback === "function") {
                    opts.callback({ message: { item_code: opts.item_code } });
                }
                // Keep webshop's cart_count cookie in sync so its
                // existing badge code reads the right number even if
                // the page hasn't been told about LT_CART yet.
                try {
                    document.cookie = "cart_count=" + LT_CART.getCount() + "; path=/; SameSite=Lax";
                } catch (err) { /* ignore cookie write failures */ }
            } catch (err) {
                console.error("[lt-cart] add failed:", err);
                if (typeof window.frappe !== "undefined" && window.frappe.show_alert) {
                    window.frappe.show_alert({
                        message: ADD_TO_CART_FAILURE,
                        indicator: "red",
                    }, 5);
                }
            }
        };
        return true;
    }

    var patchAttempts = 0;
    function tryPatch() {
        if (patchWebshopUpdateCart()) return;
        if (++patchAttempts > 100) return;  // 100 * 50ms = 5s ceiling
        setTimeout(tryPatch, 50);
    }
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", tryPatch);
    } else {
        tryPatch();
    }

    // Capture-phase click intercept for webshop's stock product list
    // buttons (.btn-add-to-cart-list). Runs BEFORE webshop's bubble-phase
    // listener, so its login redirect never fires.
    document.addEventListener("click", function (ev) {
        var target = ev.target;
        if (!target || !target.closest) return;
        var btn = target.closest(".btn-add-to-cart-list");
        if (!btn) return;

        // Walk up to find data-item-code; webshop puts it on the button.
        var itemCode = btn.dataset && btn.dataset.itemCode;
        if (!itemCode) {
            // Webshop sometimes puts it on a parent. Look one level up.
            var parent = btn.closest("[data-item-code]");
            if (parent) itemCode = parent.dataset.itemCode;
        }
        if (!itemCode) return;

        ev.stopImmediatePropagation();
        ev.preventDefault();

        try {
            LT_CART.add(itemCode, 1);
            // Visual feedback on the button itself: webshop's class swap
            // already moves things between hidden/visible; mimic the
            // "now in cart" state by triggering its own UI toggles.
            btn.classList.add("hidden");
            var container = btn.closest(".cart-action-container");
            if (container) container.classList.add("d-flex");
            var sibling = btn.parentElement && btn.parentElement.querySelector(".go-to-cart, .go-to-cart-grid, .cart-indicator");
            if (sibling) sibling.classList.remove("hidden");
            // Toast confirmation.
            if (typeof window.frappe !== "undefined" && window.frappe.show_alert) {
                window.frappe.show_alert({ message: "Added to cart.", indicator: "green" }, 3);
            }
        } catch (err) {
            console.error("[lt-cart] capture-phase add failed:", err);
            if (typeof window.frappe !== "undefined" && window.frappe.show_alert) {
                window.frappe.show_alert({
                    message: ADD_TO_CART_FAILURE,
                    indicator: "red",
                }, 5);
            }
        }
    }, true);  // capture phase

    // Cart count badge subscriber. Any element with id="lt-cart-count"
    // (or class .lt-cart-count) gets its text content updated on every
    // cart change. Lets the navbar render a server-side 0 and have it
    // hydrate to the real count on load + stay live across changes.
    function paintBadges(cart) {
        var count = 0;
        if (cart && Array.isArray(cart.items)) {
            for (var i = 0; i < cart.items.length; i++) count += cart.items[i].qty;
        } else {
            count = LT_CART.getCount();
        }
        var nodes = document.querySelectorAll("#lt-cart-count, .lt-cart-count");
        nodes.forEach(function (n) {
            n.textContent = count > 0 ? String(count) : "";
            if (count > 0) n.classList.add("is-populated");
            else n.classList.remove("is-populated");
        });
    }
    LT_CART.subscribe(paintBadges);
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () { paintBadges(LT_CART.getCart()); });
    } else {
        paintBadges(LT_CART.getCart());
    }
})();
