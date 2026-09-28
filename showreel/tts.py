import json,sys,base64,urllib.request
import os
K=os.environ["ELEVENLABS_API_KEY"]
voice=sys.argv[1]; out=sys.argv[2]
text=open('script.txt',encoding='utf8').read().strip()
body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","language_code":"de",
 "voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.45,"use_speaker_boost":True,"speed":1.1}}).encode()
r=urllib.request.Request(f"https://api.us.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",data=body,headers={"xi-api-key":K,"Content-Type":"application/json"})
try: d=json.load(urllib.request.urlopen(r))
except urllib.error.HTTPError as e: print(e.read()[:400]); sys.exit(1)
open(out+'.mp3','wb').write(base64.b64decode(d['audio_base64']))
json.dump(d['alignment'],open(out+'.json','w'))
a=d['alignment']; print(out, a['character_end_times_seconds'][-1])
