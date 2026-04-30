'use client';

/**
 * balloon-twisting/page.tsx — Synthesis Balloon Twisting & Face Painting
 *
 * Structural source: D3 (The Studio Archive)
 *   - Dense editorial approach: no excessive white space, every section earns its space
 *   - Dual-service detail (twisting + face painting) at equal weight
 *   - Spec tables using <dl> (definition list) — "Best at / Duration / Team size / Good for"
 *     DL reads as a professional data sheet, not a brochure bullet list
 *   - Occasion types (birthday / corporate / community / festival)
 *   - Accordion FAQ — 5 practical questions
 *   - Pre-select inquiry builder: selections serialize to /inquire?event_type=X&guests=Y&service=Z
 *     Query params pre-populate the inquiry form — same D3 pattern as the look book configurator
 *
 * Visual language: LT STYLE-GUIDE.md only
 *   - DM Serif Display + Raleway (not Cormorant, not DM Mono)
 *   - Near-white/white ground, teal for CTA only
 *   - Section alternation: white → near-white → white (not stacked accent colors)
 *   - Accent as thin bands between sections
 *
 * Loud failure: URL builder shows error if required fields absent on click.
 */

import { useState, useCallback } from 'react';
import SynthesisLayout from '../layout';

// ── Photo placeholder ─────────────────────────────────────────────────────────
function PhotoBlock({
  alt,
  aspectRatio = '3/4',
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

// ── Spec list (D3's <dl> approach) ───────────────────────────────────────────
interface Spec {
  term: string;
  detail: string;
}

function SpecList({ specs }: { specs: Spec[] }) {
  return (
    <dl className="spec-list">
      {specs.map(({ term, detail }) => (
        <div key={term} className="spec-row">
          <dt className="spec-term">{term}</dt>
          <dd className="spec-detail">{detail}</dd>
        </div>
      ))}
    </dl>
  );
}

// ── 1. Page header ────────────────────────────────────────────────────────────
function PageHeader() {
  return (
    <section
      aria-label="Services introduction"
      style={{
        backgroundColor: 'var(--color-near-white)',
        paddingTop: 'var(--space-12)',
        paddingBottom: 'var(--space-8)',
        borderBottom: '1px solid var(--color-border)',
      }}
    >
      <div className="container">
        <p className="label" style={{ marginBottom: 'var(--space-4)', color: 'var(--color-soft-gray)' }}>
          Live services
        </p>

        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(1.75rem, 5vw, 3.5rem)',
            color: 'var(--color-near-black)',
            maxWidth: '18ch',
            lineHeight: 1.05,
            marginBottom: 'var(--space-6)',
          }}
        >
          Something for the middle of the party.
        </h1>

        <p style={{ maxWidth: '52ch' }}>
          Roaming balloon twisting and face painting for events large and small.
          Jeff and his team work the room — keeping energy up, turning a crowd into a memory.
        </p>
      </div>
    </section>
  );
}

// ── 2. Service split ──────────────────────────────────────────────────────────
// Equal weight, spec-table format — D3's editorial density.
const TWISTING_SPECS: Spec[] = [
  { term: 'Best at',   detail: '50+ guests'                                    },
  { term: 'Duration',  detail: 'Flexible — typically 1–3 hours'                },
  { term: 'Team size', detail: '1–4 artists depending on crowd'                 },
  { term: 'Good for',  detail: 'Birthdays, corporate mixers, festivals, schools' },
];

const FACE_PAINT_SPECS: Spec[] = [
  { term: 'Best at',   detail: '30+ guests'                                     },
  { term: 'Duration',  detail: 'Typically 1–2 hours'                            },
  { term: 'Artists',   detail: '1–2 per event'                                  },
  { term: 'Good for',  detail: 'Birthday parties, school events, fairs, corporate' },
];

