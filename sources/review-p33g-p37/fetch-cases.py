from pathlib import Path
import urllib.request,urllib.error,json,hashlib,datetime,zipfile,io,xml.etree.ElementTree as E,re
D=Path(__file__).resolve().parent;caps=json.loads((D/'captures.json').read_text());corpus=[]
for doc in ['WBRE410018529','KORE317652022','KORE627742023']:
 url=f'https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-{doc}.zip';t=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with urllib.request.urlopen(url,timeout=40) as r:b=r.read();status=r.status
 (D/(doc+'.zip')).write_bytes(b);assert b.startswith(b'PK');z=zipfile.ZipFile(io.BytesIO(b));names=[n for n in z.namelist() if n.endswith('.xml')];assert len(names)==1;x=z.read(names[0]);root=E.fromstring(x);(D/(doc+'.xml')).write_bytes(x)
 caps.append({'url':url,'accessed_at':t,'http_status':status,'path':str((D/(doc+'.zip')).relative_to(D.parent.parent)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'validated_format':'zip','xml_path':str((D/(doc+'.xml')).relative_to(D.parent.parent)),'xml_sha256':hashlib.sha256(x).hexdigest(),'xml_root':root.tag,'court':root.findtext('gertyp'),'docket':root.findtext('aktenzeichen'),'decision_date':root.findtext('entsch-datum')})
 ps=[]
 for tag in ['leitsatz','tenor','tatbestand','entscheidungsgruende','gruende']:
  el=root.find(tag)
  if el is not None:ps+=['## '+tag]+[' '.join(p.itertext()).strip() for p in el.findall('.//p')]
 (D/(doc+'-text.md')).write_text('\n\n'.join(ps)+'\n')
 src=Path('/Volumes/LaCie/law-intake/eu/de/rii')/('rii-'+doc.lower()+'.md');local=src.read_text();(D/src.name).write_text(local)
 # Compare all substantive XML paragraphs to corpus, ignoring pure layout whitespace.
 norm=lambda s:re.sub(r'\s+','',s)
 missing=[p[:120] for p in ps if not p.startswith('## ') and norm(p) not in norm(local)]
 corpus.append({'original_read_only_path':str(src),'snapshot_path':str((D/src.name).relative_to(D.parent.parent)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'official_xml':str((D/(doc+'.xml')).relative_to(D.parent.parent)),'paragraphs':len(ps)-sum(p.startswith('## ') for p in ps),'missing_from_local_corpus':missing})
(D/'captures.json').write_text(json.dumps(caps,indent=2)+'\n');(D/'case-corpus-comparison.json').write_text(json.dumps(corpus,indent=2)+'\n');print(json.dumps(corpus,indent=2))
