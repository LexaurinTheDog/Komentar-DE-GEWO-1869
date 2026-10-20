#!/usr/bin/env python3
"""Reproducible technical evidence for the bounded p1–p13 review.

This script does not perform or certify substantive legal review.
"""
from pathlib import Path
import collections
import difflib
import hashlib
import json
import re
import xml.etree.ElementTree as ET

W = Path(__file__).resolve().parent
D = W / 'sources/review-p1-p13'
BASELINE = 'a97ee4aea315eb7e4244a4332d6157928d23ae2b'
IDS = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p6a', 'p6b', 'p6c', 'p7',
       'p8', 'p9', 'p10', 'p11', 'p11a', 'p11b', 'p11c', 'p11d', 'p12', 'p13']


def blocks(text):
    return {i: t.strip() for i, t in re.findall(r'^=== (\S+)\n(.*?)(?=^=== |\Z)', text, re.M | re.S)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', text)


before, after = {}, {}
for p in sorted((W / 'commentary').glob('*.md')):
    rel = str(p.relative_to(W))
    old = (D / 'baseline-commentary' / p.name).read_text()
    before.update(blocks(old))
    after.update(blocks(p.read_text()))

units = {u['id']: u for u in map(json.loads, (W / 'units.jsonl').read_text().splitlines())}
root = ET.parse(D / 'BJNR002450869.xml').getroot()
expected = []
checks = []
for n in root.findall('norm'):
    label = n.findtext('metadaten/enbez', '')
    unit_id = 'p' + label.removeprefix('§ ').strip()
    if unit_id not in IDS:
        continue
    expected.append(unit_id)
    content = n.find('textdaten/text/Content')
    raw = ''.join(content.itertext()) if content is not None else ''
    raw = raw.split('-----', 1)[0].strip()
    for note in n.findall('textdaten/text/Content/P/noindex'):
        raw = raw.replace(''.join(note.itertext()), '', 1).lstrip()
    if not raw:
        raw = n.findtext('metadaten/titel', '')
    u = units[unit_id]
    checks.append({'id': unit_id, 'label': label, 'official_doknr': n.get('doknr'),
                   'statutory_text_agrees': compact(raw) == compact(u['text']),
                   'statutory_text_sha256': sha(u['text'].encode()),
                   'commentary_before_sha256': sha(before[unit_id].encode()),
                   'commentary_after_sha256': sha(after[unit_id].encode()),
                   'commentary_chars': len(after[unit_id]),
                   'changed': before[unit_id] != after[unit_id]})

changed = [i for i in after if before.get(i) != after[i]]
outside_changes = sorted(set(changed) - set(IDS))
paragraphs = collections.defaultdict(set)
for i, text in after.items():
    for p in text.split('\n\n'):
        if len(p) > 160:
            paragraphs[p].add(i)
duplicates = [{'ids': sorted(ids), 'paragraph_sha256': sha(p.encode())}
              for p, ids in paragraphs.items() if len(ids) > 1 and ids.intersection(IDS)]
diff = []
for i in IDS:
    diff.extend(difflib.unified_diff((before[i] + '\n').splitlines(True), (after[i] + '\n').splitlines(True),
                                     fromfile='before/' + i, tofile='after/' + i))
(D / 'commentary-changes.diff').write_text(''.join(diff))
result = {
    'scope': 'Technical checks supporting exactly 20 manually reviewed units; no whole-book substantive certification.',
    'baseline_work_commit': BASELINE, 'assigned_ids': IDS,
    'expected_ids_independently_selected_from_xml_metadata': expected,
    'missing': sorted(set(IDS) - set(expected)), 'duplicate_expected_ids': [i for i, c in collections.Counter(expected).items() if c > 1],
    'raw_xml': 'sources/review-p1-p13/BJNR002450869.xml',
    'raw_xml_sha256': sha((D / 'BJNR002450869.xml').read_bytes()),
    'fresh_xml_agrees_with_canonical_source': (D / 'BJNR002450869.xml').read_bytes() == (W / 'sources/BJNR002450869.xml').read_bytes(),
    'unit_checks': checks, 'changed_ids': changed,
    'commentary_ids_outside_assignment_changed': outside_changes,
    'unassigned_commentaries_preserved': len(set(after) - set(IDS)),
    'duplicate_commentary_paragraphs_involving_assigned_units': duplicates,
    'full_book_commentary_count': len(after), 'full_book_commentary_chars': sum(map(len, after.values())),
    'limitations': ['Character counts and duplicate detection do not establish legal quality. Legal findings are recorded separately in review-result.json.']
}
result['ok'] = expected == IDS and all(c['statutory_text_agrees'] for c in checks) and not outside_changes and not duplicates and set(before) == set(after) and result['fresh_xml_agrees_with_canonical_source']
(D / 'batch-checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['assigned_ids', 'changed_ids', 'unassigned_commentaries_preserved', 'full_book_commentary_chars', 'ok']}, ensure_ascii=False))
raise SystemExit(0 if result['ok'] else 1)
