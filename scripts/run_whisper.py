"""Transcribe every clip with OpenAI's open Whisper large-v3 (github.com/openai/whisper).

Settings are the whisper command-line defaults: beam search 5, best_of 5,
temperature fallback, condition on previous text. The spoken language is given,
as it is for TranscriptGo. Output: results/whisper-large-v3/<lang>.tsv
"""
import csv, os, sys, time, whisper

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = {"es_419": "es", "fr_fr": "fr", "ar_eg": "ar", "hi_in": "hi", "ur_pk": "ur", "bn_in": "bn", "id_id": "id"}
langs = sys.argv[1:] or list(CODES)
model = whisper.load_model("large-v3", device="cpu")
out_dir = os.path.join(ROOT, "results", "whisper-large-v3"); os.makedirs(out_dir, exist_ok=True)
for lang in langs:
    with open(os.path.join(ROOT, "data", lang, "clips.tsv"), encoding="utf-8") as f:
        clips = [r["file"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)]
    rows, t0 = [], time.time()
    for name in clips:
        r = model.transcribe(os.path.join(ROOT, "audio", lang, name), language=CODES[lang],
                             beam_size=5, best_of=5, fp16=False)
        rows.append((name, " ".join(r["text"].split())))
    with open(os.path.join(out_dir, f"{lang}.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n"); w.writerow(["file", "hypothesis"]); w.writerows(rows)
    print(lang, len(rows), f"{time.time()-t0:.0f}s", flush=True)
