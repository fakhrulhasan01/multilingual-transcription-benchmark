"""Score every system against the FLEURS reference sentences.

Word error rate (WER) = (substituted + deleted + inserted words) / reference words,
pooled over all clips of a language. "Words right" = 100% - WER.

Before comparing, both sides get the same light normalisation, and nothing else:
  - Unicode NFC, lower case
  - punctuation and symbols (Unicode categories P* and S*) become spaces
  - digits in any script become the same ASCII digits
  - Arabic and Urdu: the optional vowel marks (harakat, superscript alef,
    tatweel) are removed and the alef forms are unified
  - Hindi: the nukta dot is removed
Letters and vowel signs are never touched, so a spelling difference is an error.

Usage: python scripts/score.py            -> prints a table, writes results/summary.md
"""
import csv, glob, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = [("es_419", "Spanish"), ("fr_fr", "French"), ("ar_eg", "Arabic"),
         ("hi_in", "Hindi"), ("ur_pk", "Urdu"), ("bn_in", "Bangla"), ("id_id", "Indonesian")]
HARAKAT = re.compile("[ً-ْٰـ]")
ALEF = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا"})


def normalise(text, lang):
    text = unicodedata.normalize("NFC", text).lower()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat[0] in "PS":
            out.append(" ")
        elif cat == "Nd":
            out.append(str(unicodedata.digit(ch)))
        else:
            out.append(ch)
    text = "".join(out)
    if lang in ("ar_eg", "ur_pk"):
        text = HARAKAT.sub("", text).translate(ALEF)
    if lang == "hi_in":
        text = text.replace("़", "")
    return text.split()


def edit_counts(ref, hyp):
    """Levenshtein alignment on words: returns (substitutions, deletions, insertions)."""
    n, m = len(ref), len(hyp)
    d = [[(0, 0, 0, 0)] * (m + 1) for _ in range(n + 1)]  # (cost, S, D, I)
    for i in range(1, n + 1):
        d[i][0] = (i, 0, i, 0)
    for j in range(1, m + 1):
        d[0][j] = (j, 0, 0, j)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                d[i][j] = d[i - 1][j - 1]
                continue
            c, s, dl, ins = d[i - 1][j - 1]; sub = (c + 1, s + 1, dl, ins)
            c, s, dl, ins = d[i - 1][j]; dele = (c + 1, s, dl + 1, ins)
            c, s, dl, ins = d[i][j - 1]; inse = (c + 1, s, dl, ins + 1)
            d[i][j] = min(sub, dele, inse)
    return d[n][m][1:]


def read_tsv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))


def score(system_dir, lang):
    refs = {r["file"]: r["reference"] for r in read_tsv(os.path.join(ROOT, "data", lang, "clips.tsv"))}
    path = os.path.join(system_dir, f"{lang}.tsv")
    if not os.path.exists(path):
        return None
    hyps = {r["file"]: r["hypothesis"] for r in read_tsv(path)}
    words = errors = 0
    for name, ref in refs.items():
        r, h = normalise(ref, lang), normalise(hyps.get(name, ""), lang)
        words += len(r)
        errors += sum(edit_counts(r, h))
    return words, errors


def main():
    systems = sorted(d for d in glob.glob(os.path.join(ROOT, "results", "*")) if os.path.isdir(d))
    names = [os.path.basename(s) for s in systems]
    runs = [s for s in systems if os.path.basename(s).startswith("transcriptgo-run")]
    head = (["transcriptgo (average of runs)"] if len(runs) > 1 else []) + names
    lines = ["| Language | Words | " + " | ".join(head) + " |", "|---|---|" + "---|" * len(head)]
    for lang, label in LANGS:
        cells, words = [], None
        run_words = run_errors = 0
        for s in systems:
            r = score(s, lang)
            if r is None:
                cells.append("n/a")
                continue
            words, errors = r
            if s in runs:
                run_words += words; run_errors += errors
            cells.append(f"{100 - 100 * errors / words:.1f}% ({errors} errors)")
        if len(runs) > 1:
            cells.insert(0, f"**{100 - 100 * run_errors / run_words:.1f}%**" if run_words else "n/a")
        lines.append(f"| {label} | {words or ''} | " + " | ".join(cells) + " |")
    table = "\n".join(lines)
    print(table)
    with open(os.path.join(ROOT, "results", "summary.md"), "w", encoding="utf-8") as f:
        f.write("Words transcribed exactly right (100% minus word error rate), pooled over 20 clips per language.\n\n" + table + "\n")


if __name__ == "__main__":
    main()
