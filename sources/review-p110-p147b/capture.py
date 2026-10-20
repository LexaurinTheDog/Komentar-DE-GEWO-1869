"""Capture primary evidence for the bounded independent review; no credential access."""
from pathlib import Path
import urllib.request,urllib.error,datetime,json,hashlib,zipfile,io,xml.etree.ElementTree as E,concurrent.futures
D=Path(__file__).resolve().parent;W=D.parent.parent
items=[
('https://www.gesetze-im-internet.de/gewo/','index.html','html'),
('https://www.gesetze-im-internet.de/gewo/BJNR002450869.html','gewo-full.html','html'),
('https://www.gesetze-im-internet.de/gewo/xml.zip','gewo.zip','zip'),
('https://www.gesetze-im-internet.de/aktuDienst.html','aktudienst.html','html'),
('https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf?__blob=publicationFile','amendment-139.pdf','pdf'),
('https://www.recht.bund.de/bgbl/1/2026/215/regelungstext.pdf?__blob=publicationFile','amendment-215.pdf','pdf'),
('https://www.recht.bund.de/bgbl/1/2026/226/regelungstext.pdf?__blob=publicationFile','amendment-226.pdf','pdf'),
('https://www.recht.bund.de/bgbl/1/2025/349/regelungstext.pdf?__blob=publicationFile','amendment-2025-349.pdf','pdf'),
('https://www.recht.bund.de/bgbl/1/2026/33/regelungstext.pdf?__blob=publicationFile','amendment-33.pdf','pdf'),
('https://www.bundesarbeitsgericht.de/entscheidung/10-azr-448-15/','bag-10azr448-15.html','html'),
('https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-KARE600052708.zip','KARE600052708.zip','casezip'),
]+[('https://www.gesetze-im-internet.de/'+law+'/xml.zip',law+'.zip','otherzip') for law in ['hgb','bgb','owig_1968']]+[('https://www.gesetze-im-internet.de/hgb/__'+i+'.html','hgb-'+i+'.html','html') for i in ['74','74a','75d']]+[
('https://www.gesetze-im-internet.de/owig_1968/__17.html','owig-17.html','html'),
('https://www.gesetze-im-internet.de/owig_1968/__10.html','owig-10.html','html'),
]+[('https://www.gesetze-im-internet.de/bgb/__'+i+'.html','bgb-'+i+'.html','html') for i in ['651t','651u','651v','651w']]
def get(item):
 url,name,kind=item;rec={'url':url,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'expected_format':kind}
 try:
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OpenCommentary-source-verification/1.0'}),timeout=45) as r:b=r.read();rec.update(http_status=r.status,final_url=r.url,headers=dict(r.headers))
  except urllib.error.HTTPError as e:b=e.read();rec.update(http_status=e.code,final_url=e.url,headers=dict(e.headers))
  p=D/name;p.write_bytes(b);rec.update(path=str(p.relative_to(W)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
  if kind in ['zip','casezip','otherzip']:
   assert zipfile.is_zipfile(io.BytesIO(b))
   with zipfile.ZipFile(io.BytesIO(b)) as z:
    rec['zip_members']=z.namelist()
    for member in z.namelist():
     assert Path(member).name==member
     raw=z.read(member);root=E.fromstring(raw);(D/member).write_bytes(raw)
     if kind in ['zip','otherzip']:
      abk={'gewo.zip':'GewO','hgb.zip':'HGB','bgb.zip':'BGB','owig_1968.zip':'OWiG'}[name]
      assert abk in [n.text for n in root.findall('norm/metadaten/jurabk')];rec['xml_sha256']=hashlib.sha256(raw).hexdigest()
     else:assert root.tag=='dokument';rec['case_metadata']={x:root.findtext(x) for x in ['gertyp','entsch-datum','aktenzeichen','ecli']}
  elif kind=='pdf':assert b.startswith(b'%PDF-')
  else:assert b'<html' in b.lower() or b'<!doctype html' in b.lower()
  assert rec['http_status']==200
  if name in ['index.html','gewo-full.html']:assert b'Gewerbeordnung' in b
  if name.startswith(('bgb-','hgb-','owig-')):assert b'jurAbsatz' in b
  if name.startswith('bag-'):assert b'10 AZR 448/15' in b and b'Entscheidungsgr' in b
  rec['format_valid']=True
 except Exception as e:rec['format_valid']=False;rec['error']=str(e)
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(get,items))
(D/'captures.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:r.get(k) for k in ['path','http_status','format_valid','error','case_metadata']} for r in records]))
