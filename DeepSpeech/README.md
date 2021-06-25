
#### Custom/fine-tuning models

See [here](https://deepspeech.readthedocs.io/en/latest/TRAINING.html)

#### DStest.py

This tool can be used to query a deepspeech-server instance using various filtering mechanisms.  For de-noising, requires the [xipn rnnoise](https://github.com/xiph/rnnoise) library to be compiled and installed and [this](https://github.com/Shb742/rnnoise_python) to be locally available (also included in this repo).  For the future, will add filter to make the silence padding optional as well.

```$ python3 ./DStest.py -h
usage: DStest.py [-h] [-H HIGHPASS] [-L LOWPASS] -U URL [-D] [-N] 
                 [-O ORDER] [-v] [--targetdb TARGETDB]
                 wavfile

positional arguments:
  wavfile               wav file to test on.

optional arguments:
  -h, --help            show this help message and exit
  -H HIGHPASS, --highpass HIGHPASS
                        high pass frequency.
  -L LOWPASS, --lowpass LOWPASS
                        low pass frequency.
  -U URL, --url URL     Deepspeech Server URL.
  -D, --denoise         de-noise clip.
  -N, --normalize       normalize clip.
  -O ORDER, --order ORDER
                        order of filters. Optional. HLDN would be Highpass,
                        Lowpass, denoise, then normalize. If order is
                        specified, only items included are run. N = normalize
                        D = de-noise L = low pass filter H = high pass filter
  -v, --verbose         Be verbose
  --targetdb TARGETDB   Decibel target for normalize. (optional)
```

Typical usage:
```
$ DStest.py  -N -D -L 3000 -H 300 --order NHLD -U http://localhost:1880/stt $wavfile
Filtered: you might have to say that a different way
```

#### Other things

Splitting a large file into separate wavs (adjust .3 as needed):
```sox input.wav output.wav silence 1 0.1 1% 1 0.3 1% : newfile : restart ```

Converting a file to the default DS format:
```sox input.wav -c 1 -b 16 -r 16000 output.wav```
