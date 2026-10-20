from pathlib import Path
import collections,datetime,difflib,hashlib,html,json,re,subprocess,urllib.request,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;W=D.parent.parent
IDS=['p154','p154a','p155','p155a','p156','p157','p158','p159','p160','p161','anlage']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def comp(t):return re.sub(r'\s+','',html.unescape(t))
def blocks(t):return dict((i,t.strip()) for i,t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',t,re.M|re.S))
# Independently examine a new XML capture, rather than trusting consolidated metadata.
fresh=D/'BJNR002450869.xml';assert fresh.read_bytes()==(W/'sources/BJNR002450869.xml').read_bytes()
r=E.parse(fresh).getroot();assert r.findtext('norm/metadaten/jurabk')=='GewO'
units=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()];um={u['id']:u for u in units};ud={u['official_doknr']:u for u in units}
expected=[];records=[];bad=[];annex=[];selected=[]
for n in r.findall('norm'):
 label=n.findtext('metadaten/enbez','');doc=n.get('doknr');c=n.find('textdaten/text/Content');t=''.join(c.itertext()) if c is not None else ''
 if n.find('metadaten/gliederungseinheit') is not None:kind='structure';assert not t.strip()
 elif label=='Inhaltsübersicht':kind='navigation'
 elif not label:kind='framework';assert not t.strip()
 else:
  kind='statutory_unit';expected.append({'doknr':doc,'label':label});u=ud.get(doc)
  t=t.split('-----',1)[0].strip()
  for note in n.findall('textdaten/text/Content/P/noindex'):t=t.replace(''.join(note.itertext()),'',1).lstrip()
  if not t:t=n.findtext('metadaten/titel','')
  if u is None or u['label']!=label or comp(t)!=comp(u['text']):bad.append(doc)
  if u and u['id'] in IDS:selected.append(u['id'])
  if label.startswith(('Anlage','Anhang')):
   dt=[''.join(x.itertext()).strip() for x in n.findall('.//text/Content//DT')]
   parsed=[x['labels'][-1] for x in u['list_hierarchy']]
   assert dt==parsed;annex.append({'parent_label':label,'doknr':doc,'unit_id':u['id'],'official_list_labels':dt,'parsed_list_labels':parsed,'full_text_agrees':comp(t)==comp(u['text']),'evidence_path':str(fresh.relative_to(W)),'evidence_sha256':sha(fresh)})
 records.append({'doknr':doc,'label':label,'disposition':kind})
assert len(expected)==171 and selected==IDS and not bad
labels=[x['label'] for x in expected];docs=[x['doknr'] for x in expected]
assert len(set(labels))==len(labels) and len(set(docs))==len(docs)
assert docs==[u['official_doknr'] for u in units]
full=(D/'full.html').read_bytes().decode('iso-8859-1');hids=re.findall(r'<div class="jnnorm" id="([^"]+)" title="Einzelnorm">',full)
toc=[n.get('doknr') for n in r.findall('norm') if n.findtext('metadaten/enbez')=='Inhaltsübersicht']
assert [d for d in hids if d not in toc]==docs
cov={'official_xml':str(fresh.relative_to(W)),'sha256':sha(fresh),'expected_official_identifiers':expected,'parsed_official_identifiers':[{'doknr':u['official_doknr'],'label':u['label'],'id':u['id']} for u in units],'expected_count':171,'parsed_count':len(units),'missing':[],'extra':[],'duplicates':[],'text_disagreements':bad,'all_xml_records':records,'record_counts':dict(collections.Counter(x['disposition'] for x in records)),'annexes':annex,'eingangsformel_present':False,'unclassified_operative_records':[],'official_html_id_order_agrees':True,'ok':True}
(D/'coverage.json').write_text(json.dumps(cov,ensure_ascii=False,indent=2)+'\n')
