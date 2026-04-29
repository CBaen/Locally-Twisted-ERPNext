/* THE COLOR STAGE - Locally Twisted Design Studio
 * Contestant 1 - Vanilla JS + jQuery (Frappe-compatible)
 * No build step, no NPM, no frameworks.
 * All state is in-memory. Persistence is downstream (inquiry form).
 */

/* COLOR CATALOG - LT Balloon Colors (representative subset) */
var LT_COLORS = {
  popular: [
    { name: "Pearl White", hex: "#F8F4EF" },
    { name: "Blush",       hex: "#F4A0A0" },
    { name: "Coral",       hex: "#FF6B6B" },
    { name: "Dusty Rose",  hex: "#D4849A" },
    { name: "Mauve",       hex: "#C06B85" },
    { name: "Lavender",    hex: "#C3B1E1" },
    { name: "Periwinkle",  hex: "#8BA5D8" },
    { name: "Baby Blue",   hex: "#ADD8E6" },
    { name: "Sage",        hex: "#9DC08B" },
    { name: "Mint",        hex: "#88FED0" },
    { name: "Gold",        hex: "#D4AF37" },
    { name: "Champagne",   hex: "#F7E7CE" }
  ],
  groups: [
    { name: "Neutrals & Whites", colors: [
      { name: "Pearl White", hex: "#F8F4EF" },
      { name: "Ivory",       hex: "#FFFFF0" },
      { name: "Champagne",   hex: "#F7E7CE" },
      { name: "Sand",        hex: "#C2B280" },
      { name: "Mocha",       hex: "#967969" },
      { name: "Black",       hex: "#1A1A1A" }
    ]},
    { name: "Pinks & Reds", colors: [
      { name: "Baby Pink",  hex: "#FFD1DC" },
      { name: "Blush",      hex: "#F4A0A0" },
      { name: "Coral",      hex: "#FF6B6B" },
      { name: "Dusty Rose", hex: "#D4849A" },
      { name: "Hot Pink",   hex: "#FF69B4" },
      { name: "Mauve",      hex: "#C06B85" }
    ]},
    { name: "Purples & Blues", colors: [
      { name: "Lavender",   hex: "#C3B1E1" },
      { name: "Lilac",      hex: "#B57EDC" },
      { name: "Periwinkle", hex: "#8BA5D8" },
      { name: "Royal Blue", hex: "#4169E1" },
      { name: "Baby Blue",  hex: "#ADD8E6" },
      { name: "Navy",       hex: "#001F5B" }
    ]},
    { name: "Greens & Teals", colors: [
      { name: "Mint",     hex: "#88FED0" },
      { name: "Sage",     hex: "#9DC08B" },
      { name: "Seafoam",  hex: "#93E9BE" },
      { name: "Forest",   hex: "#228B22" },
      { name: "Emerald",  hex: "#50C878" },
      { name: "Hunter",   hex: "#355E3B" }
    ]},
    { name: "Yellows & Oranges", colors: [
      { name: "Lemon",     hex: "#FFF44F" },
      { name: "Butter",    hex: "#FFF8DC" },
      { name: "Peach",     hex: "#FFCBA4" },
      { name: "Orange",    hex: "#FF8C00" },
      { name: "Tangerine", hex: "#F28500" },
      { name: "Mustard",   hex: "#FFDB58" }
    ]},
    { name: "Metallics & Special", colors: [
      { name: "Gold",       hex: "#D4AF37" },
      { name: "Rose Gold",  hex: "#B76E79" },
      { name: "Silver",     hex: "#C0C0C0" },
      { name: "Chrome Gold",hex: "#FFD700" },
      { name: "Copper",     hex: "#B87333" },
      { name: "Iridescent", hex: "#E8D5E8" }
    ]}
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
    $(".selected-color-name").text(name);
    $(".selected-color-hex").text(hex);
    this.applyColorToRegion(hex);
    if (this.activeRegion) {
      var dotSel = ".region-chip[data-region='" + this.activeRegion + "'] .region-chip__dot";
      $(dotSel).css("background-color", hex);
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
        .attr({"data-hex": col.hex, "data-name": col.name, "title": col.name + " " + col.hex})
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
          .attr({"data-hex": col.hex, "data-name": col.name, "title": col.name + " " + col.hex})
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
