from pathlib import Path
import xml.etree.ElementTree as E,urllib.request,datetime,hashlib,json,re,html
D=Path(__file__).resolve().parent;W=D.parent.parent
caps=json.loads((D/'captures.json').read_text());out=[]
def compact(t):return re.sub(r'\s+','',html.unescape(t))
for name,slug,abk,labels in [('BJNR263110007.xml','vvg_2008','VVG',['§ 7c','§ 59']),('BJNR004810968.xml','owig_1968','OWiG',['§ 10','§ 17','§ 22','§ 23','§ 24','§ 30']),('BJNR006290950.xml','stpo','StPO',['§ 488','§ 493']),('BJNR013140974.xml','gewo_34cdv','MaBV',['§ 16']),('BJNR001270871.xml','stgb','StGB',['§ 15'])]:
 r=E.parse(D/name).getroot();selected=[]
 for label in labels:
  nodes=[n for n in r.findall('norm') if n.findtext('metadaten/enbez')==label];assert len(nodes)==1
  n=nodes[0];c=n.find('textdaten/text/Content');t=''.join(c.itertext());number=label.replace('§ ','');u='https://www.gesetze-im-internet.de/'+slug+'/__'+number+'.html';p=D/(abk.lower()+'-'+number+'.html');row={'url':u,'path':str(p.relative_to(W)),'accessed_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  with urllib.request.urlopen(u,timeout=20) as resp:b=resp.read();row.update(http_status=resp.status,final_url=resp.url,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  p.write_bytes(b);h=html.unescape(re.sub('<[^>]+>','',b.decode('iso-8859-1')));assert compact(t) in compact(h);row['validated_format']='html containing the complete selected XML unit';caps.append(row)
  selected.append({'label':label,'doknr':n.get('doknr'),'content':t,'content_sha256':hashlib.sha256(t.encode()).hexdigest(),'html':str(p.relative_to(W)),'html_xml_agree':True})
 out.append({'law':abk,'raw_xml':str((D/name).relative_to(W)),'sha256':hashlib.sha256((D/name).read_bytes()).hexdigest(),'framework_metadata':E.tostring(r.find('norm/metadaten'),encoding='unicode'),'selected_units':selected,'selection':'One exact official current XML record per unit, entire body independently compared with official single-unit HTML. Publication and deferred commencement checked separately; no full-code review claimed.'})
(D/'captures.json').write_text(json.dumps(caps,ensure_ascii=False,indent=2)+'\n');(D/'external-provisions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('External units:',sum(len(x['selected_units']) for x in out))
