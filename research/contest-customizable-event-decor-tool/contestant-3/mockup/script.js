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
  // 50+ named balloon colors with hex values
  // Organized into families for the grouped palette pattern
  // (Baymard research: grouped families beat flat 50+ grid on mobile)
  // =========================================================
  var BALLOON_COLORS = {
    hot: [
      { name: 'White',       hex: '#F5F5F5' },
      { name: 'Blush',       hex: '#F4DFD7' },
      { name: 'Rose',        hex: '#E8A8A0' },
      { name: 'Red',         hex: '#D63838' },
      { name: 'Coral',       hex: '#FF6F61' },
      { name: 'Gold',        hex: '#D4AF37' },
      { name: 'Lemon',       hex: '#F9F871' },
      { name: 'Lime',        hex: '#B8FF9E' },
      { name: 'Mint',        hex: '#A8E6CF' },
      { name: 'Seafoam',     hex: '#88FED0' },
      { name: 'Teal',        hex: '#008080' },
      { name: 'Sky Blue',    hex: '#A0E9FF' },
      { name: 'Soft Blue',   hex: '#C3DCF3' },
      { name: 'Lavender',    hex: '#C9B8F5' },
      { name: 'Plum',        hex: '#7B4F9E' },
      { name: 'Black',       hex: '#1A1A1A' },
    ],
    families: [
      {
        label: 'Reds & Pinks',
        colors: [
          { name: 'Deep Red',    hex: '#8B1A1A' },
          { name: 'Cherry',      hex: '#D63838' },
          { name: 'Coral',       hex: '#FF6F61' },
          { name: 'Salmon',      hex: '#FA8072' },
          { name: 'Hot Pink',    hex: '#FF69B4' },
          { name: 'Fuchsia',     hex: '#E91E8C' },
          { name: 'Rose',        hex: '#E8A8A0' },
          { name: 'Blush',       hex: '#F4DFD7' },
          { name: 'Petal',       hex: '#FFD1DC' },
        ]
      },
      {
        label: 'Oranges & Yellows',
        colors: [
          { name: 'Tangerine',   hex: '#FF8C00' },
          { name: 'Orange',      hex: '#FF6A00' },
          { name: 'Peach',       hex: '#FFCBA4' },
          { name: 'Butter',      hex: '#FFF3B0' },
          { name: 'Lemon',       hex: '#F9F871' },
          { name: 'Sunflower',   hex: '#FFD700' },
          { name: 'Gold',        hex: '#D4AF37' },
        ]
      },
      {
        label: 'Greens',
        colors: [
          { name: 'Lime',        hex: '#B8FF9E' },
          { name: 'Mint',        hex: '#A8E6CF' },
          { name: 'Seafoam',     hex: '#88FED0' },
          { name: 'Sage',        hex: '#B2C9A0' },
          { name: 'Forest',      hex: '#228B22' },
          { name: 'Emerald',     hex: '#50C878' },
          { name: 'Olive',       hex: '#808000' },
        ]
      },
      {
        label: 'Blues & Teals',
        colors: [
          { name: 'Sky Cyan',    hex: '#A0E9FF' },
          { name: 'Aqua',        hex: '#80F5F3' },
          { name: 'Soft Blue',   hex: '#C3DCF3' },
          { name: 'Cornflower',  hex: '#6495ED' },
          { name: 'Royal Blue',  hex: '#4169E1' },
          { name: 'Navy',        hex: '#1A237E' },
          { name: 'Teal',        hex: '#008080' },
          { name: 'Cobalt',      hex: '#0047AB' },
        ]
      },
      {
        label: 'Purples & Neutrals',
        colors: [
          { name: 'Lavender',    hex: '#C9B8F5' },
          { name: 'Lilac',       hex: '#E0C8F8' },
          { name: 'Violet',      hex: '#8B00FF' },
          { name: 'Plum',        hex: '#7B4F9E' },
          { name: 'Champagne',   hex: '#F7E7CE' },
          { name: 'Silver',      hex: '#C0C0C0' },
          { name: 'White',       hex: '#F5F5F5' },
          { name: 'Ivory',       hex: '#FFFFF0' },
          { name: 'Black',       hex: '#1A1A1A' },
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
      var regionId = $(this).attr('id');
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
