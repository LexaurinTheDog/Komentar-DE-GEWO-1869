#!/usr/bin/env python3
"""Independent official XML inventory; does not import the extraction parser.

Checks exact official labels as well as doknr, so a display-label normalization
cannot mask omissions. Re-run after _parse.py; no commentary is changed.
"""
from pathlib import Path
import collections
import hashlib
import json
import re
import xml.etree.ElementTree as ET

W = Path(__file__).resolve().parent
RAW = W / 'sources/BJNR002450869.xml'
root = ET.parse(RAW).getroot()
units = [json.loads(line) for line in (W / 'units.jsonl').read_text().splitlines() if line.strip()]
by_doknr = {u['official_doknr']: u for u in units}


def chars(element):
    return ''.join(element.itertext()) if element is not None else ''


def compact(text):
    return re.sub(r'\s+', '', text)


def duplicate(values):
    return [x for x, count in collections.Counter(values).items() if count > 1]


expected, records, text_errors, annexes, unclassified = [], [], [], [], []
for norm in root.findall('norm'):
    doknr = norm.attrib['doknr']
    label = norm.findtext('metadaten/enbez', '')
    content = norm.find('textdaten/text/Content')
    raw = chars(content)
    structure = norm.find('metadaten/gliederungseinheit')
    rec = {'doknr': doknr, 'official_label': label, 'content_chars_without_whitespace': len(compact(raw))}
    if structure is not None:
        rec['disposition'] = 'structural_heading'
        if compact(raw):
            unclassified.append({'doknr': doknr, 'reason': 'substantive content in structural record'})
    elif label == 'Inhaltsübersicht':
        rec['disposition'] = 'navigation_table_of_contents'
    elif not label:
        rec['disposition'] = 'framework_metadata_and_editorial_notes'
        rec['opening_formula_present'] = bool(compact(raw))
        if compact(raw):
            unclassified.append({'doknr': doknr, 'reason': 'unlabelled substantive content'})
    else:
        rec['disposition'] = 'statutory_unit'
        expected.append({'doknr': doknr, 'label': label})
        u = by_doknr.get(doknr)
        primary = raw.split('-----', 1)[0].strip()
        for note in norm.findall('textdaten/text/Content/P/noindex'):
            primary = primary.replace(chars(note), '', 1).lstrip()
        if not primary.strip():
            primary = chars(norm.find('metadaten/titel'))
        if u is None or compact(primary) != compact(u['text']):
            text_errors.append({'doknr': doknr, 'label': label})
        if label.startswith(('Anlage', 'Anhang')):
            official_lists = [compact(chars(dt)) for dt in norm.findall('.//text/Content//DT')]
            parsed_lists = [compact(item['labels'][-1]) for item in u['list_hierarchy']] if u else []
            sections = [chars(p).strip() for p in norm.findall('textdaten/text/Content/P') if p.find('B') is not None]
            annexes.append({'parent_label': label, 'doknr': doknr, 'unit_id': u['id'] if u else None,
                            'included_as': 'one complete operative annex, retaining nested numbering',
                            'official_sections': sections, 'official_list_labels': official_lists,
                            'parsed_list_labels': parsed_lists,
                            'list_order_agrees': official_lists == parsed_lists,
                            'full_text_agrees': u is not None and compact(primary) == compact(u['text']),
                            'evidence_path': str(RAW.relative_to(W)),
                            'evidence_sha256': hashlib.sha256(RAW.read_bytes()).hexdigest()})
    records.append(rec)

