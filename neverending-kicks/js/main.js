/* NeverEnding.Kicks — original motion/interaction script */

document.addEventListener('DOMContentLoaded', () => {
  buildMarquee();
  buildCollection();
  buildFeatured();
  buildBrands();
  initPreloader();
  initCursor();
  initMagnetic();
  initRevealObserver();
  initWordReveal();
  initCounters();
  initNav();
  initFeaturedScroller();
  initHeroParallax();
  initCartAndForm();
});

/* ---------- data helpers ---------- */

function fmtPrice(n) { return '$' + n; }

/* Original vector running-shoe silhouette, side profile, toe pointing right.
   Colors are applied as inline attributes so no CSS-var/shadow-tree issues. */
function shoeSVG(colors, extraClass) {
  const c1 = colors[0];
  const c2 = colors[1] || colors[0];
  return `
  <svg viewBox="0 0 420 200" class="shoe-svg ${extraClass || ''}">
    <path fill="${c1}" d="M28,150
      C24,132 28,112 42,98
      C56,84 70,78 78,64
      C84,53 96,46 108,50
      C116,53 118,62 126,64
      C150,58 178,54 208,54
      C248,54 286,60 318,72
      C348,83 372,98 388,116
      C398,128 400,140 392,150
      C378,158 350,152 322,150
      C250,146 130,146 60,150
      C48,151 34,151 28,150 Z"/>
    <path fill="${c2}" d="M318,72 C348,83 372,98 388,116 C398,128 400,140 392,150 C378,158 358,153 336,151
      C340,132 335,110 322,92 C316,84 310,77 302,71 C307,71 313,71 318,72 Z"/>
    <path fill="#141416" d="M22,150 C40,144 70,142 110,142 L360,142 C382,142 402,146 406,157
      C408,165 400,172 386,174 L48,174 C30,174 18,168 18,158 C18,155 19,152 22,150 Z"/>
    <path fill="rgba(255,255,255,.85)" d="M40,158 L392,158 L392,163 L40,163 Z" opacity=".5"/>
    <g stroke="rgba(0,0,0,.55)" stroke-width="5" stroke-linecap="round" fill="none">
      <path d="M128,66 L118,90"/>
      <path d="M152,60 L141,86"/>
      <path d="M176,56 L164,83"/>
      <path d="M200,54 L188,82"/>
    </g>
    <path fill="rgba(255,255,255,.16)" d="M90,120 C150,102 230,108 300,86 L326,98 C250,132 170,140 92,138 Z"/>
  </svg>`;
}

/* ---------- preloader ---------- */

function initPreloader() {
  const pre = document.getElementById('preloader');
  const count = document.getElementById('preloadCount');
  let n = 0;
  const done = () => {
    count.textContent = '100';
    setTimeout(() => pre.classList.add('is-done'), 250);
  };
  const tick = () => {
    n += Math.random() * 18 + 6;
    if (n >= 100) { done(); return; }
    count.textContent = Math.floor(n);
    setTimeout(tick, 90 + Math.random() * 90);
  };
  tick();
  window.addEventListener('load', () => {}); // reserved
}

/* ---------- custom cursor ---------- */

function initCursor() {
  const cursor = document.getElementById('cursor');
  if (!cursor) return;
  let x = window.innerWidth / 2, y = window.innerHeight / 2;
  let cx = x, cy = y;
  window.addEventListener('mousemove', (e) => { x = e.clientX; y = e.clientY; });
  function raf() {
    cx += (x - cx) * 0.18;
    cy += (y - cy) * 0.18;
    cursor.style.transform = `translate(${cx}px, ${cy}px) translate(-50%, -50%)`;
    requestAnimationFrame(raf);
  }
  raf();
  document.querySelectorAll('[data-hover], a, button').forEach(el => {
    el.addEventListener('mouseenter', () => cursor.classList.add('is-active'));
    el.addEventListener('mouseleave', () => cursor.classList.remove('is-active'));
  });
}

/* ---------- magnetic buttons ---------- */

function initMagnetic() {
  document.querySelectorAll('[data-hover]').forEach(el => {
    el.addEventListener('mousemove', (e) => {
      const r = el.getBoundingClientRect();
      const mx = e.clientX - r.left - r.width / 2;
      const my = e.clientY - r.top - r.height / 2;
      el.style.transform = `translate(${mx * 0.18}px, ${my * 0.28}px)`;
    });
    el.addEventListener('mouseleave', () => { el.style.transform = ''; });
  });
}

/* ---------- reveal on scroll ---------- */

function initRevealObserver() {
  const els = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('is-visible'); });
  }, { threshold: 0.2 });
  els.forEach(el => io.observe(el));
}

function initWordReveal() {
  const words = document.querySelectorAll('.reveal-word');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        const idx = Array.from(words).indexOf(e.target);
        setTimeout(() => e.target.classList.add('is-visible'), idx * 35);
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.4 });
  words.forEach(w => io.observe(w));
}

/* ---------- animated counters ---------- */

function initCounters() {
  const nums = document.querySelectorAll('.stat__num');
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const el = e.target;
      const target = parseInt(el.dataset.count, 10);
      const dur = 1200;
      const start = performance.now();
      function step(t) {
        const p = Math.min(1, (t - start) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.floor(eased * target);
        if (p < 1) requestAnimationFrame(step); else el.textContent = target;
      }
      requestAnimationFrame(step);
      io.unobserve(el);
    });
  }, { threshold: 0.5 });
  nums.forEach(n => io.observe(n));
}

