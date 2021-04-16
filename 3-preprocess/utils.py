import pandas as pd
import numpy as np

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