#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Transcribe campaign audio with faster-whisper, biased toward local proper nouns.

    python tools/transcribe.py audio/chamber-interview-2026-09-01.mp3

Writes <name>.transcript.txt (plain text) and <name>.segments.json (timestamped)
next to the audio file.

Why this exists
---------------
YouTube's auto-captions rendered "Shakopee" ten different ways (Shakape,
Shakipi, Shakabby, Shockby...) and turned "Van Alstyne" into "Vanstein".
Whisper fixes most of that on its own, but only if it is told the vocabulary
first -- that is what tools/whisper-vocab.txt is for. The text in that file is
fed to the model as `initial_prompt`, which biases decoding toward those
spellings. Edit it as names change.

Two non-obvious settings, both learned the hard way:

  * condition_on_previous_text=False
      Whisper feeds its own output back as context. On a 30-minute recording it
      can derail and loop -- an earlier run emitted "we set out a memo on all
      social media" four times and produced "the 12 year old is now yogurt" in
      the middle of the fire-staffing answer. Disabling this trades a little
      cross-sentence coherence for far fewer hallucinations.

  * CUDA DLLs (see _register_cuda_dlls)
      ctranslate2 needs cublas64_12.dll, which itself needs cudart64_12.dll.
      No pip wheel pulls the latter in automatically, and neither PATH nor
      os.add_dll_directory reaches ctranslate2's loader. The DLLs must sit in
      the ctranslate2 package directory. Run --setup-cuda once to do that.

