from pathlib import Path
import datetime,hashlib,json
W=Path(__file__).resolve().parents[2]
files=[]
for p in sorted((W/'sources').rglob('*')):
 if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts:
  files.append({'path':str(p.relative_to(W)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(W/'sources/manifest.json').write_text(json.dumps({'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verification':'sources/verification.json','files':files,'scope':'Preserved statutory/case evidence and bounded review artifacts. Failed responses explicitly rejected; raw platform editorial material is not commentary authority.'},ensure_ascii=False,indent=2)+'\n')
