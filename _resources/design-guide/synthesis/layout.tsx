'use client';

/**
 * layout.tsx — Synthesis (Locally Twisted)
 *
 * Shared shell: sticky top nav, mobile drawer, footer.
 *
 * Sources:
 *   Structure: D3's IA (Work / Services / Shop / Contact order, phone in nav)
 *   Visual: LT STYLE-GUIDE.md (DM Serif Display + Raleway, teal CTA only,
 *           near-black headings, soft-blue footer, 8px spacing grid)
 *
 * NOT D5's left-rail. NOT D7's amber accent. NOT D3's near-black surface.
 * This shell is white and near-white — the LT brand.
 */

import { useState, useEffect, useCallback } from 'react';
import './globals.css';

// ── IA tree (from D3's menu reasoning — 95% inquiry / 5% shop split) ───────
interface NavLink {
  label: string;
  href: string;
}

const NAV_LINKS: NavLink[] = [
  { label: 'Work',     href: '/synthesis/lookbook'          },
  { label: 'Services', href: '/synthesis/balloon-twisting'  },
  { label: 'Shop',     href: '/synthesis/shop'              },
  { label: 'Contact',  href: '/inquire'                     },
];

// ── Top Nav ──────────────────────────────────────────────────────────────────
function SiteNav({
  activePath,
  onMenuOpen,
  menuOpen,
}: {
  activePath: string;
  onMenuOpen: () => void;
  menuOpen: boolean;
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', handler, { passive: true });
    return () => window.removeEventListener('scroll', handler);
  }, []);

  return (
    <nav
      className={`site-nav${scrolled ? ' site-nav--scrolled' : ''}`}
      aria-label="Primary navigation"
    >
      <div className="container site-nav__inner">
        {/* Wordmark — DM Serif Display, LT brand */}
        <a href="/synthesis" className="site-nav__wordmark" aria-label="Locally Twisted — home">
          Locally Twisted
          <span className="site-nav__wordmark-sub">Est. 1998 · Wasatch Front</span>
        </a>

        {/* Desktop links */}
        <ul className="site-nav__links" role="list">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className={`site-nav__link${activePath.includes(link.href.split('/').pop() ?? '') ? ' site-nav__link--active' : ''}`}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Right side: phone + CTA + hamburger */}
        <div className="site-nav__right">
          <a
            href="tel:+18012850860"
            className="site-nav__phone"
            aria-label="Call us at (801) 285-0860"
          >
            (801) 285-0860
          </a>

          {/* Teal CTA — the one and only teal element */}
          <a
            href="/inquire"
            className="btn btn-primary"
            aria-label="Tell us about your event"
          >
            Tell us about yours
          </a>

          <button
            className="site-nav__hamburger"
            onClick={onMenuOpen}
            aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={menuOpen}
            aria-controls="mobile-menu"
          >
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            <span aria-hidden="true" />
          </button>
        </div>
      </div>
    </nav>
  );
}

// ── Mobile drawer ─────────────────────────────────────────────────────────────
function MobileMenu({
  isOpen,
  onClose,
  activePath,
}: {
  isOpen: boolean;
  onClose: () => void;
  activePath: string;
}) {
  useEffect(() => {
    document.body.style.overflow = isOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  return (
    <div
      id="mobile-menu"
      className={`mobile-menu${isOpen ? ' mobile-menu--open' : ''}`}
      aria-modal="true"
      role="dialog"
      aria-label="Navigation menu"
      aria-hidden={!isOpen}
    >
      <button
        className="mobile-menu__close"
        onClick={onClose}
        aria-label="Close navigation menu"
      >
        Close ✕
      </button>

      {/* Nav links — DM Serif Display large, editorial feel */}
      <ul className="mobile-menu__links" role="list">
        {NAV_LINKS.map((link) => (
          <li key={link.href}>
            <a
              href={link.href}
              className="mobile-menu__link"
              onClick={onClose}
              aria-current={activePath.includes(link.href.split('/').pop() ?? '') ? 'page' : undefined}
            >
              {link.label}
            </a>
          </li>
        ))}
      </ul>

      {/* Phone + CTA at bottom — what birthday parents at 11pm need */}
      <div className="mobile-menu__bottom">
        <a
          href="tel:+18012850860"
          className="mobile-menu__phone"
          aria-label="Call us at (801) 285-0860"
        >
          (801) 285-0860
        </a>

        <a
          href="/inquire"
          className="btn btn-primary btn-mobile-full"
          onClick={onClose}
        >
          Tell us about yours
        </a>

        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '0.625rem',
            fontWeight: 600,
            letterSpacing: '0.10em',
            textTransform: 'uppercase',
            color: 'var(--color-soft-gray)',
          }}
        >
          Est. 1998 · Wasatch Front
        </p>
      </div>
    </div>
  );
}