function ServiceSplit() {
  return (
    <section
      className="section"
      aria-labelledby="services-split-heading"
      style={{ backgroundColor: 'var(--color-white)' }}
    >
      <div className="container">
        <h2 id="services-split-heading" className="visually-hidden">Our live services</h2>

        <div className="grid-2" style={{ alignItems: 'start' }}>
          {/* Balloon Twisting */}
          <article aria-labelledby="twisting-heading">
            <PhotoBlock
              alt="Jeff Kimber twisting a balloon sword for a child at a birthday party"
              aspectRatio="3/4"
              accent="var(--color-blush-tint)"
            />

            <div style={{ paddingTop: 'var(--space-6)' }}>
              <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
                Balloon Twisting
              </p>

              <h3
                id="twisting-heading"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 2rem)',
                  color: 'var(--color-near-black)',
                  lineHeight: 1.1,
                  marginBottom: 'var(--space-4)',
                }}
              >
                Roaming entertainment at any scale.
              </h3>

              <p style={{ maxWidth: '44ch', marginBottom: 'var(--space-6)' }}>
                Jeff and his team move through the event making balloon animals, hats,
                swords, flowers — whatever the crowd wants. Adults and kids both.
                Works best at gatherings of 50 or more.
              </p>

              <SpecList specs={TWISTING_SPECS} />
            </div>
          </article>

          {/* Face Painting */}
          <article aria-labelledby="face-painting-heading">
            <PhotoBlock
              alt="Face painter at a corporate summer event — Locally Twisted"
              aspectRatio="3/4"
              accent="var(--color-blush-tint)"
            />

            <div style={{ paddingTop: 'var(--space-6)' }}>
              <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
                Face Painting
              </p>

              <h3
                id="face-painting-heading"
                style={{
                  fontSize: 'clamp(1.25rem, 3vw, 2rem)',
                  color: 'var(--color-near-black)',
                  lineHeight: 1.1,
                  marginBottom: 'var(--space-4)',
                }}
              >
                A line they'll wait in happily.
              </h3>

              <p style={{ maxWidth: '44ch', marginBottom: 'var(--space-6)' }}>
                Professional face painting that keeps energy up for the full event.
                Designs range from simple patterns for quick throughput to detailed
                portraits for special guests.
              </p>

              <SpecList specs={FACE_PAINT_SPECS} />
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}

// ── Thin accent band ──────────────────────────────────────────────────────────
function AccentBand({ color }: { color: string }) {
  return (
    <div
      className="accent-band"
      style={{ backgroundColor: color }}
      aria-hidden="true"
    />
  );
}

// ── 3. How it works ───────────────────────────────────────────────────────────
// D3: plain language, not "3 easy steps!" banner.
const PROCESS_STEPS = [
  {
    num: '01',
    title: 'Tell us about your event',
    body: 'Date, location, guest count, and what you're imagining. Use the form below or call. We respond same day on weekdays.',
  },
  {
    num: '02',
    title: 'We confirm availability and scope',
    body: 'We'll let you know if the date works and recommend the right team size for your crowd. A quote follows.',
  },
  {
    num: '03',
    title: 'Deposit holds your date',
    body: 'A deposit reserves the team. The balance is due closer to the event. We send a confirmation with all logistics.',
  },
  {
    num: '04',
    title: 'We show up and work the room',
    body: 'We arrive early, set up, and run for the agreed duration. You don't manage us — that's not your job at the party.',
  },
];

