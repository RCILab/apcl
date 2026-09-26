# APCL project page

Project website for **Ambiguity-Preserving Contact Localization (APCL)**.
The page and manuscript omit author names, affiliations, and contact details.
Project assets use relative links so the site can be moved to another static host.

## Preview

Open `index.html` directly, or run the following command from this directory:

```powershell
python -B tools/serve.py
```

Visit <http://127.0.0.1:8765/>. The site uses static HTML, CSS, and JavaScript;
no build step or Node.js installation is required. HTTP preview is recommended
for captions. The preview server supports byte-range requests for video seeking.
For an extracted release ZIP, run `python -B preview.py` instead.

## Contents

- A looping MuJoCo comparison with playback controls and reduced-motion support.
- An interactive illustration of contact ambiguity across force directions.
- A 30-second film with a 0.9 kg suspended load, attachment-point close-ups,
  recorded particle distributions, English and Korean captions, and an MP4 download.
- Results for all 1,200 trials and the 556 trials accepted by the trust gate.
- **Read Paper** and **Supplementary** links in the hero and resources section.
- Code and data marked **TBD**, with no active download links.

## Evidence and scope

The aggregate summary comes from `../claude_try/results/main.jsonl`.
Its source hash is recorded locally in `static/data/results.json`.
The film uses development seed 17 from `../gpt_try/tether_demo/output/`
and is separate from the 1,200-trial aggregate study.

The left robot replays CPF and the right robot replays APCL. Both start from the
same state and independently select the same next orientation in this example.
They represent separate paired trials displayed side by side.
Gold dots mark the true attachment points; coral and mint diamonds mark the
weighted estimates. Symbols are enlarged for visibility without displacing
their positions. The 8.4-second simulation is presented over 30 seconds with
pauses and slower playback; inference between saved snapshots is not interpolated.

The weight is connected to a fixed point on the object through a unilateral
length constraint in MuJoCo. Gravity and cable tension produce the load.
The estimator receives neither the object or cable geometry, the true attachment
point, nor the suspended mass as prior information. Settling checks use the
simulated load angle, speed, and tension. Final errors in this illustrative
episode are 22.5 mm for CPF and 8.7 mm for APCL.

Hardware validation is pending. Red hardware text in the manuscript describes
planned results, not completed measurements. The supplementary material compares
recursive and batch estimation on identical measurement windows, including
uncertainty coverage and calibrated reporting.

## Updating the PDFs

The published files are copies of the manuscript PDFs:

| Source | Website file |
| --- | --- |
| `../paper/main.pdf` | `static/papers/apcl.pdf` |
| `../paper/supplementary.pdf` | `static/papers/apcl-supplementary.pdf` |

When replacing a PDF, also update its page count and link version in `index.html`.
The link version uses the first 12 characters of the file's SHA-256 hash.
Both PDFs are tracked in Git and included in the release ZIPs.

## Regenerating media

These commands require the original research workspace, including the sibling
`claude_try/` and `gpt_try/` directories. They cannot run from a standalone clone
of this website repository. The published site itself does not require Python.

From the workspace root:

```powershell
python -B gpt_try/tether_demo/capture_tether.py
python -B gpt_try/tether_demo/render_tether.py
python -B apcl/tools/prepare_tether_media.py
python -B apcl/tools/package_site.py
```

The workflow requires Python 3.12, NumPy, SciPy, MuJoCo, Pillow, imageio-ffmpeg,
and PyMuPDF. Rendering uses Windows Segoe UI fonts and the existing MuJoCo
Menagerie mesh cache at `apcl/.build/franka_fr3/assets/`. The visual model includes
a simplified gripper attachment without changing the recorded trajectories or estimates.

`static/site.js` embeds the result summary for direct file viewing. When refreshing
results, keep it consistent with `static/data/results.json` and run
`python -B tools/validate_site.py` from this directory with the preview server running.
Browser validation also requires Playwright and Chrome.
The older `capture_episode.py` and `render_video.py` scripts generate the earlier
force-arrow film; use `prepare_tether_media.py` for the current film.

## Packaging and hosting

Run `python -B tools/package_site.py` from this directory to create `apcl-site.zip`
and an identical `apcl-review.zip`. Each contains the page, public assets, both
PDFs, documentation, and a standalone `preview.py` server.

Local data and download folders (`static/data/` and `static/downloads/`) are
excluded from Git and both ZIPs while their release status is TBD. The ZIPs also
exclude Git history, rendering tools, build caches, and the research workspace.
Place the archive's `apcl/` directory at the web root to serve it under `/apcl/`.

For anonymous review, upload the bundle to a separate anonymous host and share
that URL. The page uses relative asset links and omits the original host from
its social metadata.

## Third-party assets

The MuJoCo Menagerie Franka FR3 asset license is in
`static/licenses/FR3-LICENSE.txt`. See `THIRD_PARTY.md` for attribution and visual
modifications.
