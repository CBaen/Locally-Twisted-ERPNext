/**
 * Locally Twisted — Design Studio
 * script.js — Vanilla JS + jQuery, no build step, no NPM
 *
 * Frappe-recreatable: everything here is plain DOM API + jQuery 3.x
 * jQuery is available globally from Frappe's bundle; for the mockup
 * it's loaded via CDN in each HTML file.
 */

// ==============================
// COLOR CATALOG
// A representative 20-color subset for mockup; production will have 50+
// ==============================
var LT_COLORS = [
  { name: "White",         hex: "#FFFFFF" },
  { name: "Ivory",         hex: "#FFFFF0" },
  { name: "Blush",         hex: "#F4DFD7" },
  { name: "Rose",          hex: "#E8A0A0" },
  { name: "Coral",         hex: "#E8735A" },
  { name: "Red",           hex: "#C0392B" },
  { name: "Burgundy",      hex: "#7B2D42" },
  { name: "Lavender",      hex: "#C3A8E0" },
  { name: "Lilac",         hex: "#D8B4E2" },
  { name: "Purple",        hex: "#7D3C98" },
  { name: "Navy",          hex: "#1B3A6B" },
  { name: "Soft Blue",     hex: "#C3DCF3" },
  { name: "Sky",           hex: "#A0E9FF" },
  { name: "Teal",          hex: "#008080" },
  { name: "Seafoam",       hex: "#88FED0" },
  { name: "Lime",          hex: "#B8FF9E" },
  { name: "Yellow",        hex: "#F9F871" },
  { name: "Gold",          hex: "#D4A017" },
  { name: "Champagne",     hex: "#F0D9B5" },
  { name: "Black",         hex: "#1A1A1A" }
];

// ==============================
// DESIGN STATE
// Client-side only — no DB writes during the design experience
// ==============================
var DesignState = {
  pieces: [],          // Array of { id, type, name, colors: { primary, accent } }
  activeRegion: null,  // 'primary' or 'accent'
  recentColors: [],    // Up to 8 recently used hex values

  addPiece: function(type, name) {
    var id = 'piece-' + Date.now();
    this.pieces.push({ id: id, type: type, name: name, colors: { primary: '#E8A0A0', accent: '#C3DCF3' } });
    return id;
  },

  updateColor: function(pieceId, region, hex) {
    var piece = this.pieces.find(function(p) { return p.id === pieceId; });
    if (piece) {
      piece.colors[region] = hex;
    }
    this.addRecent(hex);
  },

  addRecent: function(hex) {
    var idx = this.recentColors.indexOf(hex);
    if (idx > -1) this.recentColors.splice(idx, 1);
    this.recentColors.unshift(hex);
    if (this.recentColors.length > 8) this.recentColors = this.recentColors.slice(0, 8);
    this.saveToSession();
  },

  saveToSession: function() {
    try {
      sessionStorage.setItem('lt_design', JSON.stringify({ pieces: this.pieces, recentColors: this.recentColors }));
    } catch(e) {}
  },

  loadFromSession: function() {
    try {
      var raw = sessionStorage.getItem('lt_design');
      if (raw) {
        var data = JSON.parse(raw);
        this.pieces = data.pieces || [];
        this.recentColors = data.recentColors || [];
      }
    } catch(e) {}
  }
};

