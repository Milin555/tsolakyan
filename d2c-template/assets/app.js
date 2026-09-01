/* ══════════════════════════════════════════════════════════════════════
   Shared chrome and behaviour for every page.

   The ticker, header, drawer and footer are rendered from BRAND so that
   rebranding stays a one-file job (assets/data.js). Page-specific code
   lives in each page's own <script>.
   ══════════════════════════════════════════════════════════════════════ */

const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];

/* ── icons ─────────────────────────────────────────────────────── */
const ICONS = {
  cart:   '<path d="M3 5h2l2 11h11l2-8H7"/><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/>',
  menu:   '<path d="M3 6h18M3 12h18M3 18h18"/>',
  close:  '<path d="M5 5l14 14M19 5L5 19"/>',
  check:  '<path d="M4 12l5 5L20 6"/>',
  truck:  '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="18" r="1.5"/><circle cx="17" cy="18" r="1.5"/>',
  shield: '<path d="M12 3l7 3v6c0 4-3 7-7 9-4-2-7-5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
  swap:   '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
  chat:   '<path d="M21 12a8 8 0 1 1-3.4-6.5"/><path d="M21 4v5h-5"/>',
  ig:     '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1"/>',
  fb:     '<path d="M14 9h3V5h-3a4 4 0 0 0-4 4v2H8v4h2v6h4v-6h3l1-4h-4V9a1 1 0 0 1 1-1z"/>',
  yt:     '<rect x="2.5" y="6" width="19" height="12" rx="4"/><path d="M11 10l4 2-4 2z"/>'
};
const icon = (n, cls = 'icon') => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${ICONS[n]}</svg>`;
const WA_GLYPH = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.62.71.23 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.42-.07-.13-.27-.2-.57-.35zM12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.87 9.87 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2z"/></svg>';

const WA_PATH = 'M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.62.71.23 1.36.19 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.42-.07-.13-.27-.2-.57-.35zM12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.87 9.87 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.82 9.82 0 0 0 12.04 2z';
const WA_GLYPH_SM = `<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor" style="flex:none" aria-hidden="true"><path d="${WA_PATH}"/></svg>`;

const NAV = [
  { label:'Shop',    href:'index.html#shop' },
  { label:'Girls',   href:'index.html#shop?cat=girls' },
  { label:'Boys',    href:'index.html#shop?cat=boys' },
  { label:'Festive', href:'index.html#shop?cat=festive' },
  { label:'FAQ',     href:'index.html#faq' }
];

/* ── chrome ────────────────────────────────────────────────────── */
function mountChrome(){
  const wordmark = `${BRAND.name}<em>${BRAND.nameAccent}</em>`;

  document.body.insertAdjacentHTML('afterbegin', `
    <a class="skip" href="#main">Skip to content</a>

    <div class="ticker" aria-hidden="true">
      <div class="ticker__row">
        ${[0,1].map(() => `<span>${TICKER.join('</span><span>')}</span>`).join('')}
      </div>
    </div>

    <header class="mast">
      <div class="wrap mast__in">
        <button class="iconbtn burger" id="burger" aria-label="Open menu" aria-expanded="false">${icon('menu')}</button>
        <a href="index.html" class="mark">${wordmark}</a>
        <nav class="mast__nav">${NAV.map(n => `<a href="${n.href}">${n.label}</a>`).join('')}</nav>
        <div class="mast__act">
          <a class="iconbtn" href="https://wa.me/${BRAND.whatsapp}" aria-label="Chat on WhatsApp">${icon('chat')}</a>
          <a class="iconbtn" href="cart.html" aria-label="Cart">
            ${icon('cart')}<span class="badge" id="cartBadge" hidden>0</span>
          </a>
        </div>
      </div>
    </header>

    <div class="drawer" id="drawer" role="dialog" aria-modal="true" aria-label="Menu">
      <div class="drawer__top">
        <span class="mark">${wordmark}</span>
        <button class="iconbtn" id="drawerX" aria-label="Close menu">${icon('close')}</button>
      </div>
      <nav>${NAV.map(n => `<a href="${n.href}" data-close>${n.label}</a>`).join('')}</nav>
      <div class="drawer__foot">
        <a class="btn btn--wa btn--full" href="https://wa.me/${BRAND.whatsapp}">Order on WhatsApp</a>
        <a class="btn btn--line btn--full" href="tel:${BRAND.phone.replace(/\s/g,'')}">${BRAND.phone}</a>
      </div>
    </div>
  `);

  document.body.insertAdjacentHTML('beforeend', `
    <footer class="foot">
      <div class="wrap foot__g">
        <div>
          <div class="foot__mark">${wordmark}</div>
          <p>${BRAND.blurb}</p>
          <div class="social">
            <a href="${BRAND.instagram}" target="_blank" rel="noopener" aria-label="Instagram">${icon('ig')}</a>
            <a href="#" aria-label="Facebook">${icon('fb')}</a>
            <a href="#" aria-label="YouTube">${icon('yt')}</a>
          </div>
        </div>
        <div><h4>Shop</h4><ul>
          ${CATEGORIES.map(c => `<li><a href="index.html#shop">${c.name}</a></li>`).join('')}
        </ul></div>
        <div><h4>Help</h4><ul>
          <li><a href="index.html#faq">Size guide</a></li>
          <li><a href="index.html#faq">Shipping</a></li>
          <li><a href="index.html#faq">Exchanges</a></li>
          <li><a href="https://wa.me/${BRAND.whatsapp}">Contact us</a></li>
        </ul></div>
        <div><h4>Reach us</h4><ul>
          <li><a href="tel:${BRAND.phone.replace(/\s/g,'')}">${BRAND.phone}</a></li>
          <li><a href="mailto:${BRAND.email}">${BRAND.email}</a></li>
          <li>${BRAND.address}</li>
        </ul></div>
      </div>
      <div class="wrap foot__b">
        <span>© ${new Date().getFullYear()} ${BRAND.name}${BRAND.nameAccent}</span>
        <span>${BRAND.codAvailable ? 'COD available across India' : ''}</span>
      </div>
    </footer>

    <a class="wa-fab" href="https://wa.me/${BRAND.whatsapp}" aria-label="Chat on WhatsApp">${WA_GLYPH}</a>
    <div class="toast" id="toast" role="status" aria-live="polite"></div>
  `);

  /* drawer, focus-trapped */
  const drawer = $('#drawer'), burger = $('#burger');
  let lastFocus = null;
  const focusable = () => $$('a[href],button', drawer).filter(el => el.offsetParent !== null);

  const open = () => {
    lastFocus = document.activeElement;
    drawer.classList.add('is-open');
    burger.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
    focusable()[0]?.focus();
  };
  const close = () => {
    if (!drawer.classList.contains('is-open')) return;
    drawer.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    lastFocus?.focus();
  };
  burger.addEventListener('click', open);
  $('#drawerX').addEventListener('click', close);
  $$('[data-close]', drawer).forEach(a => a.addEventListener('click', close));
  document.addEventListener('keydown', e => {
    if (!drawer.classList.contains('is-open')) return;
    if (e.key === 'Escape') return close();
    if (e.key !== 'Tab') return;
    const f = focusable(); if (!f.length) return;
    const [first, last] = [f[0], f[f.length - 1]];
    if (e.shiftKey && document.activeElement === first){ e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last){ e.preventDefault(); first.focus(); }
  });

  syncBadge();
  document.addEventListener('cart:change', syncBadge);
}

