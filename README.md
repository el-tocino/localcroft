## Local mycroft things

This includes several file changes to help run a local instance of mycroft, and one how-i-did-it for running a local wikipedia copy. They can be used piecemeal or all at once.  

### localDS-fix

Trying to improve local deep speech audio handling. First remove the start_listening noise.  Second, padding the wav file with half a second of silence at the beginning and the end.  

Uses pydub. ```pip3 install pytdub ; sudo apt install ffmpeg``` to usually get these installed on picroft.    

File itself replaces the one in mycroft-core/mycroft/stt/, then restart services. 

### m2-tts
Local Mimic2 tts quickie.  No visimes, no chunking, NO LIMITS!  Does some pseudo-caching of responses.  You have to manually clean that up, though. :)

Move your existing /path/to/mycroft-core/mycroft/tts/mimic2.py to /path/to/mycroft-core/mycroft/tts/default-mimic2.py and then copy this file into its place.

If you have a .wav file return tool, this could be modified easily to handle pretty much any end point.

See the TTS config bits below for how to configure in your local conf.

### Wiki

See [here](Wiki.md) for more on that.

### precise uploads

Run the uploader.py in a screen session on a viable host. Requires flask. May need to edit to adjust listen IP or save directory.  This makes use of the listener.url config.  Also will require adjusting mic.py to only upload the audio portion (remove the comma from the audio line (353?) and then comment out the metadata line.  Will add it here in a bit.

### config

bits I use to make things work locally...
```
  "listener": {
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
