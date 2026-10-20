"""Preserve only the actually used external norms and court text, reproducibly."""
from pathlib import Path
import datetime, hashlib, html, json, re, xml.etree.ElementTree as E
D=Path(__file__).resolve().parent; W=D.parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def compact(t): return re.sub(r'\s+', '', html.unescape(t))
def visible(s): return html.unescape(re.sub(r'<[^>]+>', '', s))
out=[]
for file,abk,label,htm,url in [
 ('BJNR002430971.xml','BZRG','§ 44a','bzrg-44a.html','https://www.gesetze-im-internet.de/bzrg/__44a.html'),
 ('BJNR088210019.xml','BewachRV','§ 14','bewachrv-14.html','https://www.gesetze-im-internet.de/bewachrv/__14.html')]:
 p=D/file;root=E.parse(p).getroot();assert root.findtext('norm/metadaten/jurabk')==abk
 ns=[n for n in root.findall('norm') if n.findtext('metadaten/enbez')==label];assert len(ns)==1
 n=ns[0];text='\n\n'.join(''.join(x.itertext()) for x in n.findall('textdaten/text/Content/P'))
 assert compact(text) in compact(visible((D/htm).read_bytes().decode('iso-8859-1')))
 out.append({'law':abk,'label':label,'official_url':url,'xml_path':str(p.relative_to(W)), 'xml_sha256':sha(p),'html_path':str((D/htm).relative_to(W)), 'html_sha256':sha(D/htm),'official_doknr':n.get('doknr'),'text':text,'html_and_xml_agree':True,'version_notes':('Art. 4 Nr. 8 and Art. 7 Abs. 2, BGBl. 2026 I Nr. 183: §44a amended effective 25 June 2026. Later Nr.199 Art15(15) only changes §41, effective 1 January 2027, not §44a.' if abk=='BZRG' else 'Original regulation of 24 June 2019, BGBl.I882; no modifying standangabe or alternative §14 in current official XML. Full current §14 and HTML agree; no claim to a separate historical consolidated edition.')})
(D/'external-provisions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
# The raw HTML is evidence only. Editorial headnotes and norm-chain metadata
# are excluded from the reusable court-only text and are never cited as holdings.
s=(D/'vg-muenchen.html').read_text();start=s.index('<h2 class="entsueber">Tenor</h2>');s=s[start:s.index('</main>',start)]
paras=[];current='Tenor';rn=None
for m in re.finditer(r'<h2 class="entsueber">(.*?)</h2>|<div class="rd">(.*?)</div>|<div class="absatz (tenor|tatbestand|gruende)">(.*?)</div>',s,re.S):
 if m.group(1):current=visible(m.group(1));rn=None
 elif m.group(2) is not None:rn=visible(m.group(2)).strip() or None
 else:paras.append({'section':current,'paragraph':rn,'text':visible(m.group(4)).strip()})
assert [x['paragraph'] for x in paras if x['paragraph']]==list(map(str,range(1,33)))
assert len([x for x in paras if x['section']=='Tenor'])==3
(D/'vg-muenchen-court-text.json').write_text(json.dumps(paras,ensure_ascii=False,indent=2)+'\n')
(D/'vg-muenchen.txt').write_text('\n\n'.join((('Rn. '+x['paragraph']+'\n') if x['paragraph'] else '')+x['text'] for x in paras)+'\n')
(D/'case-evidence.json').write_text(json.dumps({'court':'VG München','date':'2022-05-05','docket':'M 16 K 21.4969','ecli':None,'ecli_note':'No ECLI identified on the official page; none invented.','official_url':'https://www.gesetze-bayern.de/Content/Document/Y-300-Z-BECKRS-B-2022-N-39302','raw_html':str((D/'vg-muenchen.html').relative_to(W)),'raw_sha256':sha(D/'vg-muenchen.html'),'court_only_text':str((D/'vg-muenchen.txt').relative_to(W)),'court_only_sha256':sha(D/'vg-muenchen.txt'),'read':'Tenor I–III, full Tatbestand Rn1–13, complete Entscheidungsgründe Rn14–32','relied_on_paragraphs':[18,19,20,21,22,23,24,25],'editorial_headnotes_used':False,'local_corpus_match':False,'local_search':'sources/review-p154-anlage/corpus-search.json','current_law_comparison':'§160 remains unchanged in fresh official XML; no conflicting historical alternative. §34i current source checked as context; no present rule derived from editorial §34a typo.','limits':['First-instance judgment; no independently established finality or appellate outcome.','Published editorial headnotes and the erroneous §34a reference in Rn28 do not supply commentary propositions.','EU directive and ImmVermV details reported by the court are context, not independently adopted as a comprehensive current account.']},ensure_ascii=False,indent=2)+'\n')
checks=[]
for row in json.loads((D/'captures.json').read_text()):
 p=W/row['path']
 if row.get('validated_format')=='zip':
  import zipfile
  z=zipfile.ZipFile(p);xmls=[n for n in z.namelist() if n.endswith('.xml')];assert len(xmls)==1
  r=E.fromstring(z.read(xmls[0]));abk=r.findtext('norm/metadaten/jurabk');expected={'gewo.zip':'GewO','bzrg.zip':'BZRG','bewachrv.zip':'BewachRV'}[p.name];assert abk==expected
  checks.append({'file':str(p.relative_to(W)),'check':'ZIP magic, one parseable statute XML, correct jurabk','expected':expected,'actual':abk,'ok':True})
 elif row.get('validated_format')=='pdf':
  t=p.with_suffix('.txt').read_text();assert 'Bundesgesetzblatt' in t and len(t)>500
  checks.append({'file':str(p.relative_to(W)),'check':'PDF magic and pdftotext contains Bundesgesetzblatt and substantial enactment text','ok':True})
 elif row.get('validated_format')=='html':
  b=p.read_bytes();assert b'<html' in b[:10000].lower()
  expected={'index.html':b'Gewerbeordnung','full.html':b'Gewerbeordnung','aktudienst.html':b'Aktualit','bzrg-44a.html':b'Zeugenschutz','bewachrv-14.html':b'Protokoll','vg-muenchen.html':b'M 16 K 21.4969'}[p.name];assert expected in b
  checks.append({'file':str(p.relative_to(W)),'check':'HTML with expected statute/court identity; no CAPTCHA/challenge accepted','ok':True})
 else:checks.append({'file':row['path'],'check':'Request failure, not used as evidence','ok':False,'http_status':row.get('http_status'),'error':row.get('error')})
(D/'format-validation.json').write_text(json.dumps({'usable_sources_validated':True,'checks':checks,'failed_request_disposition':'Nonexistent BZRG44b page returned404 and is not relied on; actual referral is44a.'},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'external_provisions':len(out),'court_numbered_paragraphs':32,'usable_formats_checked':sum(x['ok'] for x in checks)}))
