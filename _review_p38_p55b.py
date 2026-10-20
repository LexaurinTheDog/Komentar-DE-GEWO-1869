#!/usr/bin/env python3
"""Reproduce technical evidence for exactly the assigned p38–p55b review.

Substantive legal review is documented separately; this script cannot perform it.
"""
from pathlib import Path
import collections,difflib,hashlib,json,re,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent;D=W/'sources/review-p38-p55b'
IDS=['p38', 'p39', 'p39a', 'p40', 'p41', 'p41a-und-41b', 'p42', 'p42a-bis-44a', 'p45', 'p46', 'p47', 'p48', 'p49', 'p50', 'p51', 'p52', 'p53-bis-54', 'p55', 'p55a', 'p55b']
def blocks(s):return {i:t.strip() for i,t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',s,re.M|re.S)}
def sha(b):return hashlib.sha256(b).hexdigest()
def compact(s):return re.sub(r'\s+','',s)
before={};after={}
for p in sorted((W/'commentary').glob('*.md')):
 before.update(blocks((D/'baseline-commentary'/p.name).read_text()));after.update(blocks(p.read_text()))
units={u['id']:u for u in map(json.loads,(W/'units.jsonl').read_text().splitlines())}
expected=[];checks=[]
for n in ET.parse(D/'BJNR002450869.xml').getroot().findall('norm'):
 label=n.findtext('metadaten/enbez','');i='p'+label.replace('(XXXX) ','').replace('§','').strip().replace(' ','-')
 if i not in IDS:continue
 expected.append(i);content=n.find('textdaten/text/Content');raw=''.join(content.itertext()) if content is not None else ''
 raw=raw.split('-----',1)[0].strip()
 for note in n.findall('textdaten/text/Content/P/noindex'):raw=raw.replace(''.join(note.itertext()),'',1).lstrip()
 if not raw:raw=n.findtext('metadaten/titel','')
 u=units[i]
 checks.append({'id':i,'label':label,'official_doknr':n.get('doknr'),'statutory_text_agrees':compact(raw)==compact(u['text']),'statutory_text_sha256':sha(u['text'].encode()),'commentary_before_sha256':sha(before[i].encode()),'commentary_after_sha256':sha(after[i].encode()),'commentary_chars':len(after[i]),'changed':before[i]!=after[i]})
changed=[i for i in after if before.get(i)!=after[i]];outside=sorted(set(changed)-set(IDS));paras=collections.defaultdict(set)
for i,t in after.items():
 for p in t.split('\n\n'):
  if len(p)>160:paras[p].add(i)
duplicates=[{'ids':sorted(ids),'sha256':sha(p.encode())} for p,ids in paras.items() if len(ids)>1 and ids.intersection(IDS)]
diff=[]
for i in IDS:diff+=list(difflib.unified_diff((before[i]+'\n').splitlines(True),(after[i]+'\n').splitlines(True),fromfile='before/'+i,tofile='after/'+i))
(D/'commentary-changes.diff').write_text(''.join(diff))
r={'scope':'Technical evidence for exactly 20 assigned manually reviewed units; no whole-book substantive certification.','baseline':json.loads((D/'baseline.json').read_text()),'assigned_ids':IDS,'expected_ids_independently_selected_from_xml_metadata':expected,'missing':sorted(set(IDS)-set(expected)),'duplicate_expected_ids':[i for i,c in collections.Counter(expected).items() if c>1],'raw_xml':'sources/review-p38-p55b/BJNR002450869.xml','raw_xml_sha256':sha((D/'BJNR002450869.xml').read_bytes()),'fresh_xml_agrees_with_canonical_source':(D/'BJNR002450869.xml').read_bytes()==(W/'sources/BJNR002450869.xml').read_bytes(),'unit_checks':checks,'changed_ids':changed,'commentary_ids_outside_assignment_changed':outside,'unassigned_commentaries_preserved':len(set(after)-set(IDS)),'duplicate_commentary_paragraphs_involving_assigned_units':duplicates,'full_book_commentary_count':len(after),'full_book_commentary_chars':sum(map(len,after.values())),'limitations':['Counts, hashes and duplication diagnostics do not certify legal quality. See review-result.json for manual findings.']}
r['ok']=expected==IDS and all(c['statutory_text_agrees'] for c in checks) and not outside and not duplicates and set(before)==set(after) and r['fresh_xml_agrees_with_canonical_source']
(D/'batch-checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['changed_ids','unassigned_commentaries_preserved','full_book_commentary_count','full_book_commentary_chars','ok']}));raise SystemExit(0 if r['ok'] else 1)
