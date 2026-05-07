import os
import numpy as np
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt
from scipy.signal import correlate
from scipy.signal import butter, filtfilt

SAMPLING_RATE = 100 

# Data Dir where experiment data is stored
EXP_DATA_DIR = "./data" 

# Familiarity score for each trial (0; unFamiliar, 1; Familiar)
familiarity_info = {
    'Trial 01': 1,
    'Trial 02': 1,
    'Trial 03': 0,
    'Trial 04': 0,
    'Trial 05': 0,
    'Trial 06': 0,
    'Trial 07': 1,
}

# Band pass Filter 
# Removes frequencies outside the specified range (0.5-5 Hz)
def bandpass_filter(data, lowcut=0.5, highcut=3, fs=SAMPLING_RATE, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, data)
    return y
    
# Function to load and preprocess data
def load_and_preprocess_data(experiment, level, min_length):
    file_path = f'{EXP_DATA_DIR}/{experiment}/level-{level}@pulse_data.json'
    df = pd.read_json(file_path)
    
    # Forward fill to replace NaN values with the next valid value
    df.ffill(inplace=True)
    # Backward fill to replace NaN values with the previous valid value
    df.bfill(inplace=True)

    df = df.iloc[-min_length:]

    game_score = df['Game_score'].iloc[-1]

    df['RAW_IBI_0'] = df['IBI_0'].copy()
    df['RAW_IBI_1'] = df['IBI_1'].copy()
    # Apply band pass filter to IBI_0 and IBI_1
    raw_ibi_0 = df["IBI_0"].values
    raw_ibi_1 = df["IBI_1"].values
    fs=100
    df['IBI_0'] = bandpass_filter(df["IBI_0"].values, 0.5, 5, fs)
    df['IBI_1'] = bandpass_filter(df["IBI_1"].values, 0.5, 5, fs)

    return df, game_score

