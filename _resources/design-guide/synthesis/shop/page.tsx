'use client';

/**
 * shop/page.tsx — Synthesis Shop (Take Home)
 *
 * Structural source: D5 (The Studio)
 *   - Product grid with category filter pills
 *   - Slide-in cart drawer
 *   - "Custom event? Start a conversation" cross-link to inquiry for big-ticket items
 *   - Honest, unapologetically small SKU set — not trying to be Amazon
 *   - Heading: "A few things you can take home today" not "SHOP ALL PRODUCTS"
 *
 * Visual language: LT STYLE-GUIDE.md only
 *   - Near-white page ground, white cards
 *   - Teal for "Add to cart" primary CTA only
 *   - DM Serif Display product names, Raleway body and labels
 *   - Filter pills use secondary (outlined) style — not teal
 *   - Cart drawer: white background on near-white ground per STYLE-GUIDE card rules
 *   - Active filter: outlined teal border on pill (Teal appears on button, secondary)
 *   NOTE: Active filter pill uses chip--selected class (near-black border, blush-tint bg)
 *         Never full teal backgrounds. Teal = CTA solid fill only.
 */

import { useState, useCallback } from 'react';
import SynthesisLayout from '../layout';

// ── Types ─────────────────────────────────────────────────────────────────────
type ShopCategory = 'all' | 'bouquets' | 'cups' | 'ready-made';

interface ShopProduct {
  id: string;
  name: string;
  price: number; // cents
  category: Exclude<ShopCategory, 'all'>;
  description: string;
  imageAlt: string;
  href: string;
  inStock: boolean;
  variants?: { label: string; priceAdjust: number }[];
}

// ── Product data (from D5's shop, preserved) ──────────────────────────────────
const PRODUCTS: ShopProduct[] = [
  {
    id: 'BQ-01',
    name: 'Classic Balloon Bouquet',
    price: 3200,
    category: 'bouquets',
    description: 'A hand-tied cluster of 5 balloons in your choice of color. Includes a weight.',
    imageAlt: 'A hand-tied 5-balloon bouquet in soft blush and ivory',
    href: '/shop/classic-balloon-bouquet',
    inStock: true,
    variants: [
      { label: '5 balloons (standard)', priceAdjust: 0 },
      { label: '9 balloons (full)', priceAdjust: 1600 },
    ],
  },
  {
    id: 'BQ-02',
    name: 'Mylar Accent Bouquet',
    price: 4500,
    category: 'bouquets',
    description: 'Three latex + two mylar foil balloons. Makes a strong statement at a table or entry.',
    imageAlt: 'A bouquet mixing latex and gold foil balloons in deep teal and gold',
    href: '/shop/mylar-accent-bouquet',
    inStock: true,
  },
  {
    id: 'BQ-03',
    name: 'Birthday Number Bouquet',
    price: 5800,
    category: 'bouquets',
    description: 'Jumbo foil number balloon + 4 coordinating latex. Choose your number and color.',
    imageAlt: 'A foil number 5 balloon surrounded by matching latex balloons in coral and gold',
    href: '/shop/birthday-number-bouquet',
    inStock: true,
  },
  {
    id: 'CU-01',
    name: 'Balloon Cup Centerpiece',
    price: 1800,
    category: 'cups',
    description: 'A single balloon attached to a cup-and-stick base. Comes in your color choice.',
    imageAlt: 'A single large balloon centerpiece in cobalt blue on a white cup base',
    href: '/shop/balloon-cup',
    inStock: true,
  },
  {
    id: 'CU-02',
    name: 'Trio Cup Set',
    price: 4800,
    category: 'cups',
    description: 'Three balloon cups in coordinating colors. Table-ready.',
    imageAlt: 'Three balloon cup centerpieces in rose, blush, and mauve on a table',
    href: '/shop/trio-cup-set',
    inStock: true,
  },
  {
    id: 'CU-03',
    name: 'Oversized Feature Cup',
    price: 2800,
    category: 'cups',
    description: 'A larger-format cup centerpiece — 24-inch balloon, double-cup base.',
    imageAlt: 'An oversized 24-inch balloon in forest green on a double-cup base',
    href: '/shop/oversized-cup',
    inStock: false,
  },
  {
    id: 'RM-01',
    name: 'Mini Arch — Tabletop',
    price: 8500,
    category: 'ready-made',
    description: 'A small organic arch designed to sit on a table or display ledge. Approx. 24-inches wide.',
    imageAlt: 'A small organic balloon arch in autumn tones — rust, cream, and sage — on a table',
    href: '/shop/mini-arch',
    inStock: true,
  },
  {
    id: 'RM-02',
    name: 'Garland by the Foot',
    price: 1400,
    category: 'ready-made',
    description: 'Pre-made balloon garland, sold per foot. Minimum 6 feet. Pickup or delivery.',
    imageAlt: 'A length of balloon garland in soft pastels curled on a surface',
    href: '/shop/garland',
    inStock: true,
    variants: [
      { label: '6 ft (minimum)', priceAdjust: 0 },
      { label: '12 ft', priceAdjust: 8400 },
      { label: '20 ft', priceAdjust: 16600 },
    ],
  },
  {
    id: 'RM-03',
    name: 'Number Balloon (Jumbo)',
    price: 1200,
    category: 'ready-made',
    description: '40-inch foil number balloon. Gold, silver, or rose gold. Self-inflating included.',
    imageAlt: 'A jumbo gold foil number 30 balloon against a neutral background',
    href: '/shop/jumbo-number',
    inStock: true,
  },
];