// ==============================
// COLOR PICKER COMPONENT
// Bottom sheet: recents row + scrollable grid of all colors
// ==============================
var ColorPicker = {
  $overlay: null,
  $sheet: null,
  onSelect: null,   // callback(hex)
  selectedHex: null,

  init: function() {
    this.$overlay = $('#picker-overlay');
    this.$sheet   = $('#picker-sheet');

    // Close on overlay click
    this.$overlay.on('click', function() { ColorPicker.close(); });

    // Build the palette grid once
    this._buildPalette();

    // Handle swatch selection
    $(document).on('click', '.swatch-item', function() {
      var hex = $(this).data('hex');
      ColorPicker.selectColor(hex);
    });

    // Recents row selection
    $(document).on('click', '.recent-swatch', function() {
      var hex = $(this).data('hex');
      if (hex) ColorPicker.selectColor(hex);
    });
  },

  _buildPalette: function() {
    var $grid = $('.swatch-grid');
    if (!$grid.length) return;
    $grid.empty();
    LT_COLORS.forEach(function(c) {
      var isDark = _isLightColor(c.hex);
      $grid.append(
        '<div class="swatch-item" data-hex="' + c.hex + '">' +
          '<div class="swatch-item__circle" style="background:' + c.hex + '; border-color:' + (isDark ? '#D0D0D0' : c.hex) + '">' +
            '<span class="hex-badge">' + c.hex + '</span>' +
          '</div>' +
          '<span class="swatch-item__name">' + c.name + '</span>' +
        '</div>'
      );
    });
  },

  _buildRecents: function() {
    var $row = $('.picker-recents__row');
    if (!$row.length) return;
    $row.empty();
    var slots = 8;
    for (var i = 0; i < slots; i++) {
      var hex = DesignState.recentColors[i];
      if (hex) {
        $row.append('<div class="swatch-circle recent-swatch" data-hex="' + hex + '" style="background:' + hex + '"></div>');
      } else {
        $row.append('<div class="swatch-circle empty"></div>');
      }
    }
  },

  open: function(currentHex, onSelectFn) {
    this.selectedHex = currentHex;
    this.onSelect = onSelectFn;
    this._buildRecents();

    // Mark current selection
    $('.swatch-item').removeClass('selected');
    $('.swatch-item[data-hex="' + currentHex + '"]').addClass('selected');

    // Update region label swatch
    $('.current-swatch').css('background', currentHex);

    this.$overlay.addClass('open');
    this.$sheet.addClass('open');
    $('body').css('overflow', 'hidden');
  },

  close: function() {
    this.$overlay.removeClass('open');
    this.$sheet.removeClass('open');
    $('body').css('overflow', '');
  },

  selectColor: function(hex) {
    this.selectedHex = hex;
    // Visual feedback — mark selected
    $('.swatch-item').removeClass('selected');
    $('.swatch-item[data-hex="' + hex + '"]').addClass('selected');
    // Apply immediately (no "confirm" button — instant apply per coloring-book UX)
    if (typeof this.onSelect === 'function') {
      this.onSelect(hex);
    }
    DesignState.addRecent(hex);
    // Short delay then close — lets the user see the fill before sheet closes
    setTimeout(function() { ColorPicker.close(); }, 220);
  }
};

// ==============================
// SHAPE FILL INTERACTION
// Handles tap-to-fill on SVG regions in the color-one screen
// ==============================
var ShapeColorizer = {
  pieceId: null,
  activeRegion: 'primary',

  init: function(pieceId) {
    this.pieceId = pieceId;
    var self = this;

    // Region selector chips
    $(document).on('click', '.region-chip', function() {
      $('.region-chip').removeClass('active');
      $(this).addClass('active');
      self.activeRegion = $(this).data('region');
    });

    // SVG fill regions — tap to open picker
    $(document).on('click', '.fill-region', function() {
      var region = $(this).data('region') || self.activeRegion;
      self.activeRegion = region;
      // Sync chip UI
      $('.region-chip').removeClass('active');
      $('.region-chip[data-region="' + region + '"]').addClass('active');

      // Activate the clicked region visually
      $('.fill-region').removeClass('active');
      $('[data-region="' + region + '"]').addClass('active');

      var piece = DesignState.pieces.find(function(p) { return p.id === pieceId; });
      var currentHex = piece ? piece.colors[region] : '#FFFFFF';

      ColorPicker.open(currentHex, function(hex) {
        // Apply color to all matching fill regions
        $('[data-region="' + region + '"]').each(function() {
          $(this).attr('fill', hex);
        });
        DesignState.updateColor(self.pieceId, region, hex);
        // Update the chip swatch
        $('.region-chip[data-region="' + region + '"] .region-chip__swatch').css('background', hex);
      });
    });
  }
};

// ==============================
// COMPOSITION BUILDER
// Populates the composition view from DesignState
// ==============================
var CompositionView = {
  init: function() {
    DesignState.loadFromSession();
    this.render();
  },

  render: function() {
    var $wrap = $('.composition-scroll-wrap');
    if (!$wrap.length) return;

    // Clear existing piece cards (keep add-card)
    $wrap.find('.piece-card').remove();

    // Insert piece cards before the add card
    var $addCard = $wrap.find('.add-piece-card');
    DesignState.pieces.forEach(function(piece) {
      var $card = $(CompositionView._cardHTML(piece));
      $addCard.before($card);
    });

    // Update piece count
    $('.composition-header__count').text(DesignState.pieces.length + ' piece' + (DesignState.pieces.length !== 1 ? 's' : ''));
  },

  _cardHTML: function(piece) {
    var svgContent = _getShapePreviewSVG(piece.type, piece.colors.primary, piece.colors.accent);
    var dots = '<div class="piece-card__color-dot" style="background:' + piece.colors.primary + '"></div>' +
               '<div class="piece-card__color-dot" style="background:' + piece.colors.accent + '"></div>';
    return '<div class="piece-card" data-piece-id="' + piece.id + '">' +
      '<div class="piece-card__illustration">' + svgContent + '</div>' +
      '<div class="piece-card__footer">' +
        '<span class="piece-card__name">' + piece.name + '</span>' +
        '<div class="piece-card__colors">' + dots + '</div>' +
      '</div>' +
    '</div>';
  }
};

