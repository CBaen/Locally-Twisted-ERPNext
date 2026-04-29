/**
 * LT Design Studio — Contestant 2
 * Vanilla JS + jQuery (already in Frappe's bundle)
 * No NPM, no build step, no CDN module imports
 *
 * Pattern sources:
 * - SVG event delegation: https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/
 * - jQuery SVG fill: https://copyprogramming.com/howto/javascript-svg-fill-jquery-in-click
 * - Recent colors localStorage: https://bams-thinkery.ca/tools/color-picker
 * - Bottom sheet slide-up: pattern from mobile coloring apps (https://diycandy.com/best-adult-coloring-apps/)
 */

// ================================================================
// State (all client-side, no backend mutations during design phase)
// ================================================================
var DesignStudio = {
  // Selected fill region ID within current shape
  selectedRegion: null,
  // Currently chosen color {hex, name}
  selectedColor: null,
  // Colors applied to each region: { regionId: { hex, name } }
  regionColors: {},
  // Pieces in the composition: [{id, type, name, regionColors}]
  composition: [],
  // Active piece index in composition
  activePieceIdx: 0,
  // Active hue family tab
  activeHueFamily: 'all',
  // Recent colors array (up to 6, localStorage-backed)
  recentColors: [],
  // localStorage key
  RECENT_KEY: 'lt_design_studio_recent'
};

// ================================================================
// Color Catalog (representative 20-color subset; production = 50+)
// Organized by hue family
// ================================================================
var COLOR_CATALOG = {
  'pinks': [
    { hex: '#FFB6C1', name: 'Light Pink' },
    { hex: '#FF69B4', name: 'Hot Pink' },
    { hex: '#FF1493', name: 'Deep Pink' },
    { hex: '#E75480', name: 'Dark Pink' },
    { hex: '#F4DFD7', name: 'Blush' }
  ],
  'blues': [
    { hex: '#87CEEB', name: 'Sky Blue' },
    { hex: '#4169E1', name: 'Royal Blue' },
    { hex: '#003087', name: 'Navy' },
    { hex: '#C3DCF3', name: 'Soft Blue' },
    { hex: '#A0E9FF', name: 'Sky Cyan' }
  ],
  'greens': [
    { hex: '#00FF7F', name: 'Spring Green' },
    { hex: '#228B22', name: 'Forest Green' },
    { hex: '#B8FF9E', name: 'Lime Pastel' },
    { hex: '#88FED0', name: 'Seafoam' },
    { hex: '#80F5F3', name: 'Aqua' }
  ],
  'yellows': [
    { hex: '#FFD700', name: 'Gold' },
    { hex: '#F9F871', name: 'Soft Lemon' },
    { hex: '#FFA500', name: 'Orange' },
    { hex: '#FF6B35', name: 'Coral' },
    { hex: '#FF4500', name: 'Tomato' }
  ],
  'neutrals': [
    { hex: '#FFFFFF', name: 'White' },
    { hex: '#F5F5F5', name: 'Ivory' },
    { hex: '#C0C0C0', name: 'Silver' },
    { hex: '#D4AF37', name: 'Champagne Gold' },
    { hex: '#A0522D', name: 'Rust' }
  ],
  'darks': [
    { hex: '#1A1A1A', name: 'Near Black' },
    { hex: '#4B0082', name: 'Indigo' },
    { hex: '#800020', name: 'Burgundy' },
    { hex: '#2F4F4F', name: 'Dark Teal' },
    { hex: '#8B0000', name: 'Dark Red' }
  ]
};

// Flat list for 'all' tab
function getAllColors() {
  var all = [];
  Object.keys(COLOR_CATALOG).forEach(function(family) {
    COLOR_CATALOG[family].forEach(function(c) { all.push(c); });
  });
  return all;
}

// ================================================================
// Recent Colors (localStorage)
// ================================================================
function loadRecentColors() {
  try {
    var stored = localStorage.getItem(DesignStudio.RECENT_KEY);
    DesignStudio.recentColors = stored ? JSON.parse(stored) : [];
  } catch(e) {
    DesignStudio.recentColors = [];
  }
}

