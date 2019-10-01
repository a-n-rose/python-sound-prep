## Sound Exploration

These are a collection of functions that I use from time to time when working with sounds.

## Jupyter

I like working with sound in Jupyter notebooks. However, not all Python sound libraries work in that environment. But Scipy.io.wavfile works perfectly in Jupyter. 

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

## Combining sounds

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
def combine_sounds(file1, file2, match2shortest=True, time_delay_sec=1,total_dur_sec=5):
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

For example, if the total duration of the long signal is 30 seconds and the shorter signal just 2 seconds, you can use the longer signal as a reference, but keep it shorter than 30 seconds... let's say 15 instead. Therefore, you would set `total_dur_sec` as 15.
