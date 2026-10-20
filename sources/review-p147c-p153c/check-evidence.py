from pathlib import Path
import collections,datetime,difflib,hashlib,html,json,re,subprocess,urllib.request,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;W=D.parent.parent
IDS=['p147c','p147d','p148','p148a','p148b','p148c','p149','p150','p150a','p150b','p150c','p150d','p150e','p150f','p151','p152','p153','p153a','p153b','p153c']
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
# Compare each fully read numbered paragraph and unnumbered continuation with local corpus.
case=E.parse(D/'case-JURE130006318.xml').getroot();corpus=(D/'corpus-bgh-3str372-12.md').read_text();checks=[]
for section in ['tenor','gruende']:
 for el in case.findall(section+'/.//dd')+case.findall(section+'/p'):
  t=''.join(el.itertext()).strip()
  if len(comp(t))>30:checks.append({'section':section,'sha256':hashlib.sha256(t.encode()).hexdigest(),'matches_corpus':comp(t) in comp(corpus)})
assert all(x['matches_corpus'] for x in checks)
rns=[a.text for a in case.findall('.//a') if a.get('name','').startswith('rd_')];assert rns==list(map(str,range(1,12)))
(D/'case-corpus-comparison.json').write_text(json.dumps({'case':'BGH 3 StR 372/12','official_xml':str((D/'case-JURE130006318.xml').relative_to(W)),'xml_sha256':sha(D/'case-JURE130006318.xml'),'corpus_source':'/Volumes/LaCie/law-intake/eu/de/rii/rii-jure130006318.md','corpus_snapshot':str((D/'corpus-bgh-3str372-12.md').relative_to(W)),'corpus_sha256':sha(D/'corpus-bgh-3str372-12.md'),'numbered_paragraphs':rns,'all_paragraphs_read':'Tenor, Rn. 1–11 and all unnumbered continuations including GBA submission adopted only in Rn. 11','text_blocks':checks,'comparison':'Compare entire court tenor and every long dd text with local national judicial corpus after whitespace/entity normalization. No third-party annotations copied.','ok':True},ensure_ascii=False,indent=2)+'\n')
# Exact preservation of all 151 unassigned blocks; duplicate diagnosis is not a quality certificate.
before={};after={}
for p in sorted((W/'commentary').glob('*.md')):before.update(blocks((D/'baseline-commentary'/p.name).read_text()));after.update(blocks(p.read_text()))
changed=[i for i in after if after[i]!=before[i]];outside=sorted(set(changed)-set(IDS));assert not outside and len(after)==171
paras=collections.defaultdict(set)
for i,t in after.items():
 for q in t.split('\n\n'):
  if len(q)>160:paras[q].add(i)
dup=[{'ids':sorted(v),'sha256':hashlib.sha256(q.encode()).hexdigest()} for q,v in paras.items() if len(v)>1 and v.intersection(IDS)]
assert not dup
pairs=[]
for i in IDS:
 for j in after:
  if i>=j:continue
  ratio=difflib.SequenceMatcher(None,after[i],after[j],autojunk=True).ratio()
  if ratio>.55:pairs.append({'a':i,'b':j,'similarity':ratio})
assert not pairs
out={'scope':'Exactly 20 manually reviewed units; no whole-book substantive certification.','baseline':json.loads((D/'baseline.json').read_text()),'assigned_ids':IDS,'expected_ids_independently_selected_from_xml_metadata':selected,'changed_ids':changed,'commentary_ids_outside_assignment_changed':outside,'unassigned_commentaries_preserved':151,'full_book_commentary_count':len(after),'full_book_commentary_chars':sum(map(len,after.values())),'unit_checks':[{'id':i,'source_text_agrees':True,'statutory_text_sha256':hashlib.sha256(um[i]['text'].encode()).hexdigest(),'before_sha256':hashlib.sha256(before[i].encode()).hexdigest(),'after_sha256':hashlib.sha256(after[i].encode()).hexdigest(),'commentary_chars':len(after[i]),'changed':before[i]!=after[i]} for i in IDS],'duplicate_paragraphs':dup,'similar_commentary_pairs':pairs,'limitations':['Text agreement, length and similarity statistics do not establish substantive legal quality.'],'ok':True}
(D/'batch-checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
diff=[]
for i in IDS:diff+=list(difflib.unified_diff((before[i]+'\n').splitlines(True),(after[i]+'\n').splitlines(True),fromfile='before/'+i,tofile='after/'+i))
(D/'commentary-changes.diff').write_text(''.join(diff))
print(json.dumps({'coverage_ok':True,'unit_count':171,'case_blocks':len(checks),'changed_ids':changed,'unassigned_preserved':151,'duplicate_paragraphs':len(dup),'similar_pairs':len(pairs),'commentary_chars':out['full_book_commentary_chars']}))
