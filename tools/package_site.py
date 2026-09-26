"""Make an upload-ready static bundle without local rendering/build files."""
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

SITE=Path(__file__).resolve().parents[1]
files=[SITE/'index.html',SITE/'README.md',SITE/'THIRD_PARTY.md',SITE/'.nojekyll']
files+=sorted(p for p in (SITE/'static').rglob('*')
              if p.is_file() and p.relative_to(SITE/'static').parts[0] not in {'data','downloads'})
target=SITE/'apcl-site.zip'
with ZipFile(target,'w',ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path,'apcl/'+path.relative_to(SITE).as_posix())
    archive.write(SITE/'tools/serve.py','apcl/preview.py')
print(f'{len(files)+1} files, {target.stat().st_size / 1e6:.2f} MB -> {target}')
review=SITE/'apcl-review.zip'
shutil.copyfile(target,review)
print(f'Review bundle (no Git history): {review}')
