#!/usr/bin/env python3
"""Latest approved two-path copy contract; no network or submissions."""
import json,re,subprocess
from pathlib import Path
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1]
class T(HTMLParser):
 def __init__(self): super().__init__();self.skip=0;self.words=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style'): self.skip+=1
 def handle_endtag(self,tag):
  if tag in ('script','style'):self.skip-=1
 def handle_data(self,data):
  if not self.skip:self.words.append(data)
errors=[]
need={
'de':['Körper Geist Meisterung','Körperlich stärker werden. Bewusster mit dir selbst umgehen.','Dich ausrichten. Vertrauen entwickeln. Dein Können abrufen.','Ich begleite dich so, wie du es brauchst.','Kraft aufbauen, Ausdauer ausbauen, Koordination und Beweglichkeit entwickeln.','Auf Wunsch können wir uns auf Yoga oder Selbstverteidigung konzentrieren.','Wirst du in wichtigen Momenten hektisch oder kommst nicht richtig in Schwung?','Bringen dich Fehler, Rückschläge oder unerwartete Veränderungen aus dem Tritt?','HRV','Anruf oder Videochat'],
'en':['Body Mind Mastery','Become physically stronger. Develop a more conscious relationship with yourself.','Find your direction. Develop confidence. Put your abilities into action.','I support you in the way you need.','Build strength and endurance, develop coordination and mobility.','If you wish, we can focus on yoga or self-defence.','Do you become restless in important moments, or struggle to get going?','Do mistakes, setbacks or unexpected changes throw you off balance?','HRV','phone or video call']}
for lang,file in [('de','index.html'),('en','en/index.html')]:
 raw=(R/file).read_text();p=T();p.feed(raw);text=' '.join(' '.join(p.words).split())
 for token in need[lang]:
  if token not in text:errors.append(file+': missing '+token)
 for bad in ['Athletik','Schnelligkeit','Grappling','Strength & Performance','Performance Coaching','60–75','Aus der Ruhe in deine Kraft']:
  if bad.lower() in text.lower():errors.append(file+': superseded '+bad)
 cards=re.findall(r'<article class="choice (pt|psy)"',raw)
 if cards!=['pt','psy']:errors.append(file+': wrong card order '+str(cards))
 if raw.count('class="hrv-note"')!=2:errors.append(file+': HRV not in both offers')
 if raw.count('class="offer-photo"')!=2:errors.append(file+': confirmed offer photos missing')
result={'ok':not errors,'errors':errors};print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
