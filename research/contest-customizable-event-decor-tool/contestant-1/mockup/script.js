/* THE COLOR STAGE - Locally Twisted Design Studio
 * Contestant 1 - Vanilla JS + jQuery (Frappe-compatible)
 * No build step, no NPM, no frameworks.
 * All state is in-memory. Persistence is downstream (inquiry form).
 *
 * ROUND 2 CHANGES:
 * - Color catalog replaced with actual 53 LT named colors (PRODUCT-DETAILS.md §2.8)
 * - Hex values are APPROXIMATIONS for visual rendering only.
 *   Color NAME is the supplier-actionable identifier; name flows to Jeff's CRM.
 * - Popular row updated to real LT names customers will recognize.
 * - Groups organized per natural families in §2.8.
 */

/* COLOR CATALOG - LT Balloon Colors (53 named, hex = approximation for rendering) */
var LT_COLORS = {
  /* 12 high-demand swatches for the Quick Row — real names that match popular requests */
  popular: [
    { name: "White",         hex: "#F5F5F0" },
    { name: "Blush",         hex: "#F2B8C0" },
    { name: "Dusk Rose",     hex: "#C98FA0" },
    { name: "Bubble Gum",    hex: "#F570A0" },
    { name: "Orchid",        hex: "#C47EC6" },
    { name: "Periwinkle",    hex: "#9BAADE" },
    { name: "Pastel Blue",   hex: "#A8C8E8" },
    { name: "Eucalyptus",    hex: "#7DB89A" },
    { name: "Pastel Green",  hex: "#A8D5B0" },
    { name: "Reflex Gold",   hex: "#C8A830" },
    { name: "Reflex Silver", hex: "#B0B8C0" },
    { name: "Empowermint",   hex: "#68C8A0" }
  ],

  /* Full 53-color catalog organized by natural family per PRODUCT-DETAILS §2.8 */
  groups: [
    {
      name: "Reflex (Metallics)",
      colors: [
        { name: "Reflex Champagne", hex: "#D4C09A" },
        { name: "Reflex Truffle",   hex: "#9A7060" },
        { name: "Reflex Silver",    hex: "#B0B8C0" },
        { name: "Reflex Gold",      hex: "#C8A830" },
        { name: "Reflex Blue",      hex: "#3058B8" },
        { name: "Reflex Green",     hex: "#208040" },
        { name: "Reflex Violet",    hex: "#7030A0" },
        { name: "Reflex Red",       hex: "#C02030" }
      ]
    },
    {
      name: "Dusk (Muted Tones)",
      colors: [
        { name: "Dusk Cream",    hex: "#E8D8BE" },
        { name: "Dusk Green Tea",hex: "#A8B898" },
        { name: "Dusk Blue",     hex: "#8898B8" },
        { name: "Dusk Lilac",    hex: "#B8A8C8" },
        { name: "Dusk Rose",     hex: "#C98FA0" }
      ]
    },
    {
      name: "Pastel",
      colors: [
        { name: "Pastel Pink",   hex: "#F8C8D0" },
        { name: "Pastel Blue",   hex: "#A8C8E8" },
        { name: "Pastel Green",  hex: "#A8D5B0" },
        { name: "Pastel Purple", hex: "#C8B8E8" },
        { name: "Pastel Yellow", hex: "#F8E898" },
        { name: "Pastel Melon",  hex: "#F8C8A8" }
      ]
    },
    {
      name: "Brights",
      colors: [
        { name: "Red",        hex: "#D02020" },
        { name: "Orange",     hex: "#F07020" },
        { name: "Yellow",     hex: "#F0D020" },
        { name: "Lime",       hex: "#80D820" },
        { name: "Raspberry",  hex: "#C02870" },
        { name: "Fuchsia",    hex: "#D83090" },
        { name: "Bubble Gum", hex: "#F570A0" },
        { name: "Honey",      hex: "#D09820" }
      ]
    },
    {
      name: "Purples & Blues",
      colors: [
        { name: "Lilac",      hex: "#C8A8D8" },
        { name: "Orchid",     hex: "#C47EC6" },
        { name: "Violet",     hex: "#7030A0" },
        { name: "Periwinkle", hex: "#9BAADE" },
        { name: "LT Blue",    hex: "#70A8E0" },
        { name: "Royal Blue", hex: "#2848C8" },
        { name: "Robin's Egg",hex: "#70C8D8" },
        { name: "Dusk Blue",  hex: "#8898B8" }
      ]
    },
    {
      name: "Greens & Teals",
      colors: [
        { name: "Eucalyptus",  hex: "#7DB89A" },
        { name: "Empowermint", hex: "#68C8A0" },
        { name: "Shamrock",    hex: "#208838" },
        { name: "Forest",      hex: "#286028" },
        { name: "Wintergreen", hex: "#488858" },
        { name: "Teal",        hex: "#008080" },
        { name: "Deep Teal",   hex: "#006870" },
        { name: "Dusk Green Tea", hex: "#A8B898" }
      ]
    },
    {
      name: "Neutrals",
      colors: [
        { name: "White",      hex: "#F5F5F0" },
        { name: "Grey",       hex: "#B0B0B0" },
        { name: "Smoke Grey", hex: "#888888" },
        { name: "Black",      hex: "#1A1A1A" },
        { name: "Latte",      hex: "#C8A888" },
        { name: "Brown",      hex: "#8B5E3C" },
        { name: "Chocolate",  hex: "#6A3520" },
        { name: "Clear",      hex: "#E8F4F8" },
        { name: "Blush",      hex: "#F2B8C0" }
      ]
    },
    {
      name: "Blue Slate & Special",
      colors: [
        { name: "Blue Slate",     hex: "#708090" }
      ]
    }
  ]
};

