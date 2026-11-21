"""Write three short public-domain melodies as single-track, quantized MIDI.

- ode_to_joy.mid    Beethoven, Symphony No. 9 (1824), D major, 4/4
- greensleeves.mid  English folk tune (16th c.), A minor, 3/4
- jasmine.mid       茉莉花, Chinese folk tune (18th c.), F major pentatonic, 2/4

Usage: uv run examples/make_examples.py
"""
from pathlib import Path

import pretty_midi

HERE = Path(__file__).parent

# Each melody: list of (midi pitch or None for rest, duration in beats).
# Jianpu degree helper for the major-key tunes.
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def deg(tonic, d, octave=0):
    return tonic + MAJOR[d - 1] + 12 * octave


def ode_to_joy():
    D = 62  # D4
    q = lambda d, o=0: (deg(D, d, o), 1.0)
    a = [q(3), q(3), q(4), q(5), q(5), q(4), q(3), q(2), q(1), q(1), q(2), q(3)]
    end1 = [(deg(D, 3), 1.5), (deg(D, 2), 0.5), (deg(D, 2), 2.0)]
    end2 = [(deg(D, 2), 1.5), (deg(D, 1), 0.5), (deg(D, 1), 2.0)]
    b = [q(2), q(2), q(3), q(1),
         q(2), (deg(D, 3), .5), (deg(D, 4), .5), q(3), q(1),
         q(2), (deg(D, 3), .5), (deg(D, 4), .5), q(3), q(2),
         q(1), q(2), (deg(D, 5, -1), 2.0)]
    return a + end1 + a + end2 + b + a + end2, 132, (4, 4), "D"


def greensleeves():
    A4, B4, C5, D5, E5, F5, G4, Gs4, Fs4, E4 = 69, 71, 72, 74, 76, 77, 67, 68, 66, 64
    phrase = [(C5, 2), (D5, 1), (E5, 1.5), (F5, .5), (E5, 1), (D5, 2), (B4, 1),
              (G4, 1.5), (A4, .5), (B4, 1)]
    mel = [(None, 2), (A4, 1)] + phrase + [
        (C5, 2), (A4, 1), (A4, 1.5), (Gs4, .5), (A4, 1), (B4, 2), (Gs4, 1), (E4, 2), (A4, 1),
    ] + phrase + [
        (C5, 1.5), (B4, .5), (A4, 1), (Gs4, 1.5), (Fs4, .5), (Gs4, 1), (A4, 3), (A4, 3),
    ]
    return mel, 120, (3, 4), "Am"


def jasmine():
    F = 65  # F4 = do
    n = lambda d, b, o=0: (deg(F, d, o), b)
    b1 = [n(3, .5), n(3, .25), n(5, .25), n(6, .25), n(1, .25, 1), n(1, .25, 1), n(6, .25)]
    b2 = [n(5, .5), n(5, .25), n(6, .25), n(5, 1)]
    rest = [
        n(5, .5), n(5, .5), n(5, .5), n(3, .25), n(5, .25),
        n(6, .5), n(6, .5), n(5, 1),
        n(3, .5), n(2, .25), n(3, .25), n(5, .5), n(3, .25), n(2, .25),
        n(1, .5), n(1, .25), n(2, .25), n(1, 1),
        n(3, .25), n(2, .25), n(1, .25), n(3, .25), n(2, .75), n(3, .25),
        n(5, .5), n(6, .25), n(1, .25, 1), n(5, 1),
        n(2, .5), n(3, .25), n(5, .25), n(2, .25), n(3, .25), n(1, .25), n(6, .25, -1),
        n(5, 2, -1),
        n(6, .5, -1), n(1, .5), n(2, .5), n(3, .25), n(2, .25),
        n(1, 2),
    ]
    return b1 + b2 + b1 + b2 + rest, 72, (2, 4), "F"


def write(name, notes, bpm, ts, key):
    pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
    pm.time_signature_changes.append(pretty_midi.TimeSignature(ts[0], ts[1], 0))
    pm.key_signature_changes.append(
        pretty_midi.KeySignature(pretty_midi.key_name_to_key_number(
            key[0] + (" minor" if key.endswith("m") else " Major")), 0))
    inst = pretty_midi.Instrument(program=0, name="melody")
    spb = 60.0 / bpm
    t = 0.0
    beats = 0.0
    for pitch, dur in notes:
        if pitch is not None:
            inst.notes.append(pretty_midi.Note(80, pitch, t, t + dur * spb * 0.95))
        t += dur * spb
        beats += dur
    assert abs(beats / ts[0] - round(beats / ts[0])) < 1e-6, f"{name}: {beats} beats not whole bars"
    pm.instruments.append(inst)
    out = HERE / f"{name}.mid"
    pm.write(str(out))
    print(f"{out.name}: {len(inst.notes)} notes, {beats / ts[0]:.0f} bars, {t:.1f}s")


if __name__ == "__main__":
    write("ode_to_joy", *ode_to_joy())
    write("greensleeves", *greensleeves())
    write("jasmine", *jasmine())
