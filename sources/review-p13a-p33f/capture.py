from pathlib import Path
from datetime import datetime,timezone
import urllib.request,urllib.error,hashlib,json,zipfile,io,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent; W=D.parents[1]; events=json.loads((D/'captures.json').read_text()) if (D/'captures.json').exists() else []
def capture(url,name,kind):
 t=datetime.now(timezone.utc).isoformat()
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OpenCommentary-source-verification/1.0'}),timeout=35) as r:b=r.read();status=r.status;headers=dict(r.headers);final=r.url
  p=D/name;p.write_bytes(b)
  if kind=='zip':
   assert zipfile.is_zipfile(io.BytesIO(b))
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    assert z.namelist()==['BJNR002450869.xml'];x=z.read(z.namelist()[0]);root=E.fromstring(x);assert root.findtext('norm/metadaten/jurabk')=='GewO';(D/'BJNR002450869.xml').write_bytes(x)
  elif kind=='pdf':assert b.startswith(b'%PDF-')
  else:assert b'<html' in b.lower() or b'<!doctype html' in b.lower()
  ev={'url':url,'final_url':final,'accessed_at':t,'http_status':status,'response_headers':headers,'path':str(p.relative_to(W)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'validated_format':kind}
 except urllib.error.HTTPError as e:
  b=e.read();p=D/name;p.write_bytes(b);ev={'url':url,'accessed_at':t,'http_status':e.code,'error':str(e),'path':str(p.relative_to(W)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'validated_format':'error response, not accepted as authority'}
 except Exception as e:ev={'url':url,'accessed_at':t,'error':str(e)}
 events.append(ev);(D/'captures.json').write_text(json.dumps(events,ensure_ascii=False,indent=2)+'\n');print(name,ev.get('http_status'),ev.get('error',''),flush=True)
for url,name,kind in [
 ('https://www.gesetze-im-internet.de/gewo/','index.html','html'),
 ('https://www.gesetze-im-internet.de/gewo/BJNR002450869.html','full.html','html'),
 ('https://www.gesetze-im-internet.de/gewo/xml.zip','gewo.zip','zip'),
 ('https://www.gesetze-im-internet.de/aktuDienst.html','aktualitaet.html','html'),
 ('https://www.recht.bund.de/bgbl/1/2026/215/regelungstext.pdf?__blob=publicationFile','amendment-215.pdf','pdf'),
 ('https://www.bverwg.de/300307B6B14.07.0','case-6b14-07.html','html'),
 ('https://www.bverwg.de/entscheidungen/pdf/300307B6B14.07.0.pdf','case-6b14-07.pdf','pdf')]:capture(url,name,kind)
