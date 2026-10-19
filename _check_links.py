from pathlib import Path
import re,json,urllib.parse
W=Path(__file__).resolve().parent;meta=json.loads((W/'meta.json').read_text());O=Path(meta['repo_dir']);broken=[];count=0;external=set()
for p in list(O.glob('*.md'))+list((O/'cases').glob('*.md')):
 for label,link in re.findall(r'\[([^\]]*)\]\(([^)]+)\)',p.read_text()):
  if link.startswith(('http://','https://')):external.add(link);continue
  if link.startswith('#'):continue
  target=urllib.parse.unquote(link.split('#')[0]);count+=1
  if not (p.parent/target).exists():broken.append({'file':str(p.relative_to(O)),'target':link})
result={'checked_local_links':count,'broken_local_links':broken,'external_urls':sorted(external),'external_method':'Official statute, gazette and cited court URLs checked through real HTTP captures in sources/verification.json. Project-context GitHub profile is a context link, not a source or publication. Raw downloaded webpage navigation is outside authored-book link checking.','ok':not broken}
(W/'link-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
