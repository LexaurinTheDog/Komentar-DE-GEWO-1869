from pathlib import Path
import shutil,json
W=Path(__file__).resolve().parent;O=Path(json.loads((W/'meta.json').read_text())['repo_dir'])
for folder in ['sources','cases','commentary']:
 shutil.copytree(W/folder,O/folder,dirs_exist_ok=True)
for name in ['SOURCES.md','REVIEW.md','completeness-report.json','coverage-report.json','preflight-result.json','review-result.json','audit-report.json','meta.json','units.jsonl','_parse.py','_coverage.py','_audit.py','_review_batch.py','_review_p13a_p33f.py','_review_p38_p55b.py','_verify_sources.py','_copy_support.py','_check_links.py','status.json','validation.json','link-report.json','batch-review-ledger.json','_finalize.py']:
 p=W/name
 if p.exists():shutil.copyfile(p,O/name)
