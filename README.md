## Sound Exploration

These are a collection of functions that I use from time to time when working with sounds. They cover:

* visualizations
* preparation of sound for online environment (i.e. JupyterLab)
* adding soundfiles together
* etc. (no examples prepared)

## Installation

Clone this repository. Establish your working directory where the files `requirements.txt` and `soundprep.py` are located.

I would suggest setting up an environment:
```
$ python3 -m venv env
$ source env/bin/activate
(env)...$ 
```
Then install the dependencies:
```
(env)...$ pip install -r requirements.txt
```
I tend to just use ipython.. which you can easily install via pip:
```
(env)...$ pip install ipython
(env)...$ ipython
```
From there you can use the functionality below, as documented.


## Visualizing sound

We will visualize sound first as a sound wave, in the time domain, and then in the frequency domain (MFCC and FBANK features).

```
>>> import explore_sound as es
>>> # first create a signal to visualize
>>> samples, samplerate = es.create_signal(freq=5, dur_sec=1)
>>> es.visualize_signal(samples, samplerate=samplerate)
```
![Imgur](https://i.imgur.com/uCV2pgN.png)

#### Add noise:
```
>>> noise = es.create_noise(len(samples), amplitude=0.025)
>>> samples_noisy = samples + noise
>>> es.visualize_signal(samples_noisy, samplerate=samplerate)
```
![Imgur](https://i.imgur.com/pj2SiY4.png)

#### Multiple frequencies: time domain
```
>>> samples500, samplerate = es.create_signal(freq=500, dur_sec=0.25)
>>> samples1200, samplerate = es.create_signal(freq=1200, dur_sec=0.25)
>>> samples2000, samplerate = es.create_signal(freq=2000, dur_sec=0.25)
>>> samples_mixed = samples500 + samples1200 + samples2000
>>> es.visualize_signal(samples_mixed, samplerate=samplerate)
```
![Imgur](https://i.imgur.com/LEfqQtO.png)

#### Multiple frequencies: frequncy domain
```
>>> es.visualize_feats(samples_mixed, samplerate=samplerate, features='mfcc', save_pic=True)
```
![Imgur](https://i.imgur.com/GeZJiBX.png)

```
>>> es.visualize_feats(samples_mixed, samplerate=samplerate, features='fbank', save_pic=True)
```
![Imgur](https://i.imgur.com/ivJ9fBG.png)


## Prepare Audio for Jupyter Lab

I like working with sound in Jupyter notebooks. However, not all Python sound libraries work in that environment. But Scipy.io.wavfile works perfectly. 

I am working on a collection of functions that help me when I am experimenting with sound and want to use them in Jupyter. 

### Examples

Let's say I want to load a file into a Jupyter notebook but it is of file type .mp3 or .flac. Or, perhaps the bit depth isn't compatible.. 

```
>>> from scipy.io.wavfile import read

>>> flac_file = 'sound.flac'
>>> sr, data = read(flac_file)
ValueError: File format b'fLaC'... not understood.
```

Oh noooo! What to do?

```
>>> import soundprep as sp
>>> data, sr = sp.loadsoundfile(flac_file)
Step 1: ensure filetype is compatible with scipy library
Success!
```
If you would rather simply create a new file that is compatible with scipy's wavfile module, you can do the following:

```
>>> filename_new = sp.prep4scipywavfile(flac_file) 
Converting file to .wav
Saved file as <filename>.wav
```

In both of the above cases, new wavfiles are saved and can be used in a Jupyter notebook.


## Combining Sounds

Often I like to explore sounds added with various other sounds, either for filtering or training or just for fun. I have also put together a couple of functions for such purposes.

### Examples

### Speech + background noise

Let's say you would like to add background noise to a signal of interest. For example, if you are trying to create a recording that sounds like is happening at the zoo, take a regular speech recording and add some zoo background noise.

```
>>> import soundprep as sp
>>> combined_samples, samplerate = sp.add_sound_to_signal(
                                                        'speech.wav',
                                                        'zoo.flac', 
                                                        delay_target_sec = 1)
>>> # save samples with scipy
>>> from scipy.io.wavfile import write
>>> write('speech_in_zoo.wav',samplerate, combined_samples)
```

What did I do above? `delay_target_sec` refers to how long should the background noise be playing without the target signal, i.e. 'speech.wav'. Here would be a full second of zoo background noise before the speech starts. 

The speech and the noise have different file types but that's just fine. The function converts them to a compatible format for scipy.io.wavfile for you. 

What's cool about this function is if the background noise is too short, it is simply repeated until it fulfills the amount of noise you need. Therefore, it is best with unremarkable/stationary background noise.

Problem: what if you play that sound and hear that the zoo background noise is waaaaaay too loud (or too quiet). Below I show you how to reduce that background noise with the argument `scale`:
```
>>> combined_samples, samplerate = sp.add_sound_to_signal(
                                                        'speech.wav',
                                                        'zoo.flac', 
                                                        delay_target_sec = 1,
                                                        scale = 0.5)
>>> # save samples with scipy
>>> from scipy.io.wavfile import write
>>> write('speech_in_zoo_half_as_loud.wav',samplerate, combined_samples)
```
You listen to it again, and it's much better. 

### Speech + Music

Let's say you have two relevant signals: a short speech signal and a long music signal. You want the speech signal to occur at some point in the music signal. This functionality allows for a bit more flexility in that regard without repeating either of the signals (as done in the above example).

```
>>> combined_samples, sr = sp.combine_sounds(
                                            'speech.wav', 
                                            'music.wav',
                                            match2shortest = False,
                                            time_delay_sec = 1,
                                            total_dur_sec = 5)
>>> write('speech_music.wav',sr, combined_samples)
```
The `match2shortest` parameter allows you to control whether the adding of the two signals respects the length of the shorter signal or the longer one. If it respects the shorter one, the longer one will simply be shortened. If it respects the longer signal, the shorter signal is zero padded. 

The parameters `time_delay_sec` and `total_dur_sec` allows you to control at which point the shorter signal gets added to the longer one, and how long the longer signal plays. 

For example, if the total duration of the long signal is 30 seconds and the shorter signal just 2 seconds, you can use the longer signal as a reference, but keep it shorter than 30 seconds... let's say 15 instead. Therefore, you would set `total_dur_sec` as 15. Let's also say that you would like the shorter signal to be added 8 seconds into the longer one; you can control that by setting `time_delay_sec` to 8.

## General functions

There are more functions you can use and I suggest to just peak through the code if you're interested. For example, there is a function for making stereo sound data mono instead, or normalizing the samples between certain values. 

## Feedback

If you wish certain functionality were available, hit me up. I'm mainly curious but who knows, maybe I'd be able to set that up!
