/**
 * LT Design Studio — Contestant 2
 * Vanilla JS + jQuery (already in Frappe's bundle)
 * No NPM, no build step, no CDN module imports
 *
 * Pattern sources:
 * - SVG event delegation: https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/
 * - jQuery SVG fill: https://copyprogramming.com/howto/javascript-svg-fill-jquery-in-click
 * - Recent colors localStorage: https://bams-thinkery.ca/tools/color-picker
 * - Bottom sheet context-preservation: https://www.nngroup.com/articles/bottom-sheet/
 * - Progressive disclosure (cascading ghost): https://www.nngroup.com/articles/progressive-disclosure/
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
  // Pieces in the composition: [{id, type, name, design, regionColors}]
  composition: [],
  // Active piece index in composition
  activePieceIdx: 0,
  // Active hue family tab
  activeHueFamily: 'all',
  // Recent colors array (up to 6, localStorage-backed)
  recentColors: [],
  // localStorage key
  RECENT_KEY: 'lt_design_studio_recent',
  // Design attribute for current piece: 'swirl' | 'layered' | 'organic'
  // Swirl: up to 4 colors. Layered: up to 8. Organic: palette-driven (no fixed cap).
  currentDesign: 'swirl',
  // Color caps per design type (per PRODUCT-DETAILS.md §2.1)
  DESIGN_COLOR_CAPS: { swirl: 4, layered: 8, organic: 53 }
};

// ================================================================
// Color Catalog — actual 53 named LT latex colors (PRODUCT-DETAILS §2.8)
// Family clusters are the natural picker-organization groups.
// NOTE: hex values are eyeball approximations for mockup rendering.
// The COLOR NAME is the supplier-actionable identifier — not the hex.
// Jeff calls his supplier with color names, not hex codes.
// ================================================================
var COLOR_CATALOG = {
  // Reflex metallics — high-gloss pearlized finish
  'reflex': [
    { hex: '#F2E8D0', name: 'Reflex Champagne' },
    { hex: '#7B6354', name: 'Reflex Truffle'   },
    { hex: '#C0C0C0', name: 'Reflex Silver'    },
    { hex: '#D4AF37', name: 'Reflex Gold'      },
    { hex: '#0047AB', name: 'Reflex Blue'      },
    { hex: '#2E6B2E', name: 'Reflex Green'     },
    { hex: '#6A0DAD', name: 'Reflex Violet'    },
    { hex: '#CC0000', name: 'Reflex Red'       }
  ],
  // Dusk — muted/desaturated tones, sophisticated palette
  'dusk': [
    { hex: '#F2EAD9', name: 'Dusk Cream'     },
    { hex: '#8FAF87', name: 'Dusk Green Tea' },
    { hex: '#7FA3C0', name: 'Dusk Blue'      },
    { hex: '#B39DBB', name: 'Dusk Lilac'     },
    { hex: '#C98F8F', name: 'Dusk Rose'      }
  ],
  // Pastel — soft tints, popular for baby showers / spring events
  'pastel': [
    { hex: '#FADADD', name: 'Pastel Pink'   },
    { hex: '#B8D8F0', name: 'Pastel Blue'   },
    { hex: '#C7E8C2', name: 'Pastel Green'  },
    { hex: '#D9C4E8', name: 'Pastel Purple' },
    { hex: '#FFF5B0', name: 'Pastel Yellow' },
    { hex: '#FAC8A8', name: 'Pastel Melon'  }
  ],
  // Brights — bold saturated tones
  'brights': [
    { hex: '#E8272A', name: 'Red'        },
    { hex: '#F57C00', name: 'Orange'     },
    { hex: '#FFD600', name: 'Yellow'     },
    { hex: '#C62828', name: 'Raspberry'  },
    { hex: '#E91E8C', name: 'Fuchsia'    },
    { hex: '#F48FB1', name: 'Bubble Gum' },
    { hex: '#A8D5A2', name: 'Eucalyptus' },
    { hex: '#BEFF00', name: 'Lime'       },
    { hex: '#6EC6F0', name: 'LT Blue'    },
    { hex: '#7986CB', name: 'Periwinkle' },
    { hex: '#1E3FA8', name: 'Royal Blue' },
    { hex: '#80DEEA', name: "Robin's Egg" },
    { hex: '#F4C842', name: 'Honey'      },
    { hex: '#7B1FA2', name: 'Violet'     },
    { hex: '#CE93D8', name: 'Orchid'     },
    { hex: '#B39DDB', name: 'Lilac'      }
  ],
  // Neutrals — white, black, grey, earth tones
  'neutrals': [
    { hex: '#FFFFFF', name: 'White'      },
    { hex: '#1A1A1A', name: 'Black'      },
    { hex: '#BDBDBD', name: 'Grey'       },
    { hex: '#808080', name: 'Smoke Grey' },
    { hex: '#D7C4A3', name: 'Latte'      },
    { hex: '#795548', name: 'Brown'      },
    { hex: '#4E342E', name: 'Chocolate'  },
    { hex: '#E0D5C1', name: 'Clear'      },
    { hex: '#F4C2C2', name: 'Blush'      }
  ],
  // Deep tones — rich, saturated darks
  'deep': [
    { hex: '#1B5E20', name: 'Forest'      },
    { hex: '#1A5744', name: 'Shamrock'    },
    { hex: '#004D40', name: 'Wintergreen' },
    { hex: '#00695C', name: 'Teal'        },
    { hex: '#006064', name: 'Deep Teal'   },
    { hex: '#37474F', name: 'Blue Slate'  },
    { hex: '#00897B', name: 'Empowermint' }
  ]
};

// Flat list for 'all' tab — preserves family order for scannability
function getAllColors() {
  var all = [];
  Object.keys(COLOR_CATALOG).forEach(function(family) {
    COLOR_CATALOG[family].forEach(function(c) { all.push(c); });
  });
  return all;
}

// ================================================================
// Design attribute helpers
// ================================================================

// Returns the color cap for the current design type
function getColorCap() {
  return DesignStudio.DESIGN_COLOR_CAPS[DesignStudio.currentDesign] || 4;
}

// Count how many distinct colors are currently in use across all regions
function getActiveColorCount() {
  var hexSet = {};
  Object.values(DesignStudio.regionColors).forEach(function(c) {
    if (c && c.hex) hexSet[c.hex] = true;
  });
  return Object.keys(hexSet).length;
}

// Returns true if adding newColorHex would exceed the design's cap
function wouldExceedCap(newColorHex) {
  var cap = getColorCap();
  var existing = {};
  Object.values(DesignStudio.regionColors).forEach(function(c) {
    if (c && c.hex) existing[c.hex] = true;
  });
  if (existing[newColorHex]) return false; // already in use, no new slot needed
  return Object.keys(existing).length >= cap;
}

// Show a color cap nudge in the picker
function showColorCapNudge() {
  var cap = getColorCap();
  var nextDesign = cap === 4 ? 'Layered' : null;
  var msg = 'Swirl designs use up to ' + cap + ' colors.';
  if (nextDesign) msg += ' Switch to ' + nextDesign + ' for more.';
  var $nudge = $('#color-cap-nudge');
  if (!$nudge.length) {
    $nudge = $('<div id="color-cap-nudge" style="' +
      'background:#FFF8E1; border-left:3px solid #F4C842; padding:8px 12px; ' +
      'font-size:0.75rem; color:#5D4037; line-height:1.4; margin:8px 16px;">' +
    '</div>');
    $('.swatch-grid').before($nudge);
  }
  $nudge.text(msg).show();
  setTimeout(function() { $nudge.fadeOut(400); }, 2800);
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
  // Cap enforcement: block selection if this color would exceed the design cap
  if (wouldExceedCap(colorObj.hex)) {
    showColorCapNudge();
    return;
  }

  DesignStudio.selectedColor = colorObj;

  // Update hex chip — NAME is primary (supplier-actionable), hex is secondary annotation
  // Per PRODUCT-DETAILS §4: "Color NAME is the supplier-actionable identifier — not the hex."
  $('#hex-chip-swatch').css('background', colorObj.hex);
  $('#hex-chip-name').text(colorObj.name);           // large, prominent
  $('#hex-chip-code').text(colorObj.hex);            // small monospace annotation
  // Update selected state in grid
  $('#swatch-grid .swatch-dot').removeClass('swatch-dot--selected');
  $('#swatch-grid .swatch-dot').each(function() {
    if ($(this).attr('title') === colorObj.name) {
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
// buildInquiryPayload — assembles everything Jeff needs to open his pitch.
// Returns a plain object matching Frappe Lead fields.
//
// Fields Jeff sees in ERPNext CRM:
//   lead_name           — customer name
//   email_id / phone    — contact (whichever they provided)
//   custom_design_ref   — "LT-{timestamp}" shared reference number
//   custom_pieces       — "Balloon Arch, Column, Centerpiece"
//   custom_palette      — "#FFB6C1 (Light Pink), #87CEEB (Sky Blue), #FFFFFF (White)"
//   custom_design_notes — optional freeform from the textarea
//   source              — "Design Studio"
//
// Hex codes are explicit in custom_palette so Jeff can match SKUs with
// his balloon supplier directly — color names alone are ambiguous across
// catalogs.
function buildInquiryPayload() {
  // --- Collect composition state ---
  // In production this comes from DesignStudio.composition; here we read
  // whatever demo state is present and fall back gracefully.
  var pieces = [];
  var paletteMap = {}; // hex -> name, deduped

  // Pull from DesignStudio state if available
  if (DesignStudio.composition && DesignStudio.composition.length) {
    DesignStudio.composition.forEach(function(piece) {
      pieces.push(piece.name || piece.type || 'Piece');
      if (piece.regionColors) {
        Object.values(piece.regionColors).forEach(function(c) {
          paletteMap[c.hex] = c.name || c.hex;
        });
      }
    });
  }

  // Fall back to demo data for mockup context
  if (!pieces.length) {
    pieces = ['Balloon Arch', 'Column', 'Centerpiece'];
  }
  if (!Object.keys(paletteMap).length) {
    paletteMap = {
      '#FFB6C1': 'Light Pink',
      '#87CEEB': 'Sky Blue',
      '#FFFFFF': 'White'
    };
  }

  // Format palette string: "#FFB6C1 (Light Pink), #87CEEB (Sky Blue), ..."
  var paletteStr = Object.keys(paletteMap).map(function(hex) {
    return hex + ' (' + paletteMap[hex] + ')';
  }).join(', ');

  // Design reference number (timestamp-based, shown on card as "LT-2026-001" in demo)
  var ref = 'LT-' + Date.now();

  // Contact fields
  var senderName    = ($('#sender-name').val()    || '').trim();
  var senderContact = ($('#sender-contact').val() || '').trim();
  var senderNotes   = ($('#sender-notes').val()   || '').trim();

  // Determine email vs phone from contact field heuristic
  var emailVal = senderContact.indexOf('@') > -1 ? senderContact : '';
  var phoneVal = senderContact.indexOf('@') > -1 ? '' : senderContact;

  return {
    doctype:              'Lead',
    lead_name:            senderName || 'Design Studio Visitor',
    email_id:             emailVal,
    phone:                phoneVal,
    source:               'Design Studio',
    custom_design_ref:    ref,
    custom_pieces:        pieces.join(', '),
    custom_palette:       paletteStr,
    custom_design_notes:  senderNotes
  };
}

// checkSendReady — enables the CTA only when name + contact are filled
function checkSendReady() {
  var name    = ($('#sender-name').val()    || '').trim();
  var contact = ($('#sender-contact').val() || '').trim();
  var ready   = name.length > 0 && contact.length > 0;
  var $btn    = $('#send-to-jeff-btn');
  $btn.prop('disabled', !ready);
  $btn.css('opacity', ready ? '1' : '0.5');
  $btn.css('cursor', ready ? 'pointer' : 'not-allowed');
}

function initDoneScreen() {
  // Populate palette row with hex + name rows (colors from state or demo fallback)
  var colors = [];
  try {
    var stored = sessionStorage.getItem('lt_design_palette');
    if (stored) colors = JSON.parse(stored);
  } catch(e) {}

  // Demo fallback with names
  if (!colors.length) {
    colors = [
      { hex: '#FFB6C1', name: 'Light Pink' },
      { hex: '#87CEEB', name: 'Sky Blue'   },
      { hex: '#FFFFFF', name: 'White'       }
    ];
  }

  // If we have live colors, replace the static HTML rows
  var $row = $('#done-palette-row');
  if ($row.length && colors.length) {
    $row.empty();
    colors.forEach(function(c) {
      var borderStyle = c.hex === '#FFFFFF' ? 'border:2px solid #EBEBEB;' : 'border:2px solid #fff;';
      $row.append(
        '<div style="display:flex; align-items:center; gap:8px;">' +
          '<div style="width:18px; height:18px; border-radius:50%; background:' + c.hex + '; ' + borderStyle + ' box-shadow:0 1px 3px rgba(0,0,0,.12); flex-shrink:0;"></div>' +
          '<span style="font-family:monospace; font-size:0.75rem; font-weight:600; color:#1A1A1A;">' + c.hex + '</span>' +
          '<span style="font-size:0.75rem; color:#595A5C;">' + (c.name || '') + '</span>' +
        '</div>'
      );
    });
  }

  // Wire contact fields
  $('#sender-name, #sender-contact').on('input', checkSendReady);

  // "Send to Jeff" button handler
  $('#send-to-jeff-btn').on('click', function() {
    if ($(this).prop('disabled')) return;

    var payload = buildInquiryPayload();

    // Production path: frappe.call() creates the Lead record.
    // The frappe global is available on all Frappe website pages.
    //
    //   frappe.call({
    //     method: 'frappe.client.insert',
    //     args:   { doc: payload },
    //     callback: function(r) {
    //       if (r.message && r.message.name) {
    //         showSentConfirmation(payload.custom_design_ref);
    //       } else {
    //         showSendError();
    //       }
    //     },
    //     error: function() { showSendError(); }
    //   });
    //
    // Mockup path (frappe not available in static HTML double-click context):
    console.log('Design Studio inquiry payload:', JSON.stringify(payload, null, 2));
    showSentConfirmation(payload.custom_design_ref);
  });
}

function showSentConfirmation(ref) {
  // Hide send form, show confirmation
  $('#send-to-jeff-btn').closest('.done-actions').hide();
  $('.done-send-note').hide();
  $('#sent-confirm').fadeIn(300);
  // Update Jeff-note to post-send message
  $('.jeff-note__msg').text(
    'Got it — I\'ll look up design ' + ref + ' and give you a call. ' +
    'Expect to hear from me within 24 hours.'
  );
}

function showSendError() {
  // Loud failure: tell the customer, never show a blank screen
  var $btn = $('#send-to-jeff-btn');
  $btn.text('Couldn\'t send — try again');
  $btn.css('background', '#8B0000');
  $btn.prop('disabled', false).css('opacity', '1').css('cursor', 'pointer');
  // Secondary channel always visible
  $('.done-send-note').html(
    'Having trouble? Call Jeff directly: <strong>(801) 285-0860</strong> or email <strong>hi@locallytwisted.com</strong>'
  ).css('color', '#8B0000');
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
