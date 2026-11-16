import json, subprocess, sys, tempfile
from pathlib import Path
here=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
 a=Path(tmp)/'a'; b=Path(tmp)/'b'
 for out in [a,b]: subprocess.run([sys.executable,str(here/'generate_data.py'),'--employees','5000','--seed','20261022','--out',str(out)],check=True,stdout=subprocess.DEVNULL)
 ma=json.loads((a/'source_manifest.json').read_text()); mb=json.loads((b/'source_manifest.json').read_text())
 ok=ma['files']==mb['files']
 print({'same_seed_same_checksums':ok,'employees':ma['employees'],'salary_history_years':ma['salary_history_years'],'file_count':len(ma['files'])})
 if not ok: raise SystemExit(1)
