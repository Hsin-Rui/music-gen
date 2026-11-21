"""Small shared MIDI helpers (pretty_midi only, so usable from every env)."""


def first_melody_track(pm):
    """Return (instrument, warnings): first non-drum track with notes."""
    tracks = [i for i in pm.instruments if not i.is_drum and i.notes]
    if not tracks:
        raise SystemExit("no non-drum notes in MIDI")
    warnings = []
    if len(tracks) > 1:
        warnings.append(f"input has {len(tracks)} non-drum tracks; using the first "
                        f"({tracks[0].name!r}) as melody")
    return tracks[0], warnings


def all_notes(pm):
    """All non-drum notes of a MIDI, onset-ordered."""
    notes = [n for i in pm.instruments if not i.is_drum for n in i.notes]
    return sorted(notes, key=lambda n: (n.start, n.pitch))
