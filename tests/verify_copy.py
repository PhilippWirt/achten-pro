#!/usr/bin/env python3
"""RC2: exact approved copy deltas; ordered text preservation, never blanket bans."""
import json, re, hashlib, argparse
from pathlib import Path
from html.parser import HTMLParser
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=HERE.parent)
ROOT=parser.parse_args().root
class Nodes(HTMLParser):
    def __init__(self): super().__init__(); self.nodes=[]; self.blocked=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.blocked+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.blocked-=1
    def handle_data(self,data):
        if not self.blocked and data.strip(): self.nodes.append(' '.join(data.split()))
def nodes(raw):
    p=Nodes(); p.feed(raw); return p.nodes
errors=[]; checks=0

def check(ok,msg):
    global checks
    checks+=1
    if not ok: errors.append(msg)
selection=json.loads((HERE/'copy_selection.json').read_text())
expected=json.loads((HERE/'copy_expected_nodes.json').read_text())
# RC2 layout: preserve original fixture; indexed and independently conserved delta only.
from collections import Counter
layout=json.loads((HERE/'layout_copy_delta.json').read_text())
for lang,delta in layout['languages'].items():
    previous=expected[lang][:]
    for op in reversed(delta['operations']):
        assert expected[lang][op['old_start']:op['old_end']]==op['old']
        expected[lang][op['old_start']:op['old_end']]=op['new']
    assert Counter(expected[lang])==Counter(delta['replacements'].get(s,s) for s in previous)+Counter(delta['added']), 'Undeclared text loss or addition'

# RC3 deltas extend, rather than replace, the original RC1/RC2 exact-node contract.
rc3=json.loads((HERE/'rc3_copy_delta.json').read_text())
for lang,operations in rc3['languages'].items():
    for op in reversed(operations):
        assert expected[lang][op['old_start']:op['old_end']]==op['old']
        expected[lang][op['old_start']:op['old_end']]=op['new']

# Explicit RC4 corrections, not a baseline reset.
rc4=json.loads((HERE/'rc4_copy_delta.json').read_text())
for lang,operations in rc4['languages'].items():
    for op in reversed(operations):
        assert expected[lang][op['old_start']:op['old_end']]==op['old']
        expected[lang][op['old_start']:op['old_end']]=op['new']

for lang,file in [('de','index.html'),('en','en/index.html')]:
    raw=(ROOT/file).read_text(); actual=nodes(raw); text=' '.join(actual)
    check(actual==expected[lang],lang+': ordered text nodes differ from exact pre-copy + approved delta fixture')
    for row in selection['entries']:
        if isinstance(row['id'],int):
            old=row.get('alt_'+lang,'').strip()
            check(not old or old not in text,lang+': selected old fragment retained ID '+str(row['id']))
            if row['id'] in (4,):
                full=row['original_list_text']
                if lang=='de':
                    new=full.replace(row['alt_de'],row['neu_de'])
                    check(new in text,lang+': positive remainder lost ID '+str(row['id']))
    check(('Beim Personal Training begleite ich dich als' if lang=='de' else 'In personal training I support you as a personal trainer;') not in text,lang+': W07 redundant role sentence removed')
    check(not re.search(r'Sportpsychologe\b|sport psychologist\b',text,re.I),lang+': prohibited self-role')
    check(('M.Sc. Sportpsychologie' if lang=='de' else 'M.Sc. Sport Psychology') in text,lang+': degree changed')
    offer='Sportpsychologisches Coaching' if lang=='de' else 'Sport psychology coaching'
    for s in re.findall(r'<(?:h2|a)\b[^>]*>(.*?)</(?:h2|a)>',raw,re.S):
        t=' '.join(nodes(s))
        if re.search(r'Sportpsychologie|Sport\u00adpsychologie|Sport Psychology\b',t) and t not in ['Sportwissenschaft, Sportpsychologie – Expertise, die sich im echten Einsatz bewährt hat.']:
            check(offer in t,lang+': stale offer label '+t)
    check(offer in re.search(r'<title>(.*?)</title>',raw,re.S)[1],lang+': title')
    check(offer.lower() in re.search(r'<meta name="description" content="(.*?)"',raw)[1].lower(),lang+': description')
    check(('subject=Anfrage%20Sportpsychologisches%20Coaching' if lang=='de' else 'subject=Inquiry%20Sport%20psychology%20coaching') in raw,lang+': mail subject')
    for section in ('personal-training','sportpsychologie'):
        body=re.search(r'<section id="'+section+r'"[^>]*>(.*?)</section>',raw,re.S)[1]
        t=' '.join(nodes(body))
        definition=next(r for r in selection['entries'] if r['id']=='HRV-definition')['neu_'+lang]
        chest=next(r for r in selection['entries'] if r['id']=='HRV-brustgurt')['neu_'+lang]
        check(t.count(definition)==1,lang+': one complete HRV/pulse/BP definition in '+section)
        check(('Brustgurt' if lang=='de' else 'chest strap') in t,lang+': chest strap remains optional in '+section)
        for token in (['Davon getrennt','Schlaf, Belastung, Erholung und Körpergefühl'] if lang=='de' else ['Separately','sleep, training load, recovery and how your body feels']):
            check(token in t,lang+': protected HRV context '+token)
        check(('Trainingsfreigabe' if lang=='de' else 'clearance to train') not in t,lang+': P15 deletion')
        check(('80 €' if section=='personal-training' else '85 €') in t,lang+': unchanged individual price')
        check(('120' in t) == (section=='personal-training'),lang+': confirmed PT-only duo attribution')
    check('Philipp@achten.pro' in text,lang+': contact preserved')
# Every nonselected ID is protected by the full ordered fixture; original quotes additionally verified exactly by verify_content.py.
print(json.dumps({'ok':not errors,'checks':checks,'errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
