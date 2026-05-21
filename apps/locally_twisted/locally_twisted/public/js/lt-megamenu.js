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

    function initSearchOverlay() {
        var panel = document.getElementById("lt-site-search-panel");
        var toggles = Array.prototype.slice.call(document.querySelectorAll("[data-lt-search-toggle]"));
        if (!panel || !toggles.length) return;

        var form = panel.querySelector("form");
        var input = panel.querySelector("[data-lt-search-input]");
        var entries = Array.prototype.slice.call(panel.querySelectorAll("[data-lt-search-entry]"));
        var empty = panel.querySelector("[data-lt-search-empty]");
        var lastToggle = null;

        function setExpanded(open) {
            toggles.forEach(function (toggle) {
                toggle.setAttribute("aria-expanded", open ? "true" : "false");
            });
        }

        function isOpen() {
            return !panel.hasAttribute("hidden");
        }

        function filterEntries() {
            var query = input ? input.value.trim().toLowerCase() : "";
            var terms = query.split(/\s+/).filter(Boolean);
            var visible = 0;

            entries.forEach(function (entry) {
                var text = (
                    (entry.textContent || "") + " " + (entry.getAttribute("data-lt-search-keywords") || "")
                ).toLowerCase();
                var isReadyOrderEntry = entry.hasAttribute("data-lt-search-ready-order-entry");
                var matched = terms.length ? terms.every(function (term) {
                    return text.indexOf(term) !== -1;
                }) : !isReadyOrderEntry;
                entry.toggleAttribute("hidden", !matched);
                if (matched) visible += 1;
            });

            if (empty) empty.toggleAttribute("hidden", visible > 0);
        }

        function openSearch(toggle) {
            lastToggle = toggle || lastToggle;
            closeAll();
            var drawer = document.getElementById("lt-mobile-nav");
            if (
                drawer &&
                drawer.classList.contains("is-open") &&
                window.LT &&
                window.LT.drawer &&
                typeof window.LT.drawer.close === "function"
            ) {
                window.LT.drawer.close(false);
            }
            panel.removeAttribute("hidden");
            setExpanded(true);
            filterEntries();
            window.setTimeout(function () {
                if (input) input.focus();
            }, 30);
        }

        function closeSearch(returnFocus) {
            panel.setAttribute("hidden", "");
            setExpanded(false);
            if (returnFocus !== false && lastToggle) {
                lastToggle.focus();
            }
        }

        toggles.forEach(function (toggle) {
            toggle.addEventListener("click", function (event) {
                event.preventDefault();
                if (isOpen()) {
                    closeSearch(true);
                } else {
                    openSearch(toggle);
                }
            });
        });

        if (input) {
            input.addEventListener("input", filterEntries);
        }

        if (form) {
            form.addEventListener("submit", function (event) {
                if (input && !input.value.trim()) {
                    event.preventDefault();
                    openSearch(lastToggle);
                }
            });
        }

        panel.addEventListener("click", function (event) {
            if (event.target.closest("a[href]")) {
                closeSearch(false);
            }
        });

        document.addEventListener("click", function (event) {
            if (!isOpen()) return;
            var target = event.target;
            var clickedToggle = toggles.some(function (toggle) {
                return toggle.contains(target);
            });
            if (!clickedToggle && !panel.contains(target)) {
                closeSearch(false);
            }
        });

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape" && isOpen()) {
                closeSearch(true);
            }
        });

        setExpanded(false);
        filterEntries();
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
        initSearchOverlay();
        initDrawer();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}());
