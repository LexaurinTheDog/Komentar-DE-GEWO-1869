"""Reproducible technical checks for the bounded p110–p147b review.

This script records preservation and source agreement, not legal quality.
"""
from pathlib import Path
import collections,difflib,hashlib,json,re,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;W=D.parent.parent
IDS='p110 p111 p112-bis-132a p133 p133a-bis-133d p133e-bis-139aa p139b p139c-bis-139h p139i p139k-und-139m p140 p141-bis-141f p142 p143 p144 p145 p146 p147 p147a p147b'.split()
def blocks(p):return dict((i,t.strip()) for i,t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',p.read_text(),re.M|re.S))
def sha(b):return hashlib.sha256(b).hexdigest()
before={};after={}
for p in sorted((W/'commentary').glob('*.md')):
 before.update(blocks(D/'baseline-commentary'/p.name));after.update(blocks(p))
units={u['id']:u for u in map(json.loads,(W/'units.jsonl').read_text().splitlines())}
root=E.parse(D/'BJNR002450869.xml').getroot();expected=[];checks=[]
for n in root.findall('norm'):
 label=n.findtext('metadaten/enbez','')
 i='p'+label.replace('(XXXX) ','').replace('§','').strip().replace(' ','-')
 if i not in IDS:continue
 expected.append(i);el=n.find('textdaten/text/Content')
 raw=''.join(el.itertext()) if el is not None else ''
 raw=raw.split('-----',1)[0].strip()
 for note in n.findall('textdaten/text/Content/P/noindex'):raw=raw.replace(''.join(note.itertext()),'',1).lstrip()
 if not raw:raw=n.findtext('metadaten/titel','')
 checks.append({'id':i,'official_label':label,'doknr':n.attrib['doknr'],
 'statutory_text_agrees_ignoring_layout':re.sub(r'\s+','',raw)==re.sub(r'\s+','',units[i]['text']),
 'before_commentary_sha256':sha(before[i].encode()),'after_commentary_sha256':sha(after[i].encode()),
 'commentary_changed':before[i]!=after[i],'commentary_chars':len(after[i])})
changed=[i for i in before if before[i]!=after[i]]
outside=[i for i in changed if i not in IDS]
paras=collections.defaultdict(list)
for i,t in after.items():
 for p in t.split('\n\n'):
  if len(p)>160:paras[p].append(i)
duplicates=[{'ids':v,'text':k} for k,v in paras.items() if len(set(v))>1 and any(i in IDS for i in v)]
report={'assigned_ids':IDS,'official_ids_in_order':expected,'units_reviewed':len(IDS),
 'checks':checks,'changed_ids':changed,'unchanged_assigned_ids':[i for i in IDS if i not in changed],
 'unassigned_commentaries_preserved':sum(before[i]==after[i] for i in before if i not in IDS),
 'unassigned_changed_ids':outside,'missing_commentary':sorted(set(units)-set(after)),
 'duplicate_paragraphs_involving_assigned_units':duplicates,
 'full_book_commentary_chars':sum(map(len,after.values())),
 'fresh_xml_identical':(D/'BJNR002450869.xml').read_bytes()==(W/'sources/BJNR002450869.xml').read_bytes(),
 'whole_book_substantive_review_claimed':False,
 'limitations':['Preservation, hashes and text agreement do not establish legal quality. Individual legal findings are recorded in review-result.json.']}
report['ok']=expected==IDS and not outside and not duplicates and not report['missing_commentary'] and report['fresh_xml_identical'] and all(c['statutory_text_agrees_ignoring_layout'] for c in checks)
(D/'batch-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
diff=[]
for p in sorted((W/'commentary').glob('*.md')):
 diff+=difflib.unified_diff((D/'baseline-commentary'/p.name).read_text().splitlines(True),p.read_text().splitlines(True),fromfile='before/'+p.name,tofile='after/'+p.name)
(D/'commentary-changes.diff').write_text(''.join(diff))
print(json.dumps({k:report[k] for k in ['units_reviewed','changed_ids','unassigned_commentaries_preserved','unassigned_changed_ids','ok']}))
assert report['ok']
