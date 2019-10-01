#A collection of functions handling sound data

from scipy.io.wavfile import read
import soundfile as sf
import librosa
import numpy as np


def normsound(samples,min_val=-1,max_val=1):
    samples = np.interp(samples,(samples.min(), samples.max()),(min_val, max_val))
    return samples

def loadsoundfile(filename, norm=True, mono=True):
    try:
        sr, data = read(filename)
    except ValueError:
        print("Ensuring {} filetype is compatible with scipy library".format(filename))
        filename = convert2wav(filename)
        try:
            data, sr = loadsoundfile(filename)
        except ValueError:
            print("Ensuring bitdepth is compatible with scipy library")
            filename = newbitdepth(filename)
            data, sr = loadsoundfile(filename)
    if mono and len(data.shape) > 1:
        if data.shape[1] > 1:
            data = stereo2mono(data)
    if norm:
        data = normsound(data, -1, 1)
    return data, sr

def prep4scipywavfile(filename):
    try:
        sr, data = read(filename)
        return filename
    except ValueError as e:
        import pathlib
        if pathlib.Path(filename).suffix.lower() != '.wav': 
            print("Converting file to .wav")
            filename = convert2wav(filename)
            print("Saved file as {}".format(filename))
        elif 'bitdepth' not in str(filename):
            print("Ensuring bitdepth is compatible with scipy library")
            filename = newbitdepth(filename)
            print("Saved file as {}".format(filename))
        else:
            #some other error
            raise e
        filename = prep4scipywavfile(filename)
    return filename

def convert2wav(filename, samplerate=None):
    '''Convert to .wav file type, to ensure compatibility with scipy.io.wavfile
    
    Scipy.io.wavfile is easily used online, for example in Jupyter notebooks.
    '''
    import pathlib
    f = pathlib.Path(filename)
    extension_orig = f.suffix
    if not extension_orig:
        f = str(f)
    else:
        f = str(f)[:len(str(f))-len(extension_orig)]
    f_wavfile = f+'.wav'
    if samplerate:
        data, sr = librosa.load(filename, sr=samplerate)
    else:
        data, sr = sf.read(filename)
    sf.write(f_wavfile, data, sr)
    return f_wavfile

def replace_ext(filename, extension):
    filestring = str(filename)[:len(str(filename))-len(filename.suffix)]
    file_newext = filestring + extension
    return file_newext

def match_ext(filename1, filename2):
    '''Matches the file extensions. If both have extensions, default set to `filename1` extension
    '''
    import pathlib
    f1 = pathlib.Path(filename1)
    f2 = pathlib.Path(filename2)
    if not f1.suffix:
        if not f2.suffix:
            raise TypeError('No file extension provided. Check the filenames.')
        else: 
            extension = f2.suffix
    else: 
        extension = f1.suffix 
    if f1.suffix != extension:
        f1 = replace_ext(f1, extension)
    else:
        f1 = str(f1)
    if f2.suffix != extension:
        f2 = replace_ext(f2, extension)
    else:
        f2 = str(f2)
    return f1, f2

def newbitdepth(wave, bitdepth=16, newname=None, overwrite=False):
    '''Convert bitdepth to 16 or 32, to ensure compatibility with scipy.io.wavfile
    
    Scipy.io.wavfile is easily used online, for example in Jupyter notebooks.
    
    Reference
    ---------
    https://stackoverflow.com/questions/44812553/how-to-convert-a-24-bit-wav-file-to-16-or-32-bit-files-in-python3
    '''
    if bitdepth == 16:
        newbit = 'PCM_16'
    elif bitdepth == 32:
        newbit = 'PCM_32'
    else:
        raise ValueError('Provided bitdepth is not an option. Available bit depths: 16, 32')
    data, sr = sf.read(wave)
    if overwrite:
        sf.write(wave, data, sr, subtype=newbit)
        savedname = wave
    else:
        try:
            sf.write(newname, data, sr, subtype=newbit)
        except TypeError as e:
            if not newname:
                newname = adjustname(wave, adjustment='_bitdepth{}'.format(bitdepth))
                print("No new filename provided. Saved file as '{}'".format(newname))
                sf.write(newname, data, sr, subtype=newbit)
            elif newname:
                #make sure new extension matches original extension
                wave, newname = match_ext(wave, newname)
                sf.write(newname, data, sr, subtype=newbit)
            else:
                raise e
        savedname = newname
    return savedname

def adjustname(filename, adjustment=None):
    import pathlib
    f = pathlib.Path(filename)
    fname = f.stem
    if adjustment:
        fname += adjustment
    else:
        fname += '_adj'
    fname += f.suffix
    return fname

def resample_audio(samples, sr_original, sr_desired):
    '''Allows audio samples to be resampled to desired sample rate.
    '''
    time_sec = len(samples)/sr_original 
    num_samples = int(time_sec * sr_desired)
    resampled = resample(samples, num_samples)
    return resampled, sr_desired

def stereo2mono(data):
    data_mono = np.take(data,0,axis=-1) 
    return data_mono

def add_sound_to_signal(target_filename, sound2add_filename, scale=1, delay_target = 1):
    target, sr = loadsoundfile(target_filename)
    sound2add, sr2 = loadsoundfile(sound2add_filename)
    if sr != sr2:
        sound2add, sr = resample_audio(sound2add, sr2, sr)
    sound2add *= scale
    firstsec = sound2add[:sr]
    sound2add = sound2add[sr:]
    if len(sound2add) < len(target):
        sound2add2 = extend_sound(sound2add, len(target))
    sound2add2 = sound2add[:len(target)]
    assert len(sound2add2) == len(target)
    combined = sound2add2 + target
    if delay_target:
        combined = np.concatenate((firstsec,combined))
    return combined, sr

def extend_sound(data, target_len):
    diff = target_len - len(data)
    while len(data) < target_len:
        data = np.concatenate((data,data))
    data = data[:target_len]
    assert len(data) == target_len
    return data

def zeropad_sound(data, target_len, sr, delay_sec=1):
    delay_samps = sr * delay_sec
    if len(data) < target_len:
        diff = target_len - len(data)
        signal_zeropadded = np.zeros((data.shape[0] + int(diff)))
        for i, row in enumerate(data):
            signal_zeropadded[i+delay_samps] += row
    return signal_zeropadded

def combine_sounds(file1, file2, match2shortest=True, time_delay_sec=1,total_dur_sec=5):
    data1, sr1 = loadsoundfile(file1)
    data2, sr2 = loadsoundfile(file2)
    if sr1 != sr2:
        data2, sr2 = resample_audio(data2, sr2, sr1)
    if time_delay_sec:
        num_extra_samples = int(sr1*time_delay_sec)
    else:
        num_extra_samples = 0
    if len(data1) > len(data2):
        data_long = data1
        data_short = data2
    else:
        data_long = data2
        data_short = data1
    dl_copy = data_long.copy()
    ds_copy = data_short.copy()
    
    if match2shortest:
        data_short = zeropad_sound(data_short, len(ds_copy) + num_extra_samples, sr1, delay_sec= time_delay_sec)
        data_long = data_long[:len(ds_copy)+num_extra_samples]
    else:
        data_short = zeropad_sound(data_short,len(dl_copy), sr1, delay_sec= time_delay_sec)
    added_sound = data_long + data_short
    
    if total_dur_sec:
        added_sound = added_sound[:sr1*total_dur_sec]
    return added_sound, sr1

