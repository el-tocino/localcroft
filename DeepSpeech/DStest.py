"""
run various adjustments on a wav file to see how it compares
when being transcribed by a deepspeech instance.
"""
import argparse
import time
import wave
import logging
import numpy as np
#from scipy.io import wavfile
from requests import post
from pydub import AudioSegment
import rnnoise

def elapsedtime():
    """
    count time since start
    """
    elt = time.time() - (start_time)
    return elt

def normalize(sound, target_dBFS):
    """
    normalize clip
    """
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def frame_generator(frame_duration_ms,
                    audio,
                    sample_rate):
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
        yield audio[offset:offset + n]
        offset += n       

def dnoise(sound):
    """
    denoise clip via rnnoise
    """
    denoiser = rnnoise.RNNoise()
    TARGET_SR = 48000
    #audio, sample_rate = rnnoise.read_wave(filename)
    sound = sound.set_frame_rate(TARGET_SR)
    sound.export('dnntemp.wav', format='wav')
    blah = wave.open('dnntemp.wav', 'rb')
    blah = blah.readframes(blah.getnframes())
    frames = frame_generator(10, blah, TARGET_SR)
    frames = list(frames)
    tups = [denoiser.process_frame(frame) for frame in frames]
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
    sound = sound.high_pass_filter(int(freq))
    return sound

def lpass(sound, freq):
    """
    low-pass filter on clip
    """
    sound = sound.low_pass_filter(int(freq))
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
parser.add_argument("-S", "--skip", help="skip transcribe on original clip.", action="store_true")
parser.add_argument(
    "-O", "--order", 
    default="hldn", 
    help="order of filters.  Optional. HLDN would be Highpass, Lowpass, denoise, then normalize. If order is specified, only items included are run.  N = normalize    D = de-noise    L = low pass filter    H = high pass filter")
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_true")
parser.add_argument(
    "--targetdb", 
    default=-22.0, 
    help="Decibel target for normalize. (optional)")
args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)

afn = args.wavfile
dsurl = args.url
start_time = time.time()

ds_audio = AudioSegment.from_wav(afn)
ds_audio = ds_audio.set_channels(1)
short_silence = AudioSegment.silent(duration=250, frame_rate=16000)
ds_audio = short_silence + ds_audio + short_silence
logging.debug("padding added %f", elapsedtime())

for filter in list(args.order):
    if filter.lower() == 'n' and args.normalize == True:
        ds_audio = normalize(ds_audio, args.targetdb)
        logging.debug("normalizing: %f" ,elapsedtime())

    if filter.lower() == 'l' and args.lowpass is not None:
        ds_audio = lpass(ds_audio, args.lowpass)
        logging.debug("lowpass %f", elapsedtime())

    if filter.lower() == 'h' and args.highpass is not None:
        ds_audio = hpass(ds_audio, args.highpass)
        logging.debug("highpass %f", elapsedtime())

    if filter.lower() == 'd' and args.denoise == True:
        ds_audio = dnoise(ds_audio)
        logging.debug("de-noising %f", elapsedtime())

ds_audio.export('filteredclip.wav', format='wav')

if args.skip is None:
    print("Original:", transcribe(afn).text)
    logging.debug("%f", elapsedtime())

print("Filtered:", transcribe('filteredclip.wav').text)
logging.debug("%f", elapsedtime())
