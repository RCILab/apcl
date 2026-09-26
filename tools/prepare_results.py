"""Refresh website statistics from complete revised runs; code/data remain unpublished."""
from __future__ import annotations
import hashlib
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pymupdf
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "apcl"
OUT = SITE / "static/data"
VARIANTS = ("rpf", "none", "d3", "full")


def load_complete(name, seeds):
    path = ROOT / "claude_try/results" / name
    raw = path.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    assert len(rows) == len(seeds), f"Incomplete study: {name} ({len(rows)} rows)"
    assert {r["seed"] for r in rows} == set(seeds), f"Unexpected seeds: {name}"
    assert all("error" not in r for r in rows), f"Failed trials: {name}"
    return sorted(rows, key=lambda r: r["seed"]), {
        "file": f"claude_try/results/{name}",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "n": len(rows),
    }


def metrics(runs):
    n = len(runs)
    err = np.array([r["err"] for r in runs])
    radius = np.array([r["r95"] for r in runs])
    assert n and np.all(np.isfinite(err)) and np.all(np.isfinite(radius))
    cbw = (radius < .01) & (err > .02)
    assert np.array_equal(cbw, [r["cbw"] for r in runs])
    k = int(cbw.sum())
    ci = [0.0 if k == 0 else float(beta.ppf(.025, k, n-k+1)),
          1.0 if k == n else float(beta.ppf(.975, k+1, n-k))]
    return {
        "n": n,
        "median_mm": float(np.median(err)*1000),
        "p95_mm": float(np.percentile(err, 95)*1000),
        "cbw_count": k,
        "cbw_pct": 100*k/n,
        "cbw_ci_pct": [100*x for x in ci],
        "coverage_pct": float(np.mean([r["covered"] for r in runs])*100),
        "ball_coverage_pct": float(np.mean(err <= radius)*100),
        "over20_pct": float(np.mean(err > .02)*100),
        "mean_views": float(np.mean([r["views"] for r in runs])),
    }


def replace_once(text, pattern, replacement):
    text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    assert count == 1, f"Missing update target: {pattern}"
    return text


def html_value(html, element_id, value):
    pattern = rf'(<(?P<tag>\w+)\b[^>]*\bid="{re.escape(element_id)}"[^>]*>).*?(</(?P=tag)>)'
    html, count = re.subn(pattern, lambda m: m[1] + value + m[3], html, count=1, flags=re.S)
    assert count == 1, element_id
    return html