function HowItWorks() {
  return (
    <section
      className="section"
      aria-labelledby="how-it-works-heading"
      style={{ backgroundColor: 'var(--color-near-white)' }}
    >
      <div className="container">
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
            The process
          </p>
          <h2 id="how-it-works-heading">Booking is straightforward.</h2>
        </div>

        <ol
          role="list"
          style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 0 }}
        >
          {PROCESS_STEPS.map((step) => (
            <li
              key={step.num}
              style={{
                display: 'grid',
                gridTemplateColumns: 'auto 1fr',
                gap: 'var(--space-6)',
                alignItems: 'start',
                paddingBlock: 'var(--space-6)',
                borderBottom: '1px solid var(--color-border)',
              }}
            >
              {/* Number in display register */}
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: 'clamp(1.5rem, 4vw, 2.5rem)',
                  color: 'var(--color-near-black)',
                  opacity: 0.25,
                  lineHeight: 1,
                  minWidth: '2.5rem',
                  flexShrink: 0,
                }}
                aria-hidden="true"
              >
                {step.num}
              </span>

              <div>
                <h3
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: 'var(--text-xl)',
                    color: 'var(--color-near-black)',
                    marginBottom: 'var(--space-2)',
                    lineHeight: 1.2,
                  }}
                >
                  {step.title}
                </h3>
                <p style={{ maxWidth: '54ch' }}>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

// ── 4. Event types ────────────────────────────────────────────────────────────
// D3's occasion list — editorial row format, not card grid.
const EVENT_TYPES = [
  { label: 'Birthday Parties',    note: 'The most requested. Works for ages 2–102.' },
  { label: 'Corporate Events',    note: 'Mixers, galas, team celebrations.'         },
  { label: 'School & Community',  note: 'Fairs, fundraisers, end-of-year events.'   },
  { label: 'Festivals',           note: 'High-volume, outdoor — we're built for it.' },
  { label: 'Holiday Parties',     note: 'Office parties, neighborhood events, HOA.' },
  { label: 'Sweet 16 & Quinces',  note: 'Entertainment between sit-down moments.'   },
];

function EventTypes() {
  return (
    <section
      className="section"
      aria-labelledby="event-types-heading"
      style={{ backgroundColor: 'var(--color-white)' }}
    >
      <div className="container">
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
            Works for
          </p>
          <h2 id="event-types-heading">Any Event. Any Size.</h2>
        </div>

        <ul role="list" style={{ listStyle: 'none' }}>
          {EVENT_TYPES.map((type) => (
            <li
              key={type.label}
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 'var(--space-4)',
                justifyContent: 'space-between',
                alignItems: 'baseline',
                paddingBlock: 'var(--space-4)',
                borderBottom: '1px solid var(--color-border)',
              }}
            >
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: 'clamp(1rem, 2.5vw, 1.375rem)',
                  color: 'var(--color-near-black)',
                }}
              >
                {type.label}
              </span>
              <span
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: 'var(--text-sm)',
                  color: 'var(--color-soft-gray)',
                  lineHeight: 1.5,
                  maxWidth: '38ch',
                }}
              >
                {type.note}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

// ── 5. FAQ accordion ──────────────────────────────────────────────────────────
const FAQ_ITEMS = [
  {
    question: 'How far in advance should we book?',
    answer:
      'For weekend events, 2–4 weeks ahead is comfortable. Saturdays in summer fill faster — 6 weeks or more is safer if you have a specific date. For weekday events, a week is usually fine. Call if you're last-minute — we'll tell you honestly what's available.',
  },
  {
    question: 'How many artists do we need for our crowd?',
    answer:
      'One balloon artist handles roughly 30–40 guests per hour depending on design complexity. One face painter handles 8–12 per hour. For a 2-hour event with 100 guests wanting balloon animals, two artists is comfortable. We'll recommend the right team size in your quote.',
  },
  {
    question: 'Do you travel outside Salt Lake City?',
    answer:
      'We serve the full Wasatch Front — Salt Lake, Davis, Utah, and Weber counties. Travel outside that range is possible with a travel fee. Ask us about your specific location.',
  },
  {
    question: 'What if the event runs long?',
    answer:
      'We book in one-hour increments. If you think you'll need more time than the original booking, let us know at least 48 hours ahead. Adding time on the day is sometimes possible, but not guaranteed.',
  },
  {
    question: 'Are your face paints safe for kids?',
    answer:
      'Yes. We use professional cosmetic-grade face paints that are FDA-compliant, water-based, and tested for skin sensitivity. We do not use acrylic, latex, or anything not designed for skin. We ask about allergies at the event.',
  },
];

