### Local mycroft things

This includes several file changes to help run a local instance of mycroft, and some how-i-did-it pages for running local resources.

#### Building my Precise custom wake word model

More on that [here](precise/Precise.md).

#### Customizing Deepspeech

[here](DScustommodel.md)

#### Mycroft client DeepSpeech STT adjustments

Trying to improve local deep speech audio handling. First remove the start_listening noise.  Second, padding the wav file with .25 seconds of silence at the beginning and the end.

Uses pydub. ```sudo apt install ffmpeg; sudo pip3 install pydub ``` to usually get these installed on picroft.

File itself replaces the one in mycroft-core/mycroft/stt/, then restart services. 

#### WAV TTS connector

Local Mimic2 tts quickie.  No visimes, no chunking, NO LIMITS!  Does some pseudo-caching of responses.  You have to manually clean that up, though.  Move your existing /path/to/mycroft-core/mycroft/tts/mimic2.py to /path/to/mycroft-core/mycroft/tts/default-mimic2.py and then copy this file into its place.  If you have a TTS that does .wav file return, this could be modified easily to handle pretty much any end point.

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
  "stt": {
    "module": "deepspeech_server",
    "deepspeech_server": {
      "uri": "http://127.0.0.1:2000/stt"
    }
  },
  "tts": {
    "module": "mimic2",
    "mimic2": {
      "lang": "en-us",
      "url": "http://127.0.0.1:3000"
    },
  // Hotword configurations
  "hotwords": {
    "yourwordhere": {
        "module": "precise",
        "phonemes": "U R FO NE M Z HE R E",
        "threshold": "1e-30",
        "local_model_file": "/home/pi/.mycroft/precise/yourwordhere.pb"
        }
    },
```
