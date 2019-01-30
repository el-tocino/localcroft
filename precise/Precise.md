The [precise page](https://github.com/MycroftAI/mycroft-precise/wiki/Training-your-own-wake-word#how-to-train-your-own-wake-word) has good instructions to get you started.  

#### data

You should pick a wakeword with at least three syllables or two words making three or more syllables, preferrably that do not have a lot of similar sounding rhymes. 

The more data you can collect, the better, up to about 50k samples.  I've collected over 300 total wake word and about 5000 fake word samples (including generated sounds).  If you're using local uploads, you can review those and add them to your dataset.  Once you have collected your data, try and have an 80/20 training/test split.  ie, for 100 clips, 80 go to the wakewords folder, 20 go to the test/wakewords folder.  In a ten minute span, I can, using precise-collect, record about 75 prepared words.  

Having a base of clean wake word samples to start with seems to work best. It is important that your core data be sourced as much as possible from your target audience.  From there it's a matter of testing to see what is best to model.  Precise modeling runs quickly, even on a cpu, so don't be afraid to start over a few times and try things. 

##### wake words

I've recorded myself quite a bit for my wake word.  I vary speed, inflection, volume, distance from mic, tone, etc. I have gotten about a dozen other folks to record samples for my model as well.  Your target audience is where you should be sourcing most of your data from.  When recording, I've used a variety of mics.  I have a cheap small diaphragm condenser that hits a usb preamp, a cheap usb mic, and a few on a PS Eye.  This isn't necessary, it's just been a matter of what was handy.

I have only recently started recording with noisy backgrounds.  Will update if I get better info.

##### fake words

The precise instructions are a good start, just be ready to add a lot of other stuff.  Thanks to a spate of allergies, I've now added over 100 cough and sniffle clips to my fake words.  My air conditioner cycling used to set it off, so I've recorded the a/c turning on and off. My microwave end tones.  A door closing.  Snores. etc.

As for spoken words, I used a scrabble word finder and rhymezone to target words that rhymed and had similar sounds.  With a list of about 120 of these, I recorded each one three times.  My helper voices usually get a list of fifteen words, containing three instances of my wake word and twelve fake words.  Sometimes there's multi-word combinations that falsely trigger it, these get added to my list and recorded.
For instance, here's a list of url's to get more fake words, in this case based off of the wake word "marvin".  

[rhymes](https://www.rhymezone.com/r/rhyme.cgi?Word=marvin&typeofrhyme=perfect)

[-vin words](https://www.onelook.com/?loc=rz4&w=*vin&scwo=1&sswo=1)

[mar- words](https://www.onelook.com/?loc=rz4&w=mar*&scwo=1&sswo=1)

[mart- words](https://www.onelook.com/?loc=rz4&w=mart*&scwo=1&sswo=1)

[-art- words](https://www.onelook.com/?loc=rz4&w=*art&scwo=1&sswo=1)

TV shows have also caused a significant number of false activations for me.  This is where having local copies can be a big help. 

#### modeling

Any time you add more data, I find it's best to start training all over.  If you aren't reviewing progress on tensorboard, you need to start. If you're having trouble hitting upper .90's in val_acc, you can try using the sensitivity settings (```-s 0.x```, default of 0.2).  

For my data, the sweet spot for number of steps appears to be 20-30k.  This gets my val_acc numbers up to the high .99s, sometimes 1.00000.  You can model further if your accuracy isn't there AND it keeps getting closer.  I once modeled to 150k, this wasn't more effective than 50k, and that wasn't noticeably different for my dataset at 30k. 

After the model completes, be sure to run precise-test.  Any false triggers should be reviewed, and new clips recorded to reinforce whatever you see.  A particular fake word? Add three more clips of it.  A slow wake word? Add a few more slow clips. After enabling local uploads, I have managed to almost double my wake word clip count in a bit over a week.  I highly recommend this if you're trying to model custom words.

Typical command I run:

``` precise-train -e 30000 wakeword.net wakeword/ && precise-test wakeword.net wakeword/ ```

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
![tensorboard](https://github.com/el-tocino/localcroft/blob/master/precise/tf-scaled-precise125ksm.png)

60k training run graphs (note val_acc don't get much better after 30k):

![val_acc](https://github.com/el-tocino/localcroft/blob/master/precise/precise-train.png)
![val_loss](https://github.com/el-tocino/localcroft/blob/master/precise/precise-train2.png)
 
