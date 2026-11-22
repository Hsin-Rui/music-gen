"""Round-3 selector: one test per I/O matrix row of docs/plan-harmony-first-round3.md, plus DoC and playability.

    uv run --with pytest pytest -q tests/test_round3.py
"""
import json
import sys
from pathlib import Path

import pretty_midi
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "steps"))
import chart as C  # noqa: E402
import metrics as M  # noqa: E402
import round3 as R  # noqa: E402

BEAT = 0.5  # 120 bpm, 4/4
CHART = {"key": "C major", "meter": "4/4", "beats_per_bar": 4,
         "bars": [[["C", 4]], [["F", 4]], [["G", 4]], [["C", 4]]]}
MELODY = [72, 74, 76, 77, 77, 76, 74, 72, 74, 76, 74, 71, 72, 72, 72, 72]


def write_midi(path, notes, melody=False):
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    pm.time_signature_changes.append(pretty_midi.TimeSignature(4, 4, 0))
    inst = pretty_midi.Instrument(program=0, name="melody" if melody else "acc")
    inst.notes = [pretty_midi.Note(80, p, s, e) for s, e, p in notes]
    pm.instruments.append(inst)
    pm.write(str(path))
    return path


@pytest.fixture
def melody(tmp_path):
    return write_midi(tmp_path / "input.mid", [(i * BEAT, (i + 1) * BEAT, p) for i, p in enumerate(MELODY)], True)


def good_acc():
    """Bass on beat 1 + broken chord tones on beats 2-4: follows the chart, not the block prompt."""
    roots = [48, 53, 55, 48]
    out = []
    for b, r in enumerate(roots):
        t = b * 4 * BEAT
        third = r + 4  # all three chords are major
        out.append((t, t + 4 * BEAT, r - 12))
        for j, p in enumerate([r + 7, third + 12, r + 12]):
            s = t + (j + 1) * BEAT + BEAT / 2
            out.append((s, s + BEAT / 2, p))
    return out


def scored(melody, path):
    rec = {"k": 0, **M.compute_r3(melody, CHART, path)}
    rec["gates"] = M.gates_r3(rec, 4)
    return rec


def test_normal_cell_passer_wins(melody, tmp_path):
    good = scored(melody, write_midi(tmp_path / "good.mid", good_acc()))
    assert all(good["gates"].values()), good
    prompt = [(s, e, p) for s, e, p, _ in C.block_notes(CHART, BEAT)]
    copyc = {**scored(melody, write_midi(tmp_path / "copy.mid", prompt)), "k": 1}
    assert not copyc["gates"]["prompt_copy"]
    sel = M.select_r3([good, copyc], selectable=True)
    assert sel == {"chosen": 0, "fallback": False, "passers": 1, "selected": True}
    assert good["ranks"] == {"prompt_sim": 1, "rules": 1, "bass_ok": 1} and good["borda"] == 3
    assert copyc["ranks"] is None and copyc["failed"] == ["prompt_copy"]


def test_no_passer_falls_back_to_fewest_failed_gates():
    def cand(k, failed, sim):
        return {"k": k, "notes": 20, "prompt_sim": sim, "rules": 0.1, "bass_ok": 0.5,
                "gates": {g: g not in failed for g in M.R3_GATES}}
    cs = [cand(0, ["prompt_copy", "playable"], 0.1), cand(1, ["playable"], 0.4), cand(2, ["chord_fit"], 0.3)]
    sel = M.select_r3(cs, selectable=True)
    assert sel["fallback"] is True and sel["passers"] == 0
    assert sel["chosen"] == 2  # same Borda as k1, broken by lower prompt_sim
    assert cs[0]["ranks"] is None and cs[1]["pool"] and cs[2]["pool"]