// ── Footer ────────────────────────────────────────────────────────────────────
// Soft Blue background per STYLE-GUIDE.md — footer uses --color-soft-blue
function SiteFooter() {
  return (
    <footer className="site-footer" aria-label="Site footer">
      <div className="container">
        <div className="site-footer__inner">
          {/* Brand block */}
          <div>
            <span className="site-footer__brand">Locally Twisted</span>
            <p className="site-footer__tagline">
              Custom balloon decor, Wasatch Front.<br />
              In the work since 1998.
            </p>
          </div>

          {/* Navigation columns */}
          <nav className="site-footer__nav" aria-label="Footer navigation">
            <div className="site-footer__nav-col">
              <h4>Work</h4>
              <ul>
                <li><a href="/synthesis/lookbook">Look Book</a></li>
                <li><a href="/synthesis/lookbook?occasion=Wedding">Weddings</a></li>
                <li><a href="/synthesis/lookbook?occasion=Corporate">Corporate</a></li>
                <li><a href="/synthesis/lookbook?occasion=Birthday">Birthdays</a></li>
              </ul>
            </div>

            <div className="site-footer__nav-col">
              <h4>Services</h4>
              <ul>
                <li><a href="/synthesis/balloon-twisting">Balloon Twisting</a></li>
                <li><a href="/synthesis/balloon-twisting">Face Painting</a></li>
                <li><a href="/inquire">Get a quote</a></li>
              </ul>
            </div>

            <div className="site-footer__nav-col">
              <h4>Shop</h4>
              <ul>
                <li><a href="/synthesis/shop">Bouquets</a></li>
                <li><a href="/synthesis/shop">Cups</a></li>
                <li><a href="/synthesis/shop">Ready-made</a></li>
                <li><a href="/faq">FAQ</a></li>
              </ul>
            </div>
          </nav>
        </div>

        {/* Bottom bar */}
        <div className="site-footer__bottom">
          <p className="site-footer__legal">
            &copy; {new Date().getFullYear()} Locally Twisted. All rights reserved.
          </p>
          <div className="site-footer__social">
            <a
              href="https://www.instagram.com/locallytwisted/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Follow Locally Twisted on Instagram (opens in new tab)"
            >
              Instagram
              <span className="visually-hidden"> (opens in new tab)</span>
            </a>
            <a href="/delivery-area">Delivery area</a>
            <a href="/accessibility">Accessibility</a>
            <a href="/privacy">Privacy</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ── Shell ─────────────────────────────────────────────────────────────────────
export default function SynthesisLayout({
  children,
  activePath = '/',
}: {
  children: React.ReactNode;
  activePath?: string;
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const openMenu  = useCallback(() => setMenuOpen(true),  []);
  const closeMenu = useCallback(() => setMenuOpen(false), []);

  return (
    <>
      {/* Skip link */}
      <a
        href="#main-content"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          zIndex: 9999,
          backgroundColor: 'var(--color-teal)',
          color: 'var(--color-white)',
          padding: 'var(--space-3) var(--space-6)',
          fontFamily: 'var(--font-body)',
          fontSize: 'var(--text-sm)',
          fontWeight: 600,
        }}
        className="visually-hidden"
      >
        Skip to main content
      </a>

      <SiteNav activePath={activePath} onMenuOpen={openMenu} menuOpen={menuOpen} />

      <MobileMenu isOpen={menuOpen} onClose={closeMenu} activePath={activePath} />

      <main id="main-content" className="page-content" tabIndex={-1}>
        {children}
      </main>

      <SiteFooter />
    </>
  );
}
