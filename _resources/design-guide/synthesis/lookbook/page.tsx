'use client';

/**
 * lookbook/page.tsx — Synthesis Look Book + Mood-First Configurator
 *
 * Structural source: D7 (The Atelier)
 *   - Mood-first 4-step configurator (mood → colors → style → scale)
 *   - No text on images, anywhere — editorial split separates image from words
 *   - Portfolio grid with category filter + occasion filter
 *   - "Something else in mind?" inquiry redirect at bottom
 *   - Selections serialize to query params → redirect to /inquire?mood=...
 *
 * Visual language: LT STYLE-GUIDE.md only
 *   - DM Serif Display + Raleway (NOT Cormorant, NOT DM Mono)
 *   - Teal for CTA buttons only
 *   - Accent palette as pill accents (border/swatch), never full backgrounds
 *   - Surface tints (blush-tint, blue-tint) for form fields and configurator bg
 *
 * Loud failure: if the inquiry redirect fails (e.g., params missing), a
 * user-visible error banner appears — per loud-failure.md rule.
 *
 * Configurator steps:
 *   Step 1: "Start with a feeling." — 6 mood pills, single-select
 *   Step 2: "Family colors." — Family tabs, 4 curated swatches + "See all 60 colors"
 *   Step 3: "What style?" — Organic / Structured / Minimal / Maximalist chips
 *   Step 4: "What scale?" — Intimate / Corporate / Wedding / Large gala
 *   Submit: serializes to /inquire?mood=X&colors=Y&style=Z&scale=W
 */

import { useState, useCallback } from 'react';
import SynthesisLayout from '../layout';

// ── Color library — product data, NOT UI tokens ───────────────────────────────
// These hex values are Jeff's actual balloon color inventory.
// They appear only as backgroundColor on swatch circles.
// All UI chrome uses --token vars. Per D7's documented exemption for product data.
interface BalloonColor {
  id: string;
  name: string;
  hex: string; // product catalog data — exempt from hardcoded-hex rule
  family: string;
}

const COLOR_FAMILIES: Record<string, { label: string; colors: BalloonColor[] }> = {
  neutrals: {
    label: 'Whites & Neutrals',
    colors: [
      { id: 'pearl-white', name: 'Pearl White',  hex: '#fafafa', family: 'neutrals' },
      { id: 'ivory',       name: 'Ivory',        hex: '#f5f0e8', family: 'neutrals' },
      { id: 'champagne',   name: 'Champagne',    hex: '#e8d5b0', family: 'neutrals' },
      { id: 'sand',        name: 'Sand',         hex: '#c9b99a', family: 'neutrals' },
      { id: 'taupe',       name: 'Taupe',        hex: '#a09080', family: 'neutrals' },
      { id: 'slate-gray',  name: 'Slate',        hex: '#7a8490', family: 'neutrals' },
    ],
  },
  pinks: {
    label: 'Pinks & Reds',
    colors: [
      { id: 'blush',       name: 'Blush',        hex: '#e8a5a0', family: 'pinks' },
      { id: 'rose',        name: 'Rose',         hex: '#d4607c', family: 'pinks' },
      { id: 'coral',       name: 'Coral',        hex: '#e06050', family: 'pinks' },
      { id: 'terracotta',  name: 'Terracotta',   hex: '#c45540', family: 'pinks' },
      { id: 'hot-pink',    name: 'Hot Pink',     hex: '#e8407a', family: 'pinks' },
      { id: 'burgundy',    name: 'Burgundy',     hex: '#7c2d3c', family: 'pinks' },
    ],
  },
  blues: {
    label: 'Blues & Purples',
    colors: [
      { id: 'sky',         name: 'Sky',          hex: '#90b8d8', family: 'blues' },
      { id: 'cornflower',  name: 'Cornflower',   hex: '#6084c8', family: 'blues' },
      { id: 'navy',        name: 'Navy',         hex: '#283858', family: 'blues' },
      { id: 'lavender',    name: 'Lavender',     hex: '#c0a8d8', family: 'blues' },
      { id: 'plum',        name: 'Plum',         hex: '#604870', family: 'blues' },
      { id: 'periwinkle',  name: 'Periwinkle',   hex: '#9090d8', family: 'blues' },
    ],
  },
  greens: {
    label: 'Greens & Teals',
    colors: [
      { id: 'sage',        name: 'Sage',         hex: '#909870', family: 'greens' },
      { id: 'mint-green',  name: 'Mint',         hex: '#a8c8b0', family: 'greens' },
      { id: 'forest',      name: 'Forest',       hex: '#506848', family: 'greens' },
      { id: 'emerald',     name: 'Emerald',      hex: '#2c7a50', family: 'greens' },
      { id: 'teal-balloon',name: 'Teal',         hex: '#408080', family: 'greens' },
      { id: 'olive',       name: 'Olive',        hex: '#7a7840', family: 'greens' },
    ],
  },
  metallics: {
    label: 'Metallics',
    colors: [
      { id: 'gold-met',    name: 'Gold',         hex: '#c8a840', family: 'metallics' },
      { id: 'silver',      name: 'Silver',       hex: '#b8bcc0', family: 'metallics' },
      { id: 'rose-gold',   name: 'Rose Gold',    hex: '#c89080', family: 'metallics' },
      { id: 'copper',      name: 'Copper',       hex: '#b87050', family: 'metallics' },
      { id: 'chrome',      name: 'Chrome',       hex: '#d0d4d8', family: 'metallics' },
      { id: 'bronze',      name: 'Bronze',       hex: '#908060', family: 'metallics' },
    ],
  },
};

