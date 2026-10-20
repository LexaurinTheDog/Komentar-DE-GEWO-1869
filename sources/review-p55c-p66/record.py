"""Record the actual bounded legal review and preserve earlier review evidence."""
from pathlib import Path
import datetime,hashlib,json,re,xml.etree.ElementTree as E
D=Path(__file__).resolve().parent;W=D.parent.parent
def read(p):return json.loads((W/p).read_text())
def save(p,obj):(W/p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
checks=read('sources/review-p55c-p66/batch-checks.json');ids=checks['assigned_ids']
coverage=read('coverage-report.json');caps=read('sources/review-p55c-p66/captures.json')
assert checks['ok'] and coverage['complete'] and all(c['http_status']==200 and c['format_valid'] for c in caps)
findings_text={
'p55c':'Beginnanzeige nur für § 55a Abs. 1 Nr. 3, 9, 10 und subsidiär zur Anmeldung nach § 14 geprüft. Entsprechende Änderungs-/Abmelderegeln, Verlegungsübermittlung und Dreitages-Empfangsbescheinigung erläutert; keine Erlaubniswirkung. Künftige Datenempfänger nicht vorgezogen. Beispiel und § 4-Nichtanwendung geprüft.',
'p55d':'Amtlicher Strich als leerer Nummernplatz, weder Pflicht noch Ausnahme. Wortlaut und knappe Erläuterung unverändert erhalten; keine historische Ersatzregel eingefügt.',
'p55e':'Abs. 1 erfasst § 55 Abs. 1 Nr. 1 mit Warenfeilbieten- und Gastgewerbeausnahme, auch unselbständige Ausübung; § 55b-Ausnahme gerade nur für Selbständige. Abs. 2 Behördenausnahme und fortbestehende externe Feiertagsfragen richtig getrennt. Vorhandene Erläuterung und Beispiel erhalten.',
'p55f':'Verordnungsermächtigung mit Bundesratszustimmung für besonders gefährliche Schaustellertätigkeiten nach § 55 Abs. 1 Nr. 2 geprüft. Keine unmittelbare Versicherungssumme oder bereits aus dem Ermächtigungstext allein folgende Abschlussmodalität behauptet. Konkrete Fachverordnung nicht Gegenstand dieses Reviews; vorhandener Text erhalten.',
'p56':'Verbotskatalog nach Vertrieb, Feilbieten, Ankauf und Vermittlung aufgeschlüsselt. Pflanzenschutz-/Schädlings-/Holzschutz-Bestellgrenze, medizinische Waren, Lotterien, Prämienvertrieb, getrennte Silberausnahmen, Alkohol und Nr. 6 erläutert. Abs. 4 nur für drei bestimmte Katalogpositionen; B2B-Ausnahme des Abs. 3 davon getrennt. Wegfallpositionen vollständig.',
'p56a':'Alle sieben Absätze und Listen geprüft. Öffentliche Werbung und organisierte Beförderung für Anzeige kumulativ; Abs. 4 gerade nicht auf Busfahrten beschränkt. Leitung, Produktverbote und ihre B2B-Ausnahme nach eigenem Verweis getrennt. § 4 nur partiell. Ältere Fundstelle mit anderem Wanderlagerbegriff nicht als Stichtagsautorität übernommen.',
'p57':'Gebundene Kartenversagung von Ermessensuntersagung nach § 59 getrennt. Tatsachenprognose und branchenspezifische Versagungsgründe erläutert; Versteigerung und § 4 separat. Bisheriges Finanzvermittlerbeispiel wegen vorher zu prüfender Kartenfreiheit durch gewöhnlichen Warenvertrieb ersetzt. Art. 7 Nr. 8/Art. 16 BGBl. 139 erst ab 20.11.2026.',
'p57a-und-58':'Gemeinsamer Wegfallvermerk einschließlich amtlichem (XXXX)-Präfix gegen XML geprüft. Keine historische Aufhebungs- oder Versagungsregel als aktuell rekonstruiert. Erläuterung erhalten.',
'p59':'Ermessen, begrenzte Übernahme des § 35 Abs. 1 Satz 2 und 3, Abs. 3, 4, 6, 7a, 8 konkret erläutert. Erweiterte Prognose, Behördenbeteiligung und Vorrang besonderer Regeln unterschieden. Wiedergestattung nur auf Antrag; vor einem Jahr besondere Gründe, kein automatischer Neustart. Beispiel geprüft.',
'p60':'Beschäftigungsverbot richtet sich an Gewerbetreibenden und erfordert tätigkeitsbezogene Unzuverlässigkeit der einzelnen beschäftigten Person. Keine automatische Gesamtbetriebsschließung; Ermessen und fiktiver Betrugsfall tragfähig. Vorhandene Erläuterung erhalten.',
'p60a':'Abs. 2 Satz 1 verweist nur auf Bauartregel, nicht unterschiedslos gesamten § 33c. LKA-Bescheinigung oder Abdruck und jeweilige örtliche Spielerlaubnis getrennt. Übernommene Aufhebungsregeln, Abs. 3 Spielhalle und Abs. 4 Verfahrensverordnung geprüft. Keine allgemeine Geldspielgeräte-Erlaubnis aus Warengeräteregel abgeleitet.',
'p60b':'Definitionsmerkmale, selektive Verweisung auf § 68a und § 69 Abs. 1/2 sowie §§ 69a–71a, Fortgeltung der Reisegewerbe-/Branchenvorgaben geprüft. BVerwG 8 B 31.11 vollständig amtlich gelesen. Auswahlgrenzen aus Rn. 5–6, 9 verwendet; gesetzliche Übertragung auf Volksfest ausdrücklich von gerichtlichem Marktfall unterschieden.',
'p60c':'Mitführ-, Vorlage- und Einstellungsanordnung nach Abs. 1 unterschieden. Kundenkontakt als Aushändigungsmerkmal des Abs. 2; für Nachweisinhaber nur Satz 1 ausdrücklich verwiesen. Sonstige glaubhaft machende Unterlage nach Abs. 3 nicht mit beglaubigter Kartenkopie gleichgesetzt. Beispiel zweier Teams konkretisiert.',
'p60d':'Eingriffskatalog, Ermessen und Abgrenzung zu § 59 geprüft. Amtlicher Verweis auf nicht mehr vorhandenen § 56 Abs. 3 Satz 2 weiterhin offen ausgewiesen; kein Eingriff durch erfundene Ersatznorm. Beispiel beruht auf tatsächlich bestehendem § 56 Abs. 1. Erläuterung erhalten.',
'p61':'Gewöhnlicher Aufenthalt für aufgezählte Karten-/Personenverfahren und Weiterführung nach Umzug nur mit Zustimmung geprüft. Keine Gesamtzuständigkeit am Verkaufsort oder für Spielortgenehmigungen behauptet. Beispiel und bestehende Erläuterung erhalten.',
'p61a':'§ 29 entsprechend mit Grenzen, branchenspezifischer Absatz-/Satzkatalog und örtlich begrenzte Ausnahme für verderbliche Versteigerungsware geprüft. Verwalterweiterbildung seit Juli 2026 von entfallener Maklerweiterbildung getrennt. Art. 7 Nr. 9/Art. 16 BGBl. 139 erst ab 20.11.2026. Keine vorgezogene neue Darlehensvermittlerpflicht.',
'p62-und-63':'Gemeinsame Wegfallstelle und Übergang zur Veranstaltungstypologie geprüft. Reisegewerbe-Prüfliste behandelt Bestellung, Ausnahme, Anzeige, Verbote, Wanderlager, Beschäftigtennachweise und Branchenpflichten konkret. Text erhalten.',
'p64':'Abs. 1 zeitlich begrenzt, grundsätzlich wiederkehrend, Vielzahl, wesentlicher Branchenumfang und überwiegender Mustervertrieb an genannten Abnehmerkreis; Abs. 2 eingeschränkter Letztverbraucherkauf. Ungenaue Formulierung „mehrere“ an gesetzliche „Vielzahl“ angepasst; übriger Text samt Beispiel erhalten.',
'p65':'Zeitliche Begrenzung zuvor nicht eigens erläutert und nun ausdrücklich ergänzt. Vielzahl, repräsentativer Branchen-/Gebietsbezug und Informationsalternative ohne sofortigen Verkauf geprüft. Keine Wiederkehr- oder Fachpublikumspflicht hineingelesen. Beispiel erhalten.',
'p66':'Vielzahl und im Wesentlichen geschäftlicher Abnehmerkreis, offener Warenumfang und Unterschied zu zeitlich begrenzten Veranstaltungstypen geprüft. „Mehrere“ zu „Vielzahl“ präzisiert; keine feste Mindestzahl erfunden. Beispiel und sachbezogene Anforderungen erhalten.'}
limitations=[
'Independent substantive review covers exactly these 20 assigned units. Earlier batches are preserved, not rereviewed. No whole-book completion or external professional approval.',
'Case-law research is selective: one additional decision read in full on official court HTML and matched to official XML/local corpus. No sufficiently relevant additional full-text-verified case selected for the other assigned units; no absence claim.',
'No comprehensive audit of Land law, implementing regulations, EU medical-device definitions or all external banking and civil-law rules. No unverified external detail values are supplied.',
'Targeted actuality/commencement checks, not an audit of every gazette issue. Original decisive date remains 2026-10-19; source recheck occurred 2026-10-20.',
'The official dangling reference in § 60d is disclosed and cannot itself supply a missing substantive rule. Technical validation and prose diagnostics do not establish legal quality.'
]
version=[
{'source':'sources/review-p55c-p66/BJNR002450869.xml','location':'framework standangabe, compared with current official HTML','effect':'Latest incorporated amendment Art. 1 G v. 20.7.2026 I Nr. 215; byte-identical to original canonical XML. Build/fetch date not used as commencement proof.'},
{'source':'sources/review-p55c-p66/amendment-139.pdf','location':'Art. 7 Nr. 8 and 9; Art. 16 Abs. 1 and Abs. 2 Nr. 2; gazette 18.05.2026','effect':'New § 57 Abs. 2 and § 61a Abs. 2 sentence only from 2026-11-20; excluded. Earlier commencement of § 34l alone does not advance them.'},
{'source':'sources/review-p55c-p66/amendment-215.pdf','location':'Art. 1 Nr. 3, Art. 11 Abs. 1; gazette 23.07.2026','effect':'§ 34c Abs. 2a administrator-only training from 2026-07-24, relevant through § 61a. Estate-agent training removed.'},
{'source':'sources/review-p55c-p66/amendment-215.pdf','location':'Art. 1 Nr. 2; Art. 11 Abs. 2','effect':'Additional § 14 Abs. 8 recipients only 2027-05-01; excluded, also from § 55c corresponding application.'}
]
pre={'complete':True,'decisive_date':'2026-10-19','official_url':'https://www.gesetze-im-internet.de/gewo/','verified_at':now,
'captures':'sources/review-p55c-p66/captures.json','raw_xml':'sources/review-p55c-p66/BJNR002450869.xml','raw_xml_sha256':hashlib.sha256((D/'BJNR002450869.xml').read_bytes()).hexdigest(),
'fresh_xml_identical_to_canonical':checks['fresh_xml_identical'],'version_evidence':version,
'historical_versions_checked':coverage['historical_versions_checked'],'annexes_checked':coverage['annex_disposition'],'eingangsformel_checked':coverage['eingangsformel'],
'coverage':{'expected':coverage['expected_count'],'parsed':coverage['parsed_count'],'all_xml_records':coverage['xml_record_count'],'missing':coverage['missing_labels'],'extra':coverage['extra_labels'],'duplicates':coverage['duplicate_source_doknr'],'unclassified_operative_records':coverage['unclassified_operative_records'],'report':'coverage-report.json'},
'intake_change_map':'sources/change-map.json','intake_operatively_changed_units':read('sources/change-map.json')['changed_count'],
'unresolved_blockers':[],'scope':'Source/parser preflight and exactly assigned commentary units; no substantive rereview of other units.'}
save('sources/review-p55c-p66/preflight.json',pre)
p=read('preflight-result.json');p['verified_at']=now;p['bounded_review_p55c_p66_source_recheck']=pre;save('preflight-result.json',p)
v=read('sources/verification.json');v['verified_at']=now;v['bounded_review_p55c_p66']=pre;save('sources/verification.json',v)
review={'kind':'review','complete':True,'decisive_date':'2026-10-19','verified_at':now,'units_reviewed':len(ids),'reviewed_ids':ids,
'changed_ids':checks['changed_ids'],'retained_ids':checks['unchanged_assigned_ids'],'unresolved_blockers':[],
'findings':[{'id':i,'disposition':'corrected' if i in checks['changed_ids'] else 'retained_after_review','review':findings_text[i]} for i in ids],
'limitations':limitations,'prior_batch_record':'sources/review-p55c-p66/before-review-result.json',
'evidence':{'preflight':'sources/review-p55c-p66/preflight.json','captures':'sources/review-p55c-p66/captures.json','preservation':'sources/review-p55c-p66/batch-checks.json','diff':'sources/review-p55c-p66/commentary-changes.diff','case_card':'cases/bverwg-8b31-11.md','case_comparison':'sources/review-p55c-p66/case-corpus-comparison.json','search_log':'sources/review-p55c-p66/search-log.json'},
'unassigned_commentaries_preserved':151,'whole_book_completion_claimed':False}
save('review-result.json',review)
s=read('status.json');s['updated_at']=now;s['stage']='bounded_review_complete';s['commentary_chars']=checks['full_book_commentary_chars'];s['source_checks']['bounded_review_p55c_p66']=pre
s['active_task']={'kind':'review','complete':True,'units_reviewed':20,'reviewed_ids':ids,'evidence':'review-result.json','whole_book_completion_claimed':False}
s['completed_units_provenance']='171 pre-existing authored comments; this process reviewed exactly 20, changed 12, preserved 151 others. Earlier 80 reviewed units not rereviewed; cumulative 100/171.'
ir=s['independent_review'];ir['reviewed_ids']=list(dict.fromkeys(ir['reviewed_ids']+ids));ir['units_reviewed']=len(ir['reviewed_ids']);ir['latest_batch_units_reviewed']=20;ir['latest_batch_reviewed_ids']=ids;ir['remaining_units']=171-ir['units_reviewed'];ir['state']='Five documented bounded batches; this process reviewed only the latest assigned 20.';ir['prior_batch_record']='sources/review-p55c-p66/before-review-result.json'
assert ir['units_reviewed']==100 and ir['remaining_units']==71
s['remaining_limitations']=limitations
case={'court':'BVerwG','date':'2011-06-24','docket':'8 B 31.11','ecli':'ECLI:DE:BVerwG:2011:240611B8B31.11.0','units':['p60b'],'all_paragraphs_read':'1–10 and tenor','paragraphs_used':[5,6,9],'card':'cases/bverwg-8b31-11.md'}
if not any(c['docket']==case['docket'] for c in s['case_law_sources']):s['case_law_sources'].append(case)
save('status.json',s)
cc=read('sources/case-coverage.json')
for u in cc['units']:
 if u['id'] in ids:
  u['latest_review_disposition']='Reviewed 2026-10-20; no additional sufficiently relevant fully verified case selected in bounded research. No absence claim.'
  if u['id']=='p60b':u['verified_cases']=['cases/bverwg-8b31-11.md'];u['latest_review_disposition']='Official full text read Rn. 1–10 and tenor; statutory transfer from market selection rule to Volksfest expressly identified.'
save('sources/case-coverage.json',cc)
queries=[
('site.bverwg.de GewO Ausstellung 65 repräsentativ Messe','No directly pertinent primary decision selected; statutory definition used.'),
('site.bverwg.de "56a" "Wanderlager"','Older 1965 I C 108.63 surfaced through secondary host; not used as authority. Its reported limitation to existing goods conflicts with current express order-taking alternatives; no historical holding imported.'),
('site.bverwg.de "60b" "Volksfest"','Official 8 B 31.11 court page located; full text then separately captured and read.'),
('site.recht.bund.de "Gewerbeordnung" "Oktober" "2026"','Current official consolidation/gazette context; no later amendment of assigned units established. Austrian GewO results excluded.'),
('site.bverwg.de "8 B 31.11"','Official court page and PDF located; court HTML and RII XML used, not search snippets.'),
('site.bverwg.de "65 GewO" "repräsentativ"','No sufficiently relevant additional full-text authority selected.')]
save('sources/review-p55c-p66/search-log.json',{'searched_at':now,'queries':[{'query':q,'disposition':d} for q,d in queries],
'firecrawl':{'status_evidence':'sources/review-p55c-p66/firecrawl-status.txt','available_credits':0,'fallback':'No install/settings/auth changes; native web discovery and direct official HTTP captures.'},
'local_corpus':{'root':'/Volumes/LaCie/law-intake/eu/de/rii','commands':['rg -l § 65 / § 60b / § 56a over *.md','rg -l 8 B 31.11 / 8 B 31/11 over *.md'],'selection':'rii-wbre410017920.md fully read, snapshotted, and compared with original RII XML; tenors and Rn. 10 additionally from official court HTML.'},
'primary_case_urls':['https://www.bverwg.de/240611B8B31.11.0','https://www.rechtsprechung-im-internet.de/jportal/docs/bsjrs/jb-WBRE410017920.zip'],
'limits':limitations})
print('Recorded',len(ids),'reviewed units; cumulative',ir['units_reviewed'])
