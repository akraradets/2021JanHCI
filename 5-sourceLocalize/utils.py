import pandas as pd
import numpy as np
import mne
import pickle 
import os

def clear_cache():
    os.remove("cache/EEG_audio.pickle")
    os.remove("cache/EEG_image.pickle")


def save(data, filename):
    if(os.path.exists('cache/') == False):
        os.mkdir('cache/')

    with open(f'cache/{filename}.pickle', 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load(filename):
    with open(f'cache/{filename}.pickle', 'rb') as handle:
        data = pickle.load(handle)
    return data


def load_data(path, exclude_list=[]):
    from os import walk
    from tqdm.notebook import tqdm
    _,_, filenames = next(walk(path))

    for id in exclude_list:
        audio_path = os.path.join(path,f"{id}-audio.csv")
        image_path = os.path.join(path,f"{id}-image.csv")
        if(os.path.exists(audio_path) == False):
            raise ValueError(f"{audio_path} is not exist")
        if(os.path.exists(image_path) == False):
            raise ValueError(f"{image_path} is not exist")
    
        filenames.remove(f"{id}-audio.csv")
        filenames.remove(f"{id}-image.csv")

    columns = {'Unnamed: 1':'Fp1',
            'Unnamed: 2':'Fp2',
            'Unnamed: 3':'F3',
            'Unnamed: 4':'F4',
            'Unnamed: 5':'F7',
            'Unnamed: 6':'F8',
            'Unnamed: 7':'P7',
            'Unnamed: 8':'P8'}

    EEG_audio, EEG_image = dict(), dict()
    from itertools import product
    categories = [1,2,3,4,5]
    blocks = [1,2]
    with tqdm(filenames) as t:
        for filename in t:
            t.set_description(f"{filename}")
            participant_id, stimuli = filename.split('-')
            stimuli = stimuli.rstrip('.csv')
            data = pd.read_csv(f'{path}/{filename}', dtype={'Marker': str}).rename(columns=columns).drop(columns='timestamps')
            # Aviod warning on stim has negative value
            marker = np.array(data['Marker'])
            marker[marker == '-1'] = '1'
            data['Marker'] = marker

            if(stimuli == 'audio'):
                EEG_audio[int(participant_id)] = data
            elif(stimuli == 'image'):
                EEG_image[int(participant_id)] = data
            else:
                raise ValueError(f"Stimuli:{stimuli} is unexpected.")
    return EEG_audio, EEG_image




def load_groudtruth(path='./HEXACO.csv'):
    df = pd.read_csv(path)
    # Honesty-Humility	Emotionality	eXtraversion	Agreeableness	Conscientiousness	Openness to Experience
    gt = df[['id','Honesty-Humility','Emotionality','eXtraversion','Agreeableness','Conscientiousness','Openness to Experience']].rename(columns={'Honesty-Humility':'h',
                                    'Emotionality':'e',
                                    'eXtraversion':'x',
                                    'Agreeableness':'a',
                                'Conscientiousness':'c',
                            'Openness to Experience':'o'}).set_index('id')

    gt['lh'] = (gt[['h']] > np.median(gt['h'])) * 1
    gt['le'] = (gt[['e']] > np.median(gt['e'])) * 1
    gt['lx'] = (gt[['x']] > np.median(gt['x'])) * 1
    gt['la'] = (gt[['a']] > np.median(gt['a'])) * 1
    gt['lc'] = (gt[['c']] > np.median(gt['c'])) * 1
    gt['lo'] = (gt[['o']] > np.median(gt['o'])) * 1
    return gt


def dataframe_to_raw(dataframe, sfreq):
    ch_names = list(dataframe.columns)
    ch_types = ['eeg'] * (len(dataframe.columns) - 1) + ['stim']
    ten_twenty_montage = mne.channels.make_standard_montage('standard_1020')

    dataframe = dataframe.T  #mne looks at the tranpose() format
    dataframe[:-1] *= 1e-6  #convert from uVolts to Volts (mne assumes Volts data)
    # dataframe[:-1] *= 1e3  #convert from uVolts to Volts (mne assumes Volts data)

    info = mne.create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sfreq, verbose=False)

    raw = mne.io.RawArray(dataframe, info,verbose=False)
    raw.set_montage(ten_twenty_montage)
    # raw.plot()
    return raw

def get_section_from_marker(dataframe, start_marker:str, last_marker:str):
    if(len(start_marker.split('_')) != 3):
        raise ValueError(f"The input start_marker:{start_marker} is not in the correct format of [cat]_[block]_[no]")
    if(len(last_marker.split('_')) != 3):
        raise ValueError(f"The input last_marker:{last_marker} is not in the correct format of [cat]_[block]_[no]")
    
    start_index = dataframe.loc[dataframe['Marker'] == start_marker].index
    # Check that there is one and only index
    if(len(start_index) != 1):
        raise ValueError(f"The number of index of marker:{start_marker} is not 1\nindex:{start_index}")

    last_index = dataframe.loc[dataframe['Marker'] == last_marker].index
    # Check that there is one and only index
    if(len(last_index) != 1):
        raise ValueError(f"The number of index of marker:{last_marker} is not 1\nindex:{last_index}")

    start_index = start_index[0]
    last_index = last_index[0]

    break_marker = '-1'
    break_indexes = dataframe.loc[dataframe['Marker'] == break_marker].index
    break_index =  break_indexes[np.argmin(abs(break_indexes - last_index))]
    if(break_index < last_index):
        break_index = last_index + 250
    section = dataframe.iloc[start_index:break_index].copy()
    section.reset_index(drop=True, inplace=True)
    return section

def get_section_from_catblock(dataframe, category:int, block:int):
    if(type(category) != int):
        raise ValueError(f"category must be type {int}")
    if(category not in [1,2,3,4,5]):
        raise ValueError(f"category must be in range {[1,2,3,4,5]}")
    
    if(type(block) != int):
        raise ValueError(f"block must be type {int}")
    if(block not in [1,2]):
        raise ValueError(f"block must be in range {[1,2]}")
    

    start_marker = f"{category}_{block}_1"
    last_marker = f"{category}_{block}_5"
    return get_section_from_marker(dataframe, start_marker, last_marker)