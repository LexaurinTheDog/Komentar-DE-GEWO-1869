"""Record the human-readable and exact machine scope of this bounded review."""
from pathlib import Path
import collections,datetime,difflib,hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;W=D.parents[1]
IDS=['p154','p154a','p155','p155a','p156','p157','p158','p159','p160','p161','anlage']
def save(p,x): (W/p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load(p): return json.loads((W/p).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def blocks(p): return dict((i,t.strip()) for i,t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)',p.read_text(),re.M|re.S))
before={};after={}
for p in sorted((W/'commentary').glob('*.md')):before.update(blocks(D/'baseline-commentary'/p.name));after.update(blocks(p))
assert len(before)==len(after)==171
changed=[i for i in IDS if before[i]!=after[i]];outside=[i for i in after if i not in IDS and before[i]!=after[i]];assert not outside
assert sha(W/'units.jsonl')==load('sources/review-p154-anlage/baseline.json')['units_sha256']
paras=collections.defaultdict(set)
for i,t in after.items():
 for q in t.split('\n\n'):
  if len(q)>160:paras[q].add(i)
dups=[{'ids':sorted(v),'sha256':hashlib.sha256(q.encode()).hexdigest()} for q,v in paras.items() if len(v)>1 and v.intersection(IDS)]
pairs=[]
for i in IDS:
 for j in after:
  if i>=j:continue
  ratio=difflib.SequenceMatcher(None,after[i],after[j],autojunk=True).ratio()
  if ratio>.55:pairs.append({'a':i,'b':j,'similarity':ratio})
assert not dups and not pairs
um={u['id']:u for u in [json.loads(x) for x in (W/'units.jsonl').read_text().splitlines()]}
checks={'assigned_ids':IDS,'changed_ids':changed,'retained_ids':[i for i in IDS if i not in changed],'unassigned_commentaries_preserved':160,'commentary_ids_outside_assignment_changed':outside,'full_book_commentary_count':len(after),'full_book_commentary_chars':sum(map(len,after.values())),'statutory_units_unchanged':True,'unit_checks':[{'id':i,'statutory_text_sha256':hashlib.sha256(um[i]['text'].encode()).hexdigest(),'before_sha256':hashlib.sha256(before[i].encode()).hexdigest(),'after_sha256':hashlib.sha256(after[i].encode()).hexdigest(),'commentary_chars':len(after[i]),'changed':before[i]!=after[i]} for i in IDS],'duplicate_paragraphs':dups,'similar_commentary_pairs':pairs,'limitations':['Text, count, length and similarity diagnostics are not a legal-quality certificate.'],'ok':True}
save('sources/review-p154-anlage/batch-checks.json',checks)
diff=[]
for i in IDS:diff+=list(difflib.unified_diff((before[i]+'\n').splitlines(True),(after[i]+'\n').splitlines(True),fromfile='before/'+i,tofile='after/'+i))
(D/'commentary-changes.diff').write_text(''.join(diff))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
versions=[
 {'source':'sources/review-p154-anlage/amendment-183.pdf','location':'Art.4 Nr.8, Art.5 Nr.5; Art.7 Abs.2, publication24.06.2026','conclusion':'§155a and amended referral §44a BZRG including temporary identity-data changes effective25.06.2026. Digital certificate commencement01.10.2026 relates only to Art.4 Nr.5.'},
 {'source':'sources/review-p154-anlage/amendment-199.pdf','location':'Art.15 Abs.15, Art.16 Abs.3','conclusion':'Later BZRG amendment affects §41 only, not §44a; it is effective01.01.2027 and not used to change the selected referral.'},
 {'source':'sources/review-p154-anlage/amendment-139.pdf','location':'Art.7 Nr.15, Art.16 Abs.1–2','conclusion':'Additional §162 transition is effective20.11.2026, excluded from19.10.2026 source. Earlier commencement of §34l does not advance §162 or reopen §160.'},
 {'source':'sources/review-p154-anlage/amendment-215.pdf','location':'Art.1, Art.11 Abs.1–2; publication23.07.2026','conclusion':'Latest enacted GewO amendment already incorporated except additional §14(8) recipients, effective01.05.2027; it does not amend §§154–161 or the annex.'},
 {'source':'sources/review-p154-anlage/amendment-2024-12.pdf','location':'Art.5 and7; publication22.01.2024','conclusion':'GewO operative annex introduced effective23.01.2024. Current complete annex has two sections and all nested list points; not confused with other professional-law annexes in same gazette.'}
]
cov=load('sources/review-p154-anlage/coverage.json');oldpf=load('sources/review-p154-anlage/before-preflight-result.json')
limits=[
 'This process substantively reviewed exactly the eleven reviewed_ids. All160 other commentaries and their earlier review evidence were preserved. No whole-book completion, final cross-batch synthesis or external professional approval is claimed.',
 'Selective case-law research: one official state-court judgment newly read in full. Local national RII corpus searched with targeted provision/docket patterns; no matching copy of the selected judgment found. No relevant additional full-text-verified case selected for the other ten units; no claim that none exists.',
 '§161 triggering notices remain independently unestablished after renewed targeted search. Commentary gives conditional analysis and neither asserts occurrence nor proves nonoccurrence. Concrete unconditional application of the affected §14(4) fragments requires separate notice evidence.',
 'VG München judgment is first instance; no independently verified finality or appellate outcome. No comprehensive current commentary of EU directive, ImmVermV, BZRG, StPO, state delegation law or every gazette issue.',
 'Source currentness rests on fresh official consolidation, complete intake comparison and targeted enacted amendment/commencement checks. Fetch timestamps or the label consolidated are not treated as proof of commencement. Technical validation and prose diagnostics do not establish legal correctness.'
]
search={'verified_at':now,'decisive_date':'2026-10-19','method':'Direct official HTTP captures plus web search for discovery; actual state-court text read fully. Firecrawl authenticated but zero credits; no API keys read. National corpus read-only. No snippet treated as court holding.','web_queries':[
 {'query':'site.recht.bund.de "Gewerbeordnung" "Identifikationsmerkmale" Bekanntmachung','result':'No independently verified §161(1) triggering notice identified.'},
 {'query':'site.recht.bund.de "Gewerbeordnung" "bundesweit" "Abmeldung"','result':'No independently verified §161(2) triggering notice identified.'},
 {'query':'site.recht.bund.de "161" "Gewerbeordnung" Bekanntmachung','evidence':'web-search1.json','result':'Current GewO and legislative materials, not a proven triggering notice.'},
 {'query':'site.bundeswirtschaftsministerium.de "161" "Bekanntmachung"','evidence':'web-search1.json','result':'No actual triggering notice verified.'},
 {'query':'"§ 161 Absatz 1" Bekanntmachung Gewerbeordnung; "§ 161 Absatz 2" Bekanntmachung Gewerbeordnung; "Wirtschafts-Identifikationsnummer" "Bekanntmachung" "Gewerbeordnung"','evidence':'web-search2.json','result':'No independent proof of either statutory notice. Tax-number introduction not substituted for required GewO notice.'},
 {'query':'site.bverwg.de "157" "Sachkunde" Gewerbeordnung; site.rechtsprechung-im-internet.de "157 Abs. 3" "GewO"','result':'No sufficiently relevant national full-text authority selected. Potential VGH BW6S460/24 discovered in broader results, not independently read or relied on.'},
 {'query':'site.rechtsprechung-im-internet.de "160" "GewO" Sachkunde; site.bverwg.de "160 Abs. 3" "GewO"','result':'VG München M16K21.4969 selected from official state database and fully read; no BVerwG holding invented.'},
 {'query':'"M 16 K 21.4969" Berufung','evidence':'web-search2.json','result':'Official judgment found; finality or appellate disposition not independently established.'}
 ],'local_corpus_search':{'path':'/Volumes/LaCie/law-intake/eu/de/rii','evidence':'sources/review-p154-anlage/corpus-search.json','result':'Initial broad number search produced unrelated provisions and was not treated as a legal match. Tightened GewO-provision and docket patterns saved. No selected-case match.','selected_case_corpus_comparison_claimed':False},'selected_case':'cases/vg-muenchen-m16k214969.md','no_additional_verified_case_ids':[i for i in IDS if i!='p160'],'limits':limits}
save('sources/review-p154-anlage/search-log.json',search)
pf={'kind':'preflight','complete':True,'decisive_date':'2026-10-19','official_url':'https://www.gesetze-im-internet.de/gewo/','verified_at':now,'review_scope_ids':IDS,'captures':'sources/review-p154-anlage/captures.json','format_checks':'sources/review-p154-anlage/format-validation.json','raw_xml':'sources/review-p154-anlage/BJNR002450869.xml','raw_xml_sha256':sha(D/'BJNR002450869.xml'),'fresh_xml_identical_to_canonical':True,'version_evidence':versions,'historical_versions_checked':{'duplicate_official_labels':[],'duplicate_doknr':[],'no_historical_alternative_records':True,'all_xml_records':194,'expected_units':171,'parsed_units':171,'coverage':'sources/review-p154-anlage/coverage.json','intake_snapshot':'sources/intake-20261001.md','intake_change_map':'sources/change-map.json','intake_changes':0,'selected_effective_version':'19.10.2026; future §162 excluded; historical transition clauses retained as actual current enactment rather than substituted former versions'},'annexes_checked':cov['annexes']+[{'parent_label':'Anhang EV','disposition':'No operative record; framework notes state former measures no longer applicable. No historical annex invented.','evidence':'sources/gewo-framework-notes.md'}],'eingangsformel_checked':{'present':False,'evidence':'The unlabelled framework record has no operative text node. All194 XML records independently classified. No missing formula to fabricate.'},'unresolved_blockers':[],'limitations':limits,'application_event_uncertainty':{'unit':'p161','events':'Both required official notices remain unverified; commentary expressly conditional.'},'whole_book_completion_claimed':False}
save('sources/review-p154-anlage/preflight.json',pf)
oldpf['verified_at']=now;oldpf['bounded_review_p154_anlage_source_recheck']=pf
oldpf['remaining_limitations'].append('Bounded §§154–161/Anlage review: see exact11 IDs and conditional §161 trigger treatment in sources/review-p154-anlage/preflight.json. No whole-book finalization.')
save('preflight-result.json',oldpf)
findings=[
 {'id':'p154','action':'retained','review':'Officially repealed slot, not an operative general jurisdiction rule. Existing short explanation correctly directs to §155; no historical replacement or unsupported authority.'},
 {'id':'p154a','action':'retained','review':'Officially repealed slot. Current permit/information claims cannot rest on it; historical references require historical law. No invented former wording.'},
 {'id':'p155','action':'corrected','review':'Clarifies that delegable regulation-making powers of Land governments need not originate in Land legislation; distinguishes delegation, subdelegation and individual administrative jurisdiction, named city-state senates and limited data purpose. Abs4 repeal retained.'},
 {'id':'p155a','action':'corrected','review':'Replaces unexplained referral with all five §44a BZRG paragraphs: blocking versus deletion, balancing and binding necessity assessment, special no-entry dataset, temporary identity changes and reserved criminal-procedure powers. Correct effective25.06.2026, not digital-certificate01.10.2026.'},
 {'id':'p156','action':'corrected','review':'Identifies old intermediary-to-adviser transition and exact waived checks; liability coverage not waived, old permission ends on new grant not application; payment timing separated from underlying pre-grant mediation. No broad new-provision exemption.'},
 {'id':'p157','action':'corrected','review':'All eight paragraphs checked. Adds exact application/registration/proof deadlines, mandatory statutory lapse rather than discretionary possibility, finality versus grant, limits of old-practitioner exception, category-specific expansion and no imported exception into Abs6. Expired carve-outs not reopened.'},
 {'id':'p158','action':'corrected','review':'Corrects conflation: protective storage does not require actual loss, retransmission does. Distinguishes one month after transfer from month after statutory date, test deletion from live transfer, and separate protocol/storage-image retention via verified §14(3)BewachRV.'},
 {'id':'p159','action':'corrected','review':'Differentiates exact data categories, industry reporting versus official enquiry, future intended sensitive assignments and three distinct2019 dates. No assumed proof of actual compliance.'},
 {'id':'p160','action':'corrected','review':'Separates acquisition/registration from application, restricted waiver and proof. Adds actual VG reasons on application deadline and independent failure of continuity evidence, plaintiff argument not adopted as holding, first-instance/finality limits; no current reactivation of historical exemption or future §162.'},
 {'id':'p161','action':'corrected','review':'Scopes temporal holdback to actual identifier fragments or specified sentence; no general §14(1) exemption. Separate notice events and renewed negative search stated conditionally, no false proof of occurrence/nonoccurrence.'},
 {'id':'anlage','action':'corrected','review':'Entire two-section operative annex and nested lists checked. Clarifies §36-specific scope, shared reservations and experience qualification, quantitative/staff restrictions, cumulative same-goal burden, EU/EWR/Swiss scope and two-week consultation; supervised activity example does not displace statutory personal expertise.'}
]
result={'kind':'review','complete':True,'decisive_date':'2026-10-19','verified_at':now,'units_reviewed':len(IDS),'reviewed_ids':IDS,'changed_ids':changed,'retained_ids':[i for i in IDS if i not in changed],'unresolved_blockers':[],'findings':findings,'limitations':limits,'prior_batch_record':'sources/review-p154-anlage/before-review-result.json','unassigned_commentaries_preserved':160,'whole_book_completion_claimed':False,'evidence':{'preflight':'sources/review-p154-anlage/preflight.json','coverage':'sources/review-p154-anlage/coverage.json','source_captures':'sources/review-p154-anlage/captures.json','external_norms':'sources/review-p154-anlage/external-provisions.json','case':'sources/review-p154-anlage/case-evidence.json','search':'sources/review-p154-anlage/search-log.json','preservation':'sources/review-p154-anlage/batch-checks.json','diff':'sources/review-p154-anlage/commentary-changes.diff'},'validation':{'state':'Rebuild and strict validation follow this content checkpoint.'}}
save('review-result.json',result)
v=load('sources/review-p154-anlage/before-verification.json');v['verified_at']=now;v['bounded_review_p154_anlage']=pf;v['captures']+=load('sources/review-p154-anlage/captures.json');save('sources/verification.json',v)
s=load('sources/review-p154-anlage/before-status.json');s['stage']='bounded_review_complete';s['updated_at']=now;s['commentary_chars']=checks['full_book_commentary_chars'];s['source_checks']['bounded_review_p154_anlage']=pf;s['active_task']={'kind':'review','complete':True,'units_reviewed':11,'reviewed_ids':IDS,'evidence':'review-result.json','whole_book_completion_claimed':False,'validation_state':'awaiting rebuild/strict validation'}
ir=s['independent_review'];ir['reviewed_ids']+=IDS;assert len(set(ir['reviewed_ids']))==171
ir.update(units_reviewed=171,latest_batch_units_reviewed=11,latest_batch_reviewed_ids=IDS,whole_book_complete=False,remaining_units=0,state='Nine bounded batches recorded; this process reviewed exactly11 latest IDs. Cross-batch finalization and whole-book approval are not performed.',prior_batch_record='sources/review-p154-anlage/before-review-result.json')
s['earlier_limitations_record']='sources/review-p154-anlage/before-status.json';s['remaining_limitations']=limits;s['case_law_sources'].append({'court':'VG München','date':'2022-05-05','docket':'M 16 K 21.4969','ecli':None,'units':['p160'],'all_paragraphs_read':'TenorI–III,Rn1–32','paragraphs_used':list(range(18,26)),'card':'cases/vg-muenchen-m16k214969.md'});save('status.json',s)
cc=load('sources/review-p154-anlage/before-case-coverage.json')
for u in cc['units']:
 if u['id'] in IDS:
  u['bounded_review_p154_anlage']={'verified_at':now,'fully_reviewed':True,'new_verified_cases':['VG München M16K21.4969'] if u['id']=='p160' else [],'search_log':'sources/review-p154-anlage/search-log.json','limits':limits[1]}
  if u['id']=='p160':u['verified_cases']=['VG München M16K21.4969'];u['disposition']='Official state-court full text read, Rn18–25 supports limited transition/deadline analysis; no national-corpus match, finality or highest-court resolution claimed.'
save('sources/case-coverage.json',cc)
print(json.dumps({'reviewed':len(IDS),'changed':len(changed),'preserved_outside_batch':160,'commentary_chars':checks['full_book_commentary_chars']}))