const CATEGORY_LABELS: Record<ShopCategory, string> = {
  all:          'All items',
  bouquets:     'Bouquets',
  cups:         'Cups & Centerpieces',
  'ready-made': 'Ready-Made',
};

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatPrice(cents: number): string {
  return `$${(cents / 100).toFixed(2).replace('.00', '')}`;
}

// ── Cart state ────────────────────────────────────────────────────────────────
interface CartItem {
  productId: string;
  variantIndex: number | null;
  quantity: number;
}

function useCart() {
  const [items, setItems] = useState<CartItem[]>([]);

  const addItem = useCallback((productId: string, variantIndex: number | null = null) => {
    setItems((prev) => {
      const existing = prev.find(
        (i) => i.productId === productId && i.variantIndex === variantIndex
      );
      if (existing) {
        return prev.map((i) =>
          i.productId === productId && i.variantIndex === variantIndex
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      return [...prev, { productId, variantIndex, quantity: 1 }];
    });
  }, []);

  const removeItem = useCallback((productId: string, variantIndex: number | null = null) => {
    setItems((prev) =>
      prev.filter((i) => !(i.productId === productId && i.variantIndex === variantIndex))
    );
  }, []);

  const totalCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const totalPrice = items.reduce((sum, item) => {
    const product = PRODUCTS.find((p) => p.id === item.productId);
    if (!product) return sum;
    const variantAdjust =
      item.variantIndex !== null && product.variants
        ? (product.variants[item.variantIndex]?.priceAdjust ?? 0)
        : 0;
    return sum + (product.price + variantAdjust) * item.quantity;
  }, 0);

  return { items, addItem, removeItem, totalCount, totalPrice };
}

// ── Product card ──────────────────────────────────────────────────────────────
function ProductCard({
  product,
  onAddToCart,
}: {
  product: ShopProduct;
  onAddToCart: (productId: string, variantIndex: number | null) => void;
}) {
  const [selectedVariant, setSelectedVariant] = useState(0);

  const effectivePrice =
    product.price +
    (product.variants ? (product.variants[selectedVariant]?.priceAdjust ?? 0) : 0);

  return (
    <article className="shop-item" aria-label={product.name}>
      {/* Photo — no text on image per D7 discipline */}
      <a href={product.href} aria-label={`View details for ${product.name}`} tabIndex={-1}>
        <div className="shop-item__image" style={{ position: 'relative' }}>
          <span className="visually-hidden">{product.imageAlt}</span>

          {/* Out of stock badge */}
          {!product.inStock && (
            <span
              aria-label="Out of stock"
              style={{
                position: 'absolute',
                top: 'var(--space-3)',
                left: 'var(--space-3)',
                backgroundColor: 'var(--color-near-black)',
                color: 'var(--color-white)',
                fontFamily: 'var(--font-body)',
                fontSize: 'var(--text-xs)',
                fontWeight: 600,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                padding: 'var(--space-1) var(--space-2)',
                borderRadius: '2px',
              }}
            >
              Out of stock
            </span>
          )}
        </div>
      </a>

      {/* Product ID in small label register */}
      <p
        className="label"
        style={{
          fontSize: '0.625rem',
          color: 'var(--color-soft-gray)',
          marginBottom: 'var(--space-2)',
        }}
      >
        {product.id}
      </p>

      {/* Name — DM Serif Display */}
      <h3 className="shop-item__name">
        <a href={product.href} style={{ color: 'inherit', textDecoration: 'none' }}>
          {product.name}
        </a>
      </h3>

      {/* Description */}
      <p
        style={{
          fontSize: 'var(--text-sm)',
          color: 'var(--color-soft-gray)',
          lineHeight: 1.5,
          marginBottom: 'var(--space-4)',
        }}
      >
        {product.description}
      </p>

      {/* Variants */}
      {product.variants && (
        <div style={{ marginBottom: 'var(--space-4)' }}>
          <label htmlFor={`variant-${product.id}`} className="form-label">
            Option
          </label>
          <select
            id={`variant-${product.id}`}
            className="form-select"
            value={selectedVariant}
            onChange={(e) => setSelectedVariant(Number(e.target.value))}
            aria-label={`Select variant for ${product.name}`}
          >
            {product.variants.map((v, i) => (
              <option key={i} value={i}>
                {v.label}
                {v.priceAdjust > 0 ? ` (+${formatPrice(v.priceAdjust)})` : ''}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Price + Add to cart */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 'var(--space-3)',
        }}
      >
        <span className="shop-item__price">{formatPrice(effectivePrice)}</span>

        <button
          className="btn btn-primary"
          disabled={!product.inStock}
          onClick={() => onAddToCart(product.id, product.variants ? selectedVariant : null)}
          aria-label={`Add ${product.name} to cart`}
          style={{
            fontSize: 'var(--text-xs)',
            padding: 'var(--space-2) var(--space-4)',
            opacity: product.inStock ? 1 : 0.4,
            cursor: product.inStock ? 'pointer' : 'not-allowed',
          }}
        >
          {product.inStock ? 'Add to cart' : 'Out of stock'}
        </button>
      </div>
    </article>
  );
}

// ── Cart drawer ───────────────────────────────────────────────────────────────
function CartDrawer({
  isOpen,
  onClose,
  items,
  onRemove,
  totalPrice,
}: {
  isOpen: boolean;
  onClose: () => void;
  items: CartItem[];
  onRemove: (productId: string, variantIndex: number | null) => void;
  totalPrice: number;
}) {
  return (
    <>
      {/* Scrim */}
      {isOpen && (
        <div
          onClick={onClose}
          aria-hidden="true"
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(26,26,26,0.4)',
            zIndex: 300,
          }}
        />
      )}

      {/* Drawer */}
      <aside
        role="dialog"
        aria-modal="true"
        aria-label="Shopping cart"
        aria-hidden={!isOpen}
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 'min(400px, 100vw)',
          backgroundColor: 'var(--color-white)',
          zIndex: 400,
          overflowY: 'auto',
          padding: 'var(--space-8) var(--space-6)',
          transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform var(--duration-base) var(--ease-out)',
          boxShadow: '-4px 0 24px rgba(26,26,26,0.12)',
        }}
      >
        {/* Drawer header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 'var(--space-8)',
          }}
        >
          <h2
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: 'var(--text-2xl)',
              color: 'var(--color-near-black)',
            }}
          >
            Your cart
          </h2>
          <button
            onClick={onClose}
            aria-label="Close cart"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--color-soft-gray)',
              minWidth: '44px',
              minHeight: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 'var(--text-xl)',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden="true">
              <line x1="4" y1="4" x2="16" y2="16" />
              <line x1="16" y1="4" x2="4" y2="16" />
            </svg>
          </button>
        </div>

        {/* Empty state */}
        {items.length === 0 ? (
          <div style={{ textAlign: 'center', paddingTop: 'var(--space-16)' }}>
            <p
              style={{
                fontFamily: 'var(--font-display)',
                fontSize: 'var(--text-xl)',
                color: 'var(--color-soft-gray)',
                marginBottom: 'var(--space-4)',
              }}
            >
              Nothing here yet.
            </p>
            <button onClick={onClose} className="btn btn-secondary">
              Keep browsing
            </button>
          </div>
        ) : (
          <>
            {/* Line items */}
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
              {items.map((item) => {
                const product = PRODUCTS.find((p) => p.id === item.productId);
                if (!product) return null;
                const variant =
                  item.variantIndex !== null && product.variants
                    ? product.variants[item.variantIndex]
                    : null;
                const itemPrice = product.price + (variant?.priceAdjust ?? 0);

                return (
                  <li
                    key={`${item.productId}-${item.variantIndex}`}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'flex-start',
                      gap: 'var(--space-4)',
                      paddingBottom: 'var(--space-4)',
                      borderBottom: '1px solid var(--color-border)',
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <p
                        style={{
                          fontFamily: 'var(--font-body)',
                          fontSize: 'var(--text-sm)',
                          fontWeight: 600,
                          color: 'var(--color-near-black)',
                          marginBottom: 'var(--space-1)',
                        }}
                      >
                        {product.name}
                      </p>
                      {variant && (
                        <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-soft-gray)', marginBottom: 'var(--space-1)' }}>
                          {variant.label}
                        </p>
                      )}
                      <p style={{ fontSize: 'var(--text-sm)', fontWeight: 700, color: 'var(--color-near-black)' }}>
                        {formatPrice(itemPrice)} × {item.quantity}
                      </p>
                    </div>
                    <button
                      onClick={() => onRemove(item.productId, item.variantIndex)}
                      aria-label={`Remove ${product.name} from cart`}
                      style={{
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: 'var(--color-soft-gray)',
                        minWidth: '44px',
                        minHeight: '44px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: 'var(--text-xl)',
                      }}
                    >
                      ×
                    </button>
                  </li>
                );
              })}
            </ul>

            {/* Total + Checkout */}
            <div style={{ marginTop: 'var(--space-8)' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: 'var(--space-6)',
                }}
              >
                <span style={{ fontFamily: 'var(--font-body)', color: 'var(--color-soft-gray)' }}>
                  Total
                </span>
                <span
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: 'var(--text-2xl)',
                    color: 'var(--color-near-black)',
                  }}
                >
                  {formatPrice(totalPrice)}
                </span>
              </div>

              <p
                style={{
                  fontSize: 'var(--text-xs)',
                  color: 'var(--color-soft-gray)',
                  marginBottom: 'var(--space-6)',
                  lineHeight: 1.5,
                }}
              >
                Delivery available along the Wasatch Front. Pickup by arrangement.
              </p>

              <a
                href="/checkout"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                Continue to checkout
              </a>
            </div>
          </>
        )}
      </aside>
    </>
  );
}