Requires: pip install faster-whisper nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-runtime-cu12
"""

import argparse
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
VOCAB = os.path.join(HERE, "whisper-vocab.txt")

# Whisper reserves half its 448-token context for the prompt. Longer prompts are
# silently truncated from the front, so the tail of the vocab file survives and
# the head is lost. Keep it short.
PROMPT_TOKEN_LIMIT = 224

# --------------------------------------------------------------------------
# Post-decode name fixes.
#
# The vocabulary prompt is a bias, not a guarantee. The 2026-09-04 validation
# run still produced one "van elstine" and one "Brandon", so these get cleaned
# up deterministically afterwards. Matched case-insensitively on word
# boundaries; the replacement's capitalisation is used as written. A trailing
# possessive survives ("Shakabe's" -> "Shakopee's") because the apostrophe is a
# word boundary.
#
# ONLY put strings here that cannot be a valid English word or a real name.
# Anything ambiguous belongs in REVIEW_WORDS below instead.
# --------------------------------------------------------------------------
CORRECTIONS = [
    # "Shakopee" -- YouTube's auto-captions rendered it ten different ways and
    # never once correctly. Whisper mostly gets it right; these are belt-and-braces.
    (r"Shakabby", "Shakopee"),
    (r"Shakapei", "Shakopee"),
    (r"Chakapei", "Shakopee"),
    (r"Shakapi",  "Shakopee"),
    (r"Shakape",  "Shakopee"),
    (r"Shakipi",  "Shakopee"),
    (r"Shakabe",  "Shakopee"),
    (r"Shakpi",   "Shakopee"),
    (r"Shaki",    "Shakopee"),
    (r"Shak",     "Shakopee"),
    (r"Shockbeby", "Shakopee"),
    (r"Shockbee",  "Shakopee"),
    (r"Shockby",   "Shakopee"),
    # people
    (r"Van ?Elstine", "Van Alstyne"),
    (r"Vanstein",     "Van Alstyne"),
    (r"Brandon",      "Brendan"),     # no other Brandon appears in this campaign
    (r"Zonker",       "Zunker"),
    (r"Verie",        "Verney"),
    (r"Angelika",     "Angelica"),    # Angelica is correct (Brendan, 2026-09-04)
    # places
    (r"Duth",        "Duluth"),
    (r"Still Water", "Stillwater"),
    # word-form errors
    (r"thatformational",  "that informational"),
    (r"micro generation", "microgeneration"),
    (r"water fronts",     "waterfronts"),
]

# URLs, fixed before the bare-word rules so the domain is not half-rewritten.
URL_CORRECTIONS = [
    (r"shakipe\.org",          "shakopee.org"),
    (r"brendanv4shaki\.\s*org", "brendanv4shakopee.org"),
]

# Real English words that were wrong in ONE transcript but are perfectly valid
# elsewhere -- "parks and wreck" was an error, but a car wreck is not. Blanket
# replacing these would corrupt legitimate text, so they are only reported.
REVIEW_WORDS = {
    "counsel": 'may be "council" (as in city council)',
    "wreck":   'may be "rec" (as in parks and rec)',
    "patting": 'may be "padding" (as in padding a budget)',
    "growed":  'may be "grew"',
}


def _register_cuda_dlls():
    """Make the pip-installed CUDA runtime visible to ctranslate2."""
    try:
        import nvidia
    except ImportError:
        return
    for root_path in nvidia.__path__:
        for root, _dirs, files in os.walk(root_path):
            if os.path.basename(root).lower() == "bin" and any(
                f.lower().endswith(".dll") for f in files
            ):
                try:
                    os.add_dll_directory(root)
                except (AttributeError, OSError):
                    pass


def setup_cuda():
    """Copy the CUDA DLLs next to ctranslate2.dll. Run once per machine."""
    try:
        import ctranslate2
        import nvidia
    except ImportError as exc:
        print("missing package: %s" % exc)
        return 1
    dest = os.path.dirname(ctranslate2.__file__)
    wanted = {"cublas64_12.dll", "cublaslt64_12.dll", "cudart64_12.dll"}
    copied = 0
    for root_path in nvidia.__path__:
        for root, _dirs, files in os.walk(root_path):
            for f in files:
                if f.lower() in wanted and not os.path.exists(os.path.join(dest, f)):
                    shutil.copy2(os.path.join(root, f), os.path.join(dest, f))
                    print("copied %s -> %s" % (f, dest))
                    copied += 1
    print("done (%d copied). ctranslate2 dir: %s" % (copied, dest))
    return 0


def load_prompt():
    if not os.path.exists(VOCAB):
        print("warning: %s not found; running without vocabulary bias" % VOCAB)
        return None
    with open(VOCAB, encoding="utf-8") as fh:
        text = " ".join(fh.read().split())
    return text or None


def apply_corrections(text):
    """Fix known ASR misspellings. Returns (text, {pattern: count})."""
    hits = {}
    for pattern, repl in URL_CORRECTIONS + CORRECTIONS:
        # \b before a pattern starting with a letter, and after one ending in a
        # letter, so possessives and punctuation still terminate the match.
        rx = r"\b" + pattern + r"\b"
        text, n = re.subn(rx, repl, text, flags=re.IGNORECASE)
        if n:
            hits[repl] = hits.get(repl, 0) + n
    return text, hits


def scan_review(text):
    """Count context-dependent words that may or may not be errors."""
    found = {}
    for word, note in REVIEW_WORDS.items():
        n = len(re.findall(r"\b" + word + r"\b", text, re.IGNORECASE))
        if n:
            found[word] = (n, note)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", nargs="?", help="audio file to transcribe")
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    ap.add_argument("--language", default="en")
    ap.add_argument("--beam", type=int, default=5)
    ap.add_argument("--no-vocab", action="store_true", help="skip the vocabulary prompt")
    ap.add_argument("--no-fix", action="store_true",
                    help="skip the post-decode name corrections (see CORRECTIONS)")
    ap.add_argument("--setup-cuda", action="store_true",
                    help="copy CUDA DLLs beside ctranslate2 and exit")
    args = ap.parse_args()

    if args.setup_cuda:
        return setup_cuda()
    if not args.audio:
        ap.error("audio file required (or use --setup-cuda)")
    if not os.path.exists(args.audio):
        print("no such file: %s" % args.audio)
        return 1

    _register_cuda_dlls()
    from faster_whisper import WhisperModel
    import ctranslate2

    device = args.device
    if device == "auto":
        try:
            device = "cuda" if ctranslate2.get_cuda_device_count() else "cpu"
        except Exception:
            device = "cpu"
    compute = "float16" if device == "cuda" else "int8"

    prompt = None if args.no_vocab else load_prompt()

    t0 = time.time()
    print("loading %s on %s (%s)..." % (args.model, device, compute))
    model = WhisperModel(args.model, device=device, compute_type=compute)

    if prompt:
        n = len(model.hf_tokenizer.encode(prompt).ids)
        flag = "" if n <= PROMPT_TOKEN_LIMIT else "  <-- TOO LONG, will be truncated"
        print("vocabulary prompt: %d tokens (limit %d)%s" % (n, PROMPT_TOKEN_LIMIT, flag))
        if flag:
            print("  trim tools/whisper-vocab.txt; the START of it is what gets dropped.")

    segments, info = model.transcribe(
        args.audio,
        language=args.language,
        beam_size=args.beam,
        initial_prompt=prompt,
        condition_on_previous_text=False,   # see module docstring
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )
    print("audio duration: %.1fs" % info.duration)

    out = []
    for seg in segments:
        out.append({"start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip()})
        if len(out) % 50 == 0:
            print("  %d segments, t=%.0fs, elapsed=%.0fs"
                  % (len(out), seg.end, time.time() - t0))

    if not args.no_fix:
        total = {}
        for seg in out:
            seg["text"], hits = apply_corrections(seg["text"])
            for k, v in hits.items():
                total[k] = total.get(k, 0) + v
        if total:
            print("\nname corrections applied:")
            for name in sorted(total):
                print("  %-22s x%d" % (name, total[name]))
        else:
            print("\nname corrections applied: none needed")

    stem = os.path.splitext(args.audio)[0]
    text = " ".join(s["text"] for s in out)

    review = scan_review(text)
    if review:
        print("\nwords to check by ear (NOT auto-changed -- valid English, wrong here before):")
        for word in sorted(review):
            n, note = review[word]
            print("  %-10s x%-3d %s" % (word, n, note))
    with open(stem + ".transcript.txt", "w", encoding="utf-8") as fh:
        fh.write(text)
    with open(stem + ".segments.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    print("\n%d segments, %d words, %.0fs elapsed" % (len(out), len(text.split()), time.time() - t0))
    print("wrote %s.transcript.txt" % stem)
    print("wrote %s.segments.json" % stem)
    print("\nStill machine output -- proofread names and numbers before publishing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