const CURATED_COUNT = 4; // swatches shown before "See all"

// ── Mood definitions ──────────────────────────────────────────────────────────
// Accent palette used as pill accents (border color) — never full backgrounds.
// Per STYLE-GUIDE: accent palette for "Small accent elements (tags, badges, pills)"
interface Mood {
  id: string;
  label: string;
  description: string;
  accentColor: string; // --token reference for pill border accent
  suggestedFamily: string;
}

const MOODS: Mood[] = [
  {
    id: 'romantic',
    label: 'Romantic',
    description: 'Soft, layered, intimate',
    accentColor: 'var(--color-blush)',
    suggestedFamily: 'pinks',
  },
  {
    id: 'bold',
    label: 'Bold',
    description: 'High contrast, statement-making',
    accentColor: 'var(--color-aqua)',
    suggestedFamily: 'blues',
  },
  {
    id: 'soft',
    label: 'Soft',
    description: 'Muted, airy, understated',
    accentColor: 'var(--color-soft-blue)',
    suggestedFamily: 'neutrals',
  },
  {
    id: 'festive',
    label: 'Festive',
    description: 'Warm, celebratory, joyful',
    accentColor: 'var(--color-lime-pastel)',
    suggestedFamily: 'pinks',
  },
  {
    id: 'elegant',
    label: 'Elegant',
    description: 'Refined, tailored, polished',
    accentColor: 'var(--color-aqua)',
    suggestedFamily: 'metallics',
  },
  {
    id: 'modern',
    label: 'Modern',
    description: 'Clean, structured, graphic',
    accentColor: 'var(--color-soft-blue)',
    suggestedFamily: 'blues',
  },
];

// ── Style options ─────────────────────────────────────────────────────────────
const STYLE_OPTIONS = ['Organic', 'Structured', 'Minimal', 'Maximalist'];

// ── Scale options ─────────────────────────────────────────────────────────────
interface ScaleOption {
  id: string;
  label: string;
  description: string;
}

const SCALE_OPTIONS: ScaleOption[] = [
  { id: 'intimate',  label: 'Intimate gathering',  description: 'Small party, home event, personal celebration' },
  { id: 'corporate', label: 'Corporate event',      description: 'Office party, brand activation, conference' },
  { id: 'wedding',   label: 'Wedding',              description: 'Ceremony arch, reception backdrop, full venue' },
  { id: 'gala',      label: 'Large gala',           description: '300+ guests, multi-room, statement balloon decor' },
];

// ── Configurator state ────────────────────────────────────────────────────────
interface ConfigState {
  step: number;
  selectedMood: string | null;
  selectedFamily: string | null;
  selectedColors: string[];
  expandedFamilies: Set<string>;
  selectedStyle: string | null;
  selectedScale: string | null;
}

