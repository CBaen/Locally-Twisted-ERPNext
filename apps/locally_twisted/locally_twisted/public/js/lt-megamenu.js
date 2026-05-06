(function () {
    "use strict";

    var DESKTOP_QUERY = "(min-width: 1200px)";
    var desktopMedia = window.matchMedia ? window.matchMedia(DESKTOP_QUERY) : null;
    var closeDelay = 180;
    var timers = {};

    function isDesktop() {
        return !desktopMedia || desktopMedia.matches;
    }

    function focusable(root) {
        return Array.prototype.slice.call(root.querySelectorAll(
            "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), " +
            "textarea:not([disabled]), [tabindex]:not([tabindex='-1'])"
        ));
    }

    function panelEntries() {
        return Array.prototype.slice.call(document.querySelectorAll("[data-lt-megamenu-trigger]"))
            .map(function (trigger) {
                var panelId = trigger.getAttribute("data-lt-megamenu-trigger");
                var panel = panelId ? document.getElementById(panelId) : null;
                if (!panel) return null;
                return {
                    id: panelId,
                    trigger: trigger,
                    panel: panel,
                    item: trigger.closest(".lt-mega-nav__item")
                };
            })
            .filter(Boolean);
    }

    function setPanel(entry, open) {
        entry.trigger.setAttribute("aria-expanded", open ? "true" : "false");
        entry.panel.toggleAttribute("hidden", !open);
        if (entry.item) {
            entry.item.classList.toggle("is-open", open);
            if (!open) entry.item.removeAttribute("data-lt-mega-pinned");
        }
    }

    function closeAll(exceptId) {
        panelEntries().forEach(function (entry) {
            if (entry.id !== exceptId) setPanel(entry, false);
        });
    }

    function openPanel(entry) {
        if (!isDesktop()) return;
        window.clearTimeout(timers[entry.id]);
        closeAll(entry.id);
        setPanel(entry, true);
    }

    function scheduleClose(entry) {
        if (entry.item && entry.item.getAttribute("data-lt-mega-pinned") === "true") return;
        window.clearTimeout(timers[entry.id]);
        timers[entry.id] = window.setTimeout(function () {
            if (entry.item && entry.item.getAttribute("data-lt-mega-pinned") === "true") return;
            setPanel(entry, false);
        }, closeDelay);
    }

    function initMegaMenus() {
        panelEntries().forEach(function (entry) {
            entry.trigger.setAttribute("aria-haspopup", "true");
            entry.trigger.setAttribute("aria-controls", entry.id);
            entry.trigger.setAttribute("aria-expanded", "false");
            entry.panel.setAttribute("hidden", "");

            entry.trigger.addEventListener("click", function (event) {
                event.preventDefault();
                if (!isDesktop()) return;
                var isOpen = entry.trigger.getAttribute("aria-expanded") === "true";
                var isPinned = entry.item && entry.item.getAttribute("data-lt-mega-pinned") === "true";
                if (isOpen && isPinned) {
                    setPanel(entry, false);
                } else {
                    if (entry.item) entry.item.setAttribute("data-lt-mega-pinned", "true");
                    openPanel(entry);
                }
            });

            if (entry.item) {
                entry.item.addEventListener("mouseenter", function () {
                    if (isDesktop()) openPanel(entry);
                });
                entry.item.addEventListener("mouseleave", function () {
                    if (isDesktop()) scheduleClose(entry);
                });
            }

            entry.panel.addEventListener("focusout", function (event) {
                if (!isDesktop()) return;
                var next = event.relatedTarget;
                if (!next || (!entry.panel.contains(next) && next !== entry.trigger)) {
                    scheduleClose(entry);
                }
            });

            entry.panel.addEventListener("click", function (event) {
                if (event.target.closest("a[href]")) {
                    closeAll();
                }
            });
        });

        document.addEventListener("click", function (event) {
            var target = event.target;
            var inside = panelEntries().some(function (entry) {
                return entry.trigger.contains(target) || entry.panel.contains(target);
            });
            if (!inside) closeAll();
        });

        document.addEventListener("keydown", function (event) {
            if (event.key !== "Escape") return;
            var openEntry = panelEntries().find(function (entry) {
                return entry.trigger.getAttribute("aria-expanded") === "true";
            });
            if (openEntry) {
                closeAll();
                openEntry.trigger.focus();
            }
        });

        if (desktopMedia && desktopMedia.addEventListener) {
            desktopMedia.addEventListener("change", function () {
                closeAll();
            });
        }

        window.addEventListener("scroll", function () {
            closeAll();
        }, { passive: true });
    }

    function initDrawer() {
        var toggle = document.getElementById("lt-mobile-toggle");
        var drawer = document.getElementById("lt-mobile-nav");
        var backdrop = document.getElementById("lt-mobile-backdrop");
        var close = document.getElementById("lt-mobile-close");
        if (!toggle || !drawer) return;

        function openDrawer() {
            drawer.classList.add("is-open");
            drawer.setAttribute("aria-hidden", "false");
            toggle.setAttribute("aria-expanded", "true");
            document.body.classList.add("lt-nav-open");
            if (backdrop) {
                backdrop.classList.add("is-open");
                backdrop.setAttribute("aria-hidden", "false");
            }
            window.setTimeout(function () {
                (close || focusable(drawer)[0] || drawer).focus();
            }, 40);
        }

        function closeDrawer(returnFocus) {
            drawer.classList.remove("is-open");
            drawer.setAttribute("aria-hidden", "true");
            toggle.setAttribute("aria-expanded", "false");
            document.body.classList.remove("lt-nav-open");
            if (backdrop) {
                backdrop.classList.remove("is-open");
                backdrop.setAttribute("aria-hidden", "true");
            }
            if (returnFocus !== false) toggle.focus();
        }

        toggle.addEventListener("click", function () {
            if (drawer.classList.contains("is-open")) {
                closeDrawer();
            } else {
                openDrawer();
            }
        });

        if (close) close.addEventListener("click", closeDrawer);
        if (backdrop) backdrop.addEventListener("click", closeDrawer);

        drawer.addEventListener("click", function (event) {
            var accordion = event.target.closest("[data-lt-drawer-accordion-trigger]");
            if (accordion) {
                var panelId = accordion.getAttribute("data-lt-drawer-accordion-trigger");
                var panel = panelId ? document.getElementById(panelId) : null;
                if (!panel) return;
                var expanded = accordion.getAttribute("aria-expanded") === "true";
                accordion.setAttribute("aria-expanded", expanded ? "false" : "true");
                panel.toggleAttribute("hidden", expanded);
                return;
            }

            if (event.target.closest("a[href]")) {
                closeDrawer(false);
            }
        });

        drawer.addEventListener("keydown", function (event) {
            if (event.key !== "Tab") return;
            var items = focusable(drawer);
            if (!items.length) return;
            var first = items[0];
            var last = items[items.length - 1];
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && drawer.classList.contains("is-open")) {
                closeDrawer();
            }
        });

        window.LT = window.LT || {};
        window.LT.drawer = { open: openDrawer, close: closeDrawer };
    }

    function init() {
        initMegaMenus();
        initDrawer();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}());
