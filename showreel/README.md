# upHill Value Marketing – Motion Showreel (9:16)

29,5 s Hochformat-Video (1080×1920, 30 fps) mit Maskottchen „Hilli“, deutschem Voiceover (ElevenLabs) und Sounddesign.

**Ergebnis:** `out/uphill_showreel_9x16.mp4`

## Aufbau
| Datei | Zweck |
|---|---|
| `index.html` | Komplette Animation als Canvas-Code (`render(t)` ist deterministisch). Im Browser öffnen = Live-Vorschau (lokalen Server nutzen, z. B. `python3 -m http.server`). |
| `render.js` | Rendert jeden Frame per Playwright (4-fach Motion Blur) → `out/frames.mp4` |
| `music.py` | Synthetisiert die 120-BPM-Musik passend zum Schnitt → `out/music.wav` |
| `mix.py` | Voice + Musik (Sidechain-Ducking) + SFX + Loudness (−14 LUFS) → finales MP4 |
| `tts.py`, `script.txt` | Voiceover mit Wort-Timestamps über ElevenLabs (Key per `ELEVENLABS_API_KEY`) |
| `assets/` | Schriften, Logo, Voice, SFX, Lip-Sync-/Timing-Daten (`data.json`) |

## Neu rendern
```bash
pip install numpy scipy imageio-ffmpeg
export FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
node render.js && python3 music.py && python3 mix.py
```
Stills zum Prüfen: `node render.js --stills 1.2,10.5,25.6`
