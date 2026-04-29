/**
 * Locally Twisted — Design Studio
 * Contestant 3: The Coloring Page Frame
 *
 * Vanilla JS + jQuery only. No frameworks, no build step.
 * Frappe-recreatable: this file maps to www/design-studio.js
 *
 * State is held in a module-level object; no backend calls
 * during the design session (read-only client-side state).
 */

(function ($) {
  'use strict';

  // =========================================================
  // BALLOON COLOR CATALOG
  // 53 named balloon colors — verbatim from LT catalog (PRODUCT-DETAILS.md Section 2.8)
  // Hex values are reasonable approximations for display only.
  // COLOR NAMES are the supplier-actionable identifiers: Jeff orders by name.
  // Hex codes are eyeball-matching aids; the catalog has no official hex values yet.
  // Organized into families for the grouped palette pattern
  // (Baymard research: grouped families beat flat 50+ grid on mobile)
  // =========================================================
  var BALLOON_COLORS = {
    // 16 "hot" picks for the quick-access grid — chosen to span the full palette range
    hot: [
      { name: 'White',            hex: '#F5F5F5' },
      { name: 'Blush',            hex: '#F4DFD7' },
      { name: 'Dusk Rose',        hex: '#D4A5A5' },
      { name: 'Raspberry',        hex: '#C0115E' },
      { name: 'Red',              hex: '#D63838' },
      { name: 'Reflex Gold',      hex: '#C9A227' },
      { name: 'Pastel Yellow',    hex: '#FFF3B0' },
      { name: 'Empowermint',      hex: '#A8E6CF' },
      { name: 'Lime',             hex: '#BFFF5C' },
      { name: 'Teal',             hex: '#008080' },
      { name: 'Robin\'s Egg',     hex: '#8ECAE6' },
      { name: 'Pastel Blue',      hex: '#C5D8F0' },
      { name: 'Periwinkle',       hex: '#CCCCFF' },
      { name: 'Orchid',           hex: '#DA70D6' },
      { name: 'Reflex Silver',    hex: '#C0C0C0' },
      { name: 'Black',            hex: '#1A1A1A' },
    ],
    families: [
      {
        // Reflex = metallic/shiny
        label: 'Reflex (Metallics)',
        colors: [
          { name: 'Reflex Champagne', hex: '#F7E7CE' },
          { name: 'Reflex Truffle',   hex: '#9C7A5A' },
          { name: 'Reflex Silver',    hex: '#C0C0C0' },
          { name: 'Reflex Gold',      hex: '#C9A227' },
          { name: 'Reflex Blue',      hex: '#2563EB' },
          { name: 'Reflex Green',     hex: '#16A34A' },
          { name: 'Reflex Violet',    hex: '#7C3AED' },
          { name: 'Reflex Red',       hex: '#B91C1C' },
        ]
      },
      {
        // Dusk = muted / desaturated tones
        label: 'Dusk (Muted)',
        colors: [
          { name: 'Dusk Cream',     hex: '#F5ECD7' },
          { name: 'Dusk Green Tea', hex: '#B5C9B0' },
          { name: 'Dusk Blue',      hex: '#8BA7C7' },
          { name: 'Dusk Lilac',     hex: '#C4B5D0' },
          { name: 'Dusk Rose',      hex: '#D4A5A5' },
        ]
      },
      {
        // Pastel = soft tints
        label: 'Pastels',
        colors: [
          { name: 'Pastel Pink',   hex: '#FFD1DC' },
          { name: 'Pastel Blue',   hex: '#C5D8F0' },
          { name: 'Pastel Green',  hex: '#C3EBC3' },
          { name: 'Pastel Purple', hex: '#DDD0F0' },
          { name: 'Pastel Yellow', hex: '#FFF3B0' },
          { name: 'Pastel Melon',  hex: '#FFCBA4' },
          { name: 'Blush',         hex: '#F4DFD7' },
        ]
      },
      {
        // Brights = saturated vivid colors
        label: 'Brights',
        colors: [
          { name: 'Red',         hex: '#D63838' },
          { name: 'Orange',      hex: '#F77F00' },
          { name: 'Yellow',      hex: '#FAD02C' },
          { name: 'Raspberry',   hex: '#C0115E' },
          { name: 'Fuchsia',     hex: '#E91E8C' },
          { name: 'Bubble Gum',  hex: '#FF88C2' },
          { name: 'Lime',        hex: '#BFFF5C' },
          { name: 'Shamrock',    hex: '#009E60' },
          { name: 'Eucalyptus',  hex: '#44A08D' },
          { name: 'Teal',        hex: '#008080' },
          { name: 'LT Blue',     hex: '#ADD8E6' },
          { name: 'Periwinkle',  hex: '#CCCCFF' },
          { name: 'Royal Blue',  hex: '#4169E1' },
          { name: 'Robin\'s Egg', hex: '#8ECAE6' },
          { name: 'Orchid',      hex: '#DA70D6' },
          { name: 'Honey',       hex: '#FFBD35' },
        ]
      },
      {
        // Greens & Teals
        label: 'Greens & Teals',
        colors: [
          { name: 'Empowermint',  hex: '#A8E6CF' },
          { name: 'Wintergreen',  hex: '#3EB489' },
          { name: 'Forest',       hex: '#228B22' },
          { name: 'Deep Teal',    hex: '#006374' },
          { name: 'Blue Slate',   hex: '#6A8FA7' },
          { name: 'Smoke Grey',   hex: '#9E9E9E' },
        ]
      },
      {
        // Purples & Blues (deeper)
        label: 'Blues & Purples',
        colors: [
          { name: 'Violet',      hex: '#8B00FF' },
          { name: 'Lilac',       hex: '#C8A2C8' },
        ]
      },
      {
        // Neutrals = whites, blacks, grays, browns
        label: 'Neutrals & Browns',
        colors: [
          { name: 'White',       hex: '#F5F5F5' },
          { name: 'Grey',        hex: '#9E9E9E' },
          { name: 'Black',       hex: '#1A1A1A' },
          { name: 'Latte',       hex: '#D4B896' },
          { name: 'Brown',       hex: '#7B3F00' },
          { name: 'Chocolate',   hex: '#3D1C02' },
          { name: 'Clear',       hex: '#E8F4FF' },
        ]
      }
    ]
  };

  // =========================================================
  // SESSION STATE
  // Held in memory only — no persistence (per brief: "downstream")
  // =========================================================
  var state = {
    selectedColor: { name: 'White', hex: '#F5F5F5' },
    selectedRegion: null,  // ID of the currently active fill region
    composition: [],       // Array of { shape, regions: { regionId: hex } }
  };

  // =========================================================
  // SWATCH RENDERING
  // Used on 02-color-one, 03-picker
  // =========================================================
  function renderSwatch(color, container, className) {
    var $swatch = $('<button>')
      .addClass(className || 'swatch')
      .css('background-color', color.hex)
      .attr('title', color.name + ' — ' + color.hex)
      .attr('aria-label', color.name)
      .data('color', color)
      .on('click touchstart', function (e) {
        e.preventDefault();
        selectColor(color);
      });
    container.append($swatch);
    return $swatch;
  }

  function selectColor(color) {
    state.selectedColor = color;

    // Update all .swatch.selected markers
    $('.swatch, .picker-swatch').removeClass('selected');
    $('.swatch[title="' + color.name + ' — ' + color.hex + '"], .picker-swatch[title="' + color.name + ' — ' + color.hex + '"]').addClass('selected');

    // Update hex pill display
    $('.hex-pill, .picker-hex-value').text(color.hex);
    $('.picker-hex-name').text(color.name);
    $('.picker-hex-preview').css('background-color', color.hex);

    // If a region is selected, fill it immediately
    if (state.selectedRegion) {
      fillRegion(state.selectedRegion, color.hex);
    }
  }

  // =========================================================
  // FILL REGION INTERACTION
  // =========================================================
  function fillRegion(regionId, hex) {
    var $region = $('#' + regionId);
    $region
      .attr('fill', hex)
      .addClass('filled')
      .removeClass('fill-region') // keep styled but mark as filled
      .addClass('fill-region');   // re-add for stroke handling

    // Also fill all mirror circles that point to this primary regionId
    $('[data-mirrors="' + regionId + '"]')
      .attr('fill', hex)
      .addClass('filled');

    // Also fill sibling circles with same base ID prefix (e.g. arch-main-2, arch-accent-2)
    // These are secondary circles within the same region group
    $('[id^="' + regionId + '-"]').each(function () {
      $(this).attr('fill', hex).addClass('filled');
    });

    // Update region-key dot color
    $('[data-region-key="' + regionId + '"] .region-key-dot')
      .css('background-color', hex)
      .addClass('filled');

    state.selectedRegion = regionId;
  }

  function initFillRegions() {
    // Listen for taps on fill regions
    $(document).on('click touchend', '.fill-region', function (e) {
      e.preventDefault();
      var $el = $(this);
      // If this is a mirror, delegate to the primary region
      var mirrorTarget = $el.data('mirrors');
      var regionId = mirrorTarget || $el.attr('id');
      if (!regionId) return;
      selectRegion(regionId);
      // Apply current color immediately
      fillRegion(regionId, state.selectedColor.hex);
    });

    // Region key items
    $(document).on('click', '.region-key-item', function () {
      var regionId = $(this).data('region');
      selectRegion(regionId);
    });
  }

  function selectRegion(regionId) {
    state.selectedRegion = regionId;
    $('.fill-region').removeClass('selected-region');
    $('#' + regionId).addClass('selected-region');
    $('.region-key-item').removeClass('active');
    $('[data-region="' + regionId + '"]').addClass('active');

    // Update tray header label
    var label = $('#' + regionId).data('label') || 'Region';
    $('.tray-region-name').text('Color: ' + label);
  }

  // =========================================================
  // PALETTE TRAY INIT (02-color-one)
  // =========================================================
  function initPaletteTray() {
    var $hot = $('#palette-hot');
    var $families = $('#palette-families');
    if (!$hot.length && !$families.length) return;

    // Render hot swatches
    $.each(BALLOON_COLORS.hot, function (i, color) {
      renderSwatch(color, $hot);
    });

    // Render family rows
    $.each(BALLOON_COLORS.families, function (i, family) {
      var $section = $('<div>').addClass('palette-family');
      var $label = $('<span>').addClass('palette-family-label').text(family.label);
      var $row = $('<div>').addClass('palette-row');

      $.each(family.colors, function (j, color) {
        renderSwatch(color, $row);
      });

      // Truncation fade indicator (last item suggest more)
      $section.append($label).append($row);
      $families.append($section);
    });

    // Init with first hot color selected
    selectColor(BALLOON_COLORS.hot[0]);
  }

  // =========================================================
  // FULL PICKER INIT (03-picker)
  // =========================================================
  function initFullPicker() {
    var $body = $('#picker-palette-body');
    if (!$body.length) return;

    // Render each family section
    $.each(BALLOON_COLORS.families, function (i, family) {
      var $section = $('<div>').addClass('picker-family-section');
      var $title = $('<div>').addClass('picker-family-title').text(family.label);
      var $grid = $('<div>').addClass('picker-swatch-grid');

      $.each(family.colors, function (j, color) {
        renderSwatch(color, $grid, 'picker-swatch');
      });

      $section.append($title).append($grid);
      $body.append($section);
    });

    // Add all hot colors to a "Popular" section at top
    var $popular = $('<div>').addClass('picker-family-section');
    var $popularTitle = $('<div>').addClass('picker-family-title').text('Popular');
    var $popularGrid = $('<div>').addClass('picker-swatch-grid');
    $.each(BALLOON_COLORS.hot, function (i, color) {
      renderSwatch(color, $popularGrid, 'picker-swatch');
    });
    $popular.append($popularTitle).append($popularGrid);
    $body.prepend($popular);

    // Search filter
    $('#picker-search-input').on('input', function () {
      var query = $(this).val().toLowerCase();
      if (!query) {
        $('.picker-swatch').show();
        $('.picker-family-section').show();
        return;
      }
      $('.picker-family-section').each(function () {
        var $section = $(this);
        var anyVisible = false;
        $section.find('.picker-swatch').each(function () {
          var colorData = $(this).data('color');
          var matches = colorData.name.toLowerCase().indexOf(query) > -1 ||
                        colorData.hex.toLowerCase().indexOf(query) > -1;
          $(this).toggle(matches);
          if (matches) anyVisible = true;
        });
        $section.toggle(anyVisible);
      });
    });

    selectColor(BALLOON_COLORS.hot[7]); // Start with "Lime" as default
  }

  // =========================================================
  // COMPOSITION VIEW INTERACTIONS (04-composition)
  // =========================================================
  function initComposition() {
    // Empty piece slot tap -> goes to entry page
    $(document).on('click', '.piece-card.empty-piece', function () {
      // In production: navigate to shape selection
      // In mockup: visual feedback only
      $(this).css('border-color', '#1A1A1A');
      setTimeout(function () {
        window.location.href = '01-entry.html';
      }, 200);
    });

    // Piece card tap -> goes to that shape's coloring screen
    $(document).on('click', '.piece-card:not(.empty-piece)', function () {
      $(this).css('box-shadow', '0 2px 12px rgba(0,128,128,0.25)');
    });
  }

  // =========================================================
  // ADD TO COMPOSITION BUTTON (02-color-one)
  // =========================================================
  function initAddToComposition() {
    $('#btn-add-composition').on('click', function () {
      // Visual feedback, then navigate to composition view
      $(this).text('Added!').addClass('btn-ghost').removeClass('btn-primary');
      setTimeout(function () {
        window.location.href = '04-composition.html';
      }, 500);
    });
  }

  // =========================================================
  // CAPTURE DESIGN (05-done)
  // =========================================================
  function initCapture() {
    $('#btn-send-jeff').on('click', function () {
      $(this).text('Opening inquiry form…');
      // In production: would pre-populate the /book form
    });
  }

  // =========================================================
  // UPSELL SCREEN INTERACTIONS (06-upsell)
  // =========================================================
  function initUpsell() {
    $('#btn-add-arch').on('click', function () {
      $(this).text('Great choice!').addClass('btn-ghost').removeClass('btn-primary');
      setTimeout(function () {
        window.location.href = '02-color-one.html';
      }, 500);
    });
  }

  // =========================================================
  // AUTO-INIT: detect which screen we're on and init
  // =========================================================
  $(document).ready(function () {
    initFillRegions();

    if ($('#palette-hot').length) {
      initPaletteTray();
    }
    if ($('#picker-palette-body').length) {
      initFullPicker();
    }
    if ($('.composition-screen').length) {
      initComposition();
    }
    if ($('#btn-add-composition').length) {
      initAddToComposition();
    }
    if ($('#btn-send-jeff').length) {
      initCapture();
    }
    if ($('#btn-add-arch').length) {
      initUpsell();
    }

    // Keyboard nav for swatches (accessibility)
    $(document).on('keydown', '.swatch, .picker-swatch', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        $(this).trigger('click');
      }
    });
  });

})(jQuery);
