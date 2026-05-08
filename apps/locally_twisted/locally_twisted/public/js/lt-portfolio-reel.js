/* Locally Twisted portfolio reel. */
(function () {
  "use strict";

  const SETTINGS = {
    density: 1.10,
    photoScale: 1.5,
    variant: "drift",
    driftSmoothing: 0.02,
    opacitySpeed: 4.0,
  };

  const BASE_UNIT = 640;
  const VERTICAL_SPACING = 80;
  const OVERLAP = 0.55;
  const CENTER_BREATH = 140;

  function layoutPhotos(photos, density) {
    let leftY = 0;
    let rightY = 0;
    const verticalSpacing = VERTICAL_SPACING * (2 - density);

    return photos.map((photo) => {
      const width = BASE_UNIT * photo.scale * density * SETTINGS.photoScale;
      const height = width / (photo.w / photo.h);

      if (photo.side === "center") {
        const startY = Math.max(leftY, rightY) + CENTER_BREATH;
        const endY = startY + height + CENTER_BREATH;
        leftY = endY;
        rightY = endY;
        return Object.assign({}, photo, { yOffset: startY, _w: width, _h: height });
      }

      const isLeft = photo.side === "left";
      const y = isLeft ? leftY : rightY;
      const next = y + height * OVERLAP + verticalSpacing;
      if (isLeft) leftY = next;
      else rightY = next;
      return Object.assign({}, photo, { yOffset: y, _w: width, _h: height });
    });
  }

  function anchorPercent(photo, index, viewportWidth) {
    if (photo.side === "center") return 50 - (photo._w / viewportWidth) * 50;
    if (photo.side === "left") return 2 + ((index * 5) % 12);
    return 100 - (photo._w / viewportWidth) * 100 - (2 + ((index * 9) % 12));
  }

  function makePhotoEl(photo, index, viewportWidth) {
    const figure = document.createElement("figure");
    figure.className = "lt-photo";
    figure.dataset.photo = "";
    figure.dataset.id = photo.id;
    figure.dataset.side = photo.side;
    figure.dataset.scale = photo.scale;
    figure.dataset.category = photo.category || "";
    figure.dataset.eventType = photo.event_type || "";
    figure.setAttribute("role", "button");
    figure.setAttribute("tabindex", "-1");
    figure.setAttribute("aria-hidden", "true");
    figure.setAttribute("aria-label", `Bring ${photo.title} forward`);

    const anchor = anchorPercent(photo, index, viewportWidth);
    figure.style.width = `${photo._w}px`;
    figure.style.left = `${Math.max(1, anchor)}%`;
    figure.style.top = `${photo.yOffset}px`;
    figure.style.setProperty("--ar", photo.w / photo.h);

    const image = document.createElement("img");
    image.loading = index < 2 ? "eager" : "lazy";
    image.decoding = "async";
    image.draggable = false;
    image.alt = photo.alt || photo.title;
    image.src = photo.image_url;
    image.width = Math.round(photo.w);
    image.height = Math.round(photo.h);
    figure.appendChild(image);

    return figure;
  }

  function setPhotoKeyboardState(element, isReachable) {
    if (!element) return;
    if (isReachable) {
      element.tabIndex = 0;
      element.removeAttribute("aria-hidden");
    } else {
      element.tabIndex = -1;
      element.setAttribute("aria-hidden", "true");
    }
  }

  function setupMobileReveal(elements) {
    const media = window.matchMedia("(max-width: 768px)");
    let observer = null;

    function disconnect() {
      if (observer) {
        observer.disconnect();
        observer = null;
      }
    }

    function apply() {
      disconnect();

      elements.forEach((element, index) => {
        const side = element.dataset.side || (index % 2 ? "right" : "left");
        const offset = side === "right" ? "34px" : side === "center" ? "0px" : "-34px";
        element.style.setProperty("--mobile-start-x", offset);
        element.classList.remove("is-visible");
        setPhotoKeyboardState(element, false);
      });

      if (!media.matches) return;

      if (!("IntersectionObserver" in window)) {
        elements.forEach((element) => {
          element.classList.add("is-visible");
          setPhotoKeyboardState(element, true);
        });
        return;
      }

      observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-visible");
            setPhotoKeyboardState(entry.target, true);
            observer.unobserve(entry.target);
          });
        },
        {
          root: null,
          rootMargin: "0px 0px -18% 0px",
          threshold: 0.28,
        }
      );

      elements.forEach((element) => observer.observe(element));
    }

    apply();

    if (typeof media.addEventListener === "function") {
      media.addEventListener("change", apply);
    } else if (typeof media.addListener === "function") {
      media.addListener(apply);
    }
  }

  function mount(root) {
    const photos = window.LT_PORTFOLIO_PHOTOS || [];
    const reel = root.querySelector("[data-reel]");
    if (!photos.length || !reel) return;

    let viewportWidth = window.innerWidth;
    let viewportHeight = window.innerHeight;
    let positioned = layoutPhotos(photos, SETTINGS.density);
    positioned.forEach((photo, index) => reel.appendChild(makePhotoEl(photo, index, viewportWidth)));
    reel.style.height = `${Math.max(...positioned.map((photo) => photo.yOffset + photo._h)) + 200}px`;

    const state = positioned.map(() => ({
      peak: 0,
      target: 0,
      smooth: 0,
      frontUntil: 0,
    }));
    const elements = Array.from(reel.querySelectorAll(".lt-photo"));
    const mobileMedia = window.matchMedia("(max-width: 768px)");
    setupMobileReveal(elements);
    let frontIndex = -1;

    window.addEventListener("resize", () => {
      viewportWidth = window.innerWidth;
      viewportHeight = window.innerHeight;
      positioned = layoutPhotos(photos, SETTINGS.density);

      positioned.forEach((photo, index) => {
        const element = elements[index];
        if (!element) return;
        const anchor = anchorPercent(photo, index, viewportWidth);
        element.style.width = `${photo._w}px`;
        element.style.left = `${Math.max(1, anchor)}%`;
        element.style.top = `${photo.yOffset}px`;
      });

      reel.style.height = `${Math.max(...positioned.map((photo) => photo.yOffset + photo._h)) + 200}px`;
    });

    elements.forEach((element, index) => {
      function bringForward() {
        if (frontIndex === index) return;
        if (frontIndex >= 0) elements[frontIndex].classList.remove("is-front");
        frontIndex = index;
        element.classList.add("is-front");
        state[index].frontUntil = performance.now() + 1000;
      }

      element.addEventListener("click", bringForward);
      element.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        bringForward();
      });
    });

    function frame() {
      const now = performance.now();
      for (let index = 0; index < positioned.length; index += 1) {
        const photo = positioned[index];
        const element = elements[index];
        const current = state[index];
        if (!element) continue;

        const rect = element.getBoundingClientRect();
        const center = rect.top + rect.height / 2;
        const progress = (viewportHeight - center) / viewportHeight;
        if (progress > current.peak) current.peak = progress;
        current.target = current.peak;

        const k = Math.max(0.005, Math.min(1, SETTINGS.driftSmoothing));
        current.smooth += (current.target - current.smooth) * k;
        const smoothProgress = current.smooth;
        const peakProgress = current.peak;
        const side = photo.side === "left" ? -1 : photo.side === "right" ? 1 : 0;

        let tx = 0;
        let ty = 0;
        let rot = 0;
        let opacity = 1;

        if (SETTINGS.variant === "drift") {
          const eased = Math.max(0, Math.min(1, smoothProgress * 1.4));
          tx = side * (1 - eased) * 320;
          ty = (1 - eased) * (side === 0 ? 120 : 60);
          opacity = Math.max(0, Math.min(1, smoothProgress * SETTINGS.opacitySpeed));
        } else if (SETTINGS.variant === "snap") {
          const eased = Math.max(0, Math.min(1, peakProgress * 1.6));
          ty = (1 - eased) * 80;
          opacity = Math.max(0, Math.min(1, peakProgress * SETTINGS.opacitySpeed));
        } else if (SETTINGS.variant === "stack") {
          const eased = Math.max(0, Math.min(1, peakProgress * 1.3));
          const xEased = Math.pow(eased, 2.6);
          const yEased = 1 - Math.pow(1 - eased, 1.8);
          tx = side * (1 - xEased) * 280;
          ty = -(1 - yEased) * 320;
          rot = side * (1 - xEased) * 6;
          opacity = Math.max(0, Math.min(1, peakProgress * SETTINGS.opacitySpeed));
        }

        const isFront = frontIndex === index;
        let momentum = 0;
        if (isFront && now < current.frontUntil) {
          const elapsed = (now - (current.frontUntil - 1000)) / 1000;
          momentum = Math.sin(Math.PI * elapsed * 2.2) * Math.exp(-3 * elapsed);
        }

        const frontScale = isFront ? 1.08 + momentum * 0.04 : 1;
        const frontLift = isFront ? -10 + momentum * -8 : 0;
        const tiltX = isFront && now < current.frontUntil ? momentum * 4 : 0;
        const tiltY = isFront && now < current.frontUntil ? momentum * 6 * side : 0;

        element.style.transform =
          `translate3d(${tx}px, ${ty + frontLift}px, 0) ` +
          `rotate(${rot}deg) perspective(1200px) ` +
          `rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(${frontScale})`;
        element.style.opacity = opacity;
        element.style.zIndex = isFront ? 50 : 1;

        if (!mobileMedia.matches) {
          const reachable =
            opacity >= 0.55 &&
            rect.bottom >= -2 &&
            rect.top <= viewportHeight + 2 &&
            rect.right >= -2 &&
            rect.left <= viewportWidth + 2;
          setPhotoKeyboardState(element, reachable);
        }
      }
      window.requestAnimationFrame(frame);
    }

    window.requestAnimationFrame(frame);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-portfolio]").forEach(mount);
  });
})();
