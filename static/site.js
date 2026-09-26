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
      "median_mm": 9.046652334675278,
      "p95_mm": 145.7824263936205,
      "cbw_count": 216,
      "cbw_pct": 18.0,
      "cbw_ci_pct": [
        15.865133816297078,
        20.292922213068458
      ],
      "coverage_pct": 69.58333333333333,
      "ball_coverage_pct": 69.58333333333333,
      "over20_pct": 23.333333333333332,
      "mean_views": 4.280833333333334
    },
    "none": {
      "n": 1200,
      "median_mm": 6.709623748713394,
      "p95_mm": 24.873030945543473,
      "cbw_count": 35,
      "cbw_pct": 2.9166666666666665,
      "cbw_ci_pct": [
        2.0397941540527644,
        4.033187853994991
      ],
      "coverage_pct": 76.08333333333334,
      "ball_coverage_pct": 78.0,
      "over20_pct": 8.083333333333332,
      "mean_views": 4.014166666666667
    },
    "d3": {
      "n": 1200,
      "median_mm": 5.443539978447325,
      "p95_mm": 20.61340322315136,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.30693461081002843
      ],
      "coverage_pct": 83.91666666666666,
      "ball_coverage_pct": 88.66666666666667,
      "over20_pct": 5.916666666666667,
      "mean_views": 4.131666666666667
    },
    "full": {
      "n": 1200,
      "median_mm": 5.483128944396411,
      "p95_mm": 20.769164652561773,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.30693461081002843
      ],
      "coverage_pct": 84.33333333333334,
      "ball_coverage_pct": 88.25,
      "over20_pct": 5.916666666666667,
      "mean_views": 4.149166666666667
    }
  },
  "accepted": {
    "rpf": {
      "n": 675,
      "median_mm": 8.413803193287317,
      "p95_mm": 157.60281403227978,
      "cbw_count": 165,
      "cbw_pct": 24.444444444444443,
      "cbw_ci_pct": [
        21.245962961443993,
        27.868156784604963
      ],
      "coverage_pct": 66.37037037037037,
      "ball_coverage_pct": 65.92592592592592,
      "over20_pct": 26.222222222222225,
      "mean_views": 4.065185185185185
    },
    "none": {
      "n": 675,
      "median_mm": 5.758871856214751,
      "p95_mm": 21.250430138049985,
      "cbw_count": 28,
      "cbw_pct": 4.148148148148148,
      "cbw_ci_pct": [
        2.773815214238009,
        5.939651562313579
      ],
      "coverage_pct": 78.37037037037037,
      "ball_coverage_pct": 80.2962962962963,
      "over20_pct": 5.481481481481482,
      "mean_views": 3.717037037037037
    },
    "d3": {
      "n": 675,
      "median_mm": 4.552340497824658,
      "p95_mm": 14.02599075858123,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.5450100616251372
      ],
      "coverage_pct": 90.07407407407408,
      "ball_coverage_pct": 93.77777777777779,
      "over20_pct": 1.7777777777777777,
      "mean_views": 3.8666666666666667
    },
    "full": {
      "n": 675,
      "median_mm": 4.373660532085967,
      "p95_mm": 14.45906604199989,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        0.5450100616251372
      ],
      "coverage_pct": 89.92592592592594,
      "ball_coverage_pct": 93.03703703703704,
      "over20_pct": 1.7777777777777777,
      "mean_views": 3.882962962962963
    }
  }
};
const plateResults = {
  "full": {
    "n": 288,
    "median_mm": 9.63399004462805,
    "p95_mm": 30.744304504255645,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 95.48611111111111,
    "ball_coverage_pct": 88.19444444444444,
    "over20_pct": 14.23611111111111,
    "mean_views": 4.989583333333333
  },
  "none": {
    "n": 288,
    "median_mm": 9.911408094074384,
    "p95_mm": 31.91582372529856,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 93.40277777777779,
    "ball_coverage_pct": 88.19444444444444,
    "over20_pct": 16.319444444444446,
    "mean_views": 4.96875
  },
  "random": {
    "n": 288,
    "median_mm": 12.517091225597014,
    "p95_mm": 39.67881381134565,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2726928093101806
    ],
    "coverage_pct": 96.875,
    "ball_coverage_pct": 94.09722222222221,
    "over20_pct": 26.73611111111111,
    "mean_views": 5.0
  },
  "accepted": {
    "n": 97,
    "median_mm": 17.145616739117592,
    "p95_mm": 36.15737924445922,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      3.7315636908736063
    ],
    "coverage_pct": 88.65979381443299,
    "ball_coverage_pct": 65.97938144329896,
    "over20_pct": 38.144329896907216,
    "mean_views": 5.0
  }
};
const studyGate = {"threshold": 1.1480989025130282, "accepted": 675, "total": 1200, "plate_accepted": 97, "plate_total": 288};
const additionalStudies = {
  "active": {
    "full": {
      "p95_two_views_mm": 24.424374765280163,
      "mean_views": 4.149166666666667
    },
    "full_random": {
      "p95_two_views_mm": 35.067926582257286,
      "mean_views": 4.879166666666666
    }
  },
  "contact": {
    "n": 300,
    "median_mm": 7.1175194134802995,
    "p95_mm": 19.84566575596026,
    "cbw_count": 0,
    "cbw_pct": 0.0,
    "cbw_ci_pct": [
      0.0,
      1.2220974694293552
    ],
    "coverage_pct": 76.0,
    "ball_coverage_pct": 75.0,
    "over20_pct": 5.0,
    "mean_views": 3.973333333333333
  },
  "contact_estimate_pivot": {
    "n": 300,
    "median_mm": 7.006435418555186,
    "p95_mm": 20.35169365003467,
    "cbw_count": 2,
    "cbw_pct": 0.6666666666666666,
    "cbw_ci_pct": [
      0.08083864127997914,
      2.3873497572173648
    ],
    "coverage_pct": 76.0,
    "ball_coverage_pct": 75.66666666666667,
    "over20_pct": 5.333333333333334,
    "mean_views": 3.95
  },
  "sensitivity": {
    "full": {
      "n": 300,
      "median_mm": 5.433159416162148,
      "p95_mm": 17.606868382000787,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 89.33333333333333,
      "ball_coverage_pct": 90.0,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.176666666666667
    },
    "full_eta10": {
      "n": 300,
      "median_mm": 5.687921561026788,
      "p95_mm": 17.90836118141086,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.66666666666667,
      "ball_coverage_pct": 91.0,
      "over20_pct": 4.0,
      "mean_views": 4.163333333333333
    },
    "full_eta50": {
      "n": 300,
      "median_mm": 5.575006419230894,
      "p95_mm": 18.904348085453396,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.66666666666667,
      "ball_coverage_pct": 90.66666666666666,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.173333333333333
    },
    "full_lmin1": {
      "n": 300,
      "median_mm": 5.456822631228727,
      "p95_mm": 17.49991304263627,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 88.66666666666667,
      "ball_coverage_pct": 89.33333333333333,
      "over20_pct": 4.0,
      "mean_views": 4.176666666666667
    },
    "full_lmin10": {
      "n": 300,
      "median_mm": 5.433159416162148,
      "p95_mm": 17.606868382000787,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 89.33333333333333,
      "ball_coverage_pct": 90.0,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.176666666666667
    },
    "full_L5": {
      "n": 300,
      "median_mm": 5.433159416162148,
      "p95_mm": 17.606868382000787,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 89.66666666666666,
      "ball_coverage_pct": 90.0,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.18
    },
    "full_L20": {
      "n": 300,
      "median_mm": 5.422120438674959,
      "p95_mm": 17.606868382000787,
      "cbw_count": 0,
      "cbw_pct": 0.0,
      "cbw_ci_pct": [
        0.0,
        1.2220974694293552
      ],
      "coverage_pct": 89.33333333333333,
      "ball_coverage_pct": 90.0,
      "over20_pct": 4.666666666666667,
      "mean_views": 4.176666666666667
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
      '%) · c ≤ ' + twoDecimals.format(studyGate.threshold) + ' · frozen trust gate';
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
    'Errors above 20 mm: ' + oneDecimal.format(a.over20_pct) + '% without recovery and ' +
    oneDecimal.format(b.over20_pct) + '% with APCL.';
  document.querySelector('#zero-note').textContent =
    'APCL: ' + b.cbw_count + ' CBW events in ' + comma(b.n) + ' trials. The exact 95% interval is ' +
    twoDecimals.format(b.cbw_ci_pct[0]) + '–' + twoDecimals.format(b.cbw_ci_pct[1]) +
    '%; zero observed events do not establish zero risk.';
  const scope = population === 'all' ? 'all trials' : 'gate-accepted trials';
  document.querySelector('#coverage-note').innerHTML =
    '<strong>Uncertainty still needs calibration.</strong> APCL’s 95% ellipsoid covered the truth in ' +
    oneDecimal.format(b.coverage_pct) + '% of ' + scope + '; its 95% particle ball covered ' +
    oneDecimal.format(b.ball_coverage_pct) + '%. Both remain below the nominal 95% level. Hardware validation is pending.';
}
populationButtons.forEach(button => button.addEventListener('click', () => setPopulation(button.dataset.population)));
setPopulation('all');
