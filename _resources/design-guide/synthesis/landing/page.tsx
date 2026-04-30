'use client';

/**
 * landing/page.tsx — Synthesis Homepage
 *
 * Structural source: D3's conceptual frame (The Studio Archive)
 *   - Editorial density: every section earns its space
 *   - Photography is the authority; copy is the annotation
 *   - Hero: photo-led, not centered-headline-plus-two-buttons
 *   - Proof strip: authority through specificity (28 years, Wasatch Front, scale)
 *   - Services callout surfaces twisting/face painting inline
 *   - No "About" nav item — brand story lives as a section on landing
 *
 * Visual language: LT STYLE-GUIDE.md only
 *   - DM Serif Display headings + Raleway body
 *   - Near-white ground, teal for CTAs only, soft-blue footer
 *   - Accent palette as thin bands between sections (40–80px)
 *   - No gradient backgrounds, no centered hero defaults
 */

import SynthesisLayout from '../layout';

// ── Photo placeholder ─────────────────────────────────────────────────────────
function PhotoBlock({
  alt,
  aspectRatio = '4/3',
  accent = 'var(--color-blush-tint)',
}: {
  alt: string;
  aspectRatio?: string;
  accent?: string;
}) {
  return (
    <div
      role="img"
      aria-label={alt}
      style={{
        width: '100%',
        aspectRatio,
        backgroundColor: accent,
        display: 'flex',
        alignItems: 'flex-end',
        padding: 'var(--space-3)',
      }}
    >
      <span
        style={{
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-xs)',
          fontWeight: 600,
          letterSpacing: '0.06em',
          textTransform: 'uppercase',
          color: 'var(--color-soft-gray)',
        }}
      >
        {alt}
      </span>
    </div>
  );
}

// ── 1. Hero ───────────────────────────────────────────────────────────────────
// D3's hero principle: photograph bleeds edge-to-edge, copy anchors bottom-left.
// NOT the AI default (centered headline + subhead + 2 buttons).
// The photo makes the first impression. Words confirm it.
function Hero() {
  return (
    <section
      aria-label="Hero"
      style={{
        position: 'relative',
        width: '100%',
        minHeight: '80svh',
        display: 'grid',
        gridTemplateRows: '1fr auto',
        overflow: 'hidden',
      }}
    >
      {/* Full-bleed photo */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'var(--color-blush-tint)',
        }}
        role="img"
        aria-label="A sweeping organic balloon arch in ivory and sage over a wedding venue — Locally Twisted"
      />

      {/* Copy — anchored bottom-left (D3 principle: photo first, words confirm) */}
      <div
        style={{
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'flex-end',
          padding: 'var(--space-8)',
          paddingTop: '40%',
          background: 'linear-gradient(to top, rgba(251,251,251,0.92) 0%, transparent 100%)',
        }}
      >
        <p
          className="label"
          style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}
        >
          Utah's Wasatch Front · Est. 1998
        </p>

        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(1.75rem, 6vw, 3.75rem)',
            color: 'var(--color-near-black)',
            lineHeight: 1.05,
            maxWidth: '15ch',
            marginBottom: 'var(--space-6)',
          }}
        >
          We make celebrations unforgettable.
        </h1>

        {/* One primary CTA — teal, earns its place */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
          <a href="/synthesis/lookbook" className="btn btn-primary">
            See the work
          </a>
          <a href="/synthesis/lookbook" className="btn btn-secondary">
            Tell us what you're imagining
          </a>
        </div>
      </div>
    </section>
  );
}

// ── Thin accent band (between sections) ──────────────────────────────────────
function AccentBand({ color }: { color: string }) {
  return (
    <div
      className="accent-band"
      style={{ backgroundColor: color }}
      aria-hidden="true"
    />
  );
}

// ── 2. Proof strip ────────────────────────────────────────────────────────────
// D3 principle: authority through specificity, not superlatives.
// "28 years" beats "award-winning." A number is a fact.
const PROOF_ITEMS = [
  { stat: '28 years',        note: 'In the work since 1998'                },
  { stat: 'Wasatch Front',   note: 'SL, Davis, Utah & Weber counties'      },
  { stat: 'Large scale',     note: 'Setup in hours, not days'              },
  { stat: 'Every occasion',  note: 'Weddings · corporate · birthdays'      },
];

