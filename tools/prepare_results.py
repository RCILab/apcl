"""Publish a compact, traceable extract of the existing paired Monte Carlo study."""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SITE=ROOT/'apcl'
SOURCE=ROOT/'claude_try/results/main.jsonl'
OUT=SITE/'static/data'


def metrics(rows, name):
    runs=[r['res'][name] for r in rows]
    error=np.array([r['err']*1000 for r in runs])
    return dict(n=len(runs),median_mm=float(np.median(error)),p95_mm=float(np.percentile(error,95)),
                cbw_count=sum(r['cbw'] for r in runs),cbw_pct=float(np.mean([r['cbw'] for r in runs])*100),
                coverage_pct=float(np.mean([r['covered'] for r in runs])*100))


def main():
    raw=SOURCE.read_bytes()
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    assert len(rows)==1200, f'Unexpected study size: {len(rows)}'
    assert len({r['seed'] for r in rows})==len(rows)
    accepted=[r for r in rows if r['c_stat']<=.87]
    summary={
        'source':'claude_try/results/main.jsonl',
        'sha256':hashlib.sha256(raw).hexdigest(),
        'scope':'Paired simulation recovery study; full set is before trust-gate filtering.',
        'gate':{'threshold':.87,'comparison':'<=','accepted':len(accepted),'total':len(rows)},
        'definitions':{'cbw':'reported 95% radius < 10 mm AND position error > 20 mm',
                       'coverage':'true position falls within the reported 95% radius',
                       'final':'adaptive stopping, minimum 2 and maximum 5 views'},
        'all':{v:metrics(rows,v) for v in ('none','full')},
        'accepted':{v:metrics(accepted,v) for v in ('none','full')},
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    buffer=io.StringIO(newline='')
    writer=csv.writer(buffer,lineterminator='\n')
    writer.writerow(['seed','gate_statistic','accepted_at_0.87','variant','views','error_mm','r95_mm','confident_but_wrong','covered'])
    for row in rows:
        for name in ('none','full'):
            result=row['res'][name]
            writer.writerow([row['seed'],row['c_stat'],row['c_stat']<=.87,name,result['views'],
                             result['err']*1000,result['r95']*1000,result['cbw'],result['covered']])
    (OUT/'paired-results.csv').write_text(buffer.getvalue(),encoding='utf-8',newline='\n')
    download=SITE/'static/downloads'
    download.mkdir(exist_ok=True)
    with zipfile.ZipFile(download/'apcl-simulation-data.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in OUT.iterdir():
            if p.is_file():
                z.write(p,'data/'+p.name)
        z.writestr('README.txt',
            'APCL simulation extract\n\n'
            'paired-results.csv: 1200 paired trials, no-recovery CPF and full recovery.\n'
            'results.json: aggregate metrics, gate-conditioned subset and source SHA-256.\n'
            'episode.npz: real q trajectories and weighted particle snapshots for seed 17.\n'
            'episode.json: episode parameters, results and study source hashes.\n\n'
            'Seed 17 is a selected development illustration, not aggregate evidence.\n'
            'Its gate statistic is 0.3503 (accepted at c <= 0.87); it was selected to illustrate recovery.\n'
            'Contact is an applied point force, fixed in the object frame, with a world-fixed nominal force.\n'
            'Object geometry is visualized but is not supplied to the estimator.\n'
            'Hardware experiments are pending. This is a research snapshot.\n')
    # Keep a self-contained snapshot of the exact local study code for review.
    sourcefiles=list((ROOT/'claude_try/ctry').glob('*.py'))+[ROOT/'claude_try/run_experiments.py']
    with zipfile.ZipFile(download/'apcl-study-code.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sourcefiles:
            z.write(p,str(p.relative_to(ROOT/'claude_try')))
        z.writestr('README.txt','APCL study code snapshot\n\n'
                   'Python 3.12; numpy, scipy and mujoco are required.\n'
                   'Entry point: python run_experiments.py --help\n'
                   'This snapshot is provided for inspection and reproduction of the simulation study.\n'
                   'The project is in progress; hardware validation is not included.\n'
                   'See episode.json in the data archive for hashes of the captured implementation.\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
