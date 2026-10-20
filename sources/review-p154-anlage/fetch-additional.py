from pathlib import Path
import urllib.request,urllib.error,datetime,hashlib,json,zipfile,io,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
out=json.loads((D/'captures.json').read_text())
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
fetch('https://www.recht.bund.de/bgbl/1/2026/199/regelungstext.pdf?__blob=publicationFile','amendment-199.pdf','pdf')
