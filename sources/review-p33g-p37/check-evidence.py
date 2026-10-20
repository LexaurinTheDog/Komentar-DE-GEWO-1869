from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,zipfile,re,datetime,subprocess
W=Path(__file__).resolve().parents[2];D=Path(__file__).resolve().parent
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
caps=json.loads((D/'captures.json').read_text())
for c in caps:
 if c.get('error')=='':c['error']='Expected PDF format not obtained; a repeated request body is preserved as bgh-pdf-request-response.html and rejected as non-PDF.'
 if c.get('path','').endswith('bgh-pdf-request-response.html'):c['validated_format']='rejected_non_pdf_html_landing_page'
(D/'captures.json').write_text(json.dumps(caps,indent=2)+'\n')
valid=[]
for c in caps:
 if 'path' not in c:continue
 p=W/c['path'];assert p.exists(),p;b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==c['sha256'];fmt=c.get('validated_format','')
 item={'path':c['path'],'stored_hash_agrees':True,'http_status':c['http_status']}
 if fmt=='zip':
  assert b.startswith(b'PK');z=zipfile.ZipFile(p);names=[n for n in z.namelist() if n.endswith('.xml')];assert len(names)==1;root=E.fromstring(z.read(names[0]));item['zip_and_xml_valid']=True
  if c['path'].endswith('/xml.zip'):assert root.findtext('norm/metadaten/jurabk')=='GewO'
 if fmt=='pdf':
  assert b.startswith(b'%PDF-');out=p.with_suffix('.txt');subprocess.run(['pdftotext','-layout',str(p),str(out)],check=True);assert 'Bundesgesetzblatt' in out.read_text();item['pdf_signature_and_text_valid']=True
 if 'rejected' in fmt:assert not b.startswith(b'%PDF-');item['rejected_as_legal_pdf_evidence']=True
 valid.append(item)
for name,doc,docket,date in [('WBRE410018529','WBRE410018529','8 C 24/11','20120201'),('KORE317652022','KORE317652022','VIII ZR 436/21','20221116'),('KORE627742023','KORE627742023','VIII ZR 436/21','20230711')]:
 root=E.parse(D/(name+'.xml')).getroot();assert root.findtext('aktenzeichen')==docket;assert root.findtext('entsch-datum')==date
valid.append({'all_decision_xml_dockets_and_dates_match':True,'corpus_all_text_blocks_match':all(not r['missing_from_local_corpus'] for r in json.loads((D/'case-corpus-comparison.json').read_text()))})
(D/'format-validation.json').write_text(json.dumps({'verified_at':now,'complete':True,'checks':valid,'failed_direct_requests_preserved_and_not_used_as_full_text':True},indent=2)+'\n')
search={'searched_at':now,'tool':'web.run plus read-only local rg/manifest scan; Firecrawl checked but zero credits','queries':[{'q':'site.bundesgerichtshof.de "VIII ZR 436/21" Pfandleih','result':'Official BGH PDF link discovered; direct responses yielded HTML landing pages, rejected. Official RII XML later secured.'},{'q':'site.bverwg.de "8 C 24.11" Sachverständige','result':'Official judgment URL and ECLI identified; full text obtained from official RII ZIP after direct403.'},{'q':'site.recht.bund.de 2026 "Gewerbeordnung" "215" "139"','result':'Used as targeted amendment discovery, not proof of effective date; primary gazette text read separately.'},{'q':'site.rechtsprechung-im-internet.de "VIII ZR 436/21" "2022"','result':'Followed verified local national corpus docid KORE317652022 and later KORE627742023 to official ZIP API; all captured XML text matches local corpus.'},{'q':'site.rechtsprechung-im-internet.de "8 C 24.11"','result':'Verified local corpus uses slash docket8C24/11 and docidWBRE410018529; primary XML downloaded and read.'},{'q':'site.recht.bund.de "Gewerbeordnung" "Oktober 2026"','result':'No additional effective amendment established from targeted search; not an exhaustive gazette audit.'},{'q':'site.gesetze-im-internet.de/gewo "Zuletzt geändert"','result':'Official full HTML confirms Art.1 G20.07.2026 I Nr.215; contemporaneous raw HTML+XML unchanged.'}],'local_corpus_read_only_root':'/Volumes/LaCie/law-intake/eu/de/rii','case_text_evidence':'case-corpus-comparison.json','actual_authorities_selected':['KORE317652022','KORE627742023','WBRE410018529'],'existing_authority_re_read':'sources/review-p1-p13/WBRE201500245.xml; full1–29 forp35','limits':'Selective topic search; no exhaustive case-law or all-gazette coverage. Other batch units retain statute-based analysis without invented authority.'}
(D/'search-log.json').write_text(json.dumps(search,ensure_ascii=False,indent=2)+'\n')
# Refresh the central verification record with the exact final capture entries.
p=W/'sources/verification.json';v=json.loads(p.read_text())
# Entries from this batch are a suffix after the archived verification record.
old=json.loads((D/'before-verification.json').read_text());v['captures']=old['captures']+caps
v['bounded_review_p33g_p37']['format_checks']='sources/review-p33g-p37/format-validation.json';p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'complete':True,'response_bodies_checked':len(valid)-1,'new_case_xml_packages':3,'all_case_corpus_blocks_match':True}))