official_labels = [e['label'] for e in expected]
parsed_labels = [u['label'] for u in units]
official_ids = [e['doknr'] for e in expected]
parsed_ids = [u['official_doknr'] for u in units]
raw_ids = [n.attrib['doknr'] for n in root.findall('norm')]
missing_labels = sorted(set(official_labels) - set(parsed_labels))
extra_labels = sorted(set(parsed_labels) - set(official_labels))
missing_ids = sorted(set(official_ids) - set(parsed_ids))
extra_ids = sorted(set(parsed_ids) - set(official_ids))
report = {
    'method': 'Independent XML metadata enumeration, all-record disposition and raw character/list comparison; no imports from _parse.py.',
    'official_source': {'url': 'https://www.gesetze-im-internet.de/gewo/xml.zip',
                        'path': str(RAW.relative_to(W)), 'sha256': hashlib.sha256(RAW.read_bytes()).hexdigest()},
    'expected_official_identifiers': expected, 'parsed_official_identifiers': [{'doknr': u['official_doknr'], 'label': u['label'], 'id': u['id']} for u in units],
    'expected_count': len(expected), 'parsed_count': len(units),
    'missing_labels': missing_labels, 'extra_labels': extra_labels,
    'missing_doknr': missing_ids, 'extra_doknr': extra_ids,
    'duplicate_expected_labels': duplicate(official_labels), 'duplicate_parsed_labels': duplicate(parsed_labels),
    'duplicate_parsed_ids': duplicate([u['id'] for u in units]), 'duplicate_parsed_doknr': duplicate(parsed_ids),
    'duplicate_source_doknr': duplicate(raw_ids),
    'official_order_preserved': official_ids == parsed_ids,
    'all_xml_records': records, 'xml_record_count': len(records),
    'record_disposition_counts': dict(collections.Counter(r['disposition'] for r in records)),
    'unclassified_operative_records': unclassified, 'text_disagreements': text_errors,
    'eingangsformel': {'present_in_official_xml': any(r.get('opening_formula_present') for r in records) or 'Eingangsformel' in official_labels,
                      'disposition': 'Verified absent: framework record contains editorial footnotes only; no statutory text node. No invented opening formula.'},
    'annex_disposition': annexes + [{'parent_label': 'Anhang EV', 'included_as': 'not operative in the current XML',
                                    'evidence_path': 'sources/gewo-framework-notes.md',
                                    'reason': 'Framework note states measures no longer applicable from 2010/2013; no operative annex record exists. Historical wording not reconstructed.'}],
    'repealed_or_empty_slots': [{'id': u['id'], 'label': u['label'], 'text': u['text'], 'empty_body_with_repeal_title': u['source_empty_text_with_repeal_title']} for u in units if u['text'] in ('(weggefallen)', '-')],
    'final_and_transitional_units': [{'id': u['id'], 'label': u['label']} for u in units if any('Schlußbestimmungen' in s for s in u['structure']) or u['label'] in ('§ 156', '§ 157', '§ 158', '§ 159', '§ 160', '§ 161')],
    'historical_versions_checked': {'duplicate_official_labels': duplicate(official_labels), 'duplicate_doknr': duplicate(raw_ids),
                                    'selection': 'One consolidated record per official identifier; TOC excluded as navigation. Historical transition clauses retained as enacted, not alternative versions.',
                                    'intake_change_map': 'sources/change-map.json',
                                    'future_units_excluded': ['§ 34k (2026-11-20)', '§ 162 (2026-11-20)']},
    'limitations': ['Whitespace-only layout changes and explicitly identified editorial notes are excluded from statutory body comparison.',
                   'This is a source/parser preflight, not independent substantive review of all commentary.']
}
report['complete'] = not any((missing_labels, extra_labels, missing_ids, extra_ids, text_errors, unclassified,
                               report['duplicate_expected_labels'], report['duplicate_parsed_labels'],
                               report['duplicate_parsed_ids'], report['duplicate_parsed_doknr'], report['duplicate_source_doknr'])) and report['official_order_preserved'] and all(a['list_order_agrees'] and a['full_text_agrees'] for a in annexes)
(W / 'coverage-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('expected_count', 'parsed_count', 'missing_labels', 'extra_labels', 'text_disagreements', 'complete')}, ensure_ascii=False))
raise SystemExit(0 if report['complete'] else 1)
