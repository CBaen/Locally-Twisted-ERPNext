(function () {
  "use strict";

  if (window.matchMedia("(hover: none), (pointer: coarse)").matches) {
    return;
  }

  var rootElement = document.documentElement;
  var cursor = document.createElement("div");
  cursor.className = "lt-balloon-cursor";
  cursor.setAttribute("aria-hidden", "true");
  cursor.innerHTML = [
    '<svg width="29" height="47.6" viewBox="0 0 56 92" fill="none" xmlns="http://www.w3.org/2000/svg">',
    '<path class="lt-balloon-cursor__string" d="M28 92 C 28 78, 28 70, 28 62" stroke="#191817" stroke-width="1" stroke-linecap="round" fill="none" opacity="0.55"/>',
    '<path class="lt-balloon-cursor__knot" d="M24 60 L32 60 L28 66 Z" fill="#7a0d20"/>',
    '<ellipse class="lt-balloon-cursor__body" cx="28" cy="32" rx="22" ry="28" fill="#b31b34"/>',
    '<path class="lt-balloon-cursor__shade" d="M50 32 C 50 50, 40 60, 28 60 C 36 56, 44 46, 44 30 C 44 22, 42 16, 40 12 C 47 18, 50 25, 50 32 Z" fill="#7a0d20" opacity="0.55"/>',
    '<ellipse class="lt-balloon-cursor__highlight" cx="20" cy="22" rx="6" ry="10" fill="#ff8a99" opacity="0.85"/>',
    '<ellipse cx="17" cy="16" rx="2" ry="3" fill="#ffffff" opacity="0.85"/>',
    "</svg>",
  ].join("");

  function appendCursor() {
    if (!document.body) {
      return;
    }

    document.body.appendChild(cursor);
    rootElement.classList.add("lt-balloon-cursor-ready");
    requestAnimationFrame(startAnimation);
  }

  if (document.body) {
    appendCursor();
  } else {
    document.addEventListener("DOMContentLoaded", appendCursor, { once: true });
  }

  var svg = cursor.querySelector("svg");
  var string = cursor.querySelector(".lt-balloon-cursor__string");
  var body = cursor.querySelector(".lt-balloon-cursor__body");
  var shade = cursor.querySelector(".lt-balloon-cursor__shade");
  var highlight = cursor.querySelector(".lt-balloon-cursor__highlight");
  var knot = cursor.querySelector(".lt-balloon-cursor__knot");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var palette = {
    red: {
      body: "#b31b34",
      shade: "#7a0d20",
      highlight: "#ff8a99",
      knot: "#7a0d20",
    },
    brass: {
      body: "#c6a25a",
      shade: "#80642a",
      highlight: "#f0d98f",
      knot: "#80642a",
    },
  };

  function paint(name) {
    var colors = palette[name];
    body.setAttribute("fill", colors.body);
    shade.setAttribute("fill", colors.shade);
    highlight.setAttribute("fill", colors.highlight);
    knot.setAttribute("fill", colors.knot);
  }

  var mouseX = window.innerWidth / 2;
  var mouseY = window.innerHeight / 2;
  var balloonX = mouseX;
  var balloonY = mouseY;
  var velocityX = 0;
  var velocityY = 0;
  var sway = 0;
  var swayVelocity = 0;
  var lastTime = performance.now();
  var visible = false;
  var press = 0;
  var hoverLift = 0;

  var stiffness = 0.1;
  var damping = 0.72;
  var swayForce = 0.00032;
  var swayDamping = 0.74;
  var swayReturn = 0.075;

  window.addEventListener(
    "mousemove",
    function (event) {
      mouseX = event.clientX;
      mouseY = event.clientY;

      if (!visible) {
        visible = true;
        cursor.style.opacity = "1";
        balloonX = mouseX;
        balloonY = mouseY;
      }
    },
    { passive: true },
  );

  document.addEventListener("mouseleave", function () {
    cursor.style.opacity = "0";
  });

  document.addEventListener("mouseenter", function () {
    if (visible) {
      cursor.style.opacity = "1";
    }
  });

  document.addEventListener("mouseover", function (event) {
    hoverLift = event.target.closest("a, button, [role='button'], input, textarea, select, label") ? 1 : 0;
  });

  window.addEventListener("mousedown", function (event) {
    press = 1;
    paint("brass");

    if (!reduceMotion) {
      addClickRing(event.clientX, event.clientY);
    }
  });

  window.addEventListener("mouseup", resetPress);
  window.addEventListener("blur", resetPress);

  function resetPress() {
    press = 0;
    paint("red");
  }

  function addClickRing(x, y) {
    var ring = document.createElement("div");
    var ringMargin = 32;
    var safeX = Math.max(ringMargin, Math.min(window.innerWidth - ringMargin, x));
    var safeY = Math.max(ringMargin, Math.min(window.innerHeight - ringMargin, y));

    ring.className = "lt-balloon-cursor-ring";
    ring.style.left = safeX + "px";
    ring.style.top = safeY + "px";
    document.body.appendChild(ring);
    window.setTimeout(function () {
      ring.remove();
    }, 650);
  }

  function startAnimation(now) {
    if (typeof now !== "number") {
      now = performance.now();
    }

    lastTime = now;
    requestAnimationFrame(tick);
  }

  function tick(now) {
    var timeStep = Math.min(40, now - lastTime);
    lastTime = now;

    var targetX = mouseX;
    var targetY = mouseY;
    var accelerationX = (targetX - balloonX) * stiffness;
    var accelerationY = (targetY - balloonY) * stiffness;

    velocityX = (velocityX + accelerationX) * damping;
    velocityY = (velocityY + accelerationY) * damping;
    balloonX += velocityX * (timeStep / 16.67);
    balloonY += velocityY * (timeStep / 16.67);

    swayVelocity += -velocityX * swayForce;
    swayVelocity += -sway * swayReturn;
    swayVelocity *= swayDamping;
    sway += swayVelocity;

    var lift = hoverLift * -4 + press * 4;
    var degrees = Math.max(-12, Math.min(12, sway * (180 / Math.PI)));
    var lean = degrees * 0.6;
    var controlOneX = 28 - lean * 0.4;
    var controlTwoX = 28 - lean * 0.2;

    var displayX = Math.max(40, Math.min(window.innerWidth - 40, balloonX));
    var displayY = Math.max(28, Math.min(window.innerHeight - 40, balloonY + lift));

    cursor.style.transform = "translate3d(" + displayX + "px, " + displayY + "px, 0)";
    svg.style.transform = "rotate(" + degrees + "deg)";
    string.setAttribute("d", "M28 92 C " + controlOneX + " 80, " + controlTwoX + " 70, 28 62");

    requestAnimationFrame(tick);
  }
})();