function saveRecentColor(colorObj) {
  loadRecentColors();
  // Remove if already exists
  DesignStudio.recentColors = DesignStudio.recentColors.filter(function(c) {
    return c.hex !== colorObj.hex;
  });
  // Prepend
  DesignStudio.recentColors.unshift(colorObj);
  // Keep max 6
  DesignStudio.recentColors = DesignStudio.recentColors.slice(0, 6);
  try {
    localStorage.setItem(DesignStudio.RECENT_KEY, JSON.stringify(DesignStudio.recentColors));
  } catch(e) {}
}

// ================================================================
// SVG Region Interaction
// Core pattern: event delegation on SVG container
// Source: https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/
// ================================================================
function initSVGInteraction(svgContainerId) {
  var container = document.getElementById(svgContainerId);
  if (!container) return;

  container.addEventListener('click', function(e) {
    var target = e.target;
    // Walk up to find a fill region
    while (target && target !== container) {
      if (target.dataset && target.dataset.region) {
        handleRegionTap(target);
        return;
      }
      target = target.parentElement;
    }
  });

  // Touch support: touchend fires like click on mobile
  container.addEventListener('touchend', function(e) {
    // Let click handler fire; prevent double-fire
    e.preventDefault();
    var touch = e.changedTouches[0];
    var target = document.elementFromPoint(touch.clientX, touch.clientY);
    if (target && target.dataset && target.dataset.region) {
      handleRegionTap(target);
    }
  });
}

function handleRegionTap(regionEl) {
  var regionId = regionEl.dataset.region;

  // Deselect all previously selected
  document.querySelectorAll('.svg-fill-region--selected').forEach(function(el) {
    el.classList.remove('svg-fill-region--selected');
    $(el).css('stroke', '');
    $(el).css('stroke-width', '');
    $(el).css('stroke-dasharray', '');
  });

  // Select this region
  DesignStudio.selectedRegion = regionId;
  regionEl.classList.add('svg-fill-region--selected');
  // Ring indicator (teal ring, solid)
  $(regionEl).css({
    'stroke': '#008080',
    'stroke-width': '2.5',
    'stroke-dasharray': 'none'
  });

  // Show bottom picker bar with region name
  showColorBar(regionId, regionEl.dataset.name || regionId);
}

function applyColorToRegion(regionId, colorObj) {
  // Find the region element(s) with this data-region
  var regions = document.querySelectorAll('[data-region="' + regionId + '"]');
  regions.forEach(function(el) {
    $(el).attr('fill', colorObj.hex);
    el.classList.add('colored');
    // Remove dashed stroke
    $(el).css({
      'stroke-dasharray': 'none',
      'stroke': regionId === DesignStudio.selectedRegion ? '#008080' : 'none',
      'stroke-width': regionId === DesignStudio.selectedRegion ? '2.5' : '0'
    });
  });

  // Store in state
  DesignStudio.regionColors[regionId] = colorObj;
  // Save to recent
  saveRecentColor(colorObj);
  // Refresh recent row if picker is open
  refreshRecentRow();
}

// ================================================================
// Color Bottom Bar
// ================================================================
function showColorBar(regionId, regionName) {
  var $bar = $('#color-bottom-bar');
  if (!$bar.length) return;

  var current = DesignStudio.regionColors[regionId];
  var hexText = current ? current.hex : 'none';
  var hexColor = current ? current.hex : '#EBEBEB';

  $bar.find('.color-bottom-bar__region-name').text(regionName);
  $bar.find('.color-bottom-bar__current-swatch').css('background', hexColor);
  $bar.find('.color-bottom-bar__hex').text(current ? current.hex : 'Tap a color below');
  $bar.find('.color-bottom-bar__prompt').hide();
  $bar.find('.color-bottom-bar__selected-info').show();
  $bar.find('#open-picker-btn').show();
}

