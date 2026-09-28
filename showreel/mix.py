"""Mixes voice, music bed and sound effects onto the rendered picture -> out/uphill_showreel_9x16.mp4"""
import subprocess, os
import imageio_ffmpeg

FF = os.environ.get('FFMPEG') or imageio_ffmpeg.get_ffmpeg_exe()
VO = 0.6
A = 'assets/'
# (file, time in s, volume)
SFX = [
    ('sfx_hit', .36, .9), ('sfx_pop', .62, .6), ('sfx_whoosh2', 2.40, .55), ('sfx_hit', 4.28, .35),
    *[('sfx_click', 4.91 + i * .32, .45) for i in range(6)],
    ('sfx_poof', 7.95, .8), ('sfx_whoosh', 8.66, .7), ('sfx_hit', 9.97, .85),
    ('sfx_pop', 11.95, .6), *[('sfx_click', 12.25 + i * .12, .4) for i in range(3)],
    ('sfx_whoosh2', 12.68, .5), ('sfx_whoosh2', 15.72, .5),
    ('sfx_pop', 17.35, .45), ('sfx_pop', 17.96, .45), ('sfx_pop', 18.80, .45),
    ('sfx_whoosh', 19.12, .6), *[('sfx_click', 21.25 + i * .2, .45) for i in range(3)],
    ('sfx_whoosh2', 22.42, .5), ('sfx_hit', 25.02, .8), ('sfx_sting', 25.95, .7),
]
inputs = ['-i', 'out/frames.mp4', '-i', 'out/music.wav', '-i', A + 'vo.mp3']
for f, _, _ in SFX: inputs += ['-i', A + f + '.mp3']
fc = [f'[2:a]aresample=48000,adelay={int(VO*1000)}|{int(VO*1000)},volume=2.4,apad=whole_dur=29.5,asplit=2[vo][key]',
      '[1:a]volume=0.3[mus]',
      '[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=280[duck]']
labels = []
for i, (f, t, v) in enumerate(SFX):
    ms = int(t * 1000)
    fc.append(f'[{i+3}:a]aresample=48000,volume={v},adelay={ms}|{ms}[s{i}]'); labels.append(f'[s{i}]')
fc.append(f'[vo][duck]{"".join(labels)}amix=inputs={2+len(SFX)}:normalize=0:duration=longest,'
          'loudnorm=I=-14:TP=-1.0:LRA=11,atrim=0:29.5[aout]')
cmd = [FF, '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]',
       '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest',
       'out/uphill_showreel_9x16.mp4']
subprocess.run(cmd, check=True)
print('done')
