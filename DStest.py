"""
run various adjustments on a wav file to see how it compares
when being transcribed by a deepspeech instance.
"""
import argparse
import time
import wave
import numpy as np
from scipy.io import wavfile
from requests import post, put, exceptions
from pydub import AudioSegment
import rnnoise

def elapsedtime():
    """
    count time since start
    """
    elt = time.time() - start_time
    return elt

def normalize(sound, target_dBFS):
    """
    normalize clip
    """
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def denoise(sound):
    """
    denoise clip via rnnoise
    """
    TARGET_SR = 48000
    #audio, sample_rate = rnnoise.read_wave(filename)
    sound = sound.set_frame_rate(TARGET_SR)
    sound.export('dnntemp.wav', format='wav')
    blah = wave.open('dnntemp.wav', 'rb')
    blah = blah.readframes(blah.getnframes())
    frames = rnnoise.frame_generator(10, blah, TARGET_SR)
    frames = list(frames)
    tups = [rnnoise.denoiser.process_frame(frame) for frame in frames]
    denoised_frames = [tup[1] for tup in tups]
    np_audio = np.concatenate([np.frombuffer(frame,
                                             dtype=np.int16)
                               for frame in denoised_frames])
    segment = AudioSegment(data=np_audio.tobytes(),
                           sample_width=2,
                           frame_rate=48000, channels=1)
    segment = segment.set_frame_rate(16000)
    return segment

def hpass(sound, freq):
    """
    high-pass filter on clip.
    """
    sound = sound.high_pass_filter(freq)
    return sound

def lpass(sound, freq):
    """
    low-pass filter on clip
    """
    sound = sound.low_pass_filter(freq)
    return sound

def transcribe(filename):
    """
    Send clip to deepspeech server
    """
    transaudio = open(filename, "rb")
    response = post(dsurl, data=transaudio.read())
    return response


parser = argparse.ArgumentParser()
parser.add_argument("wavfile", help="wav file to test on.")
parser.add_argument("-H", "--highpass", help="high pass frequency.")
parser.add_argument("-L", "--lowpass", help="low pass frequency.")
parser.add_argument("-U", "--url", help="Deepspeech Server URL.", required="True")
parser.add_argument("-D", "--denoise", help="de-noise clip.", action="store_true")
parser.add_argument("-N", "--normalize", help="normalize clip.", action="store_true")
parser.add_argument("--targetdb", default=-22.0, help="DB target for normalize. (optional)")
args = parser.parse_args()

afn = args.wavfile
dsurl = args.url
start_time = time.time()
print start_time
ds_audio = AudioSegment.from_wav(afn)
ds_audio = ds_audio.set_channels(1)
short_silence = AudioSegment.silent(duration=250, frame_rate=16000)
ds_audio = short_silence + ds_audio + short_silence
print ("padding added", elapsedtime())

if args.lowpass is not None:
    ds_audio = lpass(ds_audio, args.lowpass)
    print elapsedtime()

if args.highpass is not None:
    ds_audio = hpass(ds_audio, args.highpass)
    print elapsedtime()

if args.denoise == 'True':
    ds_audio = denoise(ds_audio)
    print elapsedtime()

if args.normalize == 'True':
    ds_audio = normalize(ds_audio, args.targetdb)
    print elapsedtime()

ds_audio.export('filteredclip.wav', format='wav')

print transcribe(afn)
print elapsedtime()
print transcribe('filteredclip.wav')
print elapsedtime()
