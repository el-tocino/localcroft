### Custom Modeling

I've been fiddling with deepspeech a bunch of late, trying to improve its accuracy when it listens to me.  
TL;DR: fine-tune the mozilla model instead of creating your own.  

If this is in your field of interest,  start with this post over on the mozilla discourse:

https://discourse.mozilla.org/t/tutorial-how-i-trained-a-specific-french-model-to-control-my-robot/22830

An extraneous list of steps I used is below.  More than a few are duplicated from the above. This isn't definitive, and will certainly need to be redone over time.  You do NOT need massive resources to compile a small (<10k clips) model, but the larger your GPU the better.  You will need deepspeech, the native_client, kenlm, and python3 installed.  I used a lot of bash for loops to do the majority of the bulk processing steps.

#### Gather your data
First, I built up my library of clips.  [Mimic recording studio](https://github.com/MycroftAI/mimic-recording-studio) can be used to do this.  I had recorded approximately 800 source clips using a combination of common commands I say to mycroft, the top 500 words in the English language, and several papers from arvix on computing topics.  These were recorded in 16 bit, 48khz stereo. Start with the best quality you can, it's easier to make that worse than try and fix bad source material.  If you have saved clips from mycroft, or can easily record noisy or bad voice quality clips, then you should do so.  Described here is a way to augment your data with lower-quality clips.  I have a pair of small diaphragm condensers connected to a usb audio interface.  One mic channel is set for -10db and oriented in approximately 90 degrees from the other in order to make for a slightly different recording on each channel.  I used a short shell script to record a sentence twice, and write out the filename and the transcription to a csv file.  In the csv file you make, it is vitally important that you limit the amount of odd characters, punctuation, and the like.  Also helps to run it through an upper to lower step as well.   

After recording, I used [webrtcvad](https://github.com/wiseman/py-webrtcvad/blob/master/example.py) to trim the silence:
```python3 example.py 1 yourwavefilehere.wav```
This sometimes results in two wave files emerging, usually just one if you're recorded cleanly enough. You should watch for multiples and pick the correct one as needed.  I then used [sox](http://sox.sourceforge.net/) to split the files into left and right channel wavs at 16 bit,16khz mono.  
``` $ sox $i l-$i remix 1```
``` $ sox $i r-$i remix 2```
Additionally, I recorded a short clip of background noise in my house (hey it's where I'll use this most).  With one channel's wav files, I combined the noise and saved those as an additional set of clips.  
``` $ sox -m $j noise.wav n-$j.wav trim 0 $(soxi -D $j) ```
After combining, I used the chorus function of sox to make the quality of the clips slightly worse for another set of clips (play with the values to make it work for you). 
```$ sox $k c-$k chorus .8 .1 25 .4  .1 -t```
 From the other channel, I recorded a fifth set of clips with bad quality (without extra noise).  Now I have left, right, noisy left, noisy bad quality left, and bad quality right.  If you were so motivated, you could also throw in some speed variations on these for good measure.  

On the training machine (local or cloud), I made a directory (/opt/voice/dsmodel/), and sub-directories within for wavs, test, dev, and train.  I placed all my wav files into the wavs directory.  The csv file full of names and transcriptions in the dsmodel dir.  For bonus points, you can run the csv file through shuf to randomize the clip order.  For deepspeech, you want to put 10% into test, 20% into dev, and the remainder into train.  DS wants a particular format for the csv, so I passed each line through a short script to get the filename, find the size of the file in question, and write the file name, size, and transcription to the relevant csv (train.csv/test.csv/dev.csv, each in their respective directory).  You end up with something like:
```
wav_filename,wav_size,transcript
c-r-1550042834-10-1.wav,86444,we are going to turn before that bridge
c-r-1550042834-13-2.wav,78764,four five six seven eight
c-r-1550042834-15-2.wav,69164,nine ten eleven twelve
c-r-1550042834-17-2.wav,88364,thirteen fourteen fifteen sixteen
c-r-1550042834-20-2.wav,69164,twenty thirty forty fifty
```
Don't knock my sample sentences til you try 'em.  ;)  The header line is necessary in each csv.  

#### Prep Steps
To make the alphabet.txt file, you'll want to grab all the transcriptions and sort into unique characters.  
```cut -d, -f3 test/test.csv >> charlist ;cut -d, -f3 train/train.csv >> charlist; cut -d, -f3 dev/dev.csv >> charlist```
I found the charparse.cpp* file on the web, and can't find the source now, will edit if I do.  Compile that (g++ -o charparse charparse.cpp), then you can do:
``` charparse < charlist >alphabet.txt```

IMPORTANT:
review your alphabet.txt and make sure it only has letters and minimal punctuation (I have period and apostophe, then lower case a-z. End on a blank line. 29 lines total for mine, you should be similar.  Non-latin character sets will certainly differ.

Now we build files to model with. Not going to pretend I know what each of these is for, feel free to look up yourself. Start in your dsmodel directory and run:

```$ lmplz --text vocabulary.txt --arpa  words.arpa --o 3```
```$ build_binary -T -s words.arpa  lm.binary```
```$ generate_trie alphabet.txt lm.binary trie```

In your Deepspeech folder (I used /opt/ for stuff), edit your run file.  Here's mine for fun:
```
#!/bin/sh
set -xe
if [ ! -f DeepSpeech.py ]; then
    echo "Please make sure you run this from DeepSpeech's top level directory."
    exit 1
fi;

python3 -u DeepSpeech.py \
  --train_files /opt/voice/dsmodel/train/train.csv \
  --dev_files /opt/voice/dsmodel/dev/dev.csv \
  --test_files /opt/voice/dsmodel/test/test.csv \
  --train_batch_size 48 \
  --dev_batch_size 40 \
  --test_batch_size 40 \
  --n_hidden 1024 \
  --epoch 64 \
  --validation_step 1 \
  --early_stop True \
  --earlystop_nsteps 6 \
  --estop_mean_thresh 0.1 \
  --estop_std_thresh 0.1 \
  --dropout_rate 0.30 \
  --default_stddev 0.046875 \
  --learning_rate 0.0005 \
  --report_count 100 \
  --use_seq_length False \
  --export_dir /opt/voice/dsmodel/results/model_export/ \
  --checkpoint_dir /opt/voice/dsmodel/results/checkout/ \
  --decoder_library_path /opt/DeepSpeech/native_client/libctc_decoder_with_kenlm.so \
  --alphabet_config_path /opt/voice/dsmodel/alphabet.txt \
  --lm_binary_path /opt/voice/dsmodel/lm.binary \
  --lm_trie_path /opt/voice/dsmodel/trie \
  "$@"
```

Two things to keep in mind here are batch_size and n_hidden.   Batch_size is basically scaling how much of the data to load per training step.  I have an 8gb gpu, and on my dataset this worked.  On yours it might be bigger or smaller.  More data is usually smaller.  Try and keep n_hidden even.  The larger you can scale n_hidden, the better your model may be, but the slower it will train. I try powers of 2 type numbers (256, 512,1024, etc).  If you don't keep batch_size even, you may experience a tiresome warning on inference later.  The early stop parameters are there to help prevent overfitting.  I'd recommend keeping them on for any small training set.   The learning rate, dropout rate, stddev bits you can use if need be, review after first model completes.  

#### Runaway with me...
After all of that...start a screen session and run your script.  In another screen session, set up tensorboard on the output directory.  Switch back to your training script and see what error it's popped up. It's fairly good about indicating what it's working on when it errors, ie, it parses the csv files and will indicate what character it doesn't like in them.  Fix anything that comes up, and try again.  

Depending on your data's size and your compute resources, go to sleep for the night or check back in ten minutes.  
```
mycroft@trainer:~/DeepSpeech$ ./run-me.sh 
+ [ ! -f DeepSpeech.py ]
+ python3 -u DeepSpeech.py --train_files /opt/voice/dsmodel/train/train.csv --dev_files /opt/voice/dsmodel/dev/dev.csv --test_files /opt/voice/dsmodel/test/test.csv --train_batch_size 48 --dev_batch_size 40 --test_batch_size 40 --n_hidden 1024 --epoch 64 --validation_step 1 --early_stop True --earlystop_nsteps 6 --estop_mean_thresh 0.05 --estop_std_thresh 0.05 --dropout_rate 0.30 --default_stddev 0.046875 --learning_rate 0.0005 --report_count 100 --use_seq_length False --export_dir /opt/voice/dsmodel/results/model_export/ --checkpoint_dir /opt/voice/dsmodel/results/checkout/ --decoder_library_path /opt/DeepSpeech/native_client/libctc_decoder_with_kenlm.so --alphabet_config_path /opt/voice/dsmodel/alphabet.txt --lm_binary_path /opt/voice/dsmodel/lm.binary --lm_trie_path /opt/voice/dsmodel/trie
Preprocessing ['/opt/voice/dsmodel/train/train.csv']
Preprocessing done
Preprocessing ['/opt/voice/dsmodel/dev/dev.csv']
Preprocessing done
I STARTING Optimization
I Training epoch 0...
 15% (7 of 46) |########################################                                                                                                                                                                                                                                | Elapsed Time: 0:00:04 ETA:   0:00:29
```
Each epoch took about a minute for me, validation on each epoch about one-tenth that.  
Pull up tensorboard from the training machine and watch it make cool graphs.  
And after modeling finished, it looks pretty good:
```
--------------------------------------------------------------------------------
WER: 0.000000, CER: 0.000000, loss: 0.003964
 - src: "wiki search pineapples"
 - res: "wiki search pineapples"
--------------------------------------------------------------------------------
WER: 0.000000, CER: 0.000000, loss: 0.004020
 - src: "the quick brown fox jumped over the lazy dog"
 - res: "the quick brown fox jumped over the lazy dog"
--------------------------------------------------------------------------------
WER: 0.000000, CER: 0.000000, loss: 0.004198
 - src: "sum three and two"
 - res: "sum three and two"
--------------------------------------------------------------------------------
WER: 0.000000, CER: 0.000000, loss: 0.004204
 - src: "a large fawn jumped quickly over white zinc boxes"
 - res: "a large fawn jumped quickly over white zinc boxes"
--------------------------------------------------------------------------------
I Exporting the model...
I Models exported at /opt/voice/dsmodel/results/model_export/
```

From here, you can copy your model to your deepspeech server host, and start doing ASR to your voice's content.  

To make an mmapped model (from https://github.com/mozilla/DeepSpeech):
```
$ convert_graphdef_memmapped_format --in_graph=output_graph.pb --out_graph=output_graph.pbmm
```

When training, the loss for training should be lower than the validation loss.  If validation is less than training loss, you're likely heading towards overfitting territory.  For smaller datasets, lowering the training rate and increasing the epochs may help. You will need to experiment to find out what works best for your data.  

#### Results

So how does it work? Eh....depends.  Largely due to my limited training set, it can work on those lines pretty well. Anything beyond that it tends to get way off course.
"could you tell me the weather in San Francisco" resulted in...

```
initialize: Initialize(model='/opt/voice/models/output_graph.pb', alphabet='/opt/voice/models/alphabet.txt', lm='/opt/voice/models/lm.binary', trie='/opt/voice/models/trie')
creating model /opt/voice/models/output_graph.pb /opt/voice/models/alphabet.txt...
TensorFlow: v1.12.0-14-g943a6c3
DeepSpeech: v0.5.0-alpha.1-67-g604c015
Warning: reading entire model file into memory. Transform model file into an mmapped graph to reduce heap usage.
model is ready.
STT result: i'm able girls able ship water hallway best surface
```

### Fine Tune Instead.

#### No really, you should fine tune instead for English.
The Deepspeech repo's [readme](https://github.com/mozilla/DeepSpeech#continuing-training-from-a-release-model) pretty much covers this.   Download the relevant pre-trained model (1.5gb or so compressed--you will want to run this on an ssd for sure).   Verify that your transcription character set (alphabet.txt) matches the one included in the model.  If not, you will have to adjust your transcriptions or you'll run into problems.  As per the readme, you can then just point the following at your csv's you created earlier:

```
python3 DeepSpeech.py --n_hidden 2048 --checkpoint_dir path/to/checkpoint/folder --epoch -3 --train_files path/to/my-train.csv --dev_files path/to/my-dev.csv --test_files path/to/my_dev.csv --learning_rate 0.0001   --export_dir /opt/deepspeech/results/model_export/ 
```
The ```epoch -3``` means three more epochs.  This appears to skip validation between epochs as well.   
Each step takes significantly longer to train (23 minutes vs. 55 seconds).  This is run on a GTX1070 backed by a ryzen 1600 and 32gb of ram on ssd's.  

```python3 DeepSpeech.py --n_hidden 2048 --checkpoint_dir /opt/deepspeech/5a1/models  --epoch -3 --train_files /opt/deepspeech/train/my-train.csv --dev_files /opt/deepspeech/dev/my-dev.csv --test_files /opt/deepspeech/test/my-test.csv --learning_rate 0.0001  --export_dir /opt/deepspeech/results/model_export/

Preprocessing ['/opt/deepspeech/train/my-train.csv']
Preprocessing done
Preprocessing ['/opt/deepspeech/dev/my-dev.csv']
Preprocessing done
W Parameter --validation_step needs to be >0 for early stopping to work
I STARTING Optimization
I Training epoch 0...
 99% (3584 of 3615) |################################################################################################################################################################################################################################################################   | Elapsed Time: 0:22:32 ETA:   0:00:24
```

That's...it.  Oh yeah, make your resulting model mmapable (see first post) for good measure.  The resulting model is much larger than the customized ones I've created, but also much improved on WER and generalized recognition.


Super annoying recording script:
```
#!/bin/bash

if [[ $# -lt 1 ]] ; then
  echo "Usage: $0 sentencesfile"
fi

if [[ $# -eq 2 ]] ; then
  SEC=$2
else
  SEC=5
fi
RED='\033[0;31m'
NC='\033[0m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
C1=1
DS=$(date +%s)
SFN=$(echo $1 | tr -s '\057' '\012' | tail -1)
echo $SFN

if [[ ! -d tmp ]]; then
  mkdir tmp
fi

record() {

for i in 1 2  ; do
  echo -e "${NC} 2...."
  sleep 1
  echo -e "${BLUE} 1...."
  sleep 1
  echo -e "${RED} Recording for $SEC seconds!"
  iterationname="${DS}-${C1}-${i}"
  #echo -e "${RED} $iterationname"
  arecord -f dat -d $SEC tmp/${iterationname}.wav  
  echo -e "${GREEN} done recording. ${YELLOW} "
  echo "${iterationname},${line}" >> tmp/metadata.csv
done

}

echo "Reading lines from file $1"
sleep 2

while read line ; do
  echo -e "${RED}___________________"

  echo -e "${GREEN}CURRENT SENTENCE: "
  echo " *************** "
  echo -e " ** ${YELLOW}${line} "
  echo -e "${GREEN} *************** "
  echo -e " line $C1${NC}"
  record 
  C1=$((C1 + 1))
done < $1
echo -e "${NC}Done!"
```

charparse.cpp
```
#include <iostream>
#include <set>

int main() {
    std::set<char> seen_chars;
    std::set<char>::const_iterator iter;
    char ch;

    /* ignore whitespace and case */
    while ( std::cin.get(ch) ) {
        if (! isspace(ch) ) {
            seen_chars.insert(tolower(ch));
        }
    }

    for( iter = seen_chars.begin(); iter != seen_chars.end(); ++iter ) {
        std::cout << *iter << std::endl;
    }

    return 0;
}
```