function FAQAccordion() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggle = useCallback((i: number) => {
    setOpenIndex((prev) => (prev === i ? null : i));
  }, []);

  return (
    <section
      className="section"
      aria-labelledby="faq-heading"
      style={{ backgroundColor: 'var(--color-near-white)' }}
    >
      <div className="container">
        <div style={{ marginBottom: 'var(--space-8)' }}>
          <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
            Common questions
          </p>
          <h2 id="faq-heading">Practical answers.</h2>
        </div>

        <dl>
          {FAQ_ITEMS.map((item, i) => {
            const isOpen = openIndex === i;
            return (
              <div key={i} className="accordion-item">
                <dt>
                  <button
                    className="accordion-btn"
                    aria-expanded={isOpen}
                    aria-controls={`faq-answer-${i}`}
                    id={`faq-question-${i}`}
                    onClick={() => toggle(i)}
                  >
                    <span>{item.question}</span>
                    <span
                      className={`accordion-icon${isOpen ? ' accordion-icon--open' : ''}`}
                      aria-hidden="true"
                    >
                      +
                    </span>
                  </button>
                </dt>

                <dd
                  id={`faq-answer-${i}`}
                  aria-labelledby={`faq-question-${i}`}
                  hidden={!isOpen}
                  className="accordion-answer"
                >
                  {item.answer}
                </dd>
              </div>
            );
          })}
        </dl>
      </div>
    </section>
  );
}