/* DESIGN STUDIO STATE + INTERACTIONS */
var DesignStudio = {
  activeRegion: null,
  selectedColor: null,

  init: function() {
    this.bindColorPicker();
    this.bindPaletteSheet();
    this.bindSVGRegions();
    this.bindRegionChips();
    this.bindStageInteractions();
  },

  bindColorPicker: function() {
    var self = this;
    $(document).on("click", ".swatch[data-hex]", function() {
      self.selectColor($(this).data("hex"), $(this).data("name"), $(this));
    });
    $(document).on("click", ".palette-swatch[data-hex]", function() {
      self.selectColor($(this).data("hex"), $(this).data("name"), $(this));
    });
  },

  selectColor: function(hex, name, swatchEl) {
    this.selectedColor = { hex: hex, name: name };
    $(".swatch, .palette-swatch").removeClass("is-selected");
    swatchEl.addClass("is-selected");
    $(".selected-color-preview").css("background-color", hex);
    /* Name is primary — shown first. Hex is visual aid only. */
    $(".selected-color-name").text(name);
    $(".selected-color-hex").text(hex);
    this.applyColorToRegion(hex);
    if (this.activeRegion) {
      var dotSel = ".region-chip[data-region='" + this.activeRegion + "'] .region-chip__dot";
      $(dotSel).css("background-color", hex);
      /* Store name on the region chip for payload assembly */
      var chip = $(".region-chip[data-region='" + this.activeRegion + "']");
      chip.attr("data-color-name", name).attr("data-color-hex", hex);
    }
  },

  applyColorToRegion: function(hex) {
    if (!this.activeRegion) return;
    var sel = "[data-region='" + this.activeRegion + "']";
    $(sel).find("path, circle, ellipse, rect").attr("fill", hex);
  },

  bindPaletteSheet: function() {
    var self = this;
    $(document).on("click", ".swatch-more-chip, .js-open-palette", function() { self.openPaletteSheet(); });
    $(document).on("click", ".palette-sheet-overlay, .js-close-palette", function() { self.closePaletteSheet(); });
    $(document).on("click", ".palette-sheet", function(e) { e.stopPropagation(); });
  },

  openPaletteSheet: function() {
    $(".palette-sheet-overlay").addClass("is-open");
    $(".palette-sheet").addClass("is-open");
    document.body.style.overflow = "hidden";
  },

  closePaletteSheet: function() {
    $(".palette-sheet-overlay").removeClass("is-open");
    $(".palette-sheet").removeClass("is-open");
    document.body.style.overflow = "";
  },

  bindSVGRegions: function() {
    var self = this;
    $(document).on("click", ".fill-region", function(e) {
      e.stopPropagation();
      self.activateRegion($(this).data("region"));
    });
    $(document).one("click", ".fill-region", function() {
      $(".fill-region").removeClass("pulse-hint");
    });
  },

  activateRegion: function(regionId) {
    this.activeRegion = regionId;
    $(".fill-region").removeClass("is-selected");
    $("[data-region='" + regionId + "']").addClass("is-selected");
    $(".region-chip").removeClass("is-active");
    $(".region-chip[data-region='" + regionId + "']").addClass("is-active");
    var lbl = $(".region-chip[data-region='" + regionId + "']").data("label") || regionId;
    $(".color-picker-panel__label").text("Color for: " + lbl);
  },

  bindRegionChips: function() {
    var self = this;
    $(document).on("click", ".region-chip", function() {
      self.activateRegion($(this).data("region"));
    });
  },

  bindStageInteractions: function() {
    $(document).on("click", ".stage-piece", function() {
      $(this).closest(".stage-strip").find(".stage-piece").removeClass("is-active");
      $(this).addClass("is-active");
    });
  },

  /* Build inquiry payload: color NAME is primary; hex is visual aid shown in parens.
   * Pattern per PRODUCT-DETAILS §4: "Reflex Gold" is the supplier SKU.
   * Hex is eyeball-matching aid only — Jeff's supplier call uses the name.
   * Output: "Column: Lavender (approx. #C3B1E1) + Blush (approx. #F2B8C0)"
   */
  buildPayloadLine: function(pieceName, regions) {
    var parts = regions.map(function(r) {
      var chip = $(".region-chip[data-region='" + r + "']");
      var cname = chip.attr("data-color-name") || "(not set)";
      var chex  = chip.attr("data-color-hex")  || "";
      return chex ? cname + " (approx. " + chex + ")" : cname;
    });
    return pieceName + ": " + parts.join(" + ");
  }
};

