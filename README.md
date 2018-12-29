# Local mycroft things

This includes two updates to help run a local instance of mycroft, and one how-i-did-it for running a local wikipedia copy.  

# localDS-fix

Trying to improve local deep speech audio handling. First remove the start_listening noise.  Second, padding the wav file with half a second of silence at the beginning and the end.  

Uses pydub. ```pip3 install pytdub ; sudo apt install ffmpeg``` to usually get these installed on picroft.    

File itself replaces the one in mycroft-core/mycroft/stt/, then restart services. 

# m2-tts
Local Mimic2 tts quickie.  No visimes, no chunking, NO LIMITS!  Does some pseudo-caching of responses.  You have to manually clean that up, though. :)

Move your existing /path/to/mycroft-core/mycroft/tts/mimic2.py to /path/to/mycroft-core/mycroft/tts/default-mimic2.py and then copy this file into its place.

If you have a .wav file return tool, this could be modified easily to handle pretty much any end point.

# Wiki

See Wiki.md for more.