function ProofStrip() {
  return (
    <section
      aria-label="Authority"
      style={{
        backgroundColor: 'var(--color-white)',
        borderTop: '1px solid var(--color-border)',
        borderBottom: '1px solid var(--color-border)',
        padding: 'var(--space-8) 0',
      }}
    >
      <div className="container">
        <ul
          role="list"
          style={{
            listStyle: 'none',
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: 'var(--space-6)',
          }}
        >
          {PROOF_ITEMS.map((item) => (
            <li key={item.stat} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-1)' }}>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: 'clamp(1.25rem, 3vw, 2rem)',
                  color: 'var(--color-near-black)',
                  lineHeight: 1.1,
                }}
              >
                {item.stat}
              </span>
              <span
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: 'var(--text-xs)',
                  fontWeight: 600,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: 'var(--color-soft-gray)',
                }}
              >
                {item.note}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

// ── 3. Featured work (portfolio preview) ─────────────────────────────────────
// Editorial photo grid — D3's density: no excessive white space, earns every section.
// No text on images per D7's discipline.
const FEATURED_WORKS = [
  {
    slug: 'ceremony-arch-ivory-sage',
    category: 'Arches & Garlands',
    title: 'Ivory and Sage Ceremony Arch',
    alt: 'A sweeping organic arch in ivory and sage over a wedding ceremony space in Salt Lake City',
    accent: 'var(--color-blush-tint)',
    occasion: 'Wedding',
  },
  {
    slug: 'corporate-wall-navy-gold',
    category: 'Walls & Backdrops',
    title: 'Navy & Gold Corporate Backdrop',
    alt: 'A full-height balloon wall in navy and gold behind a corporate awards stage',
    accent: 'var(--color-blue-tint)',
    occasion: 'Corporate',
  },
  {
    slug: 'organic-cloud-blush',
    category: 'Organic Garlands',
    title: 'Blush Cloud Arrangement',
    alt: 'A suspended organic balloon cloud in varying shades of blush above a banquet table',
    accent: 'var(--color-blush-tint)',
    occasion: 'Birthday',
  },
];