/* RENDER HELPERS - build DOM from color catalog */
function renderQuickSwatches(id) {
  var c = $(id);
  if (!c.length) return;
  LT_COLORS.popular.forEach(function(col) {
    c.append(
      $("<div></div>")
        .addClass("swatch")
        .attr({
          "data-hex": col.hex,
          "data-name": col.name,
          "title": col.name + " (approx. " + col.hex + ")"
        })
        .css("background-color", col.hex)
    );
  });
  c.append(
    $("<button></button>")
      .addClass("swatch-more-chip js-open-palette")
      .attr("type", "button")
      .text("All colors →")
  );
}

function renderFullPalette(id) {
  var c = $(id);
  if (!c.length) return;
  LT_COLORS.groups.forEach(function(grp) {
    var g = $("<div></div>").addClass("palette-group");
    g.append($("<div></div>").addClass("palette-group__name").text(grp.name));
    var grid = $("<div></div>").addClass("palette-group__grid");
    grp.colors.forEach(function(col) {
      grid.append(
        $("<div></div>")
          .addClass("palette-swatch")
          .attr({
            "data-hex": col.hex,
            "data-name": col.name,
            "title": col.name + " (approx. " + col.hex + ")"
          })
          .css("background-color", col.hex)
      );
    });
    g.append(grid);
    c.append(g);
  });
}

/* INIT */
$(document).ready(function() {
  renderQuickSwatches("#swatch-quick-row");
  renderFullPalette("#palette-full-groups");
  DesignStudio.init();

  var fr = $(".fill-region").first();
  if (fr.length) {
    DesignStudio.activateRegion(fr.data("region"));
    setTimeout(function() {
      $(".fill-region").addClass("pulse-hint");
      setTimeout(function() { $(".fill-region").removeClass("pulse-hint"); }, 4000);
    }, 500);
  }

  var fc = $(".region-chip").first();
  if (fc.length) {
    fc.addClass("is-active");
    DesignStudio.activeRegion = fc.data("region");
  }
});
