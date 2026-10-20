from pathlib import Path
import urllib.request,datetime,json,hashlib,zipfile,io,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent
captures=[]
for name,url in [('index.html','https://www.gesetze-im-internet.de/gewo/'),('full.html','https://www.gesetze-im-internet.de/gewo/BJNR002450869.html'),('xml.zip','https://www.gesetze-im-internet.de/gewo/xml.zip')]:
 t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with urllib.request.urlopen(url,timeout=60) as r: b=r.read();status=r.status;headers=dict(r.headers);final=r.url
 (D/name).write_bytes(b)
 cap={'url':url,'final_url':final,'accessed_at':t,'http_status':status,'path':str((D/name).relative_to(D.parent.parent)),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'content_type':headers.get('Content-Type')}
 if name.endswith('zip'):
  assert b.startswith(b'PK'); z=zipfile.ZipFile(io.BytesIO(b)); assert z.namelist()==['BJNR002450869.xml']; x=z.read(z.namelist()[0]);root=E.fromstring(x);assert root.findtext('norm/metadaten/jurabk')=='GewO';(D/'BJNR002450869.xml').write_bytes(x); cap.update(validated_format='zip',xml_sha256=hashlib.sha256(x).hexdigest(),identical_to_canonical=x==(D.parent/'BJNR002450869.xml').read_bytes())
 else: assert b'Gewerbeordnung' in b;cap['validated_format']='html'
 captures.append(cap)
(D/'captures.json').write_text(json.dumps(captures,indent=2)+'\n')
print(json.dumps(captures,indent=2))