// ==============================
// HELPERS
// ==============================
function _isLightColor(hex) {
  var c = hex.replace('#','');
  var r = parseInt(c.substr(0,2),16);
  var g = parseInt(c.substr(2,2),16);
  var b = parseInt(c.substr(4,2),16);
  var lum = (0.299*r + 0.587*g + 0.114*b) / 255;
  return lum > 0.85;
}

// Returns a simple SVG preview for a piece type with given colors
function _getShapePreviewSVG(type, primary, accent) {
  switch(type) {
    case 'arch':
      return _archSVG(primary, accent);
    case 'column':
      return _columnSVG(primary, accent);
    case 'centerpiece':
      return _centerpieceSVG(primary, accent);
    default:
      return _archSVG(primary, accent);
  }
}

function _archSVG(primary, accent) {
  return '<svg viewBox="0 0 160 120" xmlns="http://www.w3.org/2000/svg">' +
    // Arch curve path filled with primary
    '<path d="M 20 100 Q 20 20 80 20 Q 140 20 140 100" fill="none" stroke="' + primary + '" stroke-width="24" stroke-linecap="round"/>' +
    // Accent dots at intervals
    '<circle cx="20" cy="100" r="10" fill="' + accent + '"/>' +
    '<circle cx="35" cy="68" r="10" fill="' + accent + '"/>' +
    '<circle cx="60" cy="30" r="10" fill="' + accent + '"/>' +
    '<circle cx="100" cy="30" r="10" fill="' + accent + '"/>' +
    '<circle cx="125" cy="68" r="10" fill="' + accent + '"/>' +
    '<circle cx="140" cy="100" r="10" fill="' + accent + '"/>' +
  '</svg>';
}

function _columnSVG(primary, accent) {
  return '<svg viewBox="0 0 80 130" xmlns="http://www.w3.org/2000/svg">' +
    '<circle cx="40" cy="110" r="14" fill="' + primary + '"/>' +
    '<circle cx="40" cy="85" r="14" fill="' + accent + '"/>' +
    '<circle cx="40" cy="60" r="14" fill="' + primary + '"/>' +
    '<circle cx="40" cy="35" r="14" fill="' + accent + '"/>' +
    '<circle cx="40" cy="14" r="11" fill="' + primary + '"/>' +
    // Stem
    '<line x1="40" y1="124" x2="40" y2="130" stroke="#999" stroke-width="3"/>' +
  '</svg>';
}

function _centerpieceSVG(primary, accent) {
  return '<svg viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">' +
    '<circle cx="50" cy="30" r="18" fill="' + primary + '"/>' +
    '<circle cx="22" cy="55" r="14" fill="' + accent + '"/>' +
    '<circle cx="78" cy="55" r="14" fill="' + accent + '"/>' +
    '<circle cx="35" cy="78" r="12" fill="' + primary + '"/>' +
    '<circle cx="65" cy="78" r="12" fill="' + primary + '"/>' +
    '<circle cx="50" cy="92" r="10" fill="' + accent + '"/>' +
    '<line x1="50" y1="102" x2="50" y2="110" stroke="#999" stroke-width="2"/>' +
  '</svg>';
}

// ==============================
// PAGE-SPECIFIC INIT
// Each HTML page calls the functions it needs via DOMContentLoaded
// ==============================
document.addEventListener('DOMContentLoaded', function() {
  // Detect which page we're on and init accordingly
  var page = document.body.dataset.page;

  if (page === 'color-one' || page === 'picker') {
    // Load or create a test piece
    DesignState.loadFromSession();
    if (DesignState.pieces.length === 0) {
      DesignState.addPiece('arch', 'Balloon Arch');
    }
    var pieceId = DesignState.pieces[0].id;
    ShapeColorizer.init(pieceId);
    if (document.getElementById('picker-overlay')) {
      ColorPicker.init();
    }
  }

  if (page === 'composition') {
    CompositionView.init();
  }

  if (page === 'done') {
    DesignState.loadFromSession();
    _renderDoneScreen();
  }
});

function _renderDoneScreen() {
  var $strip = $('.done-spread__pieces');
  if (!$strip.length) return;
  $strip.empty();
  DesignState.pieces.forEach(function(piece) {
    var svgContent = _getShapePreviewSVG(piece.type, piece.colors.primary, piece.colors.accent);
    $strip.append(
      '<div class="done-mini-card">' +
        '<div class="done-mini-card__illustration">' + svgContent + '</div>' +
        '<div class="done-mini-card__name">' + piece.name + '</div>' +
      '</div>'
    );
  });
}
