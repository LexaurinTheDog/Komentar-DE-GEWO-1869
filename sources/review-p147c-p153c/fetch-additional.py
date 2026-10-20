from pathlib import Path
import urllib.request,datetime,hashlib,json,xml.etree.ElementTree as E,zipfile,io
D=Path(__file__).resolve().parent;p=D/'captures.json';rows=json.loads(p.read_text())
for url,name,fmt in [
 ('https://www.recht.bund.de/bgbl/1/2026/156/regelungstext.pdf?__blob=publicationFile','amendment-156.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/229/regelungstext.pdf?__blob=publicationFile','amendment-229.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/95/regelungstext.pdf?__blob=publicationFile','amendment-95.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2026/199/regelungstext.pdf?__blob=publicationFile','amendment-199.pdf','pdf'),
 ('https://www.recht.bund.de/bgbl/1/2025/349/regelungstext.pdf?__blob=publicationFile','amendment-2025-349.pdf','pdf'),
 ('https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32022R2554','dora.html','html'),
 ('https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32016L0097','idd.html','html'),
 ('https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-JURE130006318.xml','jb-JURE130006318.xml','xml')]:
 row={'url':url,'path':str((D/name).relative_to(D.parent.parent)),'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  with urllib.request.urlopen(url,timeout=20) as r:b=r.read();row.update(http_status=r.status,final_url=r.url,response_headers=dict(r.headers),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  (D/name).write_bytes(b)
  if fmt=='pdf':assert b.startswith(b'%PDF-')
  elif fmt=='xml':root=E.fromstring(b);assert root.tag=='dokument';row['root']=root.tag
  else:assert b'<html' in b[:10000].lower() and len(b)>100000
  row['validated_format']=fmt
 except Exception as e:row['error']=repr(e)
 rows.append(row);p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');print(name,row.get('http_status'),row.get('validated_format'),row.get('error'),flush=True)
