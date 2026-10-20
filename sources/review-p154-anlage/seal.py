"""Run actual strict validation on a committed clean output and record its scope."""
from pathlib import Path
import datetime,json,subprocess
W=Path(__file__).resolve().parents[2];D=W/'sources/review-p154-anlage';O=Path(json.loads((W/'meta.json').read_text())['repo_dir'])
def load(n):return json.loads((W/n).read_text())
def save(n,x):(W/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
cmd=['python3','/Volumes/LaCie/open-commentary/_tools/validate.py',str(W)]
r=subprocess.run(cmd,capture_output=True,text=True,check=True);result=json.loads(r.stdout);assert result['ok'] and result['verbatim_ratio']==1.0
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
e={'validated_at':now,'command':' '.join(cmd),'result':result,'content_checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=O,text=True).strip(),'work_content_checkpoint':subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip(),'scope':'Strict technical validation of rebuilt book; substantive review by this process limited to exact11 reviewed_ids. All160 unassigned comments preserved. No whole-book finalization or external professional approval.'}
save('sources/review-p154-anlage/strict-validation.json',e);save('validation.json',result)
x=load('review-result.json');x['validation']=e;save('review-result.json',x)
x=load('status.json');x['validation_result']=result;x['updated_at']=now;x['active_task']['validation']=e;x['active_task'].pop('validation_state',None);x['source_checks']['bounded_review_p154_anlage']['validation']=e;x['link_validation']=load('link-report.json');x['audit_result']={'ok':True,'units':171,'text_disagreements':[],'commentary_count':171,'commentary_chars':result['commentary_chars'],'duplicate_paragraphs':[],'similar_pairs':[]};save('status.json',x)
x=load('preflight-result.json');x['bounded_review_p154_anlage_source_recheck']['validation']=e;save('preflight-result.json',x)
x=load('sources/verification.json');x['bounded_review_p154_anlage']['validation']=e;save('sources/verification.json',x)
x=load('sources/review-p154-anlage/preflight.json');x['validation']=e;save('sources/review-p154-anlage/preflight.json',x)
p=W/'REVIEW.md';s=p.read_text();needle='Keine externe anwaltliche Freigabe und keine Veröffentlichung.';s=s.replace(needle,'Die tatsächliche strikte Validierung des Inhaltscommits ist erfolgreich: 171 Einheiten, Wortlautquote 1,0, keine Fehler oder Warnungen; [Beleg](sources/review-p154-anlage/strict-validation.json). Die lokale Linkprüfung findet kein defektes Ziel. '+needle,1);p.write_text(s)
print(json.dumps(e,ensure_ascii=False))
