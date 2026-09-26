"""Capture an actual two-view development episode without changing the study code."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "apcl" / "static" / "data"
sys.path.insert(0, str(ROOT / "claude_try"))


def jsonable(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer, np.bool_)):
        return value.item()
    raise TypeError(type(value).__name__)


def main():
    from ctry.robot import Nominal
    import ctry.episode as episode
    from ctry.sim import Plant
    from run_experiments import VARIANTS

    OUT.mkdir(parents=True, exist_ok=True)
    seed = 17  # The representative development seed already used in the manuscript.
    nom = Nominal()
    trial = episode.sample_trial(seed)
    print("Calibrating development seed 17...", flush=True)
    plant, cal = episode.phase1(trial, nom)
    original_step = Plant.step
    original_max = episode.MAX_VIEWS
    captured = []

    def record_step(self):
        value = original_step(self)
        if int(round(self.t / self.dt)) % 20 == 0:
            captured.append([self.t - plant.t, *self.d.qpos.copy()])
        return value

    arrays = {"contact": trial["p"], "force": trial["fW"], "origin": cal["o_home"],
              "dims": trial["obj"]["dims"], "offset": trial["obj"]["offset"]}
    results = {}
    try:
        Plant.step = record_step
        episode.MAX_VIEWS = 2
        for name in ("none", "full"):
            captured.clear()
            snapshots = []
            print(f"Capturing {name}...", flush=True)
            result = episode.phase2(plant, cal, trial, {**VARIANTS[name], "stop": False}, nom,
                                    snapshots=snapshots)
            arrays[f"{name}_trajectory"] = np.asarray(captured)
            for snap in snapshots:
                for field in ("P", "w", "R"):
                    arrays[f"{name}_{snap['stage']}_{field}"] = snap[field]
            results[name] = result
            print(name, "two-view error mm", result["err"] * 1000, flush=True)
    finally:
        Plant.step = original_step
        episode.MAX_VIEWS = original_max
    np.savez_compressed(OUT / "episode.npz", **arrays)
    summary = {
        "seed": seed, "split": "development", "views": 2,
        "description": "Selected illustrative development episode; not an aggregate result.",
        "simulation": "MuJoCo FR3; 1 kHz torque-controlled plant; full/no-recovery variants",
        "trajectory_sampling_hz": 50,
        "contact": trial["p"], "force_world": trial["fW"], "object": trial["obj"],
        "gate_statistic": cal["c_stat"],
        "gate_note": "Recovery demonstration; the gate is recorded, not used to select this episode.",
        "results": results,
        "source_sha256": {
            str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [ROOT / "claude_try" / "ctry" / f"{n}.py"
                      for n in ("episode", "estimator", "model", "robot", "sim")]
        },
    }
    (OUT / "episode.json").write_text(json.dumps(summary, default=jsonable, indent=2), encoding="utf-8")
    print("Saved", OUT, flush=True)


if __name__ == "__main__":
    main()
