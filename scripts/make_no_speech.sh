#!/bin/sh
# Builds the three Korean "no speech" test files in audio/ko_no_speech/ (needs ffmpeg
# and the Korean FLEURS clips from fetch_fleurs.py):
#   silence_hiss.wav      25 s of quiet pink noise, no speech at all
#   music_chord.wav       25 s of a pulsing three-note chord, no speech at all
#   speech_with_gaps.wav  12 s of quiet noise, one FLEURS sentence, 12 s of quiet noise
# A good transcript of the first two is empty; of the third, only the sentence.
set -e
cd "$(dirname "$0")/.."
out=audio/ko_no_speech; mkdir -p "$out"
ffmpeg -v error -y -f lavfi -i "anoisesrc=color=pink:amplitude=0.01:duration=25:seed=1" -ar 16000 -ac 1 "$out/silence_hiss.wav"
ffmpeg -v error -y -f lavfi -i "sine=frequency=220:duration=25" -f lavfi -i "sine=frequency=277:duration=25" \
  -f lavfi -i "sine=frequency=330:duration=25" \
  -filter_complex "[0][1][2]amix=inputs=3,volume=0.6,tremolo=f=2:d=0.6" -ar 16000 -ac 1 "$out/music_chord.wav"
ffmpeg -v error -y -f lavfi -i "anoisesrc=color=pink:amplitude=0.01:duration=12:seed=2" -i audio/ko_kr/1007237877117014760.wav \
  -f lavfi -i "anoisesrc=color=pink:amplitude=0.01:duration=12:seed=3" \
  -filter_complex "[0]aresample=16000[a];[1]aresample=16000[b];[2]aresample=16000[c];[a][b][c]concat=n=3:v=0:a=1" \
  -ac 1 "$out/speech_with_gaps.wav"
echo "3 files in $out"
