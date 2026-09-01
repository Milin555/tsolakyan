/* ══════════════════════════════════════════════════════════════════════
   D2C STOREFRONT TEMPLATE — single source of truth

   To rebrand for a new client you edit THIS FILE and the six colour
   tokens at the top of site.css. Nothing else.

   Every page (home, product, cart) renders from the objects below.
   ══════════════════════════════════════════════════════════════════════ */

const BRAND = {
  name:      'Vedora',
  nameAccent:'Kids',                        // rendered in the accent colour
  monogram:  'VK',
  tagline:   'Traditions made for little smiles',
  blurb:     'Festive ethnic wear for children — lehenga choli, kediyu sets and dhoti sets, lined and made to be worn again.',
  whatsapp:  '910000000000',                // ⚠️ PLACEHOLDER — set the client's number
  phone:     '+91 00000 00000',        // ⚠️ PLACEHOLDER
  email:     'hello@example.com',      // ⚠️ PLACEHOLDER — confirm before launch
  instagram: 'https://www.instagram.com/vedorakids',
  city:      'Surat, Gujarat',
  address:   'Address line, City, State PIN',  // ⚠️ PLACEHOLDER
  currency:  '₹',
  freeShipOver: 999,
  codAvailable: true
};

/* scrolling strip under the header */
const TICKER = [
  '25% OFF LIVE',
  'BUY 2 GET 1 FREE',
  'COD AVAILABLE',
  `FREE SHIPPING OVER ${BRAND.currency}${BRAND.freeShipOver}`,
  'NEW FESTIVE EDIT IN'
];

const SLIDES = [
  { img:'hero1', eyebrow:'Navratri Edit',     title:'Ready for the garba nights',
    text:'Patola lehenga choli sets and kediyu, sized 1 to 8 years.', cta:'Shop festive', href:'#shop' },
  { img:'hero2', eyebrow:'Boys Collection',   title:'Kediyu they will keep on',
    text:'Mirror-worked kediyu with dhoti pants and a matching cap.', cta:'Shop boys', href:'#shop' },
  { img:'hero3', eyebrow:'Girls Collection',  title:'Twirls that last all evening',
    text:'Lined cholis, full-flare skirts and dupattas that stay put.', cta:'Shop girls', href:'#shop' }
];

const CATEGORIES = [
  { id:'girls',   img:'c01', name:'Girls',   note:'Lehenga choli · Patola · Garba' },
  { id:'boys',    img:'c02', name:'Boys',    note:'Kediyu · Dhoti sets · Caps' },
  { id:'festive', img:'c03', name:'Festive', note:'Navratri · Garba · Diwali' },
  { id:'accessories', img:'c05', name:'Accessories', note:'Meenakari · Necklaces' },
  { id:'new',     img:'c04', name:'New In',  note:'Fresh this week' }
];

/* Prices and product names are the client's real data.
   Descriptions, fabrics and care are written for the template. */
