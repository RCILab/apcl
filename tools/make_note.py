"""Build the simulation-only project note and link-preview image."""
import json
from pathlib import Path
import shutil
import pymupdf
from PIL import Image, ImageDraw, ImageFont

SITE=Path(__file__).resolve().parents[1]
ROOT=SITE.parent
DATA=json.loads((SITE/'static/data/results.json').read_text(encoding='utf-8'))


def main():
    (SITE/'static/licenses').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'gpt_try/vendor/franka_fr3/LICENSE',SITE/'static/licenses/FR3-LICENSE.txt')
    doc=pymupdf.open()
    page=doc.new_page(width=595,height=842)
    rows=''
    for name,label in [('none','CPF / no recovery'),('full','APCL')]:
        r=DATA['all'][name]
        rows+=f"<tr><td>{label}</td><td>{r['median_mm']:.1f} mm</td><td>{r['p95_mm']:.1f} mm</td><td>{r['cbw_pct']:.2f}%</td><td>{r['coverage_pct']:.1f}%</td></tr>"
    html=f'''<div class="eyebrow">RCI LAB / KYUNG HEE UNIVERSITY · SIMULATION PROJECT NOTE</div>
    <h1>APCL</h1><h2>Ambiguity-Preserving<br>Contact Localization</h2>
    <p class="authors">Juchan Lee · Sanghyun Kim</p>
    <p class="tagline">Preserve ambiguity. Move to resolve it.</p>
    <h3>The idea</h3>
    <p>A single arm configuration leaves contact location ambiguous along the force line of action.
    APCL preserves contact hypotheses along the unresolved direction and selects a new orientation
    to obtain complementary information. It uses joint states and commanded torques, without an
    object model or joint-torque, force/torque, or tactile measurements.</p>
    <h3>Available simulation evidence</h3>
    <p>A paired recovery study on a MuJoCo Franka FR3: 1,200 trials, adaptive stopping at 2–5 views.
    These figures use the full study before trust-gate filtering.</p>
    <table><tr><th>Method</th><th>Median</th><th>95th percentile</th><th>CBW</th><th>95% coverage</th></tr>{rows}</table>
    <p class="small">CBW: reported 95% radius &lt; 10 mm and true position error &gt; 20 mm.
    Empirical coverage is below the nominal 95% level; uncertainty calibration remains incomplete.</p>
    <h3>What the film shows</h3>
    <p>Development seed 17, rerun for two views: 166.3 mm error without recovery and 3.2 mm with APCL.
    The film replays the recorded APCL joint trajectory and saved posterior snapshots.
    Each variant selects its own next orientation. The trajectory is slowed and includes holds;
    particle motion between saved snapshots is not synthesized.</p>
    <h3>Scope and limitations</h3>
    <p>The simulation uses a rigidly grasped payload, one object-fixed contact point,
    an approximately world-fixed applied force, quasi-static measurement windows,
    and regulated tool position. It does not model a physical pusher in the replay.</p>
    <p>A batch re-estimate on the same measurement windows can match filter accuracy and yield
    better-calibrated uncertainty. APCL is not established as universally more accurate or faster.
    Hardware validation is pending. This note is not a submitted or accepted journal article.</p>
    <h3>Provenance</h3><p class="small">Source: claude_try/results/main.jsonl (1,200 trials).<br>
    SHA-256: {DATA['sha256'][:32]}<br>{DATA['sha256'][32:]}<br>
    The companion data archive contains per-trial CSV records, episode trajectories, weighted
    particle snapshots, metadata, and source hashes. Contact: kim87@khu.ac.kr.</p>'''
    css='''*{font-family:Helvetica,Arial,sans-serif}body{color:#1b3434;font-size:9.5pt;line-height:1.45}
    .eyebrow{font-size:7pt;letter-spacing:1px;color:#5a8275}h1{font-size:37pt;line-height:1;margin:20px 0 6px;color:#237a6d}
    h2{font-size:20pt;font-weight:normal;line-height:1.12;margin:0 0 12px}h3{font-size:11pt;margin:16px 0 5px}
    p{margin:5px 0 8px}.authors{font-size:9pt;color:#6a7872}.tagline{font-size:13pt;margin:15px 0 17px;color:#277e6b}
    table{border-collapse:collapse;width:100%;font-size:8pt;margin:10px 0}td,th{border-bottom:1px solid #d6e1d8;padding:7px 5px;text-align:left}
    th{background:#e8f0e7;font-weight:normal;color:#456451}.small{font-size:7.5pt;color:#68756c}'''
    fit=page.insert_htmlbox(pymupdf.Rect(42,35,553,810),html,css=css,scale_low=1)
    if fit[0]<0:
        raise RuntimeError('Project note overflows; reduce content or add a page')
    doc.set_metadata({'title':'APCL — Simulation Project Note','author':'Juchan Lee; Sanghyun Kim','subject':'Simulation only; hardware validation pending'})
    doc.save(SITE/'static/downloads/apcl-project-note.pdf')
    page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(SITE/'.build/project-note.png')
    doc.close()

    # Original social graphic built from the rendered experiment.
    image=Image.new('RGB',(1200,630),(9,20,29))
    poster=Image.open(SITE/'static/images/hero-poster.jpg').resize((730,570),Image.Resampling.LANCZOS)
    image.paste(poster,(505,50))
    d=ImageDraw.Draw(image)
    def f(size,bold=False):
        return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)
    d.text((55,53),'APCL',font=f(28,True),fill=(92,229,208))
    d.text((55,136),'Preserve\nambiguity.',font=f(63,True),fill=(238,246,244),spacing=0)
    d.text((55,302),'Move to\nresolve it.',font=f(63,True),fill=(92,229,208),spacing=0)
    d.text((58,514),'Ambiguity-Preserving Contact Localization',font=f(19),fill=(163,186,193))
    d.text((58,563),'RCI LAB / KYUNG HEE UNIVERSITY',font=f(13),fill=(117,146,156))
    image.save(SITE/'static/images/social-card.jpg',quality=93)
    print('Project note, preview card and license ready.')


if __name__=='__main__':
    main()