function hideColorBarDetails() {
  var $bar = $('#color-bottom-bar');
  if (!$bar.length) return;
  $bar.find('.color-bottom-bar__prompt').show();
  $bar.find('.color-bottom-bar__selected-info').hide();
  $bar.find('#open-picker-btn').hide();
}

// ================================================================
// Picker Sheet (bottom sheet)
// ================================================================
function openPicker() {
  loadRecentColors();
  renderPickerSheet();
  var $overlay = $('#picker-overlay');
  if (!$overlay.length) {
    // Build the picker overlay dynamically if not in static HTML
    buildPickerOverlay();
    $overlay = $('#picker-overlay');
  }
  $overlay.show();
  // Prevent body scroll while picker is open
  $('body').css('overflow', 'hidden');
}

function closePicker() {
  $('#picker-overlay').hide();
  $('body').css('overflow', '');
}

function buildPickerOverlay() {
  var html = '<div id="picker-overlay" class="picker-overlay" style="display:none;">' +
    '<div class="picker-sheet">' +
    '<div class="picker-sheet__handle"></div>' +
    '<div class="picker-sheet__header">' +
      '<div class="picker-sheet__title heading">Pick a Color</div>' +
      '<button class="picker-sheet__close" onclick="closePicker()">&#215;</button>' +
    '</div>' +
    // Recent row
    '<div class="recent-colors">' +
      '<div class="recent-colors__label">Recently Used</div>' +
      '<div class="recent-colors__row" id="recent-colors-row"></div>' +
    '</div>' +
    // Hue tabs
    '<div class="hue-tabs" id="hue-tabs"></div>' +
    // Swatch grid
    '<div class="swatch-grid" id="swatch-grid"></div>' +
    // Hex chip
    '<div class="hex-chip" id="hex-chip">' +
      '<div class="hex-chip__swatch" id="hex-chip-swatch"></div>' +
      '<div class="hex-chip__code" id="hex-chip-code">#——</div>' +
      '<div class="hex-chip__name" id="hex-chip-name"></div>' +
    '</div>' +
    // Apply button
    '<div class="picker-apply-row">' +
      '<button class="btn-primary btn-primary--full" id="apply-color-btn">Apply Color</button>' +
    '</div>' +
    '</div>' +
  '</div>';
  $('body').append(html);

  // Close on overlay background click
  $('#picker-overlay').on('click', function(e) {
    if ($(e.target).is('#picker-overlay')) closePicker();
  });

  // Apply button
  $('#apply-color-btn').on('click', function() {
    if (DesignStudio.selectedColor && DesignStudio.selectedRegion) {
      applyColorToRegion(DesignStudio.selectedRegion, DesignStudio.selectedColor);
      updateColorBar();
      closePicker();
    }
  });

  renderPickerSheet();
}

function renderPickerSheet() {
  renderRecentRow();
  renderHueTabs();
  renderSwatchGrid(DesignStudio.activeHueFamily);
}

function renderRecentRow() {
  var $row = $('#recent-colors-row');
  if (!$row.length) return;
  $row.empty();
  loadRecentColors();

  var toShow = DesignStudio.recentColors.slice(0, 6);
  // Fill empties to always show 6 slots
  while (toShow.length < 6) toShow.push(null);

  toShow.forEach(function(c) {
    if (c) {
      var $dot = $('<div class="swatch-dot" title="' + c.name + ' ' + c.hex + '"></div>');
      $dot.css('background', c.hex);
      $dot.on('click', function() { selectSwatchColor(c); });
      $row.append($dot);
    } else {
      $row.append('<div class="swatch-dot swatch-dot--empty"></div>');
    }
  });
}