def main():
    rows, main_source = load_complete("main.jsonl", range(10000, 11200))
    old, rpf_source = load_complete("main_rpf.jsonl", range(10000, 11200))
    plates, plate_source = load_complete("plate.jsonl", range(90000, 90288))
    contacts, contact_source = load_complete("contact.jsonl", range(70000, 70300))
    sensitivity, sensitivity_source = load_complete("sens.jsonl", range(60000, 60300))
    _, gate_source = load_complete("gate.jsonl", range(40000, 41000))
    numbers_path = ROOT / "claude_try/results/paper_numbers.json"
    numbers_raw = numbers_path.read_bytes()
    numbers = json.loads(numbers_raw)
    numbers_source = {"file": "claude_try/results/paper_numbers.json",
                      "sha256": hashlib.sha256(numbers_raw).hexdigest()}
    threshold = numbers["gate"]["gamma"]
    for row, previous in zip(rows, old):
        assert row["seed"] == previous["seed"]
        for key in ("c_stat", "theta", "m_true"):
            assert np.allclose(row[key], previous[key], rtol=0, atol=1e-12), (row["seed"], key)
        row["res"]["rpf"] = previous["res"]["none"]
        row["res"]["d3"] = row["res"]["D3loa"]
    accepted = [r for r in rows if r["c_stat"] <= threshold]
    accepted_plate = [r for r in plates if r["c_stat"] <= threshold]
    assert len(accepted) == numbers["gate_pass"]["n"]
    assert len(accepted_plate) == numbers["plate_gate"]["n_pass"]
    results = {
        name: {v: metrics([r["res"][v] for r in population]) for v in VARIANTS}
        for name, population in (("all", rows), ("accepted", accepted))
    }
    plate = {
        v: metrics([r["res"][source] for r in plates])
        for v, source in (("full", "plate_full"), ("none", "plate_none"), ("random", "plate_random"))
    }
    plate["accepted"] = metrics([r["res"]["plate_full"] for r in accepted_plate])
    active = {
        v: {"p95_two_views_mm": float(np.percentile([r["res"][v]["log"][1]["err"] for r in rows], 95)*1000),
            "mean_views": float(np.mean([r["res"][v]["views"] for r in rows]))}
        for v in ("full", "full_random")
    }
    for v in active:
        assert np.isclose(active[v]["p95_two_views_mm"], numbers["budget"]["2"][v]["p95"])
    contact = metrics([r["res"]["fol_tcp"] for r in contacts])
    sens = {v: metrics([r["res"][v] for r in sensitivity]) for v in sensitivity[0]["res"]}
    extra = {"active": active, "contact": contact, "sensitivity": sens}
    gate = {"threshold": threshold, "accepted": len(accepted), "total": len(rows),
            "plate_accepted": len(accepted_plate), "plate_total": len(plates)}
    summary = {
        "sources": [main_source, rpf_source, plate_source, contact_source, sensitivity_source, gate_source, numbers_source],
        "scope": "Current simulation runs; numerical validation is provisional pending an estimator consistency check. Hardware measurements are pending.",
        "gate": gate,
        "definitions": {
            "cbw": "95% particle radius < 10 mm AND true error > 20 mm",
            "coverage": "95% credible ellipsoid contains the true point (NEES criterion)",
            "ball_coverage": "true position error <= reported 95% particle radius",
            "final": "final estimate after 2-5 views, with adaptive stopping",
            "interval": "two-sided 95% Clopper-Pearson interval for the observed CBW proportion",
            "rpf": "archived regularized PF without recovery; identical seeds and Phase 1",
            "none": "revised CPF with Metropolis-Hastings moves, without recovery",
            "d3": "revised CPF with MH moves and information-triggered line-of-action recovery only",
            "full": "revised CPF with Metropolis-Hastings moves and D1/D2/D3 recovery",
        },
        **results, "plate": plate, "additional": extra,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT/"results.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    js_path = SITE/"static/site.js"
    js = js_path.read_text(encoding="utf-8")
    block = "// BEGIN GENERATED RESULTS\n"
    block += "const results = " + json.dumps(results, indent=2) + ";\n"
    block += "const plateResults = " + json.dumps(plate, indent=2) + ";\n"
    block += "const studyGate = " + json.dumps(gate) + ";\n"
    block += "const additionalStudies = " + json.dumps(extra, indent=2) + ";\n"
    block += "// END GENERATED RESULTS"
    js = replace_once(js, r"// BEGIN GENERATED RESULTS.*?// END GENERATED RESULTS", block)
    js_path.write_text(js, encoding="utf-8", newline="\n")

    html_path = SITE/"index.html"
    html = html_path.read_text(encoding="utf-8")
    for v in VARIANTS:
        r = results["all"][v]
        for suffix, value in (
            ("median", f'{r["median_mm"]:.1f} mm'),
            ("p95", f'{r["p95_mm"]:.1f} mm'),
            ("cbw", f'{r["cbw_count"]} / {r["n"]:,}'),
            ("coverage", f'{r["coverage_pct"]:.1f}%'),
            ("ball", f'{r["ball_coverage_pct"]:.1f}%'),
        ):
            html = html_value(html, f"table-{v}-{suffix}", value)
        if v not in ("none", "full"):
            continue
        html = html_value(html, f"p95-{v}", f'{r["p95_mm"]:.1f} <small>mm</small>')
        html = html_value(html, f"cbw-{v}", f'{r["cbw_pct"]:.2f}<small>%</small>')
        for metric, scale, key in (("p95", 30, "p95_mm"), ("cbw", 6, "cbw_pct")):
            html = replace_once(
                html, rf'id="{metric}-{v}-bar" style="--bar-width:[^"]+"',
                f'id="{metric}-{v}-bar" style="--bar-width:{r[key]/scale*100:.6f}%"')
    for v, r in plate.items():
        for suffix, value in (
            ("median", f'{r["median_mm"]:.1f} mm'),
            ("p95", f'{r["p95_mm"]:.1f} mm'),
            ("cbw", f'{r["cbw_count"]} / {r["n"]:,}'),
            ("coverage", f'{r["coverage_pct"]:.1f}%'),
            ("ball", f'{r["ball_coverage_pct"]:.1f}%'),
        ):
            html = html_value(html, f"plate-{v}-{suffix}", value)
    a, b = results["all"]["none"], results["all"]["full"]
    html = html_value(html, "tail-note",
        f'Errors above 20 mm: {a["over20_pct"]:.1f}% without recovery and {b["over20_pct"]:.1f}% with APCL.')
    html = html_value(html, "zero-note",
        f'APCL: {b["cbw_count"]} CBW events in {b["n"]:,} trials. '
        f'The exact 95% interval is 0.00\u2013{b["cbw_ci_pct"][1]:.2f}%; zero observed events do not establish zero risk.')
    html = html_value(html, "coverage-note",
        f'<strong>Uncertainty still needs calibration.</strong> APCL\u2019s 95% ellipsoid covered the truth in '
        f'{b["coverage_pct"]:.1f}% of all trials; its 95% particle ball covered '
        f'{b["ball_coverage_pct"]:.1f}%. Both remain below the nominal 95% level. Hardware validation is pending.')
    h = numbers["gate"]["heldout"]
    html = html_value(html, "gate-note",
        f'The threshold fixed on a separate derivation set (c ≤ {threshold:.2f}) accepts '
        f'{len(accepted):,} / {len(rows):,} main-study trials. On the held-out gate study, '
        f'{h["adm_invalid"]} / {h["n_invalid"]} invalid models and {h["valid_acc"]} / {h["n_valid"]} valid models were admitted. Trial records: TBD.')
    d3 = results["all"]["d3"]
    html = html_value(html, "d3-note",
        f'Across all {len(rows):,} trials, line-of-action recovery alone (D3) reached a p95 error of '
        f'{d3["p95_mm"]:.1f} mm with {d3["cbw_count"]} CBW events, similar to the complete method. '
        'D1 and D2 are auxiliary rules; these results do not establish an additional accuracy gain from combining all three.')
    html = html_value(html, "active-summary",
        f'<strong>{active["full"]["p95_two_views_mm"]:.1f} vs {active["full_random"]["p95_two_views_mm"]:.1f} mm</strong>'
        '<span>p95 after two views · active vs random</span>')
    html = html_value(html, "active-details",
        f'With recovery on in {len(rows):,} paired trials, active selection used '
        f'{active["full"]["mean_views"]:.2f} views on average, compared with {active["full_random"]["mean_views"]:.2f} for random selection.')
    html = html_value(html, "contact-summary",
        f'<strong>{contact["median_mm"]:.1f} mm / {contact["p95_mm"]:.1f} mm</strong><span>median / p95 position error</span>')
    html = html_value(html, "contact-details",
        f'A following spherical pusher generated force through MuJoCo contact dynamics. '
        f'{contact["cbw_count"]} CBW events in {contact["n"]:,} simulated trials; hardware validation is pending.')
    p95 = [r["p95_mm"] for r in sens.values()]
    html = html_value(html, "sensitivity-summary",
        f'<strong>{min(p95):.1f}–{max(p95):.1f} mm</strong><span>p95 across tested parameter settings</span>')
    html = html_value(html, "sensitivity-details",
        f'{len(sensitivity):,} matched trials per setting varied the re-supply fraction, information threshold, and persistence. '
        f'{sum(r["cbw_count"] for r in sens.values())} CBW events across the tested settings.')
    html = html_value(html, "plate-gate-note",
        f'The gate admits {len(accepted_plate)} / {len(plates)} reference trials. Their median error is '
        f'{plate["accepted"]["median_mm"]:.1f} mm and particle-ball coverage is {plate["accepted"]["ball_coverage_pct"]:.1f}%. '
        'Passing the contact-free residual check does not guarantee lower position error or calibrated coverage in this protocol.')
    paper = ROOT / "paper/main.pdf"
    paper_raw = paper.read_bytes()
    paper_hash = hashlib.sha256(paper_raw).hexdigest()[:12]
    with pymupdf.open(paper) as pdf:
        page_count = len(pdf)
    shutil.copyfile(paper, SITE / "static/papers/apcl.pdf")
    html = re.sub(r'static/papers/apcl\.pdf\?v=[a-f0-9]+', f'static/papers/apcl.pdf?v={paper_hash}', html)
    html = re.sub(r'PDF · Draft · \d+ pages', f'PDF · Draft · {page_count} pages', html)
    html_path.write_text(html, encoding="utf-8", newline="\n")
    print(json.dumps({"main": results["all"], "gate": gate, "plate": plate}, indent=2))


if __name__ == "__main__":
    main()
