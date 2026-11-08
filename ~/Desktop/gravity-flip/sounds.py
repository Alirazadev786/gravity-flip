"""Synthesized sound effects using numpy (no external audio files needed)."""
import numpy as np
import pygame

_sounds = {}
_initialized = False

def _synth(freq, dur, wave='sine', vol=0.5, decay=True, freq_end=None):
    sr = 22050
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    if freq_end is None:
        freq_end = freq
    f = np.linspace(freq, freq_end, n)
    phase = 2 * np.pi * np.cumsum(f) / sr
    if wave == 'sine':
        w = np.sin(phase)
    elif wave == 'square':
        w = np.sign(np.sin(phase))
    elif wave == 'triangle':
        w = 2 * np.abs(2 * (phase / (2*np.pi) - np.floor(phase / (2*np.pi) + 0.5))) - 1
    elif wave == 'saw':
        w = 2 * (phase / (2*np.pi) - np.floor(phase / (2*np.pi) + 0.5))
    else:
        w = np.sin(phase)
    if decay:
        env = np.exp(-3 * t / dur)
    else:
        env = np.ones(n)
    data = (w * env * vol * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(data)

def init():
    global _initialized
    if _initialized:
        return
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    except Exception:
        return
    _sounds['jump'] = _synth(400, 0.12, 'square', 0.3, freq_end=800)
    _sounds['flip'] = _synth(300, 0.2, 'sine', 0.4, freq_end=900)
    _sounds['coin'] = _synth(988, 0.08, 'square', 0.3, freq_end=1319)
    _sounds['death'] = _synth(400, 0.5, 'saw', 0.4, freq_end=80)
    _sounds['powerup'] = _synth(523, 0.15, 'triangle', 0.35, freq_end=784)
    _sounds['portal'] = _synth(200, 0.3, 'sine', 0.4, freq_end=1200)
    _sounds['spring'] = _synth(200, 0.15, 'square', 0.35, freq_end=600)
    _sounds['hit'] = _synth(150, 0.15, 'saw', 0.4, freq_end=60)
    _sounds['star'] = _synth(600, 0.1, 'triangle', 0.3, freq_end=1200)
    _sounds['boss_hit'] = _synth(100, 0.2, 'saw', 0.5, freq_end=40)
    _sounds['boss_roar'] = _synth(80, 0.6, 'saw', 0.5, freq_end=50)
    _sounds['win'] = _synth(523, 0.15, 'triangle', 0.4, freq_end=523)
    _sounds['win2'] = _synth(659, 0.15, 'triangle', 0.4, freq_end=659)
    _sounds['win3'] = _synth(784, 0.2, 'triangle', 0.4, freq_end=784)
    _sounds['shield'] = _synth(400, 0.2, 'sine', 0.4, freq_end=800)
    _sounds['dash'] = _synth(500, 0.1, 'saw', 0.3, freq_end=1000)
    _initialized = True

def play(name):
    if name in _sounds:
        _sounds[name].play()

def stop_all():
    for s in _sounds.values():
        s.stop()