function renderHueTabs() {
  var $tabs = $('#hue-tabs');
  if (!$tabs.length) return;
  $tabs.empty();

  var families = [
    { id: 'all',      label: 'All' },
    { id: 'pinks',    label: 'Pinks' },
    { id: 'blues',    label: 'Blues' },
    { id: 'greens',   label: 'Greens' },
    { id: 'yellows',  label: 'Warm' },
    { id: 'neutrals', label: 'Neutrals' },
    { id: 'darks',    label: 'Darks' }
  ];

  families.forEach(function(f) {
    var active = f.id === DesignStudio.activeHueFamily ? ' hue-tab--active' : '';
    var $tab = $('<button class="hue-tab' + active + '">' + f.label + '</button>');
    $tab.on('click', function() {
      DesignStudio.activeHueFamily = f.id;
      renderSwatchGrid(f.id);
      $tabs.find('.hue-tab').removeClass('hue-tab--active');
      $tab.addClass('hue-tab--active');
    });
    $tabs.append($tab);
  });
}

function renderSwatchGrid(family) {
  var $grid = $('#swatch-grid');
  if (!$grid.length) return;
  $grid.empty();

  var colors = family === 'all' ? getAllColors() : (COLOR_CATALOG[family] || []);

  colors.forEach(function(c) {
    var isSelected = DesignStudio.selectedColor && DesignStudio.selectedColor.hex === c.hex;
    var $dot = $('<div class="swatch-dot' + (isSelected ? ' swatch-dot--selected' : '') + '" title="' + c.name + '"></div>');
    $dot.css('background', c.hex);
    $dot.on('click', function() { selectSwatchColor(c); });
    $grid.append($dot);
  });
}

function selectSwatchColor(colorObj) {
  DesignStudio.selectedColor = colorObj;
  // Update hex chip
  $('#hex-chip-swatch').css('background', colorObj.hex);
  $('#hex-chip-code').text(colorObj.hex);
  $('#hex-chip-name').text(colorObj.name);
  // Update selected state in grid
  $('#swatch-grid .swatch-dot').removeClass('swatch-dot--selected');
  $('#swatch-grid .swatch-dot').each(function() {
    if ($(this).css('background-color') === hexToRgb(colorObj.hex) ||
        $(this).attr('title') === colorObj.name) {
      $(this).addClass('swatch-dot--selected');
    }
  });
}

function refreshRecentRow() {
  renderRecentRow();
}

// ================================================================
// Color bar update after applying color
// ================================================================
function updateColorBar() {
  var regionId = DesignStudio.selectedRegion;
  if (!regionId) return;
  var colorObj = DesignStudio.regionColors[regionId];
  if (!colorObj) return;
  $('#color-bottom-bar .color-bottom-bar__current-swatch').css('background', colorObj.hex);
  $('#color-bottom-bar .color-bottom-bar__hex').text(colorObj.hex);
}

// ================================================================
// Hue family tab switching (standalone pages)
// ================================================================
function initHueTabs() {
  $('.hue-tab').on('click', function() {
    var family = $(this).data('family');
    DesignStudio.activeHueFamily = family;
    $('.hue-tab').removeClass('hue-tab--active');
    $(this).addClass('hue-tab--active');
    // Re-render grid in static page context
    renderStaticSwatchGrid(family);
  });
}

function renderStaticSwatchGrid(family) {
  var $grid = $('.swatch-grid');
  if (!$grid.length) return;
  $grid.empty();

  var colors = family === 'all' ? getAllColors() : (COLOR_CATALOG[family] || []);

  colors.forEach(function(c) {
    var $dot = $('<div class="swatch-dot" title="' + c.name + '"></div>');
    $dot.css('background', c.hex);
    $dot.on('click', function() {
      $('.swatch-dot').removeClass('swatch-dot--selected');
      $dot.addClass('swatch-dot--selected');
      // Update hex chip
      $('#hex-chip-swatch').css('background', c.hex);
      $('#hex-chip-code').text(c.hex);
      $('#hex-chip-name').text(c.name);
      DesignStudio.selectedColor = c;
    });
    $grid.append($dot);
  });
}

