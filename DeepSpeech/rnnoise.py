import wave
import os,sys
import ctypes
import contextlib
import numpy as np
from ctypes import util
from scipy.io import wavfile
from pydub import AudioSegment

lib_path = util.find_library("rnnoise")
if (not("/" in lib_path)):
    lib_path = (os.popen('ldconfig -p | grep '+lib_path).read().split('\n')[0].strip().split(" ")[-1] or ("/usr/local/lib/"+lib_path))

lib = ctypes.cdll.LoadLibrary(lib_path)
lib.rnnoise_process_frame.argtypes = [ctypes.c_void_p,ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float)]
lib.rnnoise_process_frame.restype = ctypes.c_float
lib.rnnoise_create.restype = ctypes.c_void_p
lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]

# borrowed from here 
# https://github.com/Shb742/rnnoise_python

class RNNoise(object):
    def __init__(self):
        #self.obj = lib.rnnoise_create()
        self.obj = lib.rnnoise_create(None)
    def process_frame(self,inbuf):
        outbuf = np.ndarray((480,), 'h', inbuf).astype(ctypes.c_float)
        outbuf_ptr = outbuf.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        VodProb =  lib.rnnoise_process_frame(self.obj,outbuf_ptr,outbuf_ptr)
        return (VodProb,outbuf.astype(ctypes.c_short).tobytes())

    def destroy(self):
        lib.rnnoise_destroy(self.obj)


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000, 48000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate        
        
      
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
        
denoiser = RNNoise() 
