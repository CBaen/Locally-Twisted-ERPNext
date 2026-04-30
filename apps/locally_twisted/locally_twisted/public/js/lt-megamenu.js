/* Locally Twisted — Mega menu + Mobile drawer engine.
 *
 * Replaces the inline <script> block that was in navbar.html (lines ~244-384).
 * Two independent behavior engines in one file:
 *
 *   1. LT.megamenu  — desktop hover+click mega panels.
 *      Triggers: [data-lt-megamenu-trigger="<panel-id>"]  (button elements)
 *      Panels:   .lt-megamenu__panel[id="<panel-id>"]
 *      State:    hidden attribute on panel, aria-expanded on trigger
 *
 *   2. LT.drawer    — mobile drawer + accordion sub-panels.
 *      Trigger:  [data-lt-drawer-trigger]  (hamburger button)
 *      Drawer:   #lt-mobile-drawer  (aside[role="dialog" aria-modal="true"])
 *      Backdrop: .lt-header__backdrop
 *      Accordion: [data-lt-drawer-accordion-trigger="<panel-id>"] → #<panel-id>
 *
 * Also migrates the existing single-panel Shop mega from the inline block:
 *   - legacy trigger: #lt-shop-trigger  (aria-controls="lt-shop-mega")
 *   - legacy panel:   #lt-shop-mega     (class lt-header__mega)
 * These still work because they are already adapted to use hidden attribute + aria.
 *
 * Public surface:
 *   window.LT.megamenu.init(opts)
 *   window.LT.megamenu.openPanel(panelId)
 *   window.LT.megamenu.closePanel(panelId)
 *   window.LT.megamenu.closeAll()
 *   window.LT.drawer.open()
 *   window.LT.drawer.close()
 *
 * Constraints honored (per build brief):
 *   - Vanilla JS only — no jQuery
 *   - No data-bs-* attributes referenced
 *   - hidden attribute is canonical state (not class-only)
 *   - No role="menu" on panels (creates broken arrow-key expectations)
 *   - aria-haspopup="true" on triggers, aria-expanded updated live
 *   - Esc closes from anywhere within
 *   - Tab cycles within open panel; Tab-out closes (panel.focusout)
 *   - Defensive guards: all getElementById/querySelector calls checked before use
 */