// ================================================================
// Composition: piece strip interaction
// ================================================================
function initPieceStrip() {
  $('.piece-chip').on('click', function() {
    var idx = $(this).data('idx');
    DesignStudio.activePieceIdx = idx;
    $('.piece-chip').removeClass('piece-chip--active');
    $(this).addClass('piece-chip--active');
    // Update composition canvas highlight
    $('.comp-piece').removeClass('comp-piece--active');
    $('.comp-piece[data-idx="' + idx + '"]').addClass('comp-piece--active');
  });
}

// ================================================================
// Ghost placeholder tap (upsell mechanic)
// ================================================================
function initGhostPlaceholder() {
  $('.ghost-shape').on('click', function() {
    // Navigate to entry page to add a new piece
    window.location.href = '01-entry.html';
  });

  $('.suggestion-panel__dismiss').on('click', function() {
    $('.suggestion-panel').slideUp(200);
  });

  // In the upsell screen: "Add this column" button
  $('#add-suggested-piece').on('click', function() {
    // In production: adds the suggested piece to composition
    // Mockup: navigate to coloring screen
    window.location.href = '02-color-one.html';
  });
}

// ================================================================
// Done / Capture screen
// ================================================================
function initDoneScreen() {
  // Populate palette row from sessionStorage (if available)
  var colors = [];
  try {
    var stored = sessionStorage.getItem('lt_design_palette');
    if (stored) colors = JSON.parse(stored);
  } catch(e) {}

  // Fallback demo colors
  if (!colors.length) {
    colors = [
      { hex: '#FFB6C1' },
      { hex: '#87CEEB' },
      { hex: '#FFFFFF' },
      { hex: '#FFD700' },
      { hex: '#FF69B4' }
    ];
  }

  var $row = $('#done-palette-row');
  if ($row.length) {
    colors.forEach(function(c) {
      $row.append('<div class="palette-swatch" style="background:' + c.hex + ';"></div>');
    });
  }

  // "Send to Jeff" button handler
  $('#send-to-jeff-btn').on('click', function() {
    // In production: frappe.call() to create a Lead with composition data
    // Mockup: show a confirmation
    var confirmed = confirm('Your design will be sent to Jeff. He\'ll reach out to talk through the details!');
    if (confirmed) {
      alert('Design sent! Jeff will be in touch at (801) 285-0860 or hi@locallytwisted.com');
    }
  });
}

// ================================================================
// Utility: hex to CSS rgb string (for comparison)
// ================================================================
function hexToRgb(hex) {
  var r = parseInt(hex.slice(1,3), 16);
  var g = parseInt(hex.slice(3,5), 16);
  var b = parseInt(hex.slice(5,7), 16);
  return 'rgb(' + r + ', ' + g + ', ' + b + ')';
}

// ================================================================
// Page-specific init
// ================================================================
$(document).ready(function() {
  loadRecentColors();

  // Screen 02: coloring a shape
  if ($('#svg-arch-container').length) {
    initSVGInteraction('svg-arch-container');
    // Open picker button
    $('#open-picker-btn').on('click', openPicker);
    // Start with prompt visible
    hideColorBarDetails();
  }

  // Screen 03: picker page (standalone)
  if ($('#picker-standalone').length) {
    initHueTabs();
    renderStaticSwatchGrid('all');
    loadRecentColors();
    renderRecentRow();
    $('#close-picker-btn').on('click', function() {
      window.history.back();
    });
    $('#apply-color-btn-standalone').on('click', function() {
      if (DesignStudio.selectedColor) {
        // In production: applies color to selected region and closes sheet
        alert('Color ' + DesignStudio.selectedColor.hex + ' (' + DesignStudio.selectedColor.name + ') selected!');
      }
    });
  }

  // Screen 04: composition
  if ($('#composition-canvas').length) {
    initPieceStrip();
    initGhostPlaceholder();
  }

  // Screen 05: done
  if ($('#done-screen').length) {
    initDoneScreen();
  }

  // Screen 06: upsell
  if ($('#upsell-screen').length) {
    initGhostPlaceholder();
    // Animate suggestion panel in after delay
    setTimeout(function() {
      $('.suggestion-panel').css('display', 'block');
    }, 800);
  }
});
