#!/usr/bin/env python3
"""Regression contract for the two independent DE/EN offers (no network)."""
import json, re, subprocess
from pathlib import Path
from html.parser import HTMLParser
ROOT = Path(__file__).resolve().parents[1]
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.blocked=0; self.text=[]; self.forms=0; self.mail=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('style','script'): self.blocked+=1
        if tag=='form': self.forms+=1
        if tag=='a' and (a.get('href') or '').startswith('mailto:'): self.mail.append(a['href'])
    def handle_endtag(self,tag):
        if tag in ('style','script'): self.blocked-=1
    def handle_data(self,data):
        if not self.blocked: self.text.append(data)
errors=[]
# Protect all out-of-scope files and the unchanged embedded legal/Playfight copy.
import hashlib
contract=json.loads((ROOT/'tests/offer_protected.json').read_text())
for file,expected in contract['files'].items():
    raw_bytes=(ROOT/file).read_bytes()
    # RC1 permits only the explicitly requested public contact substitution.
    restored=raw_bytes.replace(b'Philipp@achten.pro',b'philwirt@web.de')
    if hashlib.sha256(raw_bytes).hexdigest()!=expected and hashlib.sha256(restored).hexdigest()!=expected: errors.append('protected file changed beyond contact substitution: '+file)
for file,blocks in contract['blocks'].items():
    raw=(ROOT/file).read_bytes().decode('utf-8')
    for label,item in blocks.items():
        match=re.search(item['pattern'],raw,re.S)
        if label=='impressum' and match:
            normalized=match[0].replace('<a href="mailto:Philipp@achten.pro">Philipp@achten.pro</a>','Philipp@achten.pro')
            match=re.search(item['pattern'],normalized,re.S)
        if not match or (hashlib.sha256(match[0].encode()).hexdigest()!=item['sha256'] and hashlib.sha256(match[0].replace('Philipp@achten.pro','philwirt@web.de').encode()).hexdigest()!=item['sha256']): errors.append('protected block changed beyond contact substitution: '+file+':'+label)
for lang,file in [('de','index.html'),('en','en/index.html')]:
    raw=(ROOT/file).read_text(); p=Text(); p.feed(raw); text=' '.join(' '.join(p.text).split())
    for id in ('sportpsychologie','personal-training','angebot','kontakt','impressum','playfight'):
        if f'id="{id}"' not in raw: errors.append(f'{file}: missing {id}')
    for id,price in [('sportpsychologie','85'),('personal-training','80')]:
        match=re.search(r'<section\b[^>]*id="'+id+r'"[^>]*>(.*?)</section>',raw,re.S)
        if not match: continue
        q=Text(); q.feed(match[1]); offer=' '.join(q.text)
        if not re.search(r'60 (Minuten|minutes)',offer) or price+' €' not in offer: errors.append(f'{file}: {id} price/duration')
    claim_raw=re.sub(r'<section id="testimonials"[^>]*>.*?</section>','',raw,flags=re.S)
    claim_parser=Text(); claim_parser.feed(claim_raw); claims=' '.join(claim_parser.text)
    for bad in (r'Q3',r'60[–-]75',r'\b(?:45|75) (?:Minuten|minutes)',r'Panikattack',r'panic attack',r'Launch.phase',r'kostenloses Erstgespräch',r'free intro call'):
        if re.search(bad,claims,re.I): errors.append(f'{file}: forbidden {bad}')
    if claims.count('Performance & Recovery')!=1 or 'Performance & Recovery Specialist' in claims: errors.append(f'{file}: scope chip must not become a qualification claim')
    studio='My Private Gym, Plinganserstraße 132, 81369 München (Obersendling/Thalkirchen)'
    if claims.count(studio)!=3: errors.append(f'{file}: studio must appear exactly in intro PT, PT facts, contact PT')
    sp=re.search(r'<section id="sportpsychologie"[^>]*>(.*?)</section>',raw,re.S)[1]
    if 'Private Gym' in sp: errors.append(f'{file}: studio incorrectly assigned to sport psychology')
    if p.forms!=1 or 'id="inquiryForm"' not in raw or 'formspree' in raw.lower(): errors.append(f'{file}: expected exactly one local-only inquiry helper')
    if len(p.mail)!=9 or p.mail.count('mailto:Philipp@achten.pro')!=1 or any(not x.startswith('mailto:Philipp@achten.pro?subject=') for x in p.mail if x!='mailto:Philipp@achten.pro'): errors.append(f'{file}: wrong explicit contact links')
    if 'Für Philipp' in text or 'Freigabestand' in text or 'lokale Vorschau' in text: errors.append(f'{file}: internal QA copy leaked')
    if lang=='en' and re.search(r'\b(Minuten|Verletzungspause|Schreib mir|Körperlich|Dein Anliegen)\b',text): errors.append(f'{file}: German offer residue')
result={'ok':not errors,'errors':errors}
print(json.dumps(result,ensure_ascii=False,indent=2)); raise SystemExit(bool(errors))
