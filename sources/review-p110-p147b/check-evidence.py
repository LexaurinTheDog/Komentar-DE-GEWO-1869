"""Reproducible evidence checks; legal reading is separately recorded in review findings."""
from pathlib import Path
import xml.etree.ElementTree as E
import json,re,html,hashlib,datetime,subprocess
D=Path(__file__).resolve().parent;W=D.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(t):
 t=html.unescape(t).replace('**','').replace('\u00ad','')
 t=t.translate(str.maketrans({'–':'-','—':'-','„':'"','“':'"','”':'"','’':"'",'‘':"'"}))
 return re.sub(r'\s+','',t)
corpus=(D/'rii-kare600052708.md').read_text()
source='/Volumes/LaCie/law-intake/eu/de/rii/rii-kare600052708.md'
assert sha(D/'rii-kare600052708.md')==sha(Path(source))
raw=(D/'bag-10azr448-15.html').read_text()
main=re.search(r'<main\b.*?</main>',raw,re.S).group()
text=html.unescape(re.sub('<[^>]+>',' ',main))
(D/'bag-10azr448-15-text.txt').write_text(re.sub(r'\s+',' ',text)+'\n')
paras=[]
for dt,dd in re.findall(r'<dt\b[^>]*>(.*?)</dt>\s*<dd\b[^>]*>(.*?)</dd>',main,re.S):
 rn=re.sub('<[^>]+>','',dt).strip()
 if rn.isdigit():paras.append((int(rn),html.unescape(re.sub('<[^>]+>',' ',dd))))
assert [n for n,t in paras]==list(range(1,38))
htmlmissing=[n for n,t in paras if norm(t) not in norm(corpus)]
r=E.parse(D/'jb-KARE600052708.xml').getroot()
xmlchecks=[]
for section in ['leitsatz','tenor','tatbestand','entscheidungsgruende']:
 for dd in r.findall(section+'/.//dd'):
  t=''.join(dd.itertext()).strip()
  if len(norm(t))>30:xmlchecks.append({'section':section,'text_sha256':hashlib.sha256(t.encode()).hexdigest(),'matches_corpus':norm(t) in norm(corpus)})
 for el in r.findall(section+'/p'):
  t=''.join(el.itertext()).strip()
  if len(norm(t))>30:xmlchecks.append({'section':section,'text_sha256':hashlib.sha256(t.encode()).hexdigest(),'matches_corpus':norm(t) in norm(corpus)})
case={'case':'bag-10azr448-15','all_paragraphs_read':'1–37, tenor and unnumbered contract/text continuations',
 'official_html':'sources/review-p110-p147b/bag-10azr448-15.html',
 'official_xml':'sources/review-p110-p147b/jb-KARE600052708.xml',
 'official_xml_sha256':sha(D/'jb-KARE600052708.xml'),
 'original_read_only_path':source,'snapshot_path':'sources/review-p110-p147b/rii-kare600052708.md',
 'corpus_sha256':sha(D/'rii-kare600052708.md'),'official_html_numbered_paragraphs':len(paras),
 'html_paragraphs_missing_from_corpus':htmlmissing,'xml_text_blocks':xmlchecks,
 'method':'All 37 numbered court HTML paragraphs and every long XML dd text including unnumbered continuations compared to preserved local corpus after typography/whitespace normalization. Court tenor/outcome and all text read manually.'}
assert not htmlmissing and all(c['matches_corpus'] for c in xmlchecks)
(D/'case-corpus-comparison.json').write_text(json.dumps(case,ensure_ascii=False,indent=2)+'\n')
external=[]
for filename,abk,ids in [('BJNR002190897.xml','HGB',['§ 74','§ 74a','§ 75d']),('BJNR004810968.xml','OWiG',['§ 10','§ 17']),('BJNR001950896.xml','BGB',['§ 651t','§ 651u','§ 651v','§ 651w'])]:
 root=E.parse(D/filename).getroot();allnorm=root.findall('norm');first=allnorm[0]
 selected=[]
 for label in ids:
  ns=[n for n in allnorm if n.findtext('metadaten/enbez')==label];assert len(ns)==1
  n=ns[0];el=n.find('textdaten/text/Content');t=''.join(el.itertext())
  prefix=abk.lower();number=label.replace('§ ','');h=D/(prefix+'-'+number+'.html')
  hraw=h.read_bytes().decode('iso-8859-1');htext=html.unescape(re.sub('<[^>]+>','',hraw))
  assert norm(t) in norm(htext)
  selected.append({'label':label,'doknr':n.get('doknr'),'content':t,
   'content_sha256':hashlib.sha256(t.encode()).hexdigest(),'same_html_and_xml':True,
   'unit_notes':[''.join(e.itertext()) for e in n.findall('textdaten/fussnoten/Content')]})
 external.append({'law':abk,'raw_xml':'sources/review-p110-p147b/'+filename,'sha256':sha(D/filename),
  'stand':[e.text for e in first.findall('metadaten/standangabe/standkommentar')],
  'selected_units':selected,'selection':'Single current official record per referenced unit, HTML/XML agreement; no historical duplicate appended.'})
(D/'external-provisions.json').write_text(json.dumps(external,ensure_ascii=False,indent=2)+'\n')
caps=json.loads((D/'captures.json').read_text());formats=[]
for c in caps:
 assert c['http_status']==200 and c['format_valid'];p=W/c['path'];assert sha(p)==c['sha256']
 f={'path':c['path'],'http_status':200,'sha256':sha(p),'format_valid':True}
 if p.suffix=='.pdf':
  assert p.read_bytes().startswith(b'%PDF-')
  subprocess.run(['pdftotext','-layout',str(p),str(p.with_suffix('.txt'))],check=True)
  t=p.with_suffix('.txt').read_text();assert 'Bundesgesetzblatt' in t
  f['pdf_magic']=True;f['gazette_text_recognized']=True;f['extracted_chars']=len(t)
 formats.append(f)
(D/'format-validation.json').write_text(json.dumps(formats,ensure_ascii=False,indent=2)+'\n')
assert (D/'BJNR002450869.xml').read_bytes()==(W/'sources/BJNR002450869.xml').read_bytes()
print(json.dumps({'case_html_paragraphs':len(paras),'xml_blocks_checked':len(xmlchecks),'case_corpus_agrees':True,'external_units':sum(len(x['selected_units']) for x in external),'captures_checked':len(caps),'fresh_gewo_xml_identical':True}))
