### Local mycroft things

This includes several file changes to help run a local instance of mycroft, and some how-i-did-it pages for running local resources.

#### Building my Precise custom wake word model

More on that [here](precise/Precise.md).

#### Mycroft client DeepSpeech STT adjustments

Trying to improve local deep speech audio handling. First remove the start_listening noise*.  Second, padding the wav file with .1 seconds of silence at the beginning and the end.

Uses pydub, numpy, scipy, rnnoise-python. ```sudo apt install ffmpeg; sudo pip3 install pydub ``` or whatever for your env to usually get these installed on picroft.

File itself replaces the one in mycroft-core/mycroft/stt/, then restart services.   Note this file defaults to using rnnoise, which can add asignificant time to processing audio files.  If you're capable of using this repo you can figure out how to comment that line out if need be.  

* I created a .05s silent wav file for my start_listening.wav.  

#### non-mycroft Deepspeech stuff

[here](DeepSpeech)

#### Moz/wav TTS connector

@domcross got the mozilla tts bits into core, so just use that.  It should in theory work with most any URL submission that takes the text as url parameters and returns a wav file.  

See the TTS config bits below for how to configure in your local conf.

#### Local Wikipedia

See [here](Wiki.md) for more on that.

#### precise uploads

A [recent PR](https://github.com/MycroftAI/mycroft-core/pull/2141) has also added local saving of wake words! This can be substituted if preferred to uploading.

Run the uploader.py in a screen session on a friendly host. Requires flask. May need to edit to adjust listen IP or save directory.  This makes use of the listener.url config.

Selene backend and updated personal server should handle this more directly if you go that route.

#### config

bits I use to make things work locally...
```
  "listener": {
    "wake_word": "yourwordhere",
    "wake_word_upload": {
      "disable": false,
      "url": "http://127.0.0.1:4000/precise/upload"
    },
  "hotwords": {
    "yourwordhere": {
        "module": "precise",
        "phonemes": "U R FO NE M Z HE R E",
        "threshold": "1e-30",
        "local_model_file": "/home/pi/.mycroft/precise/yourwordhere.pb"
        }
    },
```

This is used to set your wake word, whether to upload the detected wakewords to the upload server, and which wake word engine and options to use.  Pocketsphinx uses the phonemes.

```
  "stt": {
    "module": "deepspeech_server",
    "deepspeech_server": {
      "uri": "http://127.0.0.1:2000/stt"
    }
  },
```
The default STT file has more enumeration on what choices are available, this is just the one I end up using the most.

```
  "tts": {
    "module": "mimic2",
    "mimic2": {
      "lang": "en-us",
      "url": "http://127.0.0.1:3000"
    },
```

TTS server configuration.  The URL might be tricky if your endpoint requires odd pagenames but this should work with the mimic2 connector I have here for anything that returns a .wav file. 