// ── Loud failure — serialize config to inquiry URL params ─────────────────────
// If any required field is missing, returns null and caller shows error banner.
function buildInquiryUrl(config: ConfigState): string | null {
  if (!config.selectedMood || !config.selectedStyle || !config.selectedScale) {
    return null;
  }
  const params = new URLSearchParams();
  params.set('mood',   config.selectedMood);
  params.set('style',  config.selectedStyle);
  params.set('scale',  config.selectedScale);
  if (config.selectedColors.length > 0) {
    params.set('colors', config.selectedColors.join(','));
  }
  if (config.selectedFamily) {
    params.set('family', config.selectedFamily);
  }
  return `/inquire?${params.toString()}`;
}

// ── Configurator component ────────────────────────────────────────────────────
function MoodConfigurator() {
  const [config, setConfig] = useState<ConfigState>({
    step: 1,
    selectedMood: null,
    selectedFamily: null,
    selectedColors: [],
    expandedFamilies: new Set(),
    selectedStyle: null,
    selectedScale: null,
  });
  const [submitError, setSubmitError] = useState<string | null>(null);

  const goToStep = useCallback((step: number) => {
    setConfig((c) => ({ ...c, step }));
    setSubmitError(null);
  }, []);

  const selectMood = useCallback((moodId: string) => {
    const mood = MOODS.find((m) => m.id === moodId);
    setConfig((c) => ({
      ...c,
      selectedMood: moodId,
      selectedFamily: mood?.suggestedFamily ?? null,
      selectedColors: [],
      step: 2,
    }));
    setSubmitError(null);
  }, []);

  const selectFamily = useCallback((familyKey: string) => {
    setConfig((c) => ({ ...c, selectedFamily: familyKey, selectedColors: [] }));
  }, []);

  const toggleColor = useCallback((colorId: string) => {
    setConfig((c) => ({
      ...c,
      selectedColors: c.selectedColors.includes(colorId)
        ? c.selectedColors.filter((id) => id !== colorId)
        : [...c.selectedColors, colorId].slice(0, 5), // max 5 colors
    }));
  }, []);

  const toggleFamilyExpand = useCallback((familyKey: string) => {
    setConfig((c) => {
      const next = new Set(c.expandedFamilies);
      if (next.has(familyKey)) next.delete(familyKey);
      else next.add(familyKey);
      return { ...c, expandedFamilies: next };
    });
  }, []);

  const selectStyle = useCallback((style: string) => {
    setConfig((c) => ({ ...c, selectedStyle: style, step: 4 }));
    setSubmitError(null);
  }, []);

  const selectScale = useCallback((scaleId: string) => {
    setConfig((c) => ({ ...c, selectedScale: scaleId }));
    setSubmitError(null);
  }, []);

  const handleSubmit = useCallback(() => {
    const url = buildInquiryUrl(config);
    if (!url) {
      // Loud failure: user-visible error — never a silent failure
      setSubmitError(
        'Please complete all steps before continuing — we need your mood, style, and scale to pre-fill the inquiry form.'
      );
      return;
    }
    setSubmitError(null);
    window.location.href = url;
  }, [config]);

  const STEP_LABELS = ['Feeling', 'Colors', 'Style', 'Scale'];

  const activeFamilyKey = config.selectedFamily ?? 'neutrals';
  const activeFamily = COLOR_FAMILIES[activeFamilyKey];
  const isFamilyExpanded = config.expandedFamilies.has(activeFamilyKey);
  const visibleColors = isFamilyExpanded
    ? activeFamily?.colors ?? []
    : (activeFamily?.colors ?? []).slice(0, CURATED_COUNT);

  const selectedColorNames = config.selectedColors
    .map((id) => {
      for (const fam of Object.values(COLOR_FAMILIES)) {
        const found = fam.colors.find((c) => c.id === id);
        if (found) return found.name;
      }
      return id;
    })
    .join(', ');

  return (
    <div
      className="configurator"
      aria-label="Design configurator"
      role="region"
    >
      {/* Step indicator bar */}
      <div className="configurator__step-bar" role="tablist" aria-label="Configurator steps">
        {STEP_LABELS.map((label, i) => {
          const stepNum = i + 1;
          const isActive = config.step === stepNum;
          const isDone   = config.step > stepNum;
          return (
            <button
              key={label}
              role="tab"
              aria-selected={isActive}
              aria-current={isActive ? 'step' : undefined}
              className={`configurator__step-btn${isActive ? ' configurator__step-btn--active' : isDone ? ' configurator__step-btn--done' : ''}`}
              onClick={() => goToStep(stepNum)}
            >
              {stepNum}. {label}
              {isDone && ' ✓'}
            </button>
          );
        })}
      </div>

      {/* ── Step 1: Mood ─────────────────────────────────────────────────────── */}
      {config.step === 1 && (
        <div role="tabpanel" aria-label="Step 1: Choose a feeling">
          <h3 className="configurator__label">Start with a feeling.</h3>
          <p className="configurator__helper">
            Most balloon decor begins as a mood, not a color list. Choose what resonates —
            we'll narrow to specific shades together.
          </p>

          <div className="mood-grid">
            {MOODS.map((mood) => {
              const isSelected = config.selectedMood === mood.id;
              return (
                <button
                  key={mood.id}
                  className={`mood-pill${isSelected ? ' mood-pill--selected' : ''}`}
                  onClick={() => selectMood(mood.id)}
                  aria-pressed={isSelected}
                  style={{
                    // Accent palette as pill accent (border) — not full background
                    borderColor: isSelected ? 'var(--color-near-black)' : mood.accentColor,
                    borderWidth: isSelected ? '2px' : '2px',
                  }}
                >
                  <span className="mood-pill__name">{mood.label}</span>
                  <span className="mood-pill__count">{mood.description}</span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Step 2: Colors ──────────────────────────────────────────────────── */}
      {config.step === 2 && (
        <div role="tabpanel" aria-label="Step 2: Choose colors">
          <h3 className="configurator__label">
            Family colors.
            {config.selectedColors.length > 0 && (
              <span
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 400,
                  color: 'var(--color-soft-gray)',
                  marginLeft: 'var(--space-3)',
                }}
              >
                — {selectedColorNames}
              </span>
            )}
          </h3>
          <p className="configurator__helper">
            Select up to 5. These are the starting point — Jeff refines the palette
            with you from there.
          </p>

          {/* Family tabs */}
          <div
            role="group"
            aria-label="Color families"
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 'var(--space-2)',
              marginBottom: 'var(--space-5)',
            }}
          >
            {Object.entries(COLOR_FAMILIES).map(([key, family]) => (
              <button
                key={key}
                className={`chip${activeFamilyKey === key ? ' chip--selected' : ''}`}
                onClick={() => selectFamily(key)}
                aria-pressed={activeFamilyKey === key}
              >
                {family.label}
              </button>
            ))}
          </div>

          {/* Swatch grid for active family */}
          {activeFamily && (
            <>
              <div className="swatch-grid" role="group" aria-label={`${activeFamily.label} swatches`}>
                {visibleColors.map((color) => {
                  const isSelected = config.selectedColors.includes(color.id);
                  return (
                    <div key={color.id} className="swatch-item">
                      <button
                        className={`swatch-btn${isSelected ? ' swatch-btn--selected' : ''}`}
                        style={{ backgroundColor: color.hex }}
                        onClick={() => toggleColor(color.id)}
                        aria-label={color.name}
                        aria-checked={isSelected}
                        role="checkbox"
                        title={color.name}
                      />
                      <span className="swatch-name">{color.name}</span>
                    </div>
                  );
                })}
              </div>

              {activeFamily.colors.length > CURATED_COUNT && (
                <button
                  onClick={() => toggleFamilyExpand(activeFamilyKey)}
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: 'var(--text-sm)',
                    fontWeight: 600,
                    color: 'var(--color-soft-gray)',
                    textDecoration: 'underline',
                    textUnderlineOffset: '3px',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    minHeight: '44px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    marginTop: 'var(--space-2)',
                  }}
                >
                  {isFamilyExpanded
                    ? 'Show fewer'
                    : `See all ${activeFamily.colors.length} ${activeFamily.label.toLowerCase()}`}
                </button>
              )}
            </>
          )}

          <div style={{ marginTop: 'var(--space-6)', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={() => goToStep(3)}
              disabled={config.selectedColors.length === 0}
            >
              Next: style
            </button>
          </div>
        </div>
      )}

      {/* ── Step 3: Style ───────────────────────────────────────────────────── */}
      {config.step === 3 && (
        <div role="tabpanel" aria-label="Step 3: Choose a style">
          <h3 className="configurator__label">What style?</h3>
          <p className="configurator__helper">
            The same palette reads completely differently in an organic drape versus
            a structured arch. The form is the design.
          </p>

          <div className="chip-group">
            {STYLE_OPTIONS.map((style) => (
              <button
                key={style}
                className={`chip${config.selectedStyle === style ? ' chip--selected' : ''}`}
                onClick={() => selectStyle(style)}
                aria-pressed={config.selectedStyle === style}
              >
                {style}
              </button>
            ))}
          </div>

          <div style={{ marginTop: 'var(--space-6)', display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={() => goToStep(4)}
              disabled={!config.selectedStyle}
            >
              Next: scale
            </button>
          </div>
        </div>
      )}

      {/* ── Step 4: Scale + Submit ──────────────────────────────────────────── */}
      {config.step === 4 && (
        <div role="tabpanel" aria-label="Step 4: Choose a scale">
          <h3 className="configurator__label">What scale?</h3>
          <p className="configurator__helper">
            Scale determines materials, structure, and logistics. Jeff will confirm
            feasibility for your venue when he follows up.
          </p>

          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: 'var(--space-3)',
            }}
          >
            {SCALE_OPTIONS.map((opt) => (
              <button
                key={opt.id}
                className={`scale-option${config.selectedScale === opt.id ? ' scale-option--selected' : ''}`}
                onClick={() => selectScale(opt.id)}
                aria-pressed={config.selectedScale === opt.id}
              >
                <span className="scale-option__label">{opt.label}</span>
                <span className="scale-option__desc">{opt.description}</span>
              </button>
            ))}
          </div>

          {/* Summary */}
          {config.selectedScale && (
            <div
              style={{
                marginTop: 'var(--space-8)',
                borderTop: '1px solid var(--color-border)',
                paddingTop: 'var(--space-6)',
              }}
            >
              <p
                className="label"
                style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}
              >
                Your configuration
              </p>
              <p
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.125rem',
                  color: 'var(--color-near-black)',
                  marginBottom: 'var(--space-6)',
                  lineHeight: 1.4,
                }}
              >
                {MOODS.find((m) => m.id === config.selectedMood)?.label ?? '—'}
                {' · '}
                {selectedColorNames || (config.selectedFamily ? COLOR_FAMILIES[config.selectedFamily]?.label : '—')}
                {' · '}
                {config.selectedStyle}
                {' · '}
                {SCALE_OPTIONS.find((s) => s.id === config.selectedScale)?.label}
              </p>

              {/* Loud failure error banner — never a silent failure */}
              {submitError && (
                <div className="error-banner" role="alert" aria-live="assertive">
                  <span className="error-banner__icon" aria-hidden="true">!</span>
                  <p className="error-banner__message">{submitError}</p>
                </div>
              )}

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
                <button className="btn btn-primary" onClick={handleSubmit}>
                  Continue to inquiry
                </button>
                <a
                  href="tel:+18012850860"
                  style={{
                    fontFamily: 'var(--font-body)',
                    fontSize: 'var(--text-sm)',
                    color: 'var(--color-soft-gray)',
                    minHeight: '44px',
                    display: 'inline-flex',
                    alignItems: 'center',
                    textDecoration: 'none',
                  }}
                >
                  Or call: (801) 285-0860
                </a>
              </div>

              <p
                style={{
                  marginTop: 'var(--space-3)',
                  fontSize: 'var(--text-xs)',
                  color: 'var(--color-soft-gray)',
                  maxWidth: '44ch',
                }}
              >
                No commitment. Jeff follows up with availability and a custom quote.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Look book grid ────────────────────────────────────────────────────────────
interface LookItem {
  slug: string;
  category: string;
  title: string;
  alt: string;
  occasion: string;
  accentBg: string;
}

const LOOK_ITEMS: LookItem[] = [
  {
    slug: 'ceremony-arch-ivory-sage',
    category: 'Arches & Garlands',
    title: 'Ivory and Sage Ceremony Arch',
    alt: 'A sweeping organic arch in ivory and sage over a wedding ceremony space in a Salt Lake City venue',
    occasion: 'Wedding',
    accentBg: 'var(--color-blush-tint)',
  },
  {
    slug: 'corporate-wall-navy-gold',
    category: 'Walls & Backdrops',
    title: 'Navy & Gold Corporate Backdrop',
    alt: 'A full-height balloon wall in navy and gold behind a corporate awards stage',
    occasion: 'Corporate',
    accentBg: 'var(--color-blue-tint)',
  },
  {
    slug: 'organic-cloud-blush',
    category: 'Organic Garlands',
    title: 'Blush Cloud Arrangement',
    alt: 'A suspended organic balloon cloud in varying shades of blush above a banquet table',
    occasion: 'Birthday',
    accentBg: 'var(--color-blush-tint)',
  },
  {
    slug: 'garland-autumn-milestone',
    category: 'Arches & Garlands',
    title: 'Autumn Milestone Garland',
    alt: 'A long mantle garland in burnt orange, rust, and gold for a 50th birthday celebration',
    occasion: 'Birthday',
    accentBg: 'var(--color-blush-tint)',
  },
  {
    slug: 'backdrop-terracotta-wedding',
    category: 'Walls & Backdrops',
    title: 'Terracotta Wedding Photo Wall',
    alt: 'A textured terracotta and ivory balloon backdrop at a rustic Utah barn wedding',
    occasion: 'Wedding',
    accentBg: 'var(--color-blush-tint)',
  },
  {
    slug: 'installation-corporate-teal',
    category: 'Organic Garlands',
    title: 'Teal Grand Opening Sculpture',
    alt: 'A multi-piece teal and silver organic sculpture for a Provo business grand opening',
    occasion: 'Corporate',
    accentBg: 'var(--color-blue-tint)',
  },
];

const ALL_OCCASIONS = ['All', 'Wedding', 'Corporate', 'Birthday'];
const ALL_CATEGORIES = ['All categories', 'Arches & Garlands', 'Walls & Backdrops', 'Organic Garlands'];

function LookBookGrid() {
  const [occasionFilter, setOccasionFilter] = useState('All');
  const [categoryFilter, setCategoryFilter] = useState('All categories');

  const filtered = LOOK_ITEMS.filter((item) => {
    const occMatch = occasionFilter === 'All' || item.occasion === occasionFilter;
    const catMatch = categoryFilter === 'All categories' || item.category === categoryFilter;
    return occMatch && catMatch;
  });

  return (
    <div>
      {/* Filters */}
      <div
        style={{
          display: 'flex',
          gap: 'var(--space-4)',
          flexWrap: 'wrap',
          marginBottom: 'var(--space-8)',
          alignItems: 'center',
          paddingBottom: 'var(--space-6)',
          borderBottom: '1px solid var(--color-border)',
        }}
      >
        {/* Occasion filter chips */}
        <fieldset style={{ border: 'none', display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', padding: 0 }}>
          <legend className="visually-hidden">Filter by occasion</legend>
          {ALL_OCCASIONS.map((occ) => (
            <button
              key={occ}
              className={`chip${occasionFilter === occ ? ' chip--selected' : ''}`}
              aria-pressed={occasionFilter === occ}
              onClick={() => setOccasionFilter(occ)}
            >
              {occ}
            </button>
          ))}
        </fieldset>

        {/* Divider */}
        <div style={{ width: '1px', height: 32, backgroundColor: 'var(--color-border)' }} aria-hidden="true" />

        {/* Category select */}
        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span className="visually-hidden">Filter by category</span>
          <select
            className="form-select"
            style={{ width: 'auto', minWidth: '180px' }}
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            {ALL_CATEGORIES.map((cat) => (
              <option key={cat}>{cat}</option>
            ))}
          </select>
        </label>
      </div>

      {/* Result count */}
      <p
        className="label"
        style={{ color: 'var(--color-soft-gray)', marginBottom: 'var(--space-6)' }}
      >
        {filtered.length} {filtered.length === 1 ? 'piece' : 'pieces'}
        {occasionFilter !== 'All' && ` · ${occasionFilter}`}
        {categoryFilter !== 'All categories' && ` · ${categoryFilter}`}
      </p>

      {/* Grid — 3-up on desktop per STYLE-GUIDE symmetry rule (6 items = 3+3) */}
      {filtered.length === 0 ? (
        <p style={{ color: 'var(--color-soft-gray)', fontStyle: 'italic' }}>
          No work matches that filter. Try adjusting the occasion or category.
        </p>
      ) : (
        <div className="lb-grid">
          {filtered.map((item) => (
            <article key={item.slug}>
              <a
                href={`/synthesis/lookbook#${item.slug}`}
                style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}
                aria-label={`View: ${item.title}`}
              >
                {/* Photo — no text on images per D7's discipline */}
                <div
                  className="lb-card__image"
                  style={{ backgroundColor: item.accentBg }}
                >
                  <span className="visually-hidden">{item.alt}</span>
                </div>

                {/* Text below, never on top */}
                <div style={{ paddingTop: 'var(--space-3)' }}>
                  <p className="lb-card__category">{item.category}</p>
                  <h3 className="lb-card__title">{item.title}</h3>
                </div>
              </a>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Page export ───────────────────────────────────────────────────────────────
export default function LookbookPage() {
  return (
    <SynthesisLayout activePath="/synthesis/lookbook">
      {/* Page header — near-white ground, no dark block per LT STYLE-GUIDE */}
      <section
        className="section"
        aria-labelledby="lookbook-heading"
        style={{ backgroundColor: 'var(--color-near-white)' }}
      >
        <div className="container">
          <p className="label" style={{ marginBottom: 'var(--space-4)', color: 'var(--color-soft-gray)' }}>
            What we've made
          </p>
          <h1 id="lookbook-heading" style={{ marginBottom: 'var(--space-4)', maxWidth: '18ch' }}>
            The work speaks.
          </h1>
          <p style={{ maxWidth: '52ch' }}>
            Custom balloon decor for weddings, corporate events, and milestone celebrations
            along Utah's Wasatch Front. Every piece is designed for the specific event and venue.
          </p>
        </div>
      </section>

      {/* Thin accent band */}
      <div
        className="accent-band"
        style={{ backgroundColor: 'var(--color-blush)' }}
        aria-hidden="true"
      />

      {/* Portfolio grid */}
      <section className="section" aria-labelledby="look-grid-heading">
        <div className="container">
          <h2 id="look-grid-heading" className="visually-hidden">Portfolio</h2>
          <LookBookGrid />
        </div>
      </section>

      {/* Thin accent band */}
      <div
        className="accent-band"
        style={{ backgroundColor: 'var(--color-soft-blue)' }}
        aria-hidden="true"
      />

      {/* Mood-first configurator — D7's 4-step UX, LT visual language */}
      <section
        className="section"
        aria-labelledby="configurator-heading"
        style={{ backgroundColor: 'var(--color-white)' }}
      >
        <div className="container">
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr',
              gap: 'var(--space-12)',
              alignItems: 'start',
            }}
          >
            {/* Left: heading + explanation */}
            <div style={{ maxWidth: '480px' }}>
              <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
                Start designing
              </p>
              <h2 id="configurator-heading" style={{ marginBottom: 'var(--space-4)' }}>
                Build your palette.
              </h2>
              <p style={{ marginBottom: 'var(--space-4)' }}>
                Four steps. Walk through what you're imagining — mood, colors, style, scale.
                We'll receive your configuration and follow up with a custom quote.
              </p>
              <p style={{ fontSize: 'var(--text-sm)', color: 'var(--color-soft-gray)' }}>
                Or skip ahead and call directly: <a href="tel:+18012850860" style={{ color: 'var(--color-near-black)', fontWeight: 600 }}>(801) 285-0860</a>
              </p>
            </div>

            {/* Right: configurator — D7's step-based UX */}
            <MoodConfigurator />
          </div>
        </div>
      </section>

      {/* Thin accent band */}
      <div
        className="accent-band"
        style={{ backgroundColor: 'var(--color-aqua)' }}
        aria-hidden="true"
      />

      {/* "Something else in mind?" — D7's bottom inquiry redirect */}
      <section
        className="section"
        aria-label="Open inquiry invitation"
        style={{ backgroundColor: 'var(--color-near-white)' }}
      >
        <div className="container">
          <div style={{ maxWidth: '640px', marginInline: 'auto', textAlign: 'center' }}>
            <h2 style={{ marginBottom: 'var(--space-4)' }}>
              Something else in mind?
            </h2>
            <p style={{ marginBottom: 'var(--space-6)' }}>
              The look book is a sample of the range — not a menu. If you're imagining
              something you don't see here, that's exactly the conversation Jeff is built for.
            </p>
            <a href="/inquire" className="btn btn-primary">
              Start a conversation
            </a>
          </div>
        </div>
      </section>
    </SynthesisLayout>
  );
}
