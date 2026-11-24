"""Download the first N test recordings per language from Google FLEURS.

"First" means the first N audio files in the order they appear inside the
language's test.tar.gz on Hugging Face (google/fleurs). The exact file names we
used are listed in data/<lang>/clips.tsv, so anyone can check the selection.

Usage: python scripts/fetch_fleurs.py [N]   (default 20)
Audio is saved to audio/<lang>/ (not committed; FLEURS is CC BY 4.0).
"""
import csv, io, os, sys, tarfile, urllib.request

LANGS = ["es_419", "fr_fr", "ar_eg", "hi_in", "ur_pk", "bn_in"]
BASE = "https://huggingface.co/datasets/google/fleurs/resolve/main/data"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for lang in LANGS:
    refs = {}
    with urllib.request.urlopen(f"{BASE}/{lang}/test.tsv") as r:
        for row in csv.reader(io.TextIOWrapper(r, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
            refs[row[1]] = row[2]  # file_name -> raw transcription (what the speaker read)
    out = os.path.join(ROOT, "audio", lang); os.makedirs(out, exist_ok=True)
    rows = []
    with urllib.request.urlopen(f"{BASE}/{lang}/audio/test.tar.gz") as r:
        with tarfile.open(fileobj=r, mode="r|gz") as tar:
            for m in tar:
                if not m.isfile() or not m.name.endswith(".wav"):
                    continue
                name = os.path.basename(m.name)
                if name not in refs:
                    continue
                with open(os.path.join(out, name), "wb") as f:
                    f.write(tar.extractfile(m).read())
                rows.append((name, refs[name]))
                if len(rows) == N:
                    break
    d = os.path.join(ROOT, "data", lang); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "clips.tsv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["file", "reference"])
        w.writerows(rows)
    print(lang, len(rows), "clips")
