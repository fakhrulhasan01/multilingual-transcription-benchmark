# Multilingual transcription benchmark

How many words does speech-to-text get exactly right in Spanish, French, Arabic, Hindi, Urdu, Bangla, Indonesian and Korean? And does it make up words when nobody is speaking? This repository answers that on a public dataset, with every transcript, the scoring script and the method, so anyone can check the numbers or add another service.

**Published by [TranscriptGo](https://transcriptgo.app).** We run a transcription service and we test our own service here, next to OpenAI's open Whisper large-v3. Read the results with that in mind, and please repeat the test yourself: everything you need is in this repository.

## Results

Words transcribed exactly right (100% minus word error rate), pooled over 20 recordings per language. Tested on 24 November 2026 (Indonesian on 25 November, Korean on 27 November 2026).

| Language | Words | transcriptgo (average of runs) | transcriptgo-run1 | transcriptgo-run2 | whisper-large-v3 |
|---|---|---|---|---|---|
| Spanish | 479 | **98.7%** | 98.5% (7 errors) | 99.0% (5 errors) | 98.3% (8 errors) |
| French | 624 | **96.1%** | 95.8% (26 errors) | 96.3% (23 errors) | 93.6% (40 errors) |
| Arabic | 411 | **94.6%** | 93.9% (25 errors) | 95.4% (19 errors) | 91.5% (35 errors) |
| Hindi | 527 | **93.2%** | 93.4% (35 errors) | 93.0% (37 errors) | 75.3% (130 errors) |
| Urdu | 561 | **82.3%** | 81.5% (104 errors) | 83.1% (95 errors) | 76.8% (130 errors) |
| Bangla | 408 | **85.9%** | 85.8% (58 errors) | 86.0% (57 errors) | 29.2% (289 errors) |
| Indonesian | 397 | **94.5%** | 94.7% (21 errors) | 94.2% (23 errors) | 94.0% (24 errors) |
| Korean | 291 | **89.5%** | 89.3% (31 errors) | 89.7% (30 errors) | 88.0% (35 errors) |

**Bangla has a second number.** Bangla has many accepted spellings for the same word, and the FLEURS reference sentences mix them: ভাল and ভালো, সরকারী and সরকারি, গভীর ভাবে and গভীরভাবে are all correct, but the strict count above marks every one as an error. We went through every difference by hand and marked whether the meaning changed. In TranscriptGo's transcripts, 12 of 408 words (run 1) and 13 of 408 words (run 2) changed the meaning, so **about 97% of Bangla words were right in meaning**. Every decision is listed in [`data/bn_in/meaning-review-run1.tsv`](data/bn_in/meaning-review-run1.tsv) and [`run2`](data/bn_in/meaning-review-run2.tsv), so you can disagree with any of them.

**Korean has a second number too.** Korean spacing is flexible: 통행 금지 and 통행금지, 타이 브레이크 and 타이브레이크 are both written, and the reference sentences are not consistent either, but the word count marks each one as an error. So `score.py` also compares the same text with every space removed, letter by letter:

| Language | Letters | transcriptgo (average of runs) | transcriptgo-run1 | transcriptgo-run2 | whisper-large-v3 |
|---|---|---|---|---|---|
| Korean | 891 | **98.1%** | 98.2% (16 errors) | 98.0% (18 errors) | 98.1% (17 errors) |

On these clean recordings the two systems are tied in Korean.

## When nobody is speaking (Korean)

Real uploads contain silence, music and pauses, and a speech model can invent words there. We made three files with `scripts/make_no_speech.sh` (fixed random seeds, so you get the same bytes): 25 seconds of quiet hiss, 25 seconds of a pulsing chord, and one Korean FLEURS sentence with 12 seconds of hiss before and after. The right answer is nothing, nothing, and the one sentence.

| File | TranscriptGo (both runs) | Whisper large-v3 |
|---|---|---|
| Quiet hiss | *(nothing)* | 시청해주셔서 감사합니다. ("Thank you for watching.") |
| Chord | *(nothing)* | 아멘 ("Amen") |
| Sentence between pauses | the sentence | the sentence, then an invented one: 타이 브레이크가 2세트에서 먼저 어드밴티를 얻었다. |

Three files are a demonstration, not a rate: they show the kind of error, not how often it happens. The transcripts are in `results/*/ko_no_speech.tsv`.

## What was tested

**The recordings.** [FLEURS](https://huggingface.co/datasets/google/fleurs) is a free speech dataset from Google (CC BY 4.0). Each recording is one person reading one sentence, and the dataset includes the exact sentence they read. We took the first 20 recordings of each language's test set, in the order they appear in its `test.tar.gz`: Spanish (Latin America, `es_419`), French (`fr_fr`), Arabic (Egypt, `ar_eg`), Hindi (`hi_in`), Urdu (Pakistan, `ur_pk`), Bangla (India, `bn_in`), Indonesian (`id_id`, added on 25 November 2026) and Korean (`ko_kr`, added on 27 November 2026). About 300 to 600 words per language. The exact files and reference sentences are in `data/<language>/clips.tsv`.

**TranscriptGo.** The live service at transcriptgo.app, with the same processing every upload gets on a free account (free and paid accounts use the same engines for these languages), and the spoken language chosen as a user would choose it. Each language was run twice, because the service varies by about one point between runs; the headline number pools both runs. The Bangla runs were made after a fix released the same day that keeps Hindi letters out of Bangla transcripts. Indonesian was measured on 25 November 2026, the day after the service moved Indonesian to a different speech engine. Korean was measured on 27 November 2026, the day the service moved Korean to a different speech engine.

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
- 20 recordings per language is a small sample: a difference of one or two points between two systems is within the noise. Spanish, Indonesian and Korean are such cases: the two systems are effectively tied there.
- Only TranscriptGo and Whisper large-v3 are tested here. We would welcome results for other services (see below).

## Repeat it, or add a service

```bash
python3 scripts/fetch_fleurs.py            # downloads the 160 recordings into audio/
./scripts/make_no_speech.sh                # the three Korean no-speech files
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
| `results/*/ko_no_speech.tsv` | the no-speech test transcripts |
| `results/summary.md` | the results table |
| `data/bn_in/meaning-review-run*.tsv` | every Bangla difference, marked as changed meaning or not |
| `scripts/` | download, no-speech files, Whisper, scoring and word-diff scripts |

## Licence

Code: MIT. Transcripts and reference sentences: CC BY 4.0, as they come from or are made from FLEURS (Conneau et al., 2022, "FLEURS: Few-shot Learning Evaluation of Universal Representations of Speech").
