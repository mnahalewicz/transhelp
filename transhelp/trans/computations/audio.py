# -*- coding: utf8 -*-

# based on https://github.com/wiseman/py-webrtcvad/blob/master/example.py

import collections
import contextlib
import os
import re
import subprocess
import sys
import wave
import webrtcvad


def read_wave(path):
    """Reads a .wav file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, "rb")) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        num_frames = wf.getnframes()
        pcm_data = wf.readframes(num_frames)
        return pcm_data, sample_rate, num_frames


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.

    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset : offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def get_split_second_timestamps(
    sample_rate, frame_duration_ms, padding_duration_ms, vad, frames
):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    in_speech_chunk = False
    buffer_is_speech_responses = []
    split_seconds = []
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        buffer_is_speech_responses.append(is_speech)
        if len(buffer_is_speech_responses) > num_padding_frames:
            buffer_is_speech_responses.pop(0)
        else:
            continue
        non_speech_ratio = (
            len([1 for is_sp in buffer_is_speech_responses if not is_sp])
            / num_padding_frames
        )
        if non_speech_ratio > 0.9:
            if in_speech_chunk:
                split_seconds.append(frame.timestamp)
                in_speech_chunk = False
        else:
            in_speech_chunk = True
    return split_seconds


def split_wave(in_wav_fp, split_second_timestamps, out_dp):
    assert os.path.exists(in_wav_fp), "input wave file does not exist"
    assert os.path.exists(out_dp), "output directory does not exist"
    curr_start_seconds = 0.0
    fname = os.path.basename(in_wav_fp)
    for pos, curr_end_seconds in enumerate(split_second_timestamps):
        out_fp = os.path.join(out_dp, "{:03d}_{}".format(pos, fname))
        subprocess.run(["sox", in_wav_fp, out_fp, "trim", str(curr_start_seconds), str(curr_end_seconds - curr_start_seconds)])
        curr_start_seconds = curr_end_seconds


def process_audio(in_audio_fp, const_split_seconds=None, out_dp = None):
    aggressiveness = 3
    converted_wav_fp = in_audio_fp + ".wav"
    subprocess.run(["sox", in_audio_fp, "-r", "16000", converted_wav_fp, "remix", "-"])
    audio, sample_rate, num_frames = read_wave(converted_wav_fp)
    os.remove(converted_wav_fp)
    if not (const_split_seconds is None):
        assert const_split_seconds >= 5
        assert const_split_seconds <= 60
        total_seconds = num_frames / sample_rate
        return [ i * const_split_seconds for i in range(1, int(total_seconds / const_split_seconds))]
    vad = webrtcvad.Vad(aggressiveness)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    split_second_timestamps = get_split_second_timestamps(sample_rate, 30, 300, vad, frames)
    if out_dp:
        split_wave(in_audio_fp, split_second_timestamps, out_dp)
    return split_second_timestamps


