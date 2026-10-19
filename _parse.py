#!/usr/bin/env python3
"""Reproducible extraction from official GewO XML; no authored statutory text."""
from pathlib import Path
import xml.etree.ElementTree as ET
import re,json,hashlib,collections
W=Path(__file__).resolve().parent
RAW=W/'sources/BJNR002450869.xml'
def render(el):
    if el is None:return ''
    if el.tag in ('BR','br'):return '\n'
    out=el.text or ''
    for c in el:
        x=render(c)
        if c.tag=='DT':out+='\n'+x+' '
        elif c.tag in ('P','DL','table','TR','tr'):out+='\n\n'+x+'\n\n'
        elif c.tag in ('TD','TH','td','th'):out+=' '+x+' | '
        else:out+=x
        out+=c.tail or ''
    return out

def clean(el):
    t=render(el)
    t=re.sub(r'[ \t\r\f\v]+',' ',t)
    t=re.sub(r' *\n *','\n',t)
    return re.sub(r'\n{3,}','\n\n',t).strip()

def uid(e):
    if e=='Anlage':return 'anlage'
    e=e.replace('(XXXX) ','')
    return 'p'+e.replace('§','').strip().replace(' ','-')

r=ET.parse(RAW).getroot();units=[];structure=[];struct_keys=[];dispositions=[];canonical=[]
chapter=1
for n in r.findall('norm'):
    m=n.find('metadaten');e=m.findtext('enbez','');g=m.find('gliederungseinheit')
    if g is not None:
        key=g.findtext('gliederungskennzahl'); label=re.sub(r'\s+',' ',clean(g.find('gliederungsbez'))+' — '+clean(g.find('gliederungstitel')))
        level=next((i for i in range(0,len(key),3) if key[i:i+3]=='000'),len(key))//3
        # Last nonzero triplet is actual depth, including II.1.A hierarchy.
        level=max(i+1 for i in range(len(key)//3) if key[i*3:i*3+3]!='000')
        structure=structure[:level-1]+[label];struct_keys=struct_keys[:level-1]+[key]
        dispositions.append({'doknr':n.get('doknr'),'type':'structure','key':key,'label':label});continue
    if not e:
        dispositions.append({'doknr':n.get('doknr'),'type':'metadata','notes':clean(n.find('textdaten/fussnoten/Content'))});continue
    if e=='Inhaltsübersicht':
        dispositions.append({'doknr':n.get('doknr'),'type':'table_of_contents','reason':'duplicate navigation, not an operative provision'});continue
    # editorial chapters keep statutory ordering while staying readable.
    if e in ['§ 14','§ 33a','§ 34','§ 34d','§ 35','§ 55','§ 64','§ 105','§ 143','§ 149','§ 154','Anlage']:chapter+=1
    if e=='Anlage':structure=['Anlage zu § 36 Absatz 4a Satz 1']
    text=clean(n.find('textdaten/text/Content'));title=re.sub(r'\s+',' ',clean(m.find('titel')))
    empty=not text
    if not text and title=='(weggefallen)':text=title;title=''
    if not text:raise ValueError((e,'unexplained missing statutory text'))
    notes=clean(n.find('textdaten/fussnoten/Content'))
    embedded_notes=[]
    if '\n-----' in text:
        text,embedded=text.split('\n-----',1);text=text.rstrip();embedded_notes.append(embedded.strip())
    for editorial in n.findall('textdaten/text/Content/P/noindex'):
        note=clean(editorial)
        if note and note in text:
            text=text.replace(note,'',1).lstrip();embedded_notes.append(note)
    notes='\n\n'.join(([notes] if notes else [])+embedded_notes)
    u={'id':uid(e),'label':e.replace('(XXXX) ',''),'title':title,'chapter':chapter,'structure':list(structure),'text':text,'notes':[notes] if notes else [],'official_doknr':n.get('doknr'),'source_empty_text_with_repeal_title':empty}
    units.append(u);canonical+=['## '+u['label']+(' — '+title if title else ''),text]
(W/'units.jsonl').write_text(''.join(json.dumps(u,ensure_ascii=False)+'\n' for u in units))
(W/'sources/gewo-canonical.md').write_text('# Gewerbeordnung\n\n'+ '\n\n'.join(canonical)+'\n')
chap_titles=['Gewerbefreiheit, Daten und europäische Verfahren','Anzeige und erste Erlaubnistatbestände','Schaustellungen und Spielrecht','Pfand, Bewachung, Versteigerung und Immobilien','Versicherung, Finanzanlagen und Immobiliardarlehen','Untersagung, Sachverständige und Betriebsfortführung','Reisegewerbe','Messen, Ausstellungen und Märkte','Arbeitsrecht und Gewerbeaufsicht','Ordnungswidrigkeiten und Straftaten','Gewerbezentralregister','Zuständigkeit und Übergangsrecht','Anlage: Verhältnismäßigkeit neuer Berufsregeln']
meta={'cc':'de','lang':'de','repo':'Komentar-DE-GEWO-1869','repo_dir':'/Volumes/LaCie/open-commentary/de/Komentar-DE-GEWO-1869','title':'Kommentar zur Gewerbeordnung','source_path':str(W/'sources/gewo-canonical.md'),'intro_file':'00-einleitung.md','intro_desc':'Gegenstand, Rechtsstand und Benutzung','labels':{'text':'Wortlaut der Vorschrift','chapter':'Kommentarkapitel','notes':'Redaktioneller Quellenhinweis'},'chapters':[{'n':i+1,'slug':f'gewo-{i+1:02d}','title':t} for i,t in enumerate(chap_titles)],'decisive_date':'2026-10-19','official_source':'https://www.gesetze-im-internet.de/gewo/'}
(W/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
# Independent expectation pass uses metadata only, without rendered units.
expected=[{'doknr':n.get('doknr'),'label':n.findtext('metadaten/enbez')} for n in ET.parse(RAW).getroot().findall('norm') if n.findtext('metadaten/enbez','') and n.findtext('metadaten/enbez')!='Inhaltsübersicht']
parsed=[u['official_doknr'] for u in units];exp=[x['doknr'] for x in expected]
report={'raw_xml_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'law_identification':[x.text for x in r.findall('norm/metadaten/jurabk')][:1], 'expected_official_units':expected,'parsed_official_ids':parsed,'expected_count':len(exp),'parsed_count':len(parsed),'missing':sorted(set(exp)-set(parsed)),'unexpected':sorted(set(parsed)-set(exp)),'duplicates':[x for x,c in collections.Counter(parsed).items() if c>1],'repealed_or_empty_slots':[{'id':u['id'],'label':u['label'],'text':u['text']} for u in units if u['text'] in ['(weggefallen)','-']],'nonunit_dispositions':dispositions,'annex_disposition':[{'label':'Anlage (zu § 36 Absatz 4a Satz 1)','id':'anlage','included':True,'sections':['I. Begriffsbestimmungen','II. Zu prüfende Kriterien']}], 'range_policy':'Official grouped repealed ranges remain grouped; no invented historically absent letters. Every numbered XML record and sole annex included. Inhaltsübersicht is navigation only.'}
report['complete']=not any(report[x] for x in ['missing','unexpected','duplicates'])
(W/'completeness-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'units':len(units),'chapters':chapter,'complete':report['complete']}))
