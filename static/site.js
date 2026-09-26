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

// Embedded statistics also work when the page is opened directly.
// Updated from complete trial records by tools/prepare_results.py.
// BEGIN GENERATED RESULTS
const results = {
  "all": {
    "rpf": {
      "n": 1200,
      "median_mm": 9.171640055847124,
      "p95_mm": 137.5603970670698,
      "cbw_count": 212,
      "cbw_pct": 17.666666666666668,
      "cbw_ci_pct": [
        15.548447178385436,
        19.944617009661723
      ],
      "coverage_pct": 68.5,
      "ball_coverage_pct": 68.83333333333333,
      "over20_pct": 23.583333333333336,
      "mean_views": 4.265833333333333
    },
    "none": {
      "n": 1200,
      "median_mm": 6.494797348691111,
      "p95_mm": 24.86264976447821,
      "cbw_count": 35,
      "cbw_pct": 2.9166666666666665,
      "cbw_ci_pct": [
        2.0397941540527644,
        4.033187853994991
      ],
      "coverage_pct": 76.41666666666667,
      "ball_coverage_pct": 77.75,
      "over20_pct": 8.0,
      "mean_views": 4.0216666666666665
    },
    "full": {
      "n": 1200,
      "median_mm": 5.452601939483614,
      "p95_mm": 20.970362205008676,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.30693461081002843
      ],
      "coverage_pct": 84.16666666666667,
      "ball_coverage_pct": 88.0,
      "over20_pct": 5.666666666666666,
      "mean_views": 4.145
    }
  },
  "accepted": {
    "rpf": {
      "n": 556,
      "median_mm": 8.706864165745035,
      "p95_mm": 150.31253174274627,
      "cbw_count": 139,
      "cbw_pct": 25.0,
      "cbw_ci_pct": [
        21.45176669797294,
        28.816317263213847
      ],
      "coverage_pct": 64.38848920863309,
      "ball_coverage_pct": 63.66906474820144,
      "over20_pct": 26.43884892086331,
      "mean_views": 3.9928057553956835
    },
    "none": {
      "n": 556,
      "median_mm": 5.508332017501243,
      "p95_mm": 20.406251377131735,
      "cbw_count": 26,
      "cbw_pct": 4.676258992805756,
      "cbw_ci_pct": [
        3.0770908690912298,
        6.7769771723568475
      ],
      "coverage_pct": 77.6978417266187,
      "ball_coverage_pct": 78.41726618705036,
      "over20_pct": 5.39568345323741,
      "mean_views": 3.6384892086330933
    },
    "full": {
      "n": 556,
      "median_mm": 4.27009958777513,
      "p95_mm": 13.034622822661538,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.6612714413739798
      ],
      "coverage_pct": 91.36690647482014,
      "ball_coverage_pct": 94.06474820143885,
      "over20_pct": 1.079136690647482,
      "mean_views": 3.816546762589928
    }
  }
};
const plateResults = {
  "full": {
    "n": 288,
    "median_mm": 9.82986359623498,
    "p95_mm": 31.4861188172962,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 96.52777777777779,
    "ball_coverage_pct": 88.88888888888889,
    "over20_pct": 13.88888888888889,
    "mean_views": 4.986111111111111
  },
  "none": {
    "n": 288,
    "median_mm": 9.745313469550553,
    "p95_mm": 30.331763770566212,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 92.36111111111111,
    "ball_coverage_pct": 87.15277777777779,
    "over20_pct": 15.972222222222221,
    "mean_views": 4.972222222222222
  },
  "random": {
    "n": 288,
    "median_mm": 12.170782497272981,
    "p95_mm": 37.747627452010335,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 96.875,
    "ball_coverage_pct": 95.83333333333334,
    "over20_pct": 26.38888888888889,
    "mean_views": 5.0
  }
};
const studyGate = {"threshold": 0.87, "accepted": 556, "total": 1200, "plate_accepted": 78, "plate_total": 288};
// END GENERATED RESULTS
const populationButtons = [...document.querySelectorAll('[data-population]')];
function setPopulation(population) {
  populationButtons.forEach(button => {
    const active = button.dataset.population === population;
    button.classList.toggle('active', active);
    button.setAttribute('aria-pressed', String(active));
  });
  const comma = n => n.toLocaleString('en-US');
  document.querySelector('#population-note').textContent = population === 'all'
    ? 'Revised recovery study · before gate filtering · 2–5 views'
    : comma(studyGate.accepted) + ' / ' + comma(studyGate.total) +
      ' trials accepted (' + (100*studyGate.accepted/studyGate.total).toFixed(1) +
      '%) · c ≤ ' + studyGate.threshold.toFixed(2) + ' · descriptive subset';
  for (const name of ['rpf', 'none', 'full']) {
    const row = results[population][name];
    const table = '#table-' + name;
    document.querySelector(table + '-median').textContent = row.median_mm.toFixed(1) + ' mm';
    document.querySelector(table + '-p95').textContent = row.p95_mm.toFixed(1) + ' mm';
    document.querySelector(table + '-cbw').textContent = row.cbw_count + ' / ' + comma(row.n);
    document.querySelector(table + '-coverage').textContent = row.coverage_pct.toFixed(1) + '%';
    document.querySelector(table + '-ball').textContent = row.ball_coverage_pct.toFixed(1) + '%';
    if (name === 'rpf') continue;
    document.querySelector('#p95-' + name).innerHTML = row.p95_mm.toFixed(1) + ' <small>mm</small>';
    document.querySelector('#cbw-' + name).innerHTML = row.cbw_pct.toFixed(2) + '<small>%</small>';
    document.querySelector('#p95-' + name + '-bar').style.setProperty('--bar-width', row.p95_mm/30*100 + '%');
    document.querySelector('#cbw-' + name + '-bar').style.setProperty('--bar-width', row.cbw_pct/6*100 + '%');
  }
  const a = results[population].none, b = results[population].full;
  document.querySelector('#tail-note').textContent =
    'Errors above 20 mm: ' + a.over20_pct.toFixed(1) + '% without recovery and ' +
    b.over20_pct.toFixed(1) + '% with APCL.';
  document.querySelector('#zero-note').textContent =
    'APCL: ' + b.cbw_count + ' CBW events in ' + comma(b.n) + ' trials. The exact 95% interval is ' +
    b.cbw_ci_pct[0].toFixed(2) + '–' + b.cbw_ci_pct[1].toFixed(2) +
    '%; zero observed events do not establish zero risk.';
  const scope = population === 'all' ? 'all trials' : 'gate-accepted trials';
  document.querySelector('#coverage-note').innerHTML =
    '<strong>Uncertainty still needs calibration.</strong> APCL’s 95% ellipsoid covered the truth in ' +
    b.coverage_pct.toFixed(1) + '% of ' + scope + '; its 95% particle ball covered ' +
    b.ball_coverage_pct.toFixed(1) + '%. Both remain below the nominal 95% level. Hardware validation is pending.';
}
populationButtons.forEach(button => button.addEventListener('click', () => setPopulation(button.dataset.population)));
setPopulation('all');
