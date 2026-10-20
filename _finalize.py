"""Assemble existing ledger-reviewed GewO manuscript; never rewrite commentary."""
from pathlib import Path
import collections, datetime, hashlib, json, re, shutil, subprocess
W=Path(__file__).resolve().parent
E=W/'sources/finalization-20261020'
E.mkdir(exist_ok=True)
def read(p): return json.loads((W/p).read_text())
def put(p,d): (W/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
for name in ['README.md','REVIEW.md','SOURCES.md','00-einleitung.md','status.json','review-result.json','validation.json','sources/verification.json','sources/manifest.json','preflight-result.json','audit-report.json','link-report.json']:
 target=E/('before-'+name.replace('/','--'))
 if not target.exists(): shutil.copyfile(W/name,target)
units=[json.loads(s) for s in (W/'units.jsonl').read_text().splitlines() if s.strip()]
byid={u['id']:u for u in units};com={};dup=[]
for p in sorted((W/'commentary').glob('*.md')):
 for uid,txt in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',p.read_text(),re.M|re.S):
  if uid in com: dup.append(uid)
  com[uid]=txt.strip()
ledger=read('batch-review-ledger.json');batches=[];allids=[];checks=[];findings=[];limits=[]
for key,b in ledger['batches'].items():
 r=b['review'];ids=b['ids'];assert b['complete'] and r['complete'] and not r['unresolved_blockers']
 assert ids==r['reviewed_ids'] and r['units_reviewed']==len(ids)
 paths=[]
 def paths_in(x):
  if isinstance(x,str) and x.endswith('/batch-checks.json'): paths.append(x)
  elif isinstance(x,dict):
   for v in x.values(): paths_in(v)
 paths_in(r.get('technical_evidence')); paths_in(r.get('evidence'))
 assert len(set(paths))==1,(key,paths)
 evidence=paths[0];d=read(evidence);rows=d.get('unit_checks',d.get('per_unit',d.get('checks')))
 assert {a['id'] for a in rows}==set(ids)
 for a in rows:
  uid=a['id'];expected=next((a[k] for k in ['commentary_after_sha256','after_commentary_sha256','after_sha256','commentary_sha256'] if k in a),None)
  actual=digest(com[uid]);assert expected==actual,(uid,'commentary differs from reviewed snapshot')
  st=a.get('statutory_text_sha256',a.get('statutory_sha256'))
  if st: assert st==digest(byid[uid]['text']),(uid,'statutory text changed')
  checks.append({'id':uid,'batch':key,'evidence':evidence,'reviewed_commentary_sha256':expected,'current_commentary_sha256':actual,'statutory_text_sha256':digest(byid[uid]['text']),'matches_reviewed_text':True})
 batches.append({'key':key,'ids':ids,'units':len(ids),'verified_at':r.get('reviewed_at',r.get('verified_at')),'evidence':evidence,'evidence_sha256':sha(W/evidence),'complete':True,'unresolved_blockers':[]})
 allids+=ids
 findings += [{'batch':key,'finding':f} for f in r.get('findings',[])]
 limits += r.get('limitations',[])
assert len(allids)==len(set(allids))==len(units)==171
assert set(allids)==set(byid)==set(com) and not dup
put('sources/finalization-20261020/ledger-audit.json',{'at':now,'method':'All nine ledger records checked for completion, disjoint exact coverage, and current commentary hashes compared with each batch final hash; no new substantive review.','ledger_sha256':sha(W/'batch-review-ledger.json'),'batches':batches,'unit_checks':checks,'missing_ids':sorted(set(byid)-set(allids)),'duplicate_ids':[],'ok':True})
put('sources/finalization-20261020/manuscript-preservation.json',{'at':now,'commentary_files':{str(p.relative_to(W)):sha(p) for p in sorted((W/'commentary').glob('*.md'))},'units_sha256':sha(W/'units.jsonl'),'canonical_sha256':sha(W/'sources/gewo-canonical.md'),'method':'Finalization changes metadata and evidence only; reviewed prose retained byte-for-byte.'})
rr={'kind':'finalize_from_batch_review_ledger','complete':True,'verified_at':now,'decisive_date':'2026-10-19','units_reviewed':171,'reviewed_ids':[u['id'] for u in units],'review_provenance':'Cumulative prior nine bounded reviews; zero units substantively re-reviewed by this finalization process.','units_newly_reviewed_in_finalization':0,'batches':batches,'unresolved_blockers':[],'findings':findings,'limitations':['Finalization assembles existing reports and verifies preservation; it is not a new independent whole-book legal review.','§ 161 notices remain independently unestablished; conditional commentary preserved.','Selective case-law coverage; state law, implementing regulations and external statutes are not comprehensively reviewed.','Technical validation, minimum length and similarity metrics do not establish legal correctness.','No external professional approval, publication or upload.'],'prior_batch_limitations':limits,'whole_book_completion_claimed':False,'independent_whole_book_review_performed_by_finalizer':False,'technical_evidence':'sources/finalization-20261020/ledger-audit.json','previous_review_preserved':'sources/finalization-20261020/before-review-result.json'}
put('review-result.json',rr)
lines=['# Zusammenführung und Prüfstand','', 'Am 20. Oktober 2026 wurden die neun vorhandenen Batchberichte aus [batch-review-ledger.json](batch-review-ledger.json) dokumentarisch zusammengeführt. Sie erfassen disjunkt alle 171 Einheiten. Dieser Finalisierungsschritt hat keine Einheit erneut inhaltlich geprüft und beansprucht keine neue unabhängige Gesamtprüfung oder externe fachliche Freigabe.','', 'Die unveränderten Kommentare wurden für jede Einheit anhand des im jeweiligen Batch gespeicherten abschließenden SHA-256 geprüft. Alle 171 Hashes stimmen überein. Der [Ledger-Audit](sources/finalization-20261020/ledger-audit.json) verknüpft jede Einheit mit ihrem Bericht und Prüfnachweis. Die [kumulierten Befunde](review-result.json) enthalten die bisherigen Korrekturen und Grenzen. Frühere Arbeitsstände und der [vorherige ausführliche Prüfbericht](sources/finalization-20261020/before-REVIEW.md) bleiben erhalten.','', '| Bereich | Einheiten | Vorhandener Prüfnachweis |','|---|---:|---|']
for b in batches:
 lines.append(f"| {byid[b['ids'][0]]['display_label']} bis {byid[b['ids'][-1]]['display_label']} | {b['units']} | [Batchbericht]({b['evidence']}) |")
lines += ['', 'Die Quellen-Preflights wurden am 20. Oktober 2026 tatsächlich durchgeführt; die letzten amtlichen HTTP-Antworten, Zeitstempel, Hashes und Formatprüfungen sind im [Quellennachweis](sources/verification.json) und unter [Preflight](preflight-result.json) erhalten. Rechtsstichtag bleibt der Beginn der Autorenarbeit am 19. Oktober 2026. Dieser Zusammenführungsschritt hat keinen zusätzlichen Netzabruf als neue Rechtsstandsprüfung ausgegeben. Die amtlichen XML-Kennungen, einschließlich der 17 mit „(XXXX)“ markierten Wegfallbereiche, werden unverändert wiedergegeben. Die tatsächlich fehlende Eingangsformel wird nicht ergänzt. Die einzige operative Anlage ist mit beiden Abschnitten und allen verschachtelten Listen enthalten; Anhang EV ist im aktuellen amtlichen Bestand nicht operativ.', '', 'Die getroffenen Versionsentscheidungen beruhen auf den gespeicherten amtlichen Texten und den in den Batchberichten gelesenen Änderungs- und Inkrafttretensbestimmungen. Sie schließen insbesondere § 34k und § 162 vor dem 20. November 2026, zusätzliche Empfänger des § 14 Abs. 8 vor dem 1. Mai 2027 und die ESAP-Ergänzungen vor dem 10. Januar 2030 aus. Der [Änderungsabgleich](sources/change-map.json) bewahrt beide Quellenstände und weist den Vergleich mit dem Intake nach.', '', 'Die Rechtsprechungsauswahl umfasst dreizehn Hauptentscheidungen und einen ergänzenden Berichtigungsbeschluss. Die [Fallkarten](cases/README.md) und die [Quellenübersicht](SOURCES.md) dokumentieren Volltextbelege, Randnummern, Zuordnung und Grenzen. Die damaligen Beschränkungen, insbesondere historische Rechtslagen, offene Folgefragen, fehlende Rechtskraftnachweise und erfolglose Korpussuchen, gelten fort. Die Auswahl ist keine vollständige Rechtsprechungsübersicht.', '', 'Die beiden Bekanntmachungsauslöser des § 161 bleiben unabhängig nicht nachgewiesen. Der Kommentar stellt die betroffenen Teilfragen deshalb bedingt dar und behauptet weder Eintritt noch Nichteintritt. Das bleibt eine Anwendungsgrenze. Landesrecht, sämtliche Ausführungsverordnungen und alle externen Gesetze sind nicht Gegenstand einer umfassenden Kommentierung.', '', 'Die [separate XML-Vollständigkeitsprüfung](coverage-report.json), der [HTML-/Text-/Kommentierungsaudit](audit-report.json), die [Linkprüfung](link-report.json) und die [strikte Validierung](validation.json) werden beim abschließenden Aufbau erneut ausgeführt. Das Ergebnis wird nur technisch verstanden. Die hier vorliegende Zusammenführung ist ein lokaler, technisch validierter Entwurfscheckpoint; keine Erklärung juristischer Fehlerfreiheit oder abschließender Gesamtfreigabe.']
(W/'REVIEW.md').write_text('\n'.join(lines)+'\n')
readme=(E/'before-README.md').read_text()
start=readme.index('**Aktueller begrenzter Review')
end=readme.index('\n\nDie [amtliche Gesamtausgabe]',start)
readme=readme[:start]+'**Zusammenführung vom 20. Oktober 2026:** Neun vorhandene Batchberichte erfassen alle 171 Einheiten. Der [Ledger-Audit](sources/finalization-20261020/ledger-audit.json) bestätigt die lückenlose Zuordnung und für jede Einheit die Übereinstimmung mit dem zuletzt geprüften Kommentartext. Die [kumulierten Befunde](review-result.json) und [Prüfgrenzen](REVIEW.md) sind zusammengestellt. Dieser Schritt ist eine technische Finalisierung des Entwurfs; er führt keine erneute inhaltliche Gesamtprüfung durch und erklärt keine abschließende Gesamtfreigabe.'+readme[end:]
start=readme.index('**Status:')
end=readme.index('\n\nKommentar und eigene',start)
readme=readme[:start]+'**Status: verfasster Entwurf mit zusammengeführten Batchbelegen und technischer Validierung.** Alle 171 Kommentare sind erhalten; die vorhandenen neun Batchberichte sind kumulativ dokumentiert. Eine neue unabhängige Gesamtprüfung oder externe anwaltliche Freigabe wird nicht behauptet. Technische Vollständigkeit, Texttreue und Mindestlängen bestätigen keine juristische Fehlerfreiheit. Das Werk wird im vorhandenen Zustand bereitgestellt und ersetzt keine auf den Einzelfall bezogene Rechtsberatung.'+readme[end:]
readme=readme.replace('Im aktuellen Batch wurde','Im letzten inhaltlichen Batch wurde')
(W/'README.md').write_text(readme)
intro=(E/'before-00-einleitung.md').read_text().replace('Der vollständige Entwurf wird in begrenzten gesonderten Durchgängen inhaltlich zweitgeprüft; die jeweils wirklich geprüften Kennungen und der noch offene Restbestand stehen im Review-Bericht.','Die neun vorhandenen begrenzten inhaltlichen Zweitprüfungen sind im Review-Bericht für alle 171 Einheiten zusammengeführt. Der Finalisierungsschritt gleicht ihren Bestand und die geprüften Texthashes ab; er führt keine neue unabhängige inhaltliche Gesamtprüfung durch.')
(W/'00-einleitung.md').write_text(intro)
src=(E/'before-SOURCES.md').read_text()
(W/'SOURCES.md').write_text(src+'\n\n## Dokumentarische Zusammenführung am 20. Oktober 2026\n\n[Ledger](batch-review-ledger.json), [einheitenbezogener Hashabgleich](sources/finalization-20261020/ledger-audit.json), [kumulierte Prüfungen](review-result.json) und [Prüfbericht](REVIEW.md) führen die vorhandenen Nachweise zusammen. Kein zusätzlicher Netzabruf und keine erneute inhaltliche Prüfung werden für diesen Schritt behauptet. Die vorigen Abrufprotokolle, Quellenversionen, Fallkarten und Grenzen bleiben erhalten.\n')
ver=read('sources/verification.json')
ver['finalization']={'at':now,'method':'Assembly and integrity checking of existing primary-source evidence, not a new online verification.','latest_actual_source_verification_at':ver['verified_at'],'ledger_audit':'sources/finalization-20261020/ledger-audit.json'}
ver['case_law_scope']='Selective: thirteen main decisions and one supplementary correction, as documented in cases/README.md; assembled from prior full-text-reviewed batch evidence, not newly re-read during finalization.'
put('sources/verification.json',ver)
status=read('status.json');status.update({'stage':'drafted_technical_validation','active_task':'finalize','updated_at':now,'total_units':171,'completed_units':171,'commentary_chars':sum(map(len,com.values())),'independent_review':{'prior_batch_reviewed_units':171,'prior_batches':9,'new_substantive_review_by_finalizer':False,'whole_book_legal_completion_claimed':False,'evidence':'review-result.json'},'remaining_limitations':rr['limitations'],'finalization_evidence':'sources/finalization-20261020/ledger-audit.json','publication':'Local checkpoint only; no publication or upload.'})
put('status.json',status)
print(json.dumps({'batches':len(batches),'preserved_reviewed_units':len(checks),'commentary_chars':sum(map(len,com.values())),'ok':True}))
