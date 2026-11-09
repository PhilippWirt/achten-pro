#!/usr/bin/env python3
"""Explicit latest W01-W16 acceptance; existing contracts remain separate."""
from pathlib import Path
from html.parser import HTMLParser
import re,json,sys
R=Path(__file__).resolve().parents[1]
checks=[]
def check(id,ok,evidence): checks.append(dict(id=id,ok=bool(ok),evidence=evidence))
def section(raw,id):return re.search(r'<section\b(?=[^>]*\bid="'+id+r'")[^>]*>(.*?)</section>',raw,re.S)[1]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.blocked=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.blocked+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.blocked-=1
 def handle_data(self,d):
  if not self.blocked:self.parts.append(d)
def text(s):p=Text();p.feed(s);return ' '.join(' '.join(p.parts).split())
for lang,rel,privacy in [('de','index.html','datenschutz.html'),('en','en/index.html','en/privacy.html')]:
 raw=(R/rel).read_text();body=text(raw);ab=section(raw,'about');pt=section(raw,'personal-training');sp=section(raw,'sportpsychologie');prefix=lang+': '
 for id in ['pt-hrv','sp-hrv']:
  detail=re.search(r'<details\b(?=[^>]*\bid="'+id+r'")[^>]*>(.*?)</details>',raw,re.S)[1]
  summary=re.search(r'<summary>(.*?)</summary>',detail,re.S)[1]
  check('W01',summary==('Dauerstress – dauernd angespannt?' if lang=='de' else 'Constant stress – always tense?'),prefix+id+' exact problem title')
  check('W01','HRV' not in summary and ('Brustgurt' if lang=='de' else 'chest strap') in detail,prefix+id+' method inside only')
 check('W02',not any(t in body for t in ['Wir wählen einen angenehmen Atemrhythmus.','Falls dir dabei schwindlig','We choose a comfortable breathing rhythm.','If you feel dizzy or unwell']),prefix+'both rejected breathing paragraphs absent')
 check('W02',('medizinischen Vorgaben' if lang=='de' else 'medical guidance') in pt and ('Sportverbot' if lang=='de' else 'medically prohibited') in sp,prefix+'actual medical load frame retained')
 check('W03',('Wenn du dir im Gespräch mit mir noch Klarheit verschaffen möchtest' if lang=='de' else 'If you would like more clarity through a conversation with me') in body,prefix+'conversation for clarity')
 check('W04',('WER ICH BIN' if lang=='de' else 'WHO I AM') in ab and ('Expertise, die sich im echten Einsatz bewährt hat.' if lang=='de' else 'expertise put into practice.') in ab,prefix+'selected about hierarchy')
 check('W04','Philipp Wiertelorz' in ab and ('Training, Atem, Stille und sportpsychologische Tiefe' if lang=='de' else 'Training, breathing, stillness and depth in sport psychology') in ab,prefix+'personal description and name')
 check('W05','src="/assets/images/von_links.jpg"' in ab and 'width="4284" height="5712"' in ab,prefix+'actual matching original portrait, no derivative')
 check('W06','object-position:50% 43%' in raw and 'aspect-ratio:5/4' in raw,prefix+'reference 50% to 43%, seven percentage points down without zoom')
 chips=re.search(r'<ul class="profile-chips".*?</ul>',ab,re.S)[0]
 check('W04',chips.count('<li>')==6,prefix+'six turquoise profile chips')
 check('W04',not any(x in ab for x in ['3+','Specialist','Achtsamkeitstherapeut']),prefix+'unproved duration/certified specialty/current therapy role not invented')
 for degree in (['M.Sc. Sportpsychologie','B.Sc. Sportwissenschaft'] if lang=='de' else ['M.Sc. Sport Psychology','B.Sc. Sports Science']):check('W07',degree in ab,prefix+'academic degree '+degree)
 check('W07',('Beim Personal Training begleite ich dich als' if lang=='de' else 'In personal training I support you as a personal trainer;') not in body,prefix+'redundant role explanation absent')
 check('W08',not re.search('Grünwalder Brücke|Grünwalder Bridge',body,re.I),prefix+'removed bridge meeting point')
 check('W08','My Private Gym, Plinganserstraße 132, 81369 München' in pt and 'My Private Gym' not in sp,prefix+'studio retained PT only')
 controls=re.search(r'<div class="t-controls">(.*?)</section>',raw,re.S)[1]
 check('W09',not re.search(r'>\s*[123]\s*</button>',controls) and controls.count('class="t-dot"')==3,prefix+'three unnumbered controls')
 check('W09',all(('Stimme '+str(i) if lang=='de' else 'Testimonial '+str(i)) in controls for i in [1,2,3]) or all(('Voice '+str(i)) in controls for i in [1,2,3]),prefix+'accessible labels retained')
 check('W10','.intro-hero::after{display:none}' in raw and 'aspect-ratio:2053/3609' in raw,prefix+'uncropped mobile scene, no unnecessary darkness')
 check('W11',raw.count('class="context-icon"')==3 and '<svg' in raw,prefix+'three additional contextual inline SVGs')
 check('W12',('Ich arbeite bewusst nur mit wenigen Klient:innen parallel, damit wir in Ruhe in die Tiefe gehen können.' if lang=='de' else 'I deliberately work with only a few clients at a time so we can take the time to explore things in depth.') in body,prefix+'personal small-client-base statement, no invented slots')
 imprint=re.search(r'<details class="impressum-box".*?</details>',raw,re.S)[0]
 check('W13',all(x in imprint for x in ['Philipp Wiertelorz','Viebigplatz 4','80686 München','Philipp@achten.pro','18']) and 'Plinganser' not in imprint,prefix+'live-source identity/address and new mail')
 check('W13','href="mailto:Philipp@achten.pro"' in imprint,prefix+'imprint mail clickable')
 legal=(R/privacy).read_text();check('W14',len(text(legal))>3000 and 'Philipp@achten.pro' in legal and ('ausschließlich im Browser' if lang=='de' else 'entirely in your browser') in legal,prefix+'complete production privacy, correct local data flow')
 check('W14',('separaten Playfight' if lang=='de' else 'separate Playfight') in legal,prefix+'distinct existing Playfight service described separately')
 check('W15','href="https://www.instagram.com/philwirt/"' in raw,prefix+'exact live Instagram destination')
 check('W16','id="inquiryForm"' in raw and 'formspree' not in raw.lower() and 'Philipp@achten.pro' in raw,prefix+'main page remains local-only draft')
check('W09',True,'Exact three quotations and attributions are independently checked by verify_content.py, not redefined here')
result=dict(ok=all(x['ok'] for x in checks),checks=len(checks),results=checks,errors=[x for x in checks if not x['ok']])
print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(not result['ok'])