// ── 6. Pre-select inquiry builder ─────────────────────────────────────────────
// D3's pattern: quick-select chips → serialize to inquiry URL
// /inquire?service=X&event_type=Y&guests=Z
// Loud failure: if submit clicked without all required fields, show error banner.
function BookingSection() {
  const [eventType, setEventType] = useState('');
  const [guestCount, setGuestCount] = useState('');
  const [service, setService] = useState('');
  const [submitError, setSubmitError] = useState<string | null>(null);

  const buildInquiryUrl = useCallback(() => {
    if (!service || !eventType) return null;
    const params = new URLSearchParams();
    params.set('service', service);
    params.set('event_type', eventType);
    if (guestCount) params.set('guests', guestCount);
    return `/inquire?${params.toString()}`;
  }, [service, eventType, guestCount]);

  const handleContinue = useCallback(() => {
    const url = buildInquiryUrl();
    if (!url) {
      // Loud failure — never silent
      setSubmitError(
        'Please select a service and event type before continuing.'
      );
      return;
    }
    setSubmitError(null);
    window.location.href = url;
  }, [buildInquiryUrl]);

  const chipStyle = (isSelected: boolean) => ({
    display: 'inline-flex' as const,
    alignItems: 'center' as const,
    fontFamily: 'var(--font-body)',
    fontSize: 'var(--text-sm)',
    fontWeight: isSelected ? 600 : 400,
    color: isSelected ? 'var(--color-near-black)' : 'var(--color-soft-gray)',
    backgroundColor: isSelected ? 'var(--color-blush-tint)' : 'transparent',
    border: `${isSelected ? '2px' : '1px'} solid ${isSelected ? 'var(--color-near-black)' : 'var(--color-border)'}`,
    borderRadius: '100px',
    padding: 'var(--space-2) var(--space-4)',
    cursor: 'pointer' as const,
    minHeight: '44px',
    transition: 'all var(--duration-fast) var(--ease-out)',
  });

  return (
    <section
      className="section"
      aria-labelledby="booking-heading"
      style={{
        backgroundColor: 'var(--color-white)',
        borderTop: '1px solid var(--color-border)',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr',
            gap: 'var(--space-10)',
          }}
        >
          {/* Heading */}
          <div>
            <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
              Book a service
            </p>
            <h2 id="booking-heading" style={{ marginBottom: 'var(--space-4)', maxWidth: '18ch' }}>
              Tell us about yours.
            </h2>
            <p style={{ maxWidth: '44ch' }}>
              A rough picture is enough to start. Tell us what you're planning
              and we'll come back with availability and a quote.
            </p>
          </div>

          {/* Quick-select chips */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
            {/* Service */}
            <fieldset style={{ border: 'none', padding: 0 }}>
              <legend
                className="label"
                style={{ marginBottom: 'var(--space-4)', color: 'var(--color-soft-gray)', display: 'block' }}
              >
                I'm interested in
              </legend>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {[
                  { id: 'twisting',   label: 'Balloon Twisting' },
                  { id: 'face-paint', label: 'Face Painting'    },
                  { id: 'both',       label: 'Both'             },
                ].map((opt) => (
                  <label key={opt.id} style={{ cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="service"
                      value={opt.id}
                      className="visually-hidden"
                      checked={service === opt.id}
                      onChange={() => { setService(opt.id); setSubmitError(null); }}
                    />
                    <span style={chipStyle(service === opt.id)}>{opt.label}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            {/* Event type */}
            <fieldset style={{ border: 'none', padding: 0 }}>
              <legend
                className="label"
                style={{ marginBottom: 'var(--space-4)', color: 'var(--color-soft-gray)', display: 'block' }}
              >
                Event type
              </legend>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {[
                  'Birthday party',
                  'Corporate event',
                  'School / fair',
                  'Holiday party',
                  'Other',
                ].map((type) => (
                  <label key={type} style={{ cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="event_type"
                      value={type}
                      className="visually-hidden"
                      checked={eventType === type}
                      onChange={() => { setEventType(type); setSubmitError(null); }}
                    />
                    <span style={chipStyle(eventType === type)}>{type}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            {/* Guest count */}
            <fieldset style={{ border: 'none', padding: 0 }}>
              <legend
                className="label"
                style={{ marginBottom: 'var(--space-4)', color: 'var(--color-soft-gray)', display: 'block' }}
              >
                Approximate guest count
              </legend>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                {['Under 50', '50–100', '100–250', '250–500', '500+'].map((count) => (
                  <label key={count} style={{ cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="guest_count"
                      value={count}
                      className="visually-hidden"
                      checked={guestCount === count}
                      onChange={() => setGuestCount(count)}
                    />
                    <span style={chipStyle(guestCount === count)}>{count}</span>
                  </label>
                ))}
              </div>
            </fieldset>

            {/* Loud failure error banner */}
            {submitError && (
              <div className="error-banner" role="alert" aria-live="assertive">
                <span className="error-banner__icon" aria-hidden="true">!</span>
                <p className="error-banner__message">{submitError}</p>
              </div>
            )}

            {/* CTA */}
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: 'var(--space-4)',
                alignItems: 'center',
                paddingTop: 'var(--space-4)',
                borderTop: '1px solid var(--color-border)',
              }}
            >
              <button
                className="btn btn-primary"
                onClick={handleContinue}
                aria-label="Continue to inquiry form"
              >
                Continue to inquiry form
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
          </div>
        </div>
      </div>
    </section>
  );
}

// ── Page export ───────────────────────────────────────────────────────────────
export default function BalloonTwistingPage() {
  return (
    <SynthesisLayout activePath="/synthesis/balloon-twisting">
      <PageHeader />
      <ServiceSplit />

      <AccentBand color="var(--color-blush)" />

      <HowItWorks />

      <AccentBand color="var(--color-lime-pastel)" />

      <EventTypes />

      <AccentBand color="var(--color-aqua)" />

      <FAQAccordion />

      <AccentBand color="var(--color-soft-blue)" />

      <BookingSection />
    </SynthesisLayout>
  );
}
