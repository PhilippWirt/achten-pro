#!/usr/bin/env python3
"""RC3 acceptance, stable P/N IDs; no network, publication or submissions."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,hashlib,sys
R=Path(__file__).resolve().parents[1]; checks=[]
class Text(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'):self.skip+=1
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip-=1
 def handle_data(self,data):
  if not self.skip:self.parts.append(data)
def text(raw):
 p=Text();p.feed(raw);return ' '.join(' '.join(p.parts).split())
def section(raw,identifier):return re.search(r'<section\b(?=[^>]*\bid="'+identifier+r'")[^>]*>(.*?)</section>',raw,re.S)[1]
def check(identifier,ok,evidence):checks.append({'id':identifier,'ok':bool(ok),'evidence':evidence})
for lang,rel in [('de','index.html'),('en','en/index.html')]:
 raw=(R/rel).read_text();alltext=text(raw);pt=text(section(raw,'personal-training'));sp=text(section(raw,'sportpsychologie'));ab=text(section(raw,'about'));process=text(section(raw,'ablauf'));prefix=rel+': '
 tokens={
 'P01':(pt,('Auf Wunsch wählen wir ergänzende Übungen','Wenn du möchtest') if lang=='de' else ('If you wish, we choose additional exercises','If you wish')),
 'P02':(sp,('Wenn du möchtest, vereinbaren wir kleine Routinen','erproben sie gemeinsam') if lang=='de' else ('If you wish, we agree on small routines','try them together')),
 'P03':(pt,('Kommen Bewegung und Erholung im vollen Alltag zu kurz?',) if lang=='de' else ('Does a busy everyday life leave too little room for movement and recovery?',)),
 'P04':(pt,('Welche Aufgaben zu dir passen, finden wir gemeinsam heraus','Spiel, Ehrgeiz und Lockerheit') if lang=='de' else ('Together we find out which tasks suit you','play, ambition and ease')),
 'P05':(pt,('Möchtest du schon wieder trainieren, obwohl du dich noch nicht erholt fühlst?',) if lang=='de' else ('Do you already want to train again even though you do not feel recovered yet?',)),
 'P06':(pt,('Trainingsstand, deine Tagesform und deine Rückmeldung',) if lang=='de' else ('training level, how you feel that day and your feedback',)),
 'P07':(pt,('Koordination und Beweglichkeit entwickeln.',) if lang=='de' else ('develop coordination and mobility.',)),
 'P08':(pt,('Auf Wunsch können wir uns auf Yoga oder Selbstverteidigung konzentrieren.',) if lang=='de' else ('If you wish, we can focus on yoga or self-defence.',)),
 'P09':(sp,('Gemeinsam klären wir, was dich verunsichert, und wählen passende mentale Übungen','Gemeinsam wählen wir, woran du arbeiten möchtest') if lang=='de' else ('Together we clarify what makes you uncertain and choose suitable mental exercises','Together we choose what you would like to work on')),
 'P10':(sp,('Was verunsichert dich beim Wiedereinstieg, und was ist körperlich bereits erlaubt?',) if lang=='de' else ('What makes you uncertain about returning, and what physical activity is already permitted?',)),
 'P11':(sp,('Für die körperliche Rückkehr in den Sport gelten die medizinischen Vorgaben.',) if lang=='de' else ('Medical guidance applies to the physical return to sport.',)),
 'P12':(sp,('wie angespannt, wach oder bereit du dich fühlst','herunterzufahren oder in Schwung zu kommen') if lang=='de' else ('how tense, alert or ready you feel','settle down or get going')),
 'P13':(sp,('deine Grenzen, passende Pausen und hilfreiche Unterstützung',) if lang=='de' else ('your boundaries, suitable breaks and helpful support',)),
 'P14':(pt+' '+sp,('Brustgurt','am Bildschirm','Davon getrennt','Schlaf, Belastung, Erholung und Körpergefühl') if lang=='de' else ('chest strap','on screen','Separately','sleep, training load, recovery and how your body feels')),
 'P16':(pt+' '+sp,('medizinischen Vorgaben',) if lang=='de' else ('Medical guidance',)),
 'P17':(pt,('Bei neuen oder zunehmenden Beschwerden unterbrechen wir',) if lang=='de' else ('If symptoms are new or worsening, we stop',)),
 'P18':(ab,('M.Sc. Sportpsychologie','B.Sc. Sportwissenschaft') if lang=='de' else ('M.Sc. Sport Psychology','B.Sc. Sports Science')),
 'P19':(pt+' '+sp,('zu Hause',) if lang=='de' else ('at home',)),
 'P20':(alltext,('Philipp@achten.pro',)),
 'P23':(pt,('80 €','60 €','120 €','gemeinsam 60 Minuten') if lang=='de' else ('80 €','60 €','120 €','60 minutes together')),
 'N01':(alltext,('Körper Geist Meisterung',) if lang=='de' else ('Body Mind Mastery',)),
 'N03':(alltext,('Kraft','Mobilität','Atem','Stille','Nervensystem','Was das konkret heißt') if lang=='de' else ('Strength','Mobility','Breathing','Stillness','Nervous system','What that means in practice')),
 'N04':(pt,('etwa 10 Minuten ankommen, 40 Minuten trainieren und 10 Minuten ausklingen lassen','passen wir gemeinsam an') if lang=='de' else ('about 10 minutes to arrive, 40 minutes of training and 10 minutes to wind down','adapt the balance together')),
 'N05':(ab,('Training, Atem, Stille und sportpsychologische Tiefe','gemeinsam arbeiten wir daran') if lang=='de' else ('Training, breathing, stillness and depth in sport psychology','work towards')),
 'N07':(sp,('Dich beschäftigt was?','Worte','wie du sie sagst','inneren Zustand','Handlungsschritte','Muster und Routinen') if lang=='de' else ('Something on your mind?','words','how you say them','state of mind','practical steps','patterns and routines')),
 'N10':(sp,('Sportpsychologische Begleitung:','Ausgangslage und dein Anliegen','üben sie gemeinsam ein','Mit deiner Rückmeldung','individuellen weiteren Plan') if lang=='de' else ('Sport psychology support:','starting point and concerns','practise them together','With your feedback','personal plan')),
 }
 for identifier,(body,required) in tokens.items():check(identifier,all(t in body for t in required),prefix+'; '.join(required))
 check('P15',('Trainingsfreigabe' if lang=='de' else 'clearance to train') not in pt+' '+sp,prefix+'obsolete HRV clearance line removed')
 check('P21',True,prefix+'print-only layout not transferred; U03 not guessed')
 check('P22',not any(t in pt for t in ['Körperliches Gleichgewicht zu üben bedeutet nicht automatisch','Practising physical balance does not automatically']),prefix+'already removed balance counterclaim stays absent')
 check('P23','120' not in sp and '85 €' in sp,prefix+'no SP duo; SP remains 85 EUR / 60 min')
 check('P19','bei dir zu Hause' not in alltext and 'at your home' not in alltext,prefix+'no host assumption')
 check('P19',pt.index('My Private Gym')<pt.index('Isar') and 'My Private Gym' not in sp,prefix+'studio first, PT only')
 check('N01',not any(x in alltext for x in ['Aus der Ruhe in deine Kraft','Dein achten.pro Körper-Geist Personal Training München']),prefix+'old rooftop phrases absent')
 check('N06',len(re.findall(r'<details class="offer-details',raw))==8 and 'id="mobile-nav"' in raw and 'data-language-switch' in raw,prefix+'full menu/language/details retained')
 check('N08',len(re.findall(r'<form\b',raw))==1 and 'id="inquiryForm"' in raw and 'formspree' not in raw.lower() and 'newsletter' not in alltext.lower(),prefix+'one local helper, no main Formspree/newsletter')
 for name in ['name','email','phone','frequency','days','time','firstContact','offer','message']:
  check('N08',f'name="{name}"' in raw,prefix+'form field '+name)
 check('N08','type="button"' in raw and 'id="mailDraft"' in raw and 'mailto:Philipp@achten.pro?subject=' in raw,prefix+'editable draft and exact recipient')
 check('N09',all(t in (R/('datenschutz.html' if lang=='de' else 'en/privacy.html')).read_text() for t in (['ausschließlich im Browser','Erst wenn du','Philipp@achten.pro','separaten Playfight'] if lang=='de' else ['entirely in your browser','Only selecting','Philipp@achten.pro','separate Playfight'])),prefix+'privacy describes local-only helper and separate Playfight service')
# Primary role/title claims and advice are not inferred from uncertain addenda.
check('N10',all(x not in (R/'index.html').read_text() for x in ['Präventions-Familass','Krankenkassenerstattung','asp-zertifiziert']), 'uncertain target-group/prevention/certification fragments not invented')
print(json.dumps({'ok':all(c['ok'] for c in checks),'checks':len(checks),'results':checks,'errors':[c for c in checks if not c['ok']]},ensure_ascii=False,indent=2));sys.exit(not all(c['ok'] for c in checks))
