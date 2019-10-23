####  Things I used to build my dataset:

 - the alphabet (vary your speed/inflection each time, ie, casual, urgent, happy) 3x 
 - numbers zero through 19, then by tens to one hundred, one thousand, one million.  (vary as above) 3x
 - fractional amounts (1/2, 1/4, 3/4, 1/8, 3/8, five eighths) 2x
 - the hours one through twelve o'clock, noon, midnight, fifteen, half past, quarter til. 2x
 - short responses (yes, no, yeah, maybe, nope, i don't know) 5x 
 - top 100 words https://simple.wikipedia.org/wiki/Most_common_words_in_English (use in sentences) 3x
 - top 500 words http://www.bckelk.ukfsn.org/words/uk1000n.html (make sentences with each) 1-2x
 - basic VA queries (what time is it? set an alarm for ..., how do you spell $word, turn on the lights in the kitchen, etc). Customize these for your usage.  4-10x per command, vary the queries each time.
 - (optional depending on usage) Sentences that include common colloquialisms, vernacular, and acronyms.  I used arxiv papers and a lot of reviews of computing devices to draw sentences from.
 - (optional) read a book. 
 - (optional, but more is better) Google movie conversation setences https://ai.googleblog.com/2019/09/announcing-two-new-natural-language.html

Record yourself in your natural speaking voice.  If you talk differently to your devices now, don't do that here.  I talk faster in conversation than I typically do to mycroft.  For recording, I sped through at my typical pace. 

Record at least half of your corpus as cleanly as possible.  While having less clean data is useful as well, you want it to get a good understanding of you to begin with.  
Record at the highest quality you can to begin with.  Downsampling is easier done than up. 
I tend to record a sentence, pause to review the next one for half to one second, then continue.  After completing a set of sentences, I use sox to split the resulting wav into separate chunks.  

One hundred average-length sentences takes me about fifteen minutes to record.  

Splitting a large file into separate wavs:
```sox input.wav output.wav silence 1 0.1 1% 1 0.3 1% : newfile : restart ```

Converting a file to the default DS format:
```sox input.wav -c 1 -b 16 -r 16000 output.wav```
