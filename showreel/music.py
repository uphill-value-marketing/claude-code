"""Synthesises the 120 BPM music bed for the showreel (music.wav, 48 kHz stereo).
Arrangement is locked to the picture: groove -> breakdown (pain scene) -> drop on the brand reveal -> outro."""
import numpy as np
from scipy.signal import butter, sosfilt
import wave

SR = 48000
DUR = 29.5
T0 = 0.42            # first downbeat = intro impact
BEAT = 0.5           # 120 BPM
BREAK_A, BREAK_B = 4.71, 8.75   # breakdown under the pain scene
END = 26.09          # end card
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)

def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def put(sig, t, gl=1.0, gr=None):
    i = int(t * SR)
    if i >= N or i < 0: return
    s = sig[:N - i]; L[i:i + len(s)] += s * gl; R[i:i + len(s)] += s * (gl if gr is None else gr)
def saw(f, d, det=0.0):
    t = np.arange(int(d * SR)) / SR
    return 2 * ((t * f * (1 + det)) % 1) - 1
rng = np.random.default_rng(7)

def kick(d=.45, amp=1.0):
    t = np.arange(int(d * SR)) / SR
    f = 50 + 110 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) * amp
def clap():
    t = np.arange(int(.25 * SR)) / SR
    n = rng.standard_normal(len(t)); env = np.exp(-t * 22) + .6 * np.exp(-((t - .012) * 400) ** 2)
    return hp(lp(n, 3000), 900) * env * .5
def hat(open_=False):
    t = np.arange(int((.18 if open_ else .05) * SR)) / SR
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * (18 if open_ else 70)) * .22

NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
# D major: D  A  Bm  G   (2 s each = one bar)
CHORDS = [[62, 66, 69, 74], [61, 64, 69, 73], [62, 66, 71, 74], [62, 67, 71, 74]]
ROOTS = [38, 33, 35, 31]

def in_break(t): return BREAK_A <= t < BREAK_B

t = T0; beat = 0
while t < END + 0.01:
    bar = int(beat // 4); ch = CHORDS[bar % 4]; root = ROOTS[bar % 4]
    if beat % 4 == 0:  # pad chord every bar
        dur = 2.0 if t < END - .01 else 3.4
        pad = sum(saw(NOTE(m), dur, d) for m in ch for d in (-.004, 0, .004)) / 12
        env = np.minimum(1, np.arange(len(pad)) / (SR * .08)) * np.exp(-np.arange(len(pad)) / SR * (.4 if t < END - .01 else 1.1))
        cut = 900 if in_break(t) else 2400
        pad = lp(pad * env, cut) * (.55 if in_break(t) else .32)
        put(pad, t, .9, 1.0)
    if t >= END - .01:
        put(kick(.9, 1.1), t); break
    if not in_break(t):
        put(kick(), t, .95)
        if beat % 2 == 1 and t > BREAK_B: put(clap(), t, .8, 1.0)
        for k in range(2):  # 8th hats
            put(hat(k == 1 and beat % 2 == 1), t + k * BEAT / 2, .7, 1.0)
        for k in range(2):  # 8th-note bass pluck
            b = saw(NOTE(root + (12 if k else 0)), .22)
            b = lp(b * np.exp(-np.arange(len(b)) / SR * 14), 600) * .5
            put(b, t + k * BEAT / 2)
        if t > BREAK_B:  # 16th arp on the drop
            for k in range(4):
                m = ch[(beat * 4 + k) % 4] + 12
                a = np.sin(2 * np.pi * NOTE(m) * np.arange(int(.12 * SR)) / SR) * np.exp(-np.arange(int(.12 * SR)) / SR * 30) * .1
                put(a, t + k * BEAT / 4, .6 if k % 2 else 1.0, 1.0 if k % 2 else .6)
    else:
        if beat % 2 == 0: put(kick(.3, .45), t)   # heartbeat
    t += BEAT; beat += 1

# riser into the drop (noise sweep)
d = BREAK_B - 7.8; n = rng.standard_normal(int(d * SR)); tt = np.arange(len(n)) / SR
riser = hp(n, 400) * (tt / d) ** 2 * .3
put(riser, 7.8)

mix = np.stack([L, R], 1)
fade = np.ones(N); fi = int((DUR - 1.2) * SR); fade[fi:] = np.linspace(1, 0, N - fi) ** 2
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) * 1.12
with wave.open('out/music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('music.wav written')