const PRODUCTS = [
  { sku:'VK-101', img:'v01', name:'Yellow Patola Lehenga Choli Set with Red Dupatta', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'Bestseller',
    desc:'Yellow lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y"], colours:['Yellow'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-102', img:'v02', name:'White Dandiya Garba Print Lehenga Choli Set', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'Bestseller',
    desc:'White lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['White'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-103', img:'v03', name:'Orange Dandiya Print Lehenga Choli Set', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'',
    desc:'Orange lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Orange'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-104', img:'v04', name:'Brown Dandiya Garba Print Lehenga Choli Set', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'',
    desc:'Brown lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Brown'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-105', img:'v05', name:'Pink Multicolor Embroidered Lehenga Choli Set with Navy Dupatta', price:799, mrp:1065,
    cat:'girls', tags:[], badge:'',
    desc:'Pink lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "5-6 Y", "6-7 Y", "7-8 Y"], colours:['Pink'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-106', img:'v06', name:'Cream Kaju Katri Patola Lehenga Choli Set with Black Dupatta', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'',
    desc:'Cream lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Cream'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-107', img:'v07', name:'Red Kaju Katri Patola Lehenga Choli Set with Yellow Dupatta', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'',
    desc:'Red lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Red'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-108', img:'v08', name:'Pink Kaju Katri Patola Lehenga Choli Set with Navy Dupatta', price:799, mrp:1065,
    cat:'girls', tags:["festive"], badge:'',
    desc:'Pink lehenga choli with a lined choli and full-flare skirt. Dupatta included.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Pink'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-109', img:'v09', name:'Red Kediyu Dhoti Set with Cap', price:799, mrp:1065,
    cat:'boys', tags:[], badge:'',
    desc:'Red ethnic set in breathable cotton, cut for all-day wear.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Red'],
    fabric:'Cotton', care:'Gentle hand wash, dry in shade', pieces:'Kurta, bottom' },
  { sku:'VK-110', img:'v10', name:'Blue Embroidered Kediyu with Dhoti Pants & Cap', price:799, mrp:1065,
    cat:'boys', tags:[], badge:'',
    desc:'Blue kediyu with dhoti pants and a matching cap. Mirror and thread work.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Blue'],
    fabric:'Cotton', care:'Gentle hand wash, dry in shade', pieces:'Kediyu, dhoti, cap' },
  { sku:'VK-111', img:'v11', name:'Yellow Embroidered Kediyu with Dhoti Pants & Cap', price:799, mrp:1065,
    cat:'boys', tags:[], badge:'',
    desc:'Yellow kediyu with dhoti pants and a matching cap. Mirror and thread work.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Yellow'],
    fabric:'Cotton', care:'Gentle hand wash, dry in shade', pieces:'Kediyu, dhoti, cap' },
  { sku:'VK-112', img:'v12', name:'Yellow Kediyu & Dhoti Set', price:799, mrp:1065,
    cat:'boys', tags:[], badge:'',
    desc:'Yellow ethnic set in breathable cotton, cut for all-day wear.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['Yellow'],
    fabric:'Cotton', care:'Gentle hand wash, dry in shade', pieces:'Kurta, bottom' },
  { sku:'VK-113', img:'v13', name:'White Multicolor Embroidered Kediyu with Dhoti Pants & Cap', price:799, mrp:1065,
    cat:'boys', tags:[], badge:'',
    desc:'White kediyu with dhoti pants and a matching cap. Mirror and thread work.',
    sizes:["1-2 Y", "2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y"], colours:['White'],
    fabric:'Cotton', care:'Gentle hand wash, dry in shade', pieces:'Kediyu, dhoti, cap' },
  { sku:'VK-114', img:'v14', name:'Girls Designer Embroidered Lehenga Choli Set - Ruby Red', price:799, mrp:1065,
    cat:'girls', tags:[], badge:'New',
    desc:'Red lehenga choli set, lightly worked and fully lined. Easy back tie.',
    sizes:["2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y", "7-8 Y"], colours:['Red'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-115', img:'v15', name:'Girls Designer Embroidered Lehenga Choli Set - Royal Purple', price:799, mrp:1065,
    cat:'girls', tags:[], badge:'New',
    desc:'Purple lehenga choli set, lightly worked and fully lined. Easy back tie.',
    sizes:["2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y", "7-8 Y"], colours:['Purple'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-116', img:'v16', name:'Girls Designer Embroidered Lehenga Choli Set - Rani Pink', price:799, mrp:1065,
    cat:'girls', tags:[], badge:'New',
    desc:'Pink lehenga choli set, lightly worked and fully lined. Easy back tie.',
    sizes:["2-3 Y", "3-4 Y", "4-5 Y", "5-6 Y", "6-7 Y", "7-8 Y"], colours:['Pink'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Choli, lehenga, dupatta' },
  { sku:'VK-117', img:'v17', name:'Gold Rajasthani Multi-Strand Necklace with Meenakari Dome Pendant', price:299, mrp:399,
    cat:'accessories', tags:['new'], badge:'New',
    desc:'Meenakari necklace with multi-strand detailing. Light enough for all-day wear.',
    sizes:["Free size"], colours:['Gold'],
    fabric:'Brass, meenakari', care:'Gentle hand wash, dry in shade', pieces:'Necklace' },
  { sku:'VK-118', img:'v18', name:'Gold Multi-Strand Filigree Necklace with Floral Meenakari & Tassel', price:299, mrp:399,
    cat:'accessories', tags:['new'], badge:'New',
    desc:'Meenakari necklace with multi-strand detailing. Light enough for all-day wear.',
    sizes:["Free size"], colours:['Gold'],
    fabric:'Brass, meenakari', care:'Gentle hand wash, dry in shade', pieces:'Necklace' },
  { sku:'VK-119', img:'v19', name:'Gold Multi-Strand Floral Necklace with Meenakari & Tassel Pendant', price:299, mrp:399,
    cat:'accessories', tags:['new'], badge:'New',
    desc:'Meenakari necklace with multi-strand detailing. Light enough for all-day wear.',
    sizes:["Free size"], colours:['Gold'],
    fabric:'Brass, meenakari', care:'Gentle hand wash, dry in shade', pieces:'Necklace' },
  { sku:'VK-120', img:'v20', name:'Diwali Special Boys Kurta Pyjama Set', price:1999, mrp:2665,
    cat:'boys', tags:['new'], badge:'New',
    desc:'Festive ethnic set, fully lined and cut for comfort.',
    sizes:["3-6 months", "6-9 months", "9-12 months", "12-18 months", "18-24 months", "2 Years"], colours:['Festive'],
    fabric:'Cotton silk', care:'Gentle hand wash, dry in shade', pieces:'Kurta, pyjama' },
  { sku:'VK-121', img:'v21', name:'Shivaji Maharaj Costume for Kids', price:1999, mrp:2665,
    cat:'boys', tags:['new'], badge:'New',
    desc:'Festive ethnic set, fully lined and cut for comfort.',
    sizes:["3-6 months", "6-9 months", "9-12 months", "12-18 months", "18-24 months", "2 Years"], colours:['Festive'],
    fabric:'Cotton blend', care:'Gentle hand wash, dry in shade', pieces:'Complete set' },
  { sku:'VK-122', img:'v22', name:'Blue Printed Ethnic Outfit for Kids', price:1999, mrp:2665,
    cat:'boys', tags:['new'], badge:'New',
    desc:'Blue ethnic set, fully lined and cut for comfort.',
    sizes:["3-6 months", "6-9 months", "9-12 months", "12-18 months", "18-24 months", "2 Years"], colours:['Blue'],
    fabric:'Cotton blend', care:'Gentle hand wash, dry in shade', pieces:'Complete set' }
];

const TESTIMONIALS = [
  { name:'Priya S.',  city:'Ahmedabad', text:'Ordered for Diwali and it arrived in three days. The lining is soft — she wore it all evening without complaining once.' },
  { name:'Rahul M.',  city:'Mumbai',    text:'Sizing was accurate, which never happens. Fabric feels far better than the price suggests.' },
  { name:'Aisha K.',  city:'Hyderabad', text:'Asked on WhatsApp at 10pm and got a reply the same night. Ordered two more sets after that.' }
];

const FAQ = [
  { q:'How do I choose the right size?',        a:'Sizes run by age. If your child is between two sizes, take the larger one — most sets have adjustable waists and back ties.' },
  { q:'What fabrics do you use?',               a:'Cotton, cotton silk, georgette and chanderi. Every set is lined where it touches the skin, so nothing scratches.' },
  { q:'How should I wash them?',                a:'Care is listed on each product page. Cotton pieces are machine washable cold; embroidered and net sets should be dry cleaned.' },
  { q:'How long does delivery take?',           a:'Three to five working days across India. You get a tracking link on WhatsApp as soon as it ships.' },
  { q:'Is Cash on Delivery available?',         a:'Yes, COD is available across India. Prepaid orders ship a day earlier.' },
  { q:'Can I exchange if the size is wrong?',   a:'Yes — message us within seven days of delivery and we will arrange an exchange, unworn and with tags on.' }
];

/* ── helpers shared by every page ───────────────────────────────── */
const money    = n => BRAND.currency + n.toLocaleString('en-IN');
const bySku    = s => PRODUCTS.find(p => p.sku === s);
const discount = p => p.mrp > p.price ? Math.round((1 - p.price / p.mrp) * 100) : 0;
const imgSet   = (name, w) => `assets/img/${name}-${w}.webp`;

/* ── cart: localStorage, shared across pages ────────────────────── */
const CART_KEY = 'vk_cart_v1';

const Cart = {
  read(){
    try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
    catch { return []; }
  },
  write(items){
    localStorage.setItem(CART_KEY, JSON.stringify(items));
    document.dispatchEvent(new CustomEvent('cart:change'));
  },
  add(sku, size, colour, qty = 1){
    const items = Cart.read();
    const hit = items.find(i => i.sku === sku && i.size === size && i.colour === colour);
    if (hit) hit.qty += qty;
    else items.push({ sku, size, colour, qty });
    Cart.write(items);
  },
  setQty(index, qty){
    const items = Cart.read();
    if (!items[index]) return;
    if (qty <= 0) items.splice(index, 1);
    else items[index].qty = qty;
    Cart.write(items);
  },
  remove(index){ Cart.setQty(index, 0); },
  clear(){ Cart.write([]); },
  count(){ return Cart.read().reduce((n, i) => n + i.qty, 0); },
  total(){
    return Cart.read().reduce((sum, i) => {
      const p = bySku(i.sku);
      return sum + (p ? p.price * i.qty : 0);
    }, 0);
  },
  /* the whole order as one WhatsApp message */
  orderText(){
    const items = Cart.read();
    if (!items.length) return '';
    const lines = items.map(i => {
      const p = bySku(i.sku);
      if (!p) return '';
      return `• ${p.sku} — ${p.name}\n  ${i.colour} / ${i.size} × ${i.qty} = ${money(p.price * i.qty)}`;
    }).filter(Boolean);
    const total = Cart.total();
    const ship  = total >= BRAND.freeShipOver ? 'Free shipping' : 'Shipping extra';
    return `Hello ${BRAND.name}${BRAND.nameAccent}, I'd like to order:\n\n`
         + lines.join('\n')
         + `\n\nTotal: ${money(total)} (${ship})\n\nPlease confirm availability and share payment details.`;
  }
};

const waOrder = () =>
  `https://wa.me/${BRAND.whatsapp}?text=${encodeURIComponent(Cart.orderText())}`;

const waProduct = p =>
  `https://wa.me/${BRAND.whatsapp}?text=` +
  encodeURIComponent(`Hello, I'd like to know more about ${p.sku} — ${p.name} (${money(p.price)}).`);
