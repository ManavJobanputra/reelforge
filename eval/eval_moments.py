"""Validate Gemini moment-selection output saved as JSON files.

Usage: python eval/eval_moments.py responses/*.json
Each file holds the raw text Gemini returned for one video (code fences allowed).
Reports: valid-JSON rate, 30-60s duration compliance, and non-overlap rate.
"""
import json
import sys


def parse_response(raw: str):
    """Mirror main.py: strip ```json fences, then json.loads. Returns list or None."""
    text = raw.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None
    return data


def check_clips(clips, min_len=30.0, max_len=60.0):
    """Return (n_clips, n_duration_ok, overlap_free) for one response."""
    valid = [c for c in clips if isinstance(c, dict) and "start" in c and "end" in c]
    dur_ok = sum(1 for c in valid if min_len <= (c["end"] - c["start"]) <= max_len)
    ordered = sorted(valid, key=lambda c: c["start"])
    overlap_free = all(a["end"] <= b["start"] for a, b in zip(ordered, ordered[1:]))
    return len(valid), dur_ok, overlap_free


def main(paths):
    n_files = parsed = clips_total = dur_ok_total = overlap_free_files = 0
    for p in paths:
        n_files += 1
        with open(p, encoding="utf-8") as f:
            clips = parse_response(f.read())
        if clips is None:
            continue
        parsed += 1
        n, ok, free = check_clips(clips)
        clips_total += n
        dur_ok_total += ok
        overlap_free_files += int(free)
    print(f"responses: {n_files}")
    print(f"valid JSON list: {parsed}/{n_files}")
    if clips_total:
        print(f"clips in 30-60s: {dur_ok_total}/{clips_total}")
    if parsed:
        print(f"overlap-free responses: {overlap_free_files}/{parsed}")


if __name__ == "__main__":
    main(sys.argv[1:])
