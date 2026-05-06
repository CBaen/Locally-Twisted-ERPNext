/* Locally Twisted portfolio reel. */
(function () {
  "use strict";

  const SETTINGS = {
    density: 1.5,
    variant: "drift",
    driftSmoothing: 0.02,
    opacitySpeed: 4.0,
  };

  const BASE_UNIT = 820;
  const VERTICAL_SPACING = 44;
  const OVERLAP = 0.56;
  const COLUMN_CENTERS = {
    left: 34,
    center: 50,
    right: 66,
  };
  const COLUMN_STAGGER = {
    left: 0,
    center: 40,
    right: 18,
  };

  function layoutPhotos(photos, density) {
    const columnY = {
      left: 0,
      center: 0,
      right: 0,
    };
    const verticalSpacing = VERTICAL_SPACING * (2 - density);

    return photos.map((photo, index) => {
      const width = BASE_UNIT * photo.scale * density;
      const height = width / (photo.w / photo.h);
      const side = photo.side || (index % 3 === 1 ? "center" : index % 3 === 2 ? "right" : "left");
      const y = columnY[side] || 0;
      const stagger = COLUMN_STAGGER[side] || 0;
      const yOffset = y + stagger;
      columnY[side] = y + height * OVERLAP + verticalSpacing;

      return Object.assign({}, photo, { side, yOffset, _w: width, _h: height });
    });
  }

  function anchorPercent(photo, index, viewportWidth) {
    const baseCenter = COLUMN_CENTERS[photo.side] || 50;
    const jitter = photo.side === "center" ? ((index % 2) ? 0.9 : -0.9) : ((index % 3) - 1) * 1.25;
    return baseCenter + jitter - (photo._w / viewportWidth) * 50;
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
    figure.setAttribute("tabindex", "0");
    figure.setAttribute("aria-label", `Bring ${photo.title} forward`);

    const anchor = anchorPercent(photo, index, viewportWidth);
    figure.style.width = `${photo._w}px`;
    figure.style.height = `${photo._h}px`;
    figure.style.left = `${Math.max(-8, Math.min(76, anchor))}%`;
    figure.style.top = `${photo.yOffset}px`;
    figure.style.setProperty("--ar", photo.w / photo.h);

    const frame = document.createElement("div");
    frame.className = "lt-frame";

    const image = document.createElement("img");
    image.loading = index < 2 ? "eager" : "lazy";
    image.decoding = "async";
    image.draggable = false;
    image.alt = photo.alt || photo.title;
    image.src = photo.image_url;
    image.width = Math.round(photo.w);
    image.height = Math.round(photo.h);
    frame.appendChild(image);
    figure.appendChild(frame);

    const caption = document.createElement("figcaption");
    caption.className = "lt-cap";

    const number = document.createElement("span");
    number.className = "lt-cap-num";
    number.textContent = String(index + 1).padStart(2, "0");

    const title = document.createElement("span");
    title.className = "lt-cap-title";
    title.textContent = photo.title;

    const meta = document.createElement("span");
    meta.className = "lt-cap-meta";
    meta.textContent = [photo.client, photo.year].filter(Boolean).join(" \u00b7 ");

    caption.appendChild(number);
    caption.appendChild(title);
    caption.appendChild(meta);
    figure.appendChild(caption);

    return figure;
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
      tilt: { x: 0, y: 0 },
      frontUntil: 0,
    }));
    const elements = Array.from(reel.querySelectorAll(".lt-photo"));
    let frontIndex = -1;
    let mouseX = 0;
    let mouseY = 0;

    window.addEventListener("mousemove", (event) => {
      mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
      mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
    });

    window.addEventListener("resize", () => {
      viewportWidth = window.innerWidth;
      viewportHeight = window.innerHeight;
      positioned = layoutPhotos(photos, SETTINGS.density);

      positioned.forEach((photo, index) => {
        const element = elements[index];
        if (!element) return;
        const anchor = anchorPercent(photo, index, viewportWidth);
        element.style.width = `${photo._w}px`;
        element.style.height = `${photo._h}px`;
        element.style.left = `${Math.max(-8, Math.min(76, anchor))}%`;
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
      element.addEventListener("pointermove", (event) => {
        if (frontIndex !== index) return;
        const rect = element.getBoundingClientRect();
        const nx = ((event.clientX - rect.left) / rect.width - 0.5) * 2;
        const ny = ((event.clientY - rect.top) / rect.height - 0.5) * 2;
        state[index].tilt.x = -ny * 8;
        state[index].tilt.y = nx * 10;
      });
      element.addEventListener("pointerleave", () => {
        if (frontIndex === index) state[index].tilt = { x: 0, y: 0 };
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
          tx = side * (1 - eased) * 42;
          ty = (1 - eased) * (side === 0 ? 38 : 18);
          opacity = 1;
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

        const parallax = (1 - photo.scale) * 24 + 6;
        const px = mouseX * parallax;
        const py = mouseY * parallax;
        const isFront = frontIndex === index;
        let momentum = 0;
        if (isFront && now < current.frontUntil) {
          const elapsed = (now - (current.frontUntil - 1000)) / 1000;
          momentum = Math.sin(Math.PI * elapsed * 2.2) * Math.exp(-3 * elapsed);
        }

        const frontScale = isFront ? 1.08 + momentum * 0.04 : 1;
        const frontLift = isFront ? -10 + momentum * -8 : 0;
        const tiltX = isFront ? current.tilt.x + momentum * 4 : 0;
        const tiltY = isFront ? current.tilt.y + momentum * 6 * side : 0;

        element.style.transform =
          `translate3d(${tx + px}px, ${ty + py + frontLift}px, 0) ` +
          `rotate(${rot}deg) perspective(1200px) ` +
          `rotateX(${tiltX}deg) rotateY(${tiltY}deg) scale(${frontScale})`;
        element.style.opacity = opacity;
        element.style.zIndex = isFront ? 50 : 1;
      }
      window.requestAnimationFrame(frame);
    }

    window.requestAnimationFrame(frame);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-portfolio]").forEach(mount);
  });
})();
