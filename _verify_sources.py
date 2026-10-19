from pathlib import Path
import json,datetime,hashlib,re,urllib.request,zipfile,xml.etree.ElementTree as E,shutil
W=Path(__file__).resolve().parent;S=W/'sources';events=[]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def capture(url,name,expected):
 t=datetime.datetime.now(datetime.timezone.utc).isoformat();p=S/name
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'OpenCommentary-source-verification/1.0'}),timeout=40) as r:
   b=r.read();status=r.status;headers=dict(r.headers);final=r.url
  if expected=='html':assert b'<html' in b.lower() or b'<!doctype html' in b.lower()
  if p.exists() and p.read_bytes()!=b:
   p=S/(p.stem+'-refetched'+p.suffix)
  p.write_bytes(b)
  event={'url':url,'final_url':final,'accessed_at':t,'http_status':status,'response_headers':headers,'path':str(p.relative_to(W)),'sha256':digest(p),'validated_format':expected,'bytes':len(b)}
 except Exception as e:event={'url':url,'accessed_at':t,'error':str(e)}
 events.append(event);return event
for url,name in [
 ('https://www.gesetze-im-internet.de/gewo/BJNR002450869.html','gewo-full.html'),
 ('https://www.bverwg.de/150415U8C6.14.0','case-bverwg-8c6-14.html'),
 ('https://www.bundesarbeitsgericht.de/entscheidung/10-azr-330-16/','case-bag-10azr330-16.html')]:capture(url,name,'html')
for name,url,header,typ in [
 ('gewo.zip','https://www.gesetze-im-internet.de/gewo/xml.zip','gewo-zip.headers','zip'),
 ('amendment-215.pdf','https://www.recht.bund.de/bgbl/1/2026/215/regelungstext.pdf?__blob=publicationFile','amendment-215.headers','pdf'),
 ('amendment-183.pdf','https://www.recht.bund.de/bgbl/1/2026/183/regelungstext.pdf?__blob=publicationFile','amendment-183.headers','pdf'),
 ('amendment-139.pdf','https://www.recht.bund.de/bgbl/1/2026/139/regelungstext.pdf?__blob=publicationFile','amendment-139.headers','pdf')]:
 p=S/name;h=(S/header).read_text();statuses=re.findall(r'HTTP/[\d.]+ (\d+)',h)
 if typ=='zip':
  assert zipfile.is_zipfile(p)
  with zipfile.ZipFile(p) as z:
   assert z.namelist()==['BJNR002450869.xml'];assert z.read(z.namelist()[0])==(S/'BJNR002450869.xml').read_bytes()
  r=E.parse(S/'BJNR002450869.xml').getroot();assert r.findtext('norm/metadaten/jurabk')=='GewO'
 else:assert p.read_bytes().startswith(b'%PDF-')
 events.append({'url':url,'accessed_at':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'timestamp_method':'download completion filesystem mtime; request response headers retained','http_status':int(statuses[-1]),'headers_path':'sources/'+header,'path':'sources/'+name,'sha256':digest(p),'bytes':p.stat().st_size,'validated_format':typ})
idx=json.loads((S/'gewo-index-response.json').read_text());idx['path']='sources/gewo-index.html';events.append(idx)
for filename,origin in [('rii-kare600053741.md','/Volumes/LaCie/law-intake/eu/de/rii/rii-kare600053741.md'),('rii-wbre201500245.md','/Volumes/LaCie/law-intake/eu/de/rii/rii-wbre201500245.md')]:
 p=S/filename;shutil.copyfile(origin,p);events.append({'type':'local_official_judicial_corpus','original_read_only_path':origin,'snapshot_path':'sources/'+filename,'sha256':digest(p)})
r=E.parse(S/'BJNR002450869.xml').getroot()
verification={'decisive_date':'2026-10-19','authoring_started_at':'2026-10-19','verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_source':'https://www.gesetze-im-internet.de/gewo/','raw_xml':{'path':'sources/BJNR002450869.xml','sha256':digest(S/'BJNR002450869.xml'),'jurabk':'GewO','builddate':r.find('norm').get('builddate'),'stand':[n.text for n in r.findall('norm/metadaten/standangabe/standkommentar')]},'captures':events,'effective_version_evidence':[
 {'source':'sources/amendment-215.pdf','location':'Art. 1 Nr. 1, 3; Art. 11 Abs. 1','effect':'§ 6a broad fiction and § 34c removal of estate agents from further training effective 2026-07-24'},
 {'source':'sources/amendment-215.pdf','location':'Art. 1 Nr. 2; Art. 11 Abs. 2','effect':'§ 14 Abs. 8 new recipients Nos. 15–17 effective 2027-05-01; excluded at decisive date'},
 {'source':'sources/amendment-139.pdf','location':'Art. 7 Nr. 6; Art. 16 Abs. 1, 2 Nr. 2','effect':'§ 34l effective 2026-05-19; other changes incl. § 34k and § 162 effective 2026-11-20, excluded at decisive date'},
 {'source':'sources/amendment-183.pdf','location':'Art. 5; Art. 7 Abs. 2','effect':'GewO changes effective 2026-06-25; 2026-10-01 commencement in Art. 7 Abs. 4 relates to another act, not GewO'}], 'since_intake':{'original_path':'/Volumes/LaCie/law-intake/eu/de/gesetze/gii-gewo.md','preserved_copy':'sources/intake-20261001.md','original_sha256':digest(S/'intake-20261001.md'),'change_map':'sources/change-map.json','method':'fresh official XML, current official index/full HTML, published amendment commencement provisions, targeted official-gazette search','limit':'Targeted search is not an exhaustive audit of all Bundesgesetzblatt issues; §161 triggering notices not independently established.'},'case_law_scope':'Selective, two full-text decisions, court websites and local official corpus; no exhaustive coverage.'}
(S/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'captures':len(events),'errors':[e for e in events if e.get('error')]}))