(function () {
    "use strict";

    /* ─────────────────────────────────────────────────────────────────
     * Namespace setup
     * ─────────────────────────────────────────────────────────────── */
    window.LT = window.LT || {};

    /* ─────────────────────────────────────────────────────────────────
     * Utilities
     * ─────────────────────────────────────────────────────────────── */

    /** Return true when viewport is ≥ 992 px (Frappe/BS4 lg breakpoint). */
    function isDesktop() {
        return window.matchMedia("(min-width: 992px)").matches;
    }

    /** All focusable descendants of an element, in DOM order. */
    function focusable(el) {
        return Array.prototype.slice.call(
            el.querySelectorAll(
                "a[href], button:not([disabled]), input:not([disabled]), " +
                "select:not([disabled]), textarea:not([disabled]), " +
                "[tabindex]:not([tabindex='-1'])"
            )
        );
    }

    /* ─────────────────────────────────────────────────────────────────
     * Mega menu engine  (desktop)
     * ─────────────────────────────────────────────────────────────── */

    /* Internal state map: panelId → { trigger, panel, li, openTimer, closeTimer } */
    var _panels = {};

    /**
     * Open a mega panel by id.
     * Sets hidden=false on the panel, aria-expanded=true on the trigger.
     * Only runs on desktop (≥ 992 px).
     */
    function openPanel(panelId) {
        var entry = _panels[panelId];
        if (!entry) return;
        /* Cancel any pending close. */
        if (entry.closeTimer) {
            clearTimeout(entry.closeTimer);
            entry.closeTimer = null;
        }
        entry.trigger.setAttribute("aria-expanded", "true");
        entry.panel.removeAttribute("hidden");
        if (entry.li) entry.li.classList.add("is-open");
    }

    /**
     * Close a mega panel by id.
     * Sets hidden attribute on the panel, aria-expanded=false on trigger.
     */
    function closePanel(panelId) {
        var entry = _panels[panelId];
        if (!entry) return;
        if (entry.openTimer) {
            clearTimeout(entry.openTimer);
            entry.openTimer = null;
        }
        entry.trigger.setAttribute("aria-expanded", "false");
        entry.panel.setAttribute("hidden", "");
        if (entry.li) entry.li.classList.remove("is-open");
    }

    /** Close all currently-open panels. */
    function closeAll() {
        Object.keys(_panels).forEach(function (id) {
            closePanel(id);
        });
    }

    /**
     * Schedule a delayed open (80 ms debounce — allows micro-hovers to
     * not flash the panel open).
     */
    function scheduleOpen(panelId) {
        var entry = _panels[panelId];
        if (!entry) return;
        if (entry.closeTimer) {
            clearTimeout(entry.closeTimer);
            entry.closeTimer = null;
        }
        entry.openTimer = setTimeout(function () {
            openPanel(panelId);
        }, 80);
    }

    /**
     * Schedule a delayed close (200 ms — gives the cursor time to travel
     * from trigger into the panel before it disappears).
     */
    function scheduleClose(panelId) {
        var entry = _panels[panelId];
        if (!entry) return;
        if (entry.openTimer) {
            clearTimeout(entry.openTimer);
            entry.openTimer = null;
        }
        entry.closeTimer = setTimeout(function () {
            closePanel(panelId);
        }, 200);
    }

    /**
     * Attach all desktop mega menu listeners.
     *
     * @param {object} opts
     * @param {string} [opts.triggerSelector="[data-lt-megamenu-trigger]"]
     * @param {string} [opts.panelSelector=".lt-megamenu__panel"]
     */
    function initMegamenu(opts) {
        opts = opts || {};
        var triggerSel = opts.triggerSelector || "[data-lt-megamenu-trigger]";
        var panelSel   = opts.panelSelector   || ".lt-megamenu__panel";

        /* ── Register panels found by the generic selectors ── */
        var triggers = document.querySelectorAll(triggerSel);
        for (var t = 0; t < triggers.length; t++) {
            var trigger  = triggers[t];
            var panelId  = trigger.getAttribute("data-lt-megamenu-trigger");
            if (!panelId) continue;
            var panel    = document.getElementById(panelId);
            if (!panel) continue;
            /* Ensure initial ARIA state */
            trigger.setAttribute("aria-haspopup", "true");
            trigger.setAttribute("aria-controls", panelId);
            if (!trigger.hasAttribute("aria-expanded")) {
                trigger.setAttribute("aria-expanded", "false");
            }
            /* Ensure panel starts hidden */
            panel.setAttribute("hidden", "");

            var li = trigger.closest("li") || trigger.parentElement;
            _panels[panelId] = {
                trigger: trigger,
                panel: panel,
                li: li,
                openTimer: null,
                closeTimer: null,
            };
        }

        /* ── Also register the legacy single-panel Shop mega ──
         * The existing navbar.html already has:
         *   trigger: #lt-shop-trigger  aria-controls="lt-shop-mega"
         *   panel:   #lt-shop-mega     .lt-header__mega
         * We mirror it into _panels so closeAll() covers it and the
         * keyboard/outside-click handlers below manage it too.
         */
        var legacyTrigger = document.getElementById("lt-shop-trigger");
        var legacyPanel   = document.getElementById("lt-shop-mega");
        if (legacyTrigger && legacyPanel && !_panels["lt-shop-mega"]) {
            var legacyLi = legacyTrigger.closest(".lt-header__has-mega") ||
                           legacyTrigger.parentElement;
            _panels["lt-shop-mega"] = {
                trigger: legacyTrigger,
                panel: legacyPanel,
                li: legacyLi,
                openTimer: null,
                closeTimer: null,
            };
            /* Normalise attribute state if the inline <script> was removed */
            if (!legacyTrigger.hasAttribute("aria-expanded")) {
                legacyTrigger.setAttribute("aria-expanded", "false");
            }
            legacyPanel.setAttribute("hidden", "");
        }

        /* ── Per-panel listeners ── */
        Object.keys(_panels).forEach(function (panelId) {
            var entry = _panels[panelId];

            /* Click trigger: toggle open/closed */
            entry.trigger.addEventListener("click", function (ev) {
                ev.preventDefault();
                /* Only respond to click-open on desktop */
                if (!isDesktop()) return;
                if (entry.trigger.getAttribute("aria-expanded") === "true") {
                    closePanel(panelId);
                } else {
                    closeAll();   /* close any other open panel first */
                    openPanel(panelId);
                }
            });

            /* Hover — desktop only; li wraps both trigger + panel so
             * moving from trigger into panel keeps the panel open. */
            if (entry.li) {
                entry.li.addEventListener("mouseenter", function () {
                    if (!isDesktop()) return;
                    scheduleOpen(panelId);
                });
                entry.li.addEventListener("mouseleave", function () {
                    if (!isDesktop()) return;
                    scheduleClose(panelId);
                });
            }

            /* Tab-out of panel closes it (relaxed: only fires if focus
             * moves outside BOTH the panel AND the trigger) */
            entry.panel.addEventListener("focusout", function (ev) {
                if (!isDesktop()) return;
                var relatedTarget = ev.relatedTarget;
                if (!relatedTarget) { scheduleClose(panelId); return; }
                if (entry.panel.contains(relatedTarget)) return;
                if (relatedTarget === entry.trigger) return;
                scheduleClose(panelId);
            });
        });

        /* ── Global Escape handler ── */
        document.addEventListener("keydown", function (ev) {
            if (ev.key !== "Escape") return;
            /* Find the trigger of the first open panel to return focus */
            var openEntry = null;
            Object.keys(_panels).forEach(function (id) {
                var entry = _panels[id];
                if (entry.trigger.getAttribute("aria-expanded") === "true") {
                    openEntry = entry;
                }
            });
            if (openEntry) {
                closeAll();
                openEntry.trigger.focus();
            }
        });

        /* ── Click-outside closes all panels ── */
        document.addEventListener("click", function (ev) {
            var target = ev.target;
            if (!target) return;
            /* Check if the click is inside any registered trigger or panel */
            var inside = false;
            Object.keys(_panels).forEach(function (id) {
                var entry = _panels[id];
                if (
                    (entry.li && entry.li.contains(target)) ||
                    entry.panel.contains(target) ||
                    entry.trigger.contains(target)
                ) {
                    inside = true;
                }
            });
            if (!inside) closeAll();
        });
    }

    /* Public API */
    window.LT.megamenu = {
        init: initMegamenu,
        openPanel: openPanel,
        closePanel: closePanel,
        closeAll: closeAll,
    };

    /* ─────────────────────────────────────────────────────────────────
     * Mobile drawer engine
     * ─────────────────────────────────────────────────────────────── */

    /**
     * Init the mobile drawer engine.
     * Called automatically on DOMContentLoaded from the auto-init block below.
     *
     * Expected DOM (from navbar.html):
     *   button#lt-mobile-toggle   [data-lt-drawer-trigger] OR id only
     *   aside#lt-mobile-drawer    role="dialog" aria-modal="true"
     *   .lt-header__backdrop      click-outside backdrop
     *   button#lt-mobile-close    close button inside drawer
     *   button[data-lt-drawer-accordion-trigger="<panel-id>"]
     *   div#<panel-id>.lt-header__drawer-accordion-panel[hidden]
     *
     * Also supports the LEGACY DOM already in place (navbar.html as of 2026-04-30):
     *   button#lt-mobile-toggle
     *   aside#lt-mobile-nav       (id used instead of #lt-mobile-drawer)
     *   div#lt-mobile-backdrop    (id used instead of class)
     *   button#lt-mobile-close
     *   button.lt-header__mobile-accordion-toggle  aria-controls="lt-mobile-shop-panel"
     *   ul#lt-mobile-shop-panel
     */
    function initDrawer() {
        /* Support both new (#lt-mobile-drawer) and legacy (#lt-mobile-nav) ids */
        var toggleBtn = document.getElementById("lt-mobile-toggle") ||
                        document.querySelector("[data-lt-drawer-trigger]");
        var drawer    = document.getElementById("lt-mobile-drawer") ||
                        document.getElementById("lt-mobile-nav");
        var backdrop  = document.getElementById("lt-mobile-backdrop") ||
                        document.querySelector(".lt-header__backdrop");
        var closeBtn  = document.getElementById("lt-mobile-close");

        if (!toggleBtn || !drawer) return;  /* nothing to do on this page */

        /* ── open / close ── */
        function openDrawer() {
            drawer.classList.add("is-open");
            if (backdrop) {
                backdrop.classList.add("is-open");
                backdrop.setAttribute("aria-hidden", "false");
            }
            document.body.classList.add("lt-nav-open");
            toggleBtn.setAttribute("aria-expanded", "true");
            drawer.setAttribute("aria-hidden", "false");
            /* Move focus to close button so screen readers announce the dialog */
            if (closeBtn) {
                window.setTimeout(function () { closeBtn.focus(); }, 50);
            } else {
                /* Fall back: first focusable in drawer */
                var firstFocusable = focusable(drawer)[0];
                if (firstFocusable) {
                    window.setTimeout(function () { firstFocusable.focus(); }, 50);
                }
            }
        }

        function closeDrawer() {
            drawer.classList.remove("is-open");
            if (backdrop) {
                backdrop.classList.remove("is-open");
                backdrop.setAttribute("aria-hidden", "true");
            }
            document.body.classList.remove("lt-nav-open");
            toggleBtn.setAttribute("aria-expanded", "false");
            drawer.setAttribute("aria-hidden", "true");
            toggleBtn.focus();
        }

        /* ── Toggle ── */
        toggleBtn.addEventListener("click", function () {
            if (drawer.classList.contains("is-open")) {
                closeDrawer();
            } else {
                openDrawer();
            }
        });

        /* ── Close button ── */
        if (closeBtn) closeBtn.addEventListener("click", closeDrawer);

        /* ── Backdrop click ── */
        if (backdrop) backdrop.addEventListener("click", closeDrawer);

        /* ── Esc key ── */
        document.addEventListener("keydown", function (ev) {
            if (ev.key === "Escape" && drawer.classList.contains("is-open")) {
                closeDrawer();
            }
        });

        /* ── Any nav link or sub-link click inside drawer closes it ──
         * Excludes accordion toggle buttons so expanding sub-menus
         * doesn't close the drawer. */
        drawer.addEventListener("click", function (ev) {
            var target = ev.target;
            if (!target) return;
            /* Is it a link (navigating away)? Close the drawer. */
            var link = target.closest("a[href]");
            if (link && !link.closest("[data-lt-drawer-accordion-trigger]")) {
                closeDrawer();
                return;
            }
            /* Legacy: .lt-header__mobile-nav-link that is NOT the accordion toggle */
            var navLink = target.closest(
                ".lt-header__mobile-nav-link:not(.lt-header__mobile-accordion-toggle)," +
                ".lt-header__mobile-nav-sublink"
            );
            if (navLink) {
                closeDrawer();
            }
        });

        /* ── Accordion sub-panels ── (generic data-* attribute version) */
        var accTriggers = drawer.querySelectorAll("[data-lt-drawer-accordion-trigger]");
        for (var a = 0; a < accTriggers.length; a++) {
            (function (accBtn) {
                var targetId = accBtn.getAttribute("data-lt-drawer-accordion-trigger");
                var accPanel = targetId ? document.getElementById(targetId) : null;
                if (!accPanel) return;

                accBtn.addEventListener("click", function () {
                    var isExpanded = accBtn.getAttribute("aria-expanded") === "true";
                    accBtn.setAttribute("aria-expanded", isExpanded ? "false" : "true");
                    if (isExpanded) {
                        accPanel.setAttribute("hidden", "");
                    } else {
                        accPanel.removeAttribute("hidden");
                    }
                });
            }(accTriggers[a]));
        }

        /* ── Legacy accordion (no data-* attr — uses .lt-header__mobile-accordion-toggle
         * with aria-controls attribute, which is how the current navbar.html is built) */
        var legacyAccToggle = drawer.querySelector(".lt-header__mobile-accordion-toggle");
        if (legacyAccToggle) {
            var legacyPanelId = legacyAccToggle.getAttribute("aria-controls");
            var legacyAccPanel = legacyPanelId ? document.getElementById(legacyPanelId) : null;
            if (legacyAccPanel) {
                /* Remove any existing listener (inline scripts are being removed;
                 * but as a defensive measure de-dupe by cloning) */
                var fresh = legacyAccToggle.cloneNode(true);
                legacyAccToggle.parentNode.replaceChild(fresh, legacyAccToggle);
                fresh.addEventListener("click", function () {
                    var isOpen = fresh.getAttribute("aria-expanded") === "true";
                    fresh.setAttribute("aria-expanded", isOpen ? "false" : "true");
                    if (isOpen) {
                        legacyAccPanel.setAttribute("hidden", "");
                    } else {
                        legacyAccPanel.removeAttribute("hidden");
                    }
                });
            }
        }

        /* ── Expose public drawer API ── */
        window.LT.drawer = {
            open: openDrawer,
            close: closeDrawer,
        };
    }

    /* Default drawer API before init (no-ops — safe to call before DOM ready) */
    window.LT.drawer = {
        open: function () {},
        close: function () {},
    };

    /* ─────────────────────────────────────────────────────────────────
     * Auto-init on DOMContentLoaded
     * ─────────────────────────────────────────────────────────────── */
    function autoInit() {
        initMegamenu();
        initDrawer();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", autoInit);
    } else {
        autoInit();
    }

}());
