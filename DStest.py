from requests import post, put, exceptions
from pydub import AudioSegment
import sys
import rnnoise
import numpy as np
import time
import wave
from scipy.io import wavfile

def elapsedtime():
    elt = time.time() - start_time
    return elt

def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

def denoise(filename):
    TARGET_SR = 48000
    #audio, sample_rate = rnnoise.read_wave(filename)
    refreq = AudioSegment.from_wav(filename)
    refreq = refreq.set_frame_rate(48000)
    refreq.export('/tmp/dnn.wav',format='wav')
    blah = wave.open('/tmp/dnn.wav','rb')
    blah = blah.readframes(blah.getnframes())
    frames = rnnoise.frame_generator(10, blah, TARGET_SR)
    frames = list(frames)
    tups = [rnnoise.denoiser.process_frame(frame) for frame in frames]
    denoised_frames = [tup[1] for tup in tups]
    np_audio = np.concatenate([np.frombuffer(frame,
                                             dtype=np.int16)
                               for frame in denoised_frames])
    wavfile.write('test_denoised.wav',
              48000,
              np_audio)
    #wav_sample = np_audio[1]
    #sample_rate, wav_sample = np_audio
    segment = AudioSegment(data=np_audio.tobytes(),
                       sample_width=2,
                       frame_rate=48000, channels=1)
    nsdn_audio = segment.set_frame_rate(16000)
    #nsdn_audio.export("/tmp/ndn2_audio.wav",format="wav")
    return nsdn_audio

start_time = time.time()
print (start_time)
afn = sys.argv[1]
def_audio = open(afn, "rb")
short_silence = AudioSegment.silent(duration=500, frame_rate=16000)
temp_audio = AudioSegment.from_wav(afn)
#duration = len(temp_audio)
#trim_length = (-(duration - 110))
ds_audio = short_silence + temp_audio + short_silence
print ("silence added.", elapsedtime())
# add a low_pass_filter(3000) and high (200) to help isolate and improve recog
ds_audio = ds_audio.set_channels(1)
print ("one channel", elapsedtime())
ds_audio = ds_audio.low_pass_filter(3200)
print ("low pass", elapsedtime())
ds_audio = ds_audio.high_pass_filter(300)
print ("high pass", elapsedtime())
ns_audio = match_target_amplitude(ds_audio, -17.0)
print ("normalizing done.", elapsedtime())
ds_audio.export("/tmp/ds_audio.wav",format="wav")
ns_audio.export("/tmp/ns_audio.wav",format="wav")
print ("saved first two formats.", elapsedtime())
dn_audio = denoise('/tmp/ds_audio.wav')
dn_audio.export("/tmp/dn_audio.wav",format="wav")
print ("filtered denoised", elapsedtime())
dnz_audio = denoise('/tmp/ns_audio.wav')
dnz_audio.export("/tmp/dnz_audio.wav",format="wav")
print ("filtered normalized denoised", elapsedtime())
nzdn_audio = match_target_amplitude(dn_audio, -17.0)
nzdn_audio.export("/tmp/nzdn_audio.wav",format="wav")
print ("filtered denoised normalized", elapsedtime())
ordn_audio = denoise(afn)
ordn_audio.export("/tmp/odn_audio.wav",format="wav")
print ("denoised original", elapsedtime())
dfnz_audio = ordn_audio.low_pass_filter(3200)
dfnz_audio = dfnz_audio.high_pass_filter(300)
dfnz_audio = match_target_amplitude(dfnz_audio, -22.0)
dfnz_audio.export("/tmp/dfz_audio.wav",format="wav")
print ("denoise filter normalize", elapsedtime())
stt_audio = open("/tmp/ds_audio.wav", "rb")
ntt_audio = open("/tmp/ns_audio.wav", "rb")
jdn_audio = open("/tmp/dn_audio.wav", "rb") 
nzd_audio = open("/tmp/nzdn_audio.wav", "rb")
dnn_audio = open("/tmp/dnz_audio.wav", "rb")
odn_audio = open("/tmp/odn_audio.wav", "rb")
dfz_audio = open("/tmp/dfz_audio.wav", "rb")
print ("Querying DS server for transcript of default wav", elapsedtime())
responsed = post("http://192.168.1.1:1880/stt", data=def_audio.read())
print ("now frequency filtered...",elapsedtime())
response1 = post("http://192.168.1.1:1880/stt", data=stt_audio.read())
print ("and normalized...", elapsedtime())
response2 = post("http://192.168.1.1:1880/stt", data=ntt_audio.read())
print ("and just de-noised...", elapsedtime())
response3 = post("http://192.168.1.1:1880/stt", data=jdn_audio.read())
print ("and de-noised + normalized...", elapsedtime())
response4 = post("http://192.168.1.1:1880/stt", data=dnn_audio.read())
print ("and normalized + denoised...",elapsedtime())
response5 = post("http://192.168.1.1:1880/stt", data=nzd_audio.read())
print ("and original denoised...",elapsedtime())
response6 = post("http://192.168.1.1:1880/stt", data=odn_audio.read())
print ("denoize+filter+normalized...",elapsedtime())
response7 = post("http://192.168.1.1:1880/stt", data=dfz_audio.read())
print ("original:", responsed.text)
print ("filtered only:", response1.text)
print ("filter+normalized:", response2.text)
print ("filter+denoise:",response3.text)
print ("filter+normalize+denoise:",response4.text)
print ("filter+denoise+normalize:",response5.text)
print ("denoise only:", response6.text)
print ("denoise+filter+normalize:", response7.text)
