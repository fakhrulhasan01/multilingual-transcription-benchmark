# Multilingual transcription benchmark

How many words does speech-to-text get exactly right in Spanish, French, Arabic, Hindi, Urdu and Bangla? This repository answers that on a public dataset, with every transcript, the scoring script and the method, so anyone can check the numbers or add another service.

**Published by [TranscriptGo](https://transcriptgo.app).** We run a transcription service and we test our own service here, next to OpenAI's open Whisper large-v3. Read the results with that in mind, and please repeat the test yourself: everything you need is in this repository.

## Results

Words transcribed exactly right (100% minus word error rate), pooled over 20 recordings per language. Tested on 24 November 2026.

| Language | Words | transcriptgo (average of runs) | transcriptgo-run1 | transcriptgo-run2 | whisper-large-v3 |
|---|---|---|---|---|---|
| Spanish | 479 | **98.7%** | 98.5% (7 errors) | 99.0% (5 errors) | 98.3% (8 errors) |
| French | 624 | **96.1%** | 95.8% (26 errors) | 96.3% (23 errors) | 93.6% (40 errors) |
| Arabic | 411 | **94.6%** | 93.9% (25 errors) | 95.4% (19 errors) | 91.5% (35 errors) |
| Hindi | 527 | **93.2%** | 93.4% (35 errors) | 93.0% (37 errors) | 75.3% (130 errors) |
| Urdu | 561 | **82.3%** | 81.5% (104 errors) | 83.1% (95 errors) | 76.8% (130 errors) |
| Bangla | 408 | **85.9%** | 85.8% (58 errors) | 86.0% (57 errors) | still running, added shortly |

**Bangla has a second number.** Bangla has many accepted spellings for the same word, and the FLEURS reference sentences mix them: ভাল and ভালো, সরকারী and সরকারি, গভীর ভাবে and গভীরভাবে are all correct, but the strict count above marks every one as an error. We went through every difference by hand and marked whether the meaning changed. In TranscriptGo's transcripts, 12 of 408 words (run 1) and 13 of 408 words (run 2) changed the meaning, so **about 97% of Bangla words were right in meaning**. Every decision is listed in [`data/bn_in/meaning-review-run1.tsv`](data/bn_in/meaning-review-run1.tsv) and [`run2`](data/bn_in/meaning-review-run2.tsv), so you can disagree with any of them.

## What was tested

**The recordings.** [FLEURS](https://huggingface.co/datasets/google/fleurs) is a free speech dataset from Google (CC BY 4.0). Each recording is one person reading one sentence, and the dataset includes the exact sentence they read. We took the first 20 recordings of each language's test set, in the order they appear in its `test.tar.gz`: Spanish (Latin America, `es_419`), French (`fr_fr`), Arabic (Egypt, `ar_eg`), Hindi (`hi_in`), Urdu (Pakistan, `ur_pk`) and Bangla (India, `bn_in`). About 400 to 600 words per language, 23.5 minutes of audio in total. The exact files and reference sentences are in `data/<language>/clips.tsv`.

**TranscriptGo.** The live service at transcriptgo.app, with the same processing every upload gets on a free account (free and paid accounts use the same engines for these languages), and the spoken language chosen as a user would choose it. Each language was run twice, because the service varies by about one point between runs; the headline number pools both runs. The Bangla runs were made after a fix released the same day that keeps Hindi letters out of Bangla transcripts.

**Whisper large-v3.** OpenAI's open model from [github.com/openai/whisper](https://github.com/openai/whisper) (package version 20250625), run with the command-line defaults: beam search 5, best of 5, temperature fallback, full precision on CPU, with the spoken language given. Many transcription services are built on this model, which makes it a useful reference point.

## How a word is counted

Word error rate = (substituted + deleted + inserted words) / words in the reference sentence. Before comparing, both texts get the same light normalisation and nothing else:

- Unicode NFC and lower case
- punctuation and symbols become spaces
- digits in any script count as the same digits
- Arabic and Urdu: the optional vowel marks (harakat) are removed and the alef forms are unified, the usual way Arabic speech recognition is scored
- Hindi: the nukta dot is removed

Everything else counts as an error: a misspelled name, a missing word, "1" written as "one", two words written as one.

## What the numbers do and do not show

- These are clean recordings of one person reading. Noisy rooms, phone audio, music and people talking over each other lower the score of every service.
- 20 recordings per language is a small sample: a difference of one or two points between two systems is within the noise.
- Only TranscriptGo and Whisper large-v3 are tested here. We would welcome results for other services (see below).

## Repeat it, or add a service

```bash
python3 scripts/fetch_fleurs.py            # downloads the 120 recordings into audio/
pip install openai-whisper && python3 scripts/run_whisper.py
python3 scripts/score.py                   # prints the table, writes results/summary.md
```

To score any other service, upload the files in `audio/<language>/` to it and save its text as `results/<service>/<language>.tsv` with two tab-separated columns, `file` and `hypothesis`. `score.py` picks up every folder in `results/`. To see each error, run `python3 scripts/word_diff.py bn_in results/<service>`.

If you get different numbers from ours, please open an issue.

## Files

| Path | What it is |
|---|---|
| `data/<language>/clips.tsv` | the 20 recordings and the sentence each speaker read |
| `results/transcriptgo-run1/`, `run2/` | TranscriptGo's transcripts, one row per recording |
| `results/whisper-large-v3/` | Whisper large-v3 transcripts |
| `results/summary.md` | the results table |
| `data/bn_in/meaning-review-run*.tsv` | every Bangla difference, marked as changed meaning or not |
| `scripts/` | download, Whisper, scoring and word-diff scripts |

## Licence

Code: MIT. Transcripts and reference sentences: CC BY 4.0, as they come from or are made from FLEURS (Conneau et al., 2022, "FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech").