/* ---------- nav hide/show + hero parallax ---------- */

function initNav() {
  const nav = document.getElementById('nav');
  let lastY = window.scrollY;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y > lastY && y > 200) nav.classList.add('is-hidden');
    else nav.classList.remove('is-hidden');
    lastY = y;
  }, { passive: true });
}

function initHeroParallax() {
  const bg = document.getElementById('heroBg');
  const lines = document.querySelectorAll('.hero__title .line');
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (bg) bg.style.transform = `translateY(${y * 0.25}px)`;
    lines.forEach(l => {
      const speed = parseFloat(l.dataset.speed || 1);
      l.style.transform = `translateY(${y * 0.15 * speed}px)`;
    });
  }, { passive: true });
}

/* ---------- marquee ---------- */

function buildMarquee() {
  const track = document.getElementById('marqueeTrack');
  if (!track) return;
  const chunk = BRANDS.map(b => `${b}<em>•</em>`).join('');
  track.innerHTML = `<span>${chunk}</span><span>${chunk}</span>`;
}

/* ---------- brands grid ---------- */

function buildBrands() {
  const grid = document.getElementById('brandsGrid');
  if (!grid) return;
  grid.innerHTML = BRANDS.map(b => {
    const count = SHOES.filter(s => s.brand === b).length;
    return `<div class="brand-card"><b>${b}</b><span>${count} model${count > 1 ? 's' : ''}</span></div>`;
  }).join('');
}

/* ---------- collection list + sticky preview ---------- */

function buildCollection() {
  const list = document.getElementById('collectionList');
  if (!list) return;
  list.innerHTML = SHOES.map((s, i) => `
    <li class="collection__row" data-index="${i}" data-hover>
      <span class="num">${s.n}</span>
      <span class="name"><b>${s.brand} ${s.model}</b><small>${s.cat}</small></span>
      <span class="swatches">${s.colors.map(c => `<i style="background:${c}"></i>`).join('')}</span>
      <span class="price">${fmtPrice(s.price)}</span>
    </li>
  `).join('');

  const rows = list.querySelectorAll('.collection__row');
  const setActive = (idx) => {
    rows.forEach(r => r.classList.remove('is-active'));
    rows[idx].classList.add('is-active');
    updatePreview(SHOES[idx]);
  };
  rows.forEach((row, idx) => {
    row.addEventListener('mouseenter', () => setActive(idx));
    row.addEventListener('click', () => setActive(idx));
  });
  setActive(0);
}

function updatePreview(shoe) {
  document.getElementById('previewBrand').textContent = shoe.brand;
  document.getElementById('previewModel').textContent = shoe.model;
  document.getElementById('previewCat').textContent = shoe.cat;
  document.getElementById('previewWeight').textContent = shoe.weight + 'g';
  document.getElementById('previewDrop').textContent = shoe.drop + 'mm drop';
  document.getElementById('previewPrice').textContent = fmtPrice(shoe.price);
  const wrap = document.getElementById('previewShoeWrap');
  wrap.innerHTML = shoeSVG(shoe.colors);
  const svg = wrap.querySelector('svg');
  svg.style.transform = 'scale(0.96)';
  requestAnimationFrame(() => { svg.style.transform = 'scale(1)'; });
}

/* ---------- featured pinned horizontal scroller ---------- */

function buildFeatured() {
  const track = document.getElementById('featuredTrack');
  if (!track) return;
  const featured = SHOES.filter(s => s.cat === 'Race Day');
  track.innerHTML = featured.map(s => `
    <article class="featured__card">
      <p class="brand">${s.brand}</p>
      <h3>${s.model}</h3>
      ${shoeSVG(s.colors)}
      <div class="row">
        <span>${s.weight}g / ${s.drop}mm drop</span>
        <span class="price">${fmtPrice(s.price)}</span>
      </div>
    </article>
  `).join('');
}

function initFeaturedScroller() {
  const section = document.querySelector('.featured');
  const track = document.getElementById('featuredTrack');
  const progress = document.getElementById('featuredProgress');
  if (!section || !track) return;

  function update() {
    const rect = section.getBoundingClientRect();
    const total = rect.height - window.innerHeight;
    const scrolled = Math.min(Math.max(-rect.top, 0), total);
    const p = total > 0 ? scrolled / total : 0;
    const maxScroll = Math.max(track.scrollWidth - window.innerWidth + 160, 0);
    track.style.transform = `translateX(${-p * maxScroll}px)`;
    if (progress) progress.style.width = (p * 100) + '%';
    requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

/* ---------- cart + form ---------- */

function initCartAndForm() {
  const bagBtn = document.getElementById('bagBtn');
  const bagCount = document.getElementById('bagCount');
  let count = 0;
  bagBtn.addEventListener('click', () => {
    count++;
    bagCount.textContent = count;
    showToast('Added to bag');
  });

  document.querySelectorAll('.collection__row').forEach(row => {
    row.addEventListener('dblclick', () => {
      count++;
      bagCount.textContent = count;
      showToast('Added to bag');
    });
  });

  const form = document.getElementById('ctaForm');
  const note = document.getElementById('ctaNote');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    note.textContent = "You're on the list. We'll ping you at drop.";
    form.reset();
  });
}

function showToast(msg) {
  let toast = document.querySelector('.toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.add('is-visible');
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => toast.classList.remove('is-visible'), 1600);
}