function FeaturedWork() {
  return (
    <section className="section" aria-labelledby="featured-heading">
      <div className="container">
        <div
          style={{
            display: 'flex',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            gap: 'var(--space-4)',
            marginBottom: 'var(--space-8)',
            flexWrap: 'wrap',
          }}
        >
          <h2 id="featured-heading">Something for every season.</h2>
          <a
            href="/synthesis/lookbook"
            className="btn btn-secondary"
            style={{ flexShrink: 0 }}
          >
            View all work
          </a>
        </div>

        {/* 3-column grid — balanced per STYLE-GUIDE symmetry rule */}
        <div className="lb-grid" role="list">
          {FEATURED_WORKS.map((work) => (
            <article key={work.slug} role="listitem">
              <a
                href={`/synthesis/lookbook#${work.slug}`}
                style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}
                aria-label={`View: ${work.title}`}
              >
                {/* Photo only — no text on images per D7's discipline */}
                <div className="lb-card__image" style={{ backgroundColor: work.accent }}>
                  <span className="visually-hidden">{work.alt}</span>
                </div>

                {/* Text lives below image, never on top of it */}
                <div style={{ paddingTop: 'var(--space-3)' }}>
                  <p className="lb-card__category">{work.category}</p>
                  <h3 className="lb-card__title">{work.title}</h3>
                </div>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

// ── 4. Services callout ───────────────────────────────────────────────────────
// D3 IA: balloon twisting / face painting has its own door on landing.
// Birthday parents don't navigate the look book to find it.
function ServicesCallout() {
  return (
    <section
      className="section"
      aria-labelledby="services-heading"
      style={{ backgroundColor: 'var(--color-white)' }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 'var(--space-8)',
          }}
        >
          <div>
            <p className="label" style={{ marginBottom: 'var(--space-3)' }}>
              Live services
            </p>
            <h2 id="services-heading" style={{ marginBottom: 'var(--space-4)', maxWidth: '18ch' }}>
              Something for the middle of the party.
            </h2>
            <p style={{ marginBottom: 'var(--space-6)' }}>
              Roaming balloon twisting and face painting. Jeff and his team work the room —
              keeping energy up, turning a crowd into a memory.
            </p>
            <a href="/synthesis/balloon-twisting" className="btn btn-primary">
              Services and booking
            </a>
          </div>

          {/* Two service preview cards */}
          <div className="grid-2">
            <article
              style={{
                backgroundColor: 'var(--color-near-white)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-card)',
                overflow: 'hidden',
              }}
            >
              <PhotoBlock
                alt="Jeff twisting balloon animals at a birthday party"
                aspectRatio="4/3"
                accent="var(--color-blush-tint)"
              />
              <div style={{ padding: 'var(--space-4)' }}>
                <h3 style={{ marginBottom: 'var(--space-2)' }}>Balloon Twisting</h3>
                <p style={{ fontSize: 'var(--text-sm)', marginBottom: 0 }}>
                  Animals, hats, swords, flowers. Best at 50+ guests.
                </p>
              </div>
            </article>

            <article
              style={{
                backgroundColor: 'var(--color-near-white)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-card)',
                overflow: 'hidden',
              }}
            >
              <PhotoBlock
                alt="Face painter at a corporate event"
                aspectRatio="4/3"
                accent="var(--color-blue-tint)"
              />
              <div style={{ padding: 'var(--space-4)' }}>
                <h3 style={{ marginBottom: 'var(--space-2)' }}>Face Painting</h3>
                <p style={{ fontSize: 'var(--text-sm)', marginBottom: 0 }}>
                  A line they'll wait in happily. 30+ guests.
                </p>
              </div>
            </article>
          </div>
        </div>
      </div>
    </section>
  );
}

// ── 5. About Jeff strip ───────────────────────────────────────────────────────
// D3: brand story as landing section, not nav item.
// Voice: Quiet Confidence — present tense, not promises.
function AboutStrip() {
  return (
    <section
      className="section"
      aria-labelledby="about-heading"
      style={{ backgroundColor: 'var(--color-near-white)' }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 'var(--space-8)',
            maxWidth: '720px',
          }}
        >
          <div>
            <p className="label" style={{ marginBottom: 'var(--space-3)' }}>
              The maker
            </p>
            <h2 id="about-heading" style={{ marginBottom: 'var(--space-4)' }}>
              Every detail matters.
            </h2>
            <p style={{ marginBottom: 'var(--space-3)' }}>
              Jeff Kimber has been making balloon decor along Utah's Wasatch Front since 1998.
              Not as a side business. As a craft.
            </p>
            <p style={{ marginBottom: 0 }}>
              Every piece is designed for the event, the venue, and the palette. The work varies.
              The attention doesn't.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

// ── 6. Inquiry CTA ────────────────────────────────────────────────────────────
// D3's configurator pattern: query params pre-fill the inquiry form.
// This landing version is the simple entry point — lookbook has the full configurator.
function InquiryCTA() {
  return (
    <section
      aria-label="Start a conversation"
      style={{ backgroundColor: 'var(--color-white)', padding: 'var(--space-16) 0' }}
    >
      <div className="container">
        <div style={{ maxWidth: '640px' }}>
          <h2 style={{ marginBottom: 'var(--space-4)' }}>
            Tell us what you're imagining.
          </h2>
          <p style={{ marginBottom: 'var(--space-6)' }}>
            A rough idea is enough to start. We'll come back with availability and a quote —
            no commitment required.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
            <a href="/inquire" className="btn btn-primary">
              Start a conversation
            </a>
            <a href="tel:+18012850860" className="btn btn-secondary">
              (801) 285-0860
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

// ── Page export ───────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <SynthesisLayout activePath="/synthesis">
      <Hero />
      <ProofStrip />

      {/* Thin blush band between hero/proof and featured work */}
      <AccentBand color="var(--color-blush)" />

      <FeaturedWork />

      <AccentBand color="var(--color-aqua)" />

      <ServicesCallout />

      <AccentBand color="var(--color-lime-pastel)" />

      <AboutStrip />

      <AccentBand color="var(--color-soft-blue)" />

      <InquiryCTA />
    </SynthesisLayout>
  );
}
