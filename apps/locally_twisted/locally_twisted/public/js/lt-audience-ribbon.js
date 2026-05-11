/*
 * lt-audience-ribbon.js
 *
 * Mobile-only seamless-loop slider for the "In Collaboration With" ribbon on
 * audience-lane pages (corporate-events, civic-community, private-celebrations,
 * schools-campuses).
 *
 * How it works:
 *   1. Find each [data-lt-collab-ribbon] container.
 *   2. On mobile, clone the names list 2x so we have 3 identical copies.
 *   3. Set initial scrollLeft to the start of the middle copy.
 *   4. On scroll, when the user nears the left or right edge, silently teleport
 *      scrollLeft back to the equivalent position in the middle copy. The jump
 *      is between identical content so the user perceives an infinite loop in
 *      either direction.
 *   5. On desktop, leave the DOM unmodified and let the natural flex-wrap
 *      layout handle things.
 *
 * Touch swipe works natively via overflow-x:auto. Mouse drag on touch screens
 * works the same. Keyboard: Tab still navigates through the original names.
 *
 * Re-runs on resize so a window crossing the breakpoint cleans up correctly.
 */

(function () {
    'use strict';

    var MOBILE_MAX = 767;
    var EDGE_BUFFER = 16;     // px - how close to an edge before we teleport
    var INITED_FLAG = 'ltCollabInited';
    var ORIGCOUNT_KEY = 'ltCollabOriginalCount';

    function isMobile() {
        return window.innerWidth <= MOBILE_MAX;
    }

    function measureCopyWidth(container, originalCount) {
        // Sum bounding-box widths of the first `originalCount` children plus
        // the column-gap between them.
        var total = 0;
        for (var i = 0; i < originalCount; i++) {
            var child = container.children[i];
            if (!child) continue;
            total += child.getBoundingClientRect().width;
        }
        var styles = window.getComputedStyle(container);
        var gapStr = styles.columnGap || styles.gap || '0';
        var gap = parseFloat(gapStr);
        if (!isNaN(gap) && gap > 0) {
            total += gap * Math.max(0, originalCount - 1);
        }
        return total;
    }

    function setup(container) {
        if (container.dataset[INITED_FLAG] === '1') return;
        var originals = Array.prototype.slice.call(container.children);
        if (originals.length === 0) return;

        if (!container.dataset[ORIGCOUNT_KEY]) {
            container.dataset[ORIGCOUNT_KEY] = String(originals.length);
        }

        // Clone the names list twice.
        var frag = document.createDocumentFragment();
        for (var copy = 0; copy < 2; copy++) {
            for (var i = 0; i < originals.length; i++) {
                var clone = originals[i].cloneNode(true);
                clone.setAttribute('aria-hidden', 'true');
                clone.dataset.ltCollabClone = '1';
                frag.appendChild(clone);
            }
        }
        container.appendChild(frag);

        container.dataset[INITED_FLAG] = '1';

        // Position the user at the middle copy on first paint.
        var positionToMiddle = function () {
            var copyWidth = measureCopyWidth(container, originals.length);
            container.scrollLeft = copyWidth;
            container.dataset.ltCollabCopyWidth = String(copyWidth);
        };
        // Wait one frame so layout has settled after the clones were appended.
        window.requestAnimationFrame(positionToMiddle);

        // Teleport handler.
        var teleporting = false;
        var onScroll = function () {
            if (teleporting) return;
            var copyWidth = parseFloat(container.dataset.ltCollabCopyWidth || '0');
            if (!copyWidth || copyWidth < 1) return;
            var current = container.scrollLeft;
            var maxScroll = container.scrollWidth - container.clientWidth;
            if (current < EDGE_BUFFER) {
                // Near the left end of the first copy -> jump forward by one
                // copy width into the second (middle) copy.
                teleporting = true;
                container.scrollLeft = current + copyWidth;
                window.requestAnimationFrame(function () { teleporting = false; });
            } else if (current > maxScroll - EDGE_BUFFER) {
                // Near the right end of the third copy -> jump back by one
                // copy width into the second (middle) copy.
                teleporting = true;
                container.scrollLeft = current - copyWidth;
                window.requestAnimationFrame(function () { teleporting = false; });
            }
        };
        container.addEventListener('scroll', onScroll, { passive: true });
        container._ltCollabScrollHandler = onScroll;

        // Re-measure copy width if fonts load late or content reflows.
        if (document.fonts && document.fonts.ready && typeof document.fonts.ready.then === 'function') {
            document.fonts.ready.then(function () {
                window.requestAnimationFrame(positionToMiddle);
            }).catch(function () { /* ignore */ });
        }
    }

    function teardown(container) {
        if (container.dataset[INITED_FLAG] !== '1') return;
        var originalCount = parseInt(container.dataset[ORIGCOUNT_KEY] || '0', 10);
        if (originalCount > 0) {
            while (container.children.length > originalCount) {
                container.removeChild(container.lastElementChild);
            }
        }
        if (container._ltCollabScrollHandler) {
            container.removeEventListener('scroll', container._ltCollabScrollHandler);
            container._ltCollabScrollHandler = null;
        }
        container.scrollLeft = 0;
        delete container.dataset[INITED_FLAG];
        delete container.dataset.ltCollabCopyWidth;
    }

    function refreshAll() {
        var ribbons = document.querySelectorAll('[data-lt-collab-ribbon]');
        for (var i = 0; i < ribbons.length; i++) {
            var ribbon = ribbons[i];
            if (!ribbon.dataset[ORIGCOUNT_KEY]) {
                ribbon.dataset[ORIGCOUNT_KEY] = String(ribbon.children.length);
            }
            if (isMobile()) {
                setup(ribbon);
            } else {
                teardown(ribbon);
            }
        }
    }

    function debounce(fn, ms) {
        var t;
        return function () {
            var args = arguments;
            var ctx = this;
            clearTimeout(t);
            t = setTimeout(function () { fn.apply(ctx, args); }, ms);
        };
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', refreshAll);
    } else {
        refreshAll();
    }
    window.addEventListener('resize', debounce(refreshAll, 200), { passive: true });
})();