def test_empty_and_broken_candidates_fail_enough_notes(melody, tmp_path):
    empty = write_midi(tmp_path / "cand-0.mid", [])
    broken = tmp_path / "cand-1.mid"
    broken.write_bytes(b"not a midi file")
    good = write_midi(tmp_path / "cand-2.mid", good_acc())
    cands = R.score_candidates(melody, CHART, [empty, broken, good], 4)
    assert cands[0]["notes"] == 0 and not cands[0]["gates"]["enough_notes"]
    assert "error" in cands[1] and not cands[1]["gates"]["enough_notes"]
    sel = M.select_r3(cands, selectable=True)
    assert sel["chosen"] == 2 and not sel["fallback"]


def make_round2(root, melody_src, model, files, best=0):
    mdir = root / "tune"
    (mdir / "harmony").mkdir(parents=True, exist_ok=True)
    (mdir / "input.mid").write_bytes(Path(melody_src).read_bytes())
    C.save({**CHART}, mdir / "harmony" / "llm.json")
    cd = mdir / "llm" / model / "candidates"
    cd.mkdir(parents=True)
    for i, notes in enumerate(files):
        write_midi(cd / f"cand-{i}.mid", notes)
    (cd / "scores.json").write_text(json.dumps({"best": best, "candidates": [{"k": i} for i in range(len(files))]}))
    return cd


def test_llm_cell_is_scored_not_selected(melody, tmp_path):
    src, out = tmp_path / "src", tmp_path / "out"
    make_round2(src, melody, "claude", [good_acc()])
    rec = R.process_cell("tune", "llm", "claude", src, out, render=False)
    assert rec["missing"] is False and rec["selected"] is False and rec["fallback"] is False
    assert rec["chosen"] == 0 and rec["old_chosen"] == 0
    assert rec["candidates"][0]["gates"]["enough_notes"]
    assert (out / "tune" / "llm" / "claude" / "accompaniment.mid").exists()


def test_missing_cell_is_marked_and_others_continue(melody, tmp_path, capsys):
    src, out = tmp_path / "src", tmp_path / "out"
    cd = make_round2(src, melody, "amt", [[], good_acc()], best=1)
    before = (cd / "scores.json").read_bytes()
    cells = R.run_cells(["tune"], src, out, render=False)
    assert len(cells) == len(R.R3_SOURCES) * len(R.R3_MODELS)
    amt = next(c for c in cells if c["source"] == "llm" and c["model"] == "amt")
    assert not amt["missing"] and amt["chosen"] == 1 and amt["old_chosen"] == 1 and amt["selected"]
    missing = [c for c in cells if c["missing"]]
    assert len(missing) == len(cells) - 1 and all(c["reason"] for c in missing)
    assert "new 1 / old 1 / passers 1/2" in capsys.readouterr().out
    assert (cd / "scores.json").read_bytes() == before  # round-2 files are only read


def test_prompt_against_itself_has_doc_one(melody, tmp_path):
    prompt = [(s, e, p) for s, e, p, _ in C.block_notes(CHART, BEAT)]
    r = M.compute_r3(melody, CHART, write_midi(tmp_path / "p.mid", prompt))
    assert r["prompt_doc"] == 1.0 and r["prompt_f1"] == 1.0 and r["groove_cos"] == 1.0
    assert r["prompt_sim"] == 1.0 and r["bass_ok"] == 1.0 and r["chord_match"] == 1.0


def test_two_hand_playability(melody, tmp_path):
    def play(pitches):
        return M._playable([pretty_midi.Note(80, p, 0.0, 1.0) for p in pitches])[0]
    assert play([36, 43, 60, 64, 67])          # left-hand fifth + right-hand triad
    assert play([36, 40, 43, 48, 60, 64, 67, 72])  # four notes per hand
    assert play([60, 61, 62, 63, 64, 65])      # six notes in one span: 3 + 3 with two hands
    assert not play([60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77])  # 11 notes: more than 5 per hand
    assert not play([24, 26, 48, 50, 72, 74])  # would need three hands
    assert play([36, 55, 60, 64, 67])          # split at the 19-semitone gap: [36] + [55..67]
    assert not play([36, 52, 70])              # every split leaves a part wider than 14 semitones