function syncBadge(){
  const b = $('#cartBadge');
  if (!b) return;
  const n = Cart.count();
  b.textContent = n;
  b.hidden = n === 0;
}

let toastTimer;
function toast(message){
  const t = $('#toast');
  if (!t) return;
  t.innerHTML = `${icon('check')}<span>${message}</span>`;
  t.classList.add('is-on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('is-on'), 2600);
}

/* ── product card, used on home and product pages ──────────────── */
function cardHTML(p){
  const off = discount(p);
  return `
  <article class="card">
    <div class="card__art">
      <a href="product.html?sku=${p.sku}" aria-label="${p.name}">
        <picture>
          <source type="image/webp" srcset="${imgSet(p.img, 600)}">
          <img src="assets/img/${p.img}-800.jpg" width="900" height="1350"
               alt="${p.name}" loading="lazy" decoding="async">
        </picture>
      </a>
      ${p.badge ? `<span class="card__tag">${p.badge}</span>` : ''}
      ${off ? `<span class="card__off">${off}% off</span>` : ''}
      <div class="card__quick">
        <button class="btn btn--ink btn--full" data-add="${p.sku}">Quick add</button>
      </div>
    </div>
    <a class="card__name" href="product.html?sku=${p.sku}">${p.name}</a>
    <div class="card__price">
      <span class="card__now">${money(p.price)}</span>
      ${p.mrp > p.price ? `<span class="card__was">${money(p.mrp)}</span>` : ''}
    </div>
    <div class="card__sw">${p.colours.map(c => `<i style="background:${swatch(c)}" title="${c}"></i>`).join('')}</div>
  </article>`;
}

/* approximate chips for the colour dots on cards */
const SWATCH = {
  Yellow:'#E3B23C', White:'#F1EDE6', Orange:'#D9722F', Brown:'#7A5236',
  Pink:'#DE8AA4',   Cream:'#EFE3CC', Red:'#B3302E',   Green:'#3F7A52',
  Blue:'#3B5C93',   Black:'#2A2724', Purple:'#7B5C96', Gold:'#C4903B',
  Maroon:'#6E2230', Navy:'#2C3A54',  Beige:'#DCCDB6', Mustard:'#D9A62E',
  Grey:'#8C857E',   Multicolor:'#C08A6B', Festive:'#C4903B'
};
const swatch = c => SWATCH[c] || '#D8CEC4';

/* wire every [data-add] button on the page */
function wireQuickAdd(root = document){
  $$('[data-add]', root).forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault(); e.stopPropagation();
      const p = bySku(btn.dataset.add);
      if (!p) return;
      Cart.add(p.sku, p.sizes[0], p.colours[0], 1);
      toast(`${p.name} added`);
    });
  });
}

document.addEventListener('DOMContentLoaded', mountChrome);
