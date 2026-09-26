'use strict';

const hero = document.querySelector('#hero-video');
const heroToggle = document.querySelector('#hero-toggle');
const demo = document.querySelector('#demo-video');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let userPaused = false;
let heroVisible = true;

function syncVideoButton() {
  heroToggle.innerHTML = hero.paused ? 'Play <span aria-hidden="true">▶</span>' : 'Pause <span aria-hidden="true">Ⅱ</span>';
  heroToggle.setAttribute('aria-label', hero.paused ? 'Play background simulation' : 'Pause background simulation');
}
async function playHero() {
  try { await hero.play(); } catch (_) { /* The poster remains if autoplay is unavailable. */ }
  syncVideoButton();
}
hero.addEventListener('play', syncVideoButton);
hero.addEventListener('pause', syncVideoButton);
heroToggle.addEventListener('click', () => {
  if (hero.paused) { userPaused = false; playHero(); }
  else { userPaused = true; hero.pause(); }
});
if (!reducedMotion.matches && !navigator.connection?.saveData) playHero();
reducedMotion.addEventListener('change', () => {
  if (reducedMotion.matches) hero.pause();
  else if (!userPaused && heroVisible) playHero();
});
new IntersectionObserver(([entry]) => {
  heroVisible = entry.isIntersecting;
  if (!heroVisible) hero.pause();
  else if (!userPaused && !reducedMotion.matches && demo.paused && !navigator.connection?.saveData) playHero();
}, { threshold: 0.05 }).observe(hero);
document.addEventListener('visibilitychange', () => {
  if (document.hidden) hero.pause();
  else if (heroVisible && !userPaused && !reducedMotion.matches && demo.paused) playHero();
});
demo.addEventListener('play', () => hero.pause());

const menuToggle = document.querySelector('.menu-toggle');
const menu = document.querySelector('#nav-links');
function closeMenu() {
  menuToggle.setAttribute('aria-expanded', 'false');
  menu.classList.remove('open');
}
menuToggle.addEventListener('click', () => {
  const expanded = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(expanded));
  menu.classList.toggle('open', expanded);
});
menu.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && menu.classList.contains('open')) { closeMenu(); menuToggle.focus(); }
});

const angleSlider = document.querySelector('#view-angle');
function updateGeometry() {
  const angle = Number(angleSlider.value);
  document.querySelector('#angle-output').value = `${angle}°`;
  angleSlider.setAttribute('aria-valuetext', `${angle} degrees of force separation`);
  document.querySelector('#second-line').setAttribute('transform', `rotate(${-angle} 300 160)`);
  const ellipse = document.querySelector('#ambiguity-ellipse');
  ellipse.setAttribute('rx', String(Math.min(500, 25 / Math.max(0.025, Math.sin(angle * Math.PI / 360)))));
  ellipse.setAttribute('ry', String(17 / Math.cos(angle * Math.PI / 360)));
  ellipse.setAttribute('transform', `rotate(${-angle / 2} 300 160)`);
  const label = document.querySelector('#view2-label');
  const radius = 190;
  label.setAttribute('x', String(Math.min(490, 300 + radius * Math.cos(angle * Math.PI / 180))));
  label.setAttribute('y', String(Math.max(40, 145 - radius * Math.sin(angle * Math.PI / 180))));
  document.querySelector('#geometry-note').textContent = angle === 0
    ? 'Parallel directions leave a whole line unresolved. A narrow posterior would not remove this ambiguity.'
    : angle < 15
      ? 'The lines intersect, but a small angle is poorly conditioned: small measurement errors can cause large position errors.'
      : 'Different directions resolve the contact; a wider angle improves conditioning.';
}
angleSlider.addEventListener('input', updateGeometry);
updateGeometry();

// Embedded summary keeps the site usable when index.html is opened directly.
// Values are independently checked against static/data/results.json by validate_site.py.
const results = {
  all: {
    none: {n:1200, median:9.171640055847122, p95:137.5603970670698, cbw:17.666666666666668, count:212, coverage:68.5},
    full: {n:1200, median:6.597589702205113, p95:21.87255988929896, cbw:0.8333333333333334, count:10, coverage:81.91666666666667}
  },
  accepted: {
    none: {n:556, median:8.706864165745035, p95:150.31253174274627, cbw:25, count:139, coverage:64.38848920863309},
    full: {n:556, median:5.208021540990853, p95:15.847314474302799, cbw:0.3597122302158274, count:2, coverage:84.71223021582733}
  }
};
const populationButtons = [...document.querySelectorAll('[data-population]')];
function setPopulation(population) {
  populationButtons.forEach(button => {
    const active = button.dataset.population === population;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  document.querySelector('#population-note').textContent = population === 'all'
    ? 'Recovery study · before gate filtering · 2–5 views'
    : '556 / 1,200 trials accepted (46.3%) · c ≤ 0.87 · descriptive subset';
  for (const name of ['none', 'full']) {
    const row = results[population][name];
    document.querySelector(`#p95-${name}`).innerHTML = `${row.p95.toFixed(1)} <small>mm</small>`;
    document.querySelector(`#cbw-${name}`).innerHTML = `${row.cbw.toFixed(2)}<small>%</small>`;
    document.querySelector(`#p95-${name}-bar`).style.setProperty('--bar-width', `${row.p95/160*100}%`);
    document.querySelector(`#cbw-${name}-bar`).style.setProperty('--bar-width', `${row.cbw/30*100}%`);
    document.querySelector(`#table-${name}-median`).textContent = `${row.median.toFixed(1)} mm`;
    document.querySelector(`#table-${name}-p95`).textContent = `${row.p95.toFixed(1)} mm`;
    document.querySelector(`#table-${name}-cbw`).textContent = `${row.count} / ${row.n.toLocaleString('en-US')}`;
    document.querySelector(`#table-${name}-coverage`).textContent = `${row.coverage.toFixed(1)}%`;
  }
}
populationButtons.forEach(button => button.addEventListener('click', () => setPopulation(button.dataset.population)));
setPopulation('all');
