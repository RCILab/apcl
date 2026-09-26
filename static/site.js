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
    "d3": {
      "n": 1200,
      "median_mm": 5.476042852032467,
      "p95_mm": 20.72640613886362,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.30693461081002843
      ],
      "coverage_pct": 83.83333333333334,
      "ball_coverage_pct": 88.25,
      "over20_pct": 5.5,
      "mean_views": 4.135
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
      "n": 675,
      "median_mm": 8.743746677208684,
      "p95_mm": 148.4160035924204,
      "cbw_count": 155,
      "cbw_pct": 22.962962962962962,
      "cbw_ci_pct": [
        19.839924854717726,
        26.324437089742815
      ],
      "coverage_pct": 64.88888888888889,
      "ball_coverage_pct": 64.44444444444444,
      "over20_pct": 25.185185185185183,
      "mean_views": 4.054814814814815
    },
    "none": {
      "n": 675,
      "median_mm": 5.5896008500421015,
      "p95_mm": 20.446879775204945,
      "cbw_count": 27,
      "cbw_pct": 4.0,
      "cbw_ci_pct": [
        2.65228668210453,
        5.766650710918348
      ],
      "coverage_pct": 79.11111111111111,
      "ball_coverage_pct": 80.0,
      "over20_pct": 5.481481481481482,
      "mean_views": 3.725925925925926
    },
    "d3": {
      "n": 675,
      "median_mm": 4.454824669996442,
      "p95_mm": 14.1899932965479,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.5450100616251372
      ],
      "coverage_pct": 89.92592592592594,
      "ball_coverage_pct": 93.92592592592592,
      "over20_pct": 1.7777777777777777,
      "mean_views": 3.8696296296296295
    },
    "full": {
      "n": 675,
      "median_mm": 4.390999302209292,
      "p95_mm": 14.02328280751523,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.5450100616251372
      ],
      "coverage_pct": 90.22222222222223,
      "ball_coverage_pct": 93.48148148148148,
      "over20_pct": 1.925925925925926,
      "mean_views": 3.88
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
  },
  "accepted": {
    "n": 97,
    "median_mm": 17.355067985491633,
    "p95_mm": 36.68506373959109,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      3.7315636908736063
    ],
    "coverage_pct": 90.72164948453609,
    "ball_coverage_pct": 67.0103092783505,
    "over20_pct": 39.175257731958766,
    "mean_views": 5.0
  }
};
const studyGate = {"threshold": 1.1480989025130282, "accepted": 675, "total": 1200, "plate_accepted": 97, "plate_total": 288};
const additionalStudies = {
  "active": {
    "full": {
      "p95_two_views_mm": 24.482598053321297,
      "mean_views": 4.145
    },
    "full_random": {
      "p95_two_views_mm": 34.0190102143578,
      "mean_views": 4.8758333333333335
    }
  },
  "contact": {
    "n": 300,
    "median_mm": 6.987832613065325,
    "p95_mm": 19.133235460832854,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2220974694293552
    ],
    "coverage_pct": 75.33333333333333,
    "ball_coverage_pct": 76.0,
    "over20_pct": 4.666666666666667,
    "mean_views": 3.97
  },
  "sensitivity": {
    "full": {
      "n": 300,
      "median_mm": 5.651000346303434,
      "p95_mm": 19.540461368527165,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 87.33333333333333,
      "ball_coverage_pct": 88.33333333333333,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.18
    },
    "full_eta10": {
      "n": 300,
      "median_mm": 5.399542390555908,
      "p95_mm": 19.089403400961384,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 89.66666666666666,
      "ball_coverage_pct": 91.0,
      "over20_pct": 5.0,
      "mean_views": 4.16
    },
    "full_eta50": {
      "n": 300,
      "median_mm": 5.54486153645129,
      "p95_mm": 18.155812051566805,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 90.0,
      "ball_coverage_pct": 90.33333333333333,
      "over20_pct": 4.333333333333334,
      "mean_views": 4.19
    },
    "full_lmin1": {
      "n": 300,
      "median_mm": 5.684793406016936,
      "p95_mm": 18.190803113915933,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.33333333333333,
      "ball_coverage_pct": 88.66666666666667,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.176666666666667
    },
    "full_lmin10": {
      "n": 300,
      "median_mm": 5.651000346303434,
      "p95_mm": 19.540461368527165,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 87.33333333333333,
      "ball_coverage_pct": 88.33333333333333,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.18
    },
    "full_L5": {
      "n": 300,
      "median_mm": 5.651000346303434,
      "p95_mm": 19.540461368527165,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.0,
      "ball_coverage_pct": 88.0,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.19
    },
    "full_L20": {
      "n": 300,
      "median_mm": 5.600437648945527,
      "p95_mm": 19.540461368527165,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.33333333333333,
      "ball_coverage_pct": 88.33333333333333,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.173333333333333
    }
  }
};
// END GENERATED RESULTS
const populationButtons = [...document.querySelectorAll('[data-population]')];
// Match the manuscript's half-even rounding, including exact ties such as 88.25%.
const statFormat = digits => new Intl.NumberFormat('en-US', {
  minimumFractionDigits: digits, maximumFractionDigits: digits,
  roundingMode: 'halfEven', useGrouping: false
});
const oneDecimal = statFormat(1), twoDecimals = statFormat(2);
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
      ' trials accepted (' + twoDecimals.format(100*studyGate.accepted/studyGate.total) +
      '%) · c ≤ ' + studyGate.threshold.toFixed(2) + ' · frozen trust gate';
  for (const name of ['rpf', 'none', 'd3', 'full']) {
    const row = results[population][name];
    const table = '#table-' + name;
    document.querySelector(table + '-median').textContent = oneDecimal.format(row.median_mm) + ' mm';
    document.querySelector(table + '-p95').textContent = oneDecimal.format(row.p95_mm) + ' mm';
    document.querySelector(table + '-cbw').textContent = row.cbw_count + ' / ' + comma(row.n);
    document.querySelector(table + '-coverage').textContent = oneDecimal.format(row.coverage_pct) + '%';
    document.querySelector(table + '-ball').textContent = oneDecimal.format(row.ball_coverage_pct) + '%';
    if (!['none', 'full'].includes(name)) continue;
    document.querySelector('#p95-' + name).innerHTML = oneDecimal.format(row.p95_mm) + ' <small>mm</small>';
    document.querySelector('#cbw-' + name).innerHTML = twoDecimals.format(row.cbw_pct) + '<small>%</small>';
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
