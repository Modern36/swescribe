# Development pipeline
This document describes the automated pipeline used to assist testing and
evaluation during the development of an audio-transcription library.
The library is itself a wrapper around the WhisperX library, that we test
and adapt for use on 1930s Swedish Newsreels. The pipeline represents the
final processing flow of the library, with extra intermediary steps that
better enable us to test and control the different working parts of the
workflow. The final library will take video files as input and produced
transcriptions using the `srt` standard.

During the development we have an extra, final, step that calculates the
Word Error Rate (WER). This calculation can be run manually but is also
run automatically before any changes are implemented into the codebase.
The WER is calculated based on a set or 27 files that were manually
transcribed by a research assistant very early in the project.

## 1. File paths - `paths.py`
File and directory paths are kept track of in `paths.py` making all the
relevant data easily accessible for all scripts.

## 2. Extract audio from video - `mpg_to_wav.py`
[now a discrete step -- will be part of the automatic workflow in the library]

`mpg_to_wav.py` extracts audio from the video files. The extracted audio is
saved as wav files in `data/wav_extracted` with a sample rate of 16 kHz and mono
channel, conforming to WhisperX requirements.

## 3. Clean the audio - `clean_audio.py`
[now a discrete step -- will be part of the automatic workflow in the library]


Given that the recordings originate from the early 20th century and may contain
significant noise, use `clean_audio.py` to reduce audio artifacts. This script
utilises the [noisereduce](https://github.com/timsainb/noisereduce) library with
parameters specified in
[this experiment](https://github.com/Modern36/filmarkivet_whisperx_and_wav2vec2/tree/e08be6728fb5bd7c4e3b205b740752602a50906f/noisereduce_gridsearch).
`clean_audio.py` processes files from `wav_extracted`and the cleaned wav files
are saved to `data/wav_cleaned`.

## 4. Transcribe the audio - `transcribe.py`
[now a discrete step -- will be part of the automatic workflow in the library]

Run `transcribe.py` to transcribe the audio using using
[m-bain/whisperX](https://github.com/m-bain/whisperX). The transcribed audio is
temporally aligned with
[KBLab/wav2vec2-large-voxrex-swedish](https://huggingface.co/KBLab/wav2vec2-large-voxrex-swedish).
The script reads audio files from `wav_cleaned`and generates one txt file and
one srt file per audio file. The txt files are saved to `data/txt_output`, and
the srt files are saved to `data/srt_output`.

## 5. Clean transcriptions - `run_clean_whisper.py`

The `run_clean_whisper.py` script executes functions in `clean_whisper.py` which
refines and sanitises the raw transcriptions produced by WhisperX. While
WhisperX delivers impressive transcription capabilities, it can introduce noise
and inconsistencies into the text, particularly with numbers, repeated phrases,
or artifacts from the audio such as music notations or "imaginary" URLs. The
called functions from `clean_whisper.py` process and standardise the WhisperX
transcriptions from `data/txt_output` and saves the cleaned txt files to
`txt_cleaned/`.

## 6. Perform WER analysis - `wer.py`
[Part of the evaluation -- will not be a part of the final workflow]


Assess the accuracy of the cleaned transcriptions in `data/txt_output` by
running `wer.py`, which uses the [jiwer](https://github.com/jitsi/jiwer/)
library to compute WER. Results for all files are saved to `wer_results.csv`.

### 7. Summarise WER results - `wer_descriptive_stats_calc.py`
[Part of the evaluation -- will not be a part of the final workflow]

The statistical summary produced by `wer_descriptive_stats_calc.py` is
calculated with [pandas](https://github.com/pandas-dev/pandas) and offers a
concise overview of the WER across all processed txt files. It reads the WER
results from `wer_results.csv`and writes the statistical summary to
`wer_results_summary.csv`. It includes the average WER, the standard deviation,
and the minimum and maximum WER values observed. Additionally, it presents
percentile metrics such as the 25th percentile, median (50th percentile), and
75th percentile.
