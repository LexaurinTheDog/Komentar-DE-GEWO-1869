from pathlib import Path
import urllib.request,urllib.error,datetime,hashlib,json,zipfile,io,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
out=[]
def fetch(url,name,fmt):
 row={'url':url,'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'path':str((D/name).relative_to(D.parent.parent))}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OpenCommentary-SourceVerification/1.0'}),timeout=45) as r:
   b=r.read();row.update(http_status=r.status,final_url=r.url,response_headers=dict(r.headers),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  (D/name).write_bytes(b)
  if fmt=='zip':
   assert b.startswith(b'PK');z=zipfile.ZipFile(io.BytesIO(b));row['members']=z.namelist()
   for n in z.namelist():
    if n.endswith('.xml'):
     v=z.read(n);root=E.fromstring(v);assert root.tag=='dokumente';p=D/Path(n).name;p.write_bytes(v);row['xml_sha256']=hashlib.sha256(v).hexdigest()
  elif fmt=='pdf':assert b.startswith(b'%PDF-')
  else:assert b'<html' in b[:10000].lower() and b'captcha' not in b[:10000].lower()
  row['validated_format']=fmt
 except Exception as e:row['error']=str(e)
 out.append(row);(D/'captures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(name,row.get('http_status'),row.get('validated_format'),row.get('error'))
for u,n,f in [
 ('https://www.gesetze-im-internet.de/gewo/','index.html','html'),
 ('https://www.gesetze-im-internet.de/gewo/BJNR002450869.html','full.html','html'),
 ('https://www.gesetze-im-internet.de/gewo/xml.zip','gewo.zip','zip'),
 ('https://www.gesetze-im-internet.de/aktuDienst.html','aktudienst.html','html'),
 ('https://www.gesetze-im-internet.de/vvg_2008/xml.zip','vvg.zip','zip'),
 ('https://www.gesetze-im-internet.de/owig_1968/xml.zip','owig.zip','zip'),
 ('https://www.gesetze-im-internet.de/stpo/xml.zip','stpo.zip','zip'),
 ('https://www.gesetze-im-internet.de/gewo_34cdv/xml.zip','mabv.zip','zip'),
 ('https://www.gesetze-im-internet.de/stgb/xml.zip','stgb.zip','zip'),
 ('https://www.recht.bund.de/bgbl/1/2026/33/regelungstext.pdf?__blob=publicationFile','amendment-33.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf?__blob=publicationFile','amendment-139.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/183/regelungstext.pdf?__blob=publicationFile','amendment-183.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/215/regelungstext.pdf?__blob=publicationFile','amendment-215.pdf','pdf')]:fetch(u,n,f)
