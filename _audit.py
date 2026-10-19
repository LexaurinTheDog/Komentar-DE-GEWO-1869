"""Independent inventory, text preservation, intake change map and prose diagnostics."""
from pathlib import Path
import json,re,xml.etree.ElementTree as E,hashlib,collections,html,itertools,difflib,importlib.util
W=Path(__file__).resolve().parent
U=[json.loads(l) for l in (W/'units.jsonl').read_text().splitlines()];X=E.parse(W/'sources/BJNR002450869.xml').getroot();C={};duplicate_com=[]
for p in sorted((W/'commentary').glob('*.md')):
 for id,t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',p.read_text(),re.M|re.S):
  if id in C:duplicate_com.append(id)
  C[id]=t.strip()
def compact(t):return re.sub(r'\s+','',t)
# Independent raw text comparison: parser output + relocated notes vs all Content characters.
text_checks=[]
for u in U:
 n=next(n for n in X.findall('norm') if n.get('doknr')==u['official_doknr']);content=n.find('textdaten/text/Content');raw=''.join(content.itertext()) if content is not None else ''
 if not raw.strip():raw=n.findtext('metadaten/titel','')
 primary=raw.split('-----',1)[0].strip()
 for note in n.findall('textdaten/text/Content/P/noindex'):
  primary=primary.replace(''.join(note.itertext()),'',1).lstrip()
 text_checks.append({'id':u['id'],'agreement_without_layout_whitespace':compact(primary)==compact(u['text'])})
htmlraw=(W/'sources/gewo-full.html').read_bytes().decode('iso-8859-1')
html_ids=re.findall(r'<div class="jnnorm" id="([^"]+)" title="Einzelnorm">',htmlraw)
toc=[n.get('doknr') for n in X.findall('norm') if n.findtext('metadaten/enbez')=='Inhaltsübersicht'];html_expected=[i for i in html_ids if i not in toc]
source=(W/'sources/intake-20261001.md').read_text();entries=[]
# Boundaries include structural headings; label matching prefers longest official label.
blocks=re.split(r'(?m)^#{3,4} ',source)[1:];old={}
for b in blocks:
 head,_,body=b.partition('\n');h=head.replace('(XXXX) ','')
 for u in sorted(U,key=lambda v:len(v['label']),reverse=True):
  if h.startswith(u['label']) and (len(h)==len(u['label']) or h[len(u['label'])].isspace()):old[u['id']]=(head,body.strip());break
for u in U:
 v=old.get(u['id']);oldtxt=v[1] if v else '';oldtxt=re.split(r'(?m)^Fußnote:',oldtxt)[0].strip()
 # Empty repeal text often only appears in heading in intake.
 if not oldtxt and v and '(weggefallen)' in v[0]:oldtxt='(weggefallen)'
 oldtxt=oldtxt.split('-----',1)[0].strip()
 if u['id']=='anlage':oldtxt=re.sub(r'^\(Fundstelle:[^\n]+\)\s*','',oldtxt)
 def norm(t):return re.sub(r'\s+','',t.replace('**','').replace('\u00ad',''))
 same=norm(oldtxt)==norm(u['text'])
 entry={'id':u['id'],'label':u['label'],'intake_record_found':v is not None,'same_operative_text_ignoring_layout':same,'intake_body_sha256':hashlib.sha256(oldtxt.encode()).hexdigest(),'canonical_unit_sha256':hashlib.sha256(u['text'].encode()).hexdigest()}
 if not same:entry['diff']=''.join(difflib.unified_diff(oldtxt.splitlines(True),u['text'].splitlines(True),fromfile='intake',tofile='canonical'))
 entries.append(entry)
(W/'sources/change-map.json').write_text(json.dumps({'intake_sha256':hashlib.sha256((W/'sources/intake-20261001.md').read_bytes()).hexdigest(),'xml_sha256':hashlib.sha256((W/'sources/BJNR002450869.xml').read_bytes()).hexdigest(),'method':'Compare provision bodies independently segmented from intake headings against official XML extraction; ignore layout whitespace and relocate in-Content editorial notes. Full diffs retained for mismatches.','entries':entries,'identical_count':sum(e['same_operative_text_ignoring_layout'] for e in entries),'changed_count':sum(not e['same_operative_text_ignoring_layout'] for e in entries)},ensure_ascii=False,indent=2)+'\n')
# Exact paragraph duplication and most similar full commentary pairs, including repealed slots.
paras=collections.defaultdict(list)
for id,t in C.items():
 for p in t.split('\n\n'):
  if len(p)>160:paras[p].append(id)
dup=[{'ids':ids,'text':p} for p,ids in paras.items() if len(set(ids))>1]
pairs=[]
for (i,a),(j,b) in itertools.combinations(C.items(),2):
 if min(len(a),len(b))/max(len(a),len(b))<.65:continue
 sim=difflib.SequenceMatcher(None,a,b,autojunk=True).ratio()
 if sim>.55:pairs.append({'a':i,'b':j,'similarity':round(sim,3)})
report={'unit_count':len(U),'xml_norm_record_count':len(X.findall('norm')),'independent_html_expected_count':len(html_expected),'html_missing_from_units':sorted(set(html_expected)-{u['official_doknr'] for u in U}),'units_missing_from_html':sorted({u['official_doknr'] for u in U}-set(html_expected)),'text_checks':text_checks,'text_disagreements':[x['id'] for x in text_checks if not x['agreement_without_layout_whitespace']],'commentary_count':len(C),'commentary_chars':sum(map(len,C.values())),'missing_commentary':sorted({u['id'] for u in U}-set(C)),'extra_commentary':sorted(set(C)-{u['id'] for u in U}),'duplicate_commentary_ids':duplicate_com,'duplicate_paragraphs':dup,'similar_commentary_pairs':sorted(pairs,key=lambda x:-x['similarity']),'ordinary_units_under_700_chars':[u['id'] for u in U if len(u['text'])>160 and len(C.get(u['id'],''))<700],'checklists':sum(t.count('**Prüfliste') for t in C.values()),'annexes':[{'id':'anlage','status':'included completely; both sections and all nested points preserved'},{'name':'Anhang EV','status':'No operative XML record. Framework notes explicitly declare measures no longer applicable since 2010/2013; not reconstructed as effective law.'}],'limits':['Text comparison ignores only layout whitespace and explicitly relocated editorial notes.','Similarity and length checks are diagnostics, not proof of legal quality.','Independent substantive second pass remains pending.']}
report['ok']=not any(report[k] for k in ['html_missing_from_units','units_missing_from_html','text_disagreements','missing_commentary','extra_commentary','duplicate_commentary_ids','duplicate_paragraphs'])
(W/'audit-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['unit_count','xml_norm_record_count','independent_html_expected_count','text_disagreements','commentary_count','commentary_chars','duplicate_paragraphs','similar_commentary_pairs','ok']}))
print('Intake differences:',[e['id'] for e in entries if not e['same_operative_text_ignoring_layout']])