def load():
    experiments = os.listdir(EXP_DATA_DIR)
    min_length = float('inf')

    for experiment in experiments:
        exp_files = os.listdir(os.path.join(EXP_DATA_DIR, experiment))
        pulse_data_files = [e for e in exp_files if "pulse_data.json" in e]
        
        for data_file in pulse_data_files:
            level = data_file.split("@")[0].split("-")[1]
            df, _ = load_and_preprocess_data(experiment, level, 0)
            
            if len(df) < min_length:
                min_length = len(df)
            
    # Main Analysis Function
    all_synchrony_scores = []
    all_game_scores = []
    experiment_data = {}

    experiments = os.listdir(EXP_DATA_DIR)

    for experiment in experiments:
        # print("Exp:", experiment)
        exp_files = os.listdir(os.path.join(EXP_DATA_DIR, experiment))
        pulse_data_files = [e for e in exp_files if "pulse_data.json" in e]
        
        experiment_data[experiment] = {}
        
        for data_file in pulse_data_files:
            level = data_file.split("@")[0].split("-")[1]
            # print("Level:", level)

            # Load and preprocess data
            df, game_score = load_and_preprocess_data(experiment, level, min_length)
            
            # Extract IBI and PPG signals
            ibi_0 = df['IBI_0'].values
            ibi_1 = df['IBI_1'].values

            signal_0 = df['Signal_0'].values
            signal_1 = df["Signal_1"].values

            # Ensure no NaN values in signals
            signal_0 = np.nan_to_num(signal_0, nan=np.nanmean(signal_0))
            signal_1 = np.nan_to_num(signal_1, nan=np.nanmean(signal_1))
            
            
            try:
                # Calculate IBI synchronization
                # cross-correlate function (ccf)
                
                from statsmodels.tsa.stattools import ccovf, ccf

                cross_corr_ibi = ccf(ibi_0, ibi_1)

                # Process PPG signals using NeuroKit
                processed_signal_0, info_0 = nk.ppg_process(signal_0, sampling_rate=SAMPLING_RATE)
                processed_signal_1, info_1 = nk.ppg_process(signal_1, sampling_rate=SAMPLING_RATE)
        
                # Extract cleaned signals and peaks 
                cleaned_0 = processed_signal_0['PPG_Clean']
                cleaned_1 = processed_signal_1['PPG_Clean']
                peaks_0 = processed_signal_0['PPG_Peaks']
                peaks_1 = processed_signal_1['PPG_Peaks']


                max_corr_ibi = np.max(cross_corr_ibi) #/ (np.std(ibi_0) * np.std(ibi_1) * len(ibi_0))
                # Ensure max_corr_ibi is not NaN
                if np.isnan(max_corr_ibi):
                    print(f'NaN detected in max_corr_ibi: {experiment}, {level}')
                    continue
                
                # Check if enough peaks were detected
                if sum(peaks_0) < 2 or sum(peaks_1) < 2:
                    print(f'Not enough peaks detected: {experiment}, {level}')
                    continue
                
            except Exception as e:
                print(f'Failed processing: {experiment}, {level}. Error: {str(e)}')
                continue


            all_synchrony_scores.append({
                'experiment': experiment,
                'level': level,
                'cross_corr_ibi': cross_corr_ibi,
                'max_corr_ibi': max_corr_ibi,
                'game_score': game_score,
                'familiarity': familiarity_info[experiment],
                'ibi_0': ibi_0,
                'ibi_1': ibi_1,
                'signal_0': signal_0,
                'signal_1': signal_1,
                'cleaned_0': cleaned_0,
                'cleaned_1': cleaned_1,
                'raw_ibi_0': df['RAW_IBI_0'].values,
                'raw_ibi_1': df["IBI_1"].values,
                'peaks_0': peaks_0,
                'peaks_1': peaks_1
            })

            
    # Convert results to Data Frame
    synchrony_df = pd.DataFrame(all_synchrony_scores)

    # Check if max_corr_ibi column exists and has no NaN values
    if 'max_corr_ibi' not in synchrony_df.columns:
        print("Error: 'max_corr_ibi' column is missing.")
        return None

    if synchrony_df['max_corr_ibi'].isna().any():
        print("Error: 'max_corr_ibi' column contains NaN values.")
        return None

    synchrony_df['index'] = synchrony_df.index

    synchrony_df = synchrony_df.dropna(subset=['max_corr_ibi'])

    # Check if min and max values for normalization are valid
    min_max_corr_ibi = synchrony_df['max_corr_ibi'].min()
    max_max_corr_ibi = synchrony_df['max_corr_ibi'].max()
    if min_max_corr_ibi == max_max_corr_ibi:
        print("Error: 'max_corr_ibi' column has identical min and max values, cannot normalize.")
        return None

    synchrony_df['max_corr_ibi_normalized'] = (synchrony_df['max_corr_ibi'] - min_max_corr_ibi) / (max_max_corr_ibi - min_max_corr_ibi)

    min_game_score = synchrony_df['game_score'].min()
    max_game_score = synchrony_df['game_score'].max()
    if min_game_score == max_game_score:
        print("Error: 'game_score' column has identical min and max values, cannot normalize.")
        return None

    synchrony_df['game_score_normalized'] = (synchrony_df['game_score'] - min_game_score) / (max_game_score - min_game_score)

    return synchrony_df

def load_qualtrics_data():
    qa_df = pd.read_csv("qualtrics_processed.csv")
    return qa_df

def merge_sync_qa_data(sync_df, qa_df):
    merged_df = pd.merge(sync_df, qa_df, on='experiment', how='left')
    return merged_df
    
def convert_data_time_series(synchrony_df, merged_df):
    import numpy as np
    import pandas as pd

    time_df = merged_df
    time_df = time_df[['experiment', 'level', 'game_score', 'cross_corr_ibi', 'max_corr_ibi', 'Age', 'Gender', 'familiarity', 'Overall Collaboration']]

    window_length = 200
    time_df['cross_corr_ibi'] = time_df['cross_corr_ibi'].apply(lambda x: np.convolve(x, np.ones(window_length)/window_length, mode='valid'))

    time_df = time_df.explode('cross_corr_ibi')
    time_df['order'] = time_df.groupby(['experiment', 'level']).cumcount()

    time_df['new_order'] = time_df.groupby(['experiment',]).cumcount()
    
    time_df["game_score_normalized"] = 0

    time_df['max_order'] = time_df.groupby(['experiment', 'level'])['order'].transform('max')

    time_df.loc[time_df['order'] == time_df['max_order'], 'game_score_normalized'] = synchrony_df['game_score_normalized']

    # add number values for levels instead of name
    level_mapping = {level: i+1 for i, level in enumerate(time_df["level"].unique())}

    time_df["level_num"] = time_df["level"].map(level_mapping)

    # set all max_cross_corr_ibi_norm to NA where game_score is NA to mimic time series data 
    time_df.loc[time_df["game_score_normalized"].isna(), "max_cross_corr_ibi_norm"] = pd.NA

    return time_df