// ── Page export ───────────────────────────────────────────────────────────────
export default function ShopPage() {
  const [activeCategory, setActiveCategory] = useState<ShopCategory>('all');
  const [cartOpen, setCartOpen] = useState(false);
  const { items, addItem, removeItem, totalCount, totalPrice } = useCart();

  const filteredProducts =
    activeCategory === 'all'
      ? PRODUCTS
      : PRODUCTS.filter((p) => p.category === activeCategory);

  const handleAddToCart = useCallback(
    (productId: string, variantIndex: number | null) => {
      addItem(productId, variantIndex);
      setCartOpen(true);
    },
    [addItem]
  );

  return (
    <SynthesisLayout activePath="/synthesis/shop">
      {/* Page header — near-white ground, LT brand */}
      <section
        aria-label="Shop header"
        style={{
          backgroundColor: 'var(--color-near-white)',
          paddingTop: 'var(--space-12)',
          paddingBottom: 'var(--space-8)',
        }}
      >
        <div className="container">
          <div
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: 'var(--space-4)',
            }}
          >
            <div>
              <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
                Take home
              </p>
              <h1 style={{ marginBottom: 'var(--space-4)', maxWidth: '22ch' }}>
                A few things you can take home today.
              </h1>
              <p style={{ maxWidth: '50ch', marginBottom: 0 }}>
                Smaller pieces available for pickup or delivery along the Wasatch Front.
                For custom balloon decor, start with{' '}
                <a href="/inquire" style={{ color: 'var(--color-near-black)', fontWeight: 600 }}>
                  a conversation
                </a>
                .
              </p>
            </div>

            {/* Cart trigger */}
            <button
              className="btn btn-secondary"
              onClick={() => setCartOpen(true)}
              aria-label={`View cart — ${totalCount} item${totalCount !== 1 ? 's' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', flexShrink: 0 }}
            >
              <svg width="18" height="18" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                <path d="M3 3h2l2.5 9h7l2-6H6.5" strokeLinecap="round" strokeLinejoin="round" />
                <circle cx="9" cy="16" r="1" fill="currentColor" stroke="none" />
                <circle cx="14" cy="16" r="1" fill="currentColor" stroke="none" />
              </svg>
              Cart
              {totalCount > 0 && (
                <span className="cart-badge" aria-label={`${totalCount} items`}>
                  {totalCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </section>

      {/* Thin blush band */}
      <div className="accent-band" style={{ backgroundColor: 'var(--color-blush)' }} aria-hidden="true" />

      {/* Filter bar + grid */}
      <section
        aria-label="Product grid"
        style={{
          backgroundColor: 'var(--color-white)',
          padding: 'var(--space-8) 0 var(--space-16)',
        }}
      >
        <div className="container">
          {/* Category filter pills — secondary style, never teal */}
          <div
            style={{
              display: 'flex',
              gap: 'var(--space-3)',
              flexWrap: 'wrap',
              marginBottom: 'var(--space-8)',
              paddingBottom: 'var(--space-6)',
              borderBottom: '1px solid var(--color-border)',
            }}
            role="group"
            aria-label="Filter by category"
          >
            {(Object.entries(CATEGORY_LABELS) as [ShopCategory, string][]).map(([id, label]) => (
              <button
                key={id}
                className={`chip${activeCategory === id ? ' chip--selected' : ''}`}
                onClick={() => setActiveCategory(id)}
                aria-pressed={activeCategory === id}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Result count */}
          <p
            className="label"
            style={{ color: 'var(--color-soft-gray)', marginBottom: 'var(--space-6)' }}
          >
            {filteredProducts.length} item{filteredProducts.length !== 1 ? 's' : ''}
            {activeCategory !== 'all' && ` in ${CATEGORY_LABELS[activeCategory]}`}
          </p>

          {/* Product grid — 2-up mobile, 3-up desktop per STYLE-GUIDE symmetry rule */}
          <div className="shop-grid">
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={handleAddToCart}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Thin aqua band */}
      <div className="accent-band" style={{ backgroundColor: 'var(--color-aqua)' }} aria-hidden="true" />

      {/* Cross-sell — D5's "Custom event? Start a conversation" pattern */}
      <section
        aria-label="Custom work"
        style={{
          backgroundColor: 'var(--color-near-white)',
          padding: 'var(--space-12) 0',
          borderTop: '1px solid var(--color-border)',
        }}
      >
        <div className="container">
          <div style={{ maxWidth: '540px' }}>
            <p className="label" style={{ marginBottom: 'var(--space-3)', color: 'var(--color-soft-gray)' }}>
              For something larger
            </p>
            <h2 style={{ marginBottom: 'var(--space-4)' }}>
              Custom balloon decor starts with a conversation, not a cart.
            </h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)' }}>
              <a href="/synthesis/lookbook" className="btn btn-secondary">
                See the look book
              </a>
              <a href="/inquire" className="btn btn-primary">
                Tell us what you're imagining
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Cart drawer */}
      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        items={items}
        onRemove={removeItem}
        totalPrice={totalPrice}
      />
    </SynthesisLayout>
  );
}
