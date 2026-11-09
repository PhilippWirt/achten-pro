#!/usr/bin/env python3
"""RC1 content, exact historical testimonials and semantic transfer regression.

No browser, network, mail opening or form submission. The contract is portable;
--root permits a RED run against the backed-up pre-integration tree.
"""
import argparse
import html
import json
import re
from pathlib import Path
from html.parser import HTMLParser

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=HERE.parent)
args = parser.parse_args()
ROOT = args.root
contract = json.loads((HERE / 'content_contract.json').read_text())
errors = []
checks = 0

def check(condition, message):
    global checks
    checks += 1
    if not condition:
        errors.append(message)

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.words = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.words.append(data)

def text(raw):
    p = Text()
    p.feed(raw)
    return ' '.join(' '.join(p.words).split())

pages = {lang: (ROOT / file).read_text() for lang, file in [('de', 'index.html'), ('en', 'en/index.html')]}
for lang, raw in pages.items():
    m = re.search(r'<section id="testimonials"[^>]*>(.*?)</section>', raw, re.S)
    check(bool(m), lang + ': historic testimonial section missing')
    testimonial = m[1] if m else ''
    check(contract['testimonial_context'][lang] in text(testimonial), lang + ': context not preserved')
    cards = re.findall(r'<figure\b[^>]*>(.*?)</figure>', testimonial, re.S)
    check(len(cards) == 3, lang + ': expected exactly three historic testimonials')
    for index, expected in enumerate(contract['testimonials'][lang]):
        card = cards[index] if index < len(cards) else ''
        q = re.search(r'<blockquote\b[^>]*>(.*?)</blockquote>', card, re.S)
        # Exact decoded quote, no whitespace/case normalization that hides changes.
        check(q is not None and html.unescape(q[1]) == expected['quote'], lang + ': quote changed: ' + expected['initials'])
        a = re.search(r'<strong>(.*?)</strong><span>(.*?)</span>', card, re.S)
        check(a is not None and a.groups() == (expected['initials'], expected['role']), lang + ': attribution changed: ' + expected['initials'])
    check(raw.index('id="testimonials"') > raw.index('id="about"') if m else False, lang + ': testimonials must stay separate from individual offer sections')
    for section in ('personal-training', 'sportpsychologie'):
        body = re.search(r'<section id="' + section + r'"[^>]*>(.*?)</section>', raw, re.S)
        check(body is not None and '<blockquote' not in body[1], lang + ': no reassignment of testimonials to ' + section)

for lang, raw in pages.items():
    check('class="hero-photo" src="/assets/images/Training Outdoor 1.jpg"' in raw, lang + ': confirmed rain-jacket hero missing')
    check('.intro-hero .hero-photo { display:block;width:100%;height:auto;' in raw, lang + ': hero must preserve full image proportions')

for row in contract['transfer']:
    for lang, raw in pages.items():
        for target in row['targets']:
            if target['section_id'] == 'footer':
                m = re.search(r'<footer\b[^>]*>(.*?)</footer>', raw, re.S)
            else:
                m = re.search(r'<section\b(?=[^>]*\bid="' + re.escape(target['section_id']) + r'")[^>]*>(.*?)</section>', raw, re.S)
            check(m is not None and target[lang] in text(m[1]), row['id'] + ': missing ' + lang + ' transfer anchor in #' + target['section_id'])
check(len(contract['transfer']) == 85, 'canonical transfer block count changed')
check(len({row['id'] for row in contract['transfer']}) == 85, 'canonical transfer ids must be unique')
for p in list((ROOT / 'source').rglob('*.html')) + list((ROOT / 'source/locales').glob('*.json')) + [ROOT / x for x in contract['outputs']]:
    check('philwirt@web.de' not in p.read_text(), str(p.relative_to(ROOT)) + ': stale public email')
for file in contract['outputs']:
    check('Philipp@achten.pro' in (ROOT / file).read_text(), file + ': confirmed public email missing')
# All newly integrated text nodes must have their actual EN mapping exercised.
for de, en in contract['added_translations']:
    check(de in text(pages['de']), 'new German copy absent: ' + de[:70])
    check(en in text(pages['en']), 'new English copy absent: ' + en[:70])
result = {'ok': not errors, 'checks': checks, 'transfer_blocks': len(contract['transfer']), 'testimonials_per_language': 3, 'errors': errors}
print(json.dumps(result, ensure_ascii=False, indent=2))
raise SystemExit(bool(errors))
