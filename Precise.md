The [precise page](https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word) has good instructions to get you started.  

#### data

The more data, the better.  To a point, which is about 50k samples apparently.  I have hit over 320 total wake word and about 5000 fake word samples (including generated sounsd).  If you're using local uploads, you can review those and add them to your dataset.  Once you have collected your data, try and have an 80/20 training/test split.  ie, for 100 clips, 80 go to the wakewords folder, 20 go to the test/wakewords folder.  

##### wake words

I've recorded myself quite a bit for my wake word.  I vary speed, inflection, volume, distance from mic, tone, etc. I have gotten about a dozen other folks to record samples for me, though these tend to be fairly uniform.  Know your target audience, and try and sample them.  The wider the range of samples you have, the better your model should perform.  

When recording, I've used a variety of mics.  I have a nice small diaphragm condenser that hits a usb preamp, a cheap usb mic, and a few on a PS Eye.  This isn't necessary, it's just been a matter of what was handy.  I believe that having a good base of clean wake word samples to start with is best.  From there it's a matter of testing to see what is best to record.  

I have only recently started recording with noisy backgrounds.  Will update once I have better info.  

##### fake words

Oof.  The precise instructions are a good start, just be ready to add a lot of other stuff.  Thanks to a spate of allergies, I've now added over 100 cough and sniffle clips to my fake words.  My air conditioner cycling used to set it off, so I've recorded the a/c turning on and off. My microwave end tones.  A door closing.  

As for spoken words, I used a scrabble word finder and rhymezone to target words that rhymed and had similar sounds.  With a list of about 120 of these, I recorded each one three times.  My helper voices usually get a list of fifteen words, containing three instances of my wake word and twelve fake words.  Sometimes there's multi-word combinations that falsely trigger it, these get added to my list and recorded.  

TV shows have also caused a significant number of false activations for me.  This is where having local copies would be a big help. 

#### modeling

Any time you add more data, I find it's best to start training all over. 

For my data, the sweet spot for number of steps appears to be 20-30k.  This gets my val_acc numbers up to the high .99s, sometimes 1.00000.  You can model further if your accuracy isn't there AND it keeps getting closer.  I once modeled to 150k, this wasn't more effective than 50k, and that wasn't noticeably different for my dataset at 30k. My current dataset has about 300 wake words, and 5000 fake words.  My test folder has 55 wake and 900 fake words.  

After the model completes, be sure to run precise-test.  Any false triggers should be reviewed, and new clips recorded to reinforce whatever you see.  A particular fake word? Add three more clips of it.  A slow wake word? Add a few more slow clips. After enabling local uploads, I have managed to almost double my clip count in a bit over a week.  I highly recommend this if you're trying to model custom words.  

Results of precise-test after 125k steps:
```
Loading wake-word...
Loading not-wake-word...
Using TensorFlow backend.
Data: <TrainData wake_words=277 not_wake_words=4568 test_wake_words=56 test_not_wake_words=895>
=== False Positives ===
athena/test/not-wake-word/fakewords-120.wav

=== False Negatives ===

=== Counts ===
False Positives: 1
True Negatives: 894
False Negatives: 0
True Positives: 56

=== Summary ===
950 out of 951
99.89 %

0.11 % false positives
0.0 % false negatives
```
![tensorboard](https://github.com/el-tocino/localcroft/blob/master/tf-scaled-precise125ksm.png)
