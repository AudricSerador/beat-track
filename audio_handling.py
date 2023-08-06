import librosa
import numpy as np
import time
from collections import OrderedDict
import matplotlib.pyplot as plt

t1 = time.time()

# Checks if audio file inserted has vocal lyrics. If not, return False.
def is_vocal(audio_data, sampling_rate):
    # Perform Harmonic-Percussive Source Separation (HPSS)
    harmonic, percussive = librosa.effects.hpss(audio_data)

    # Extract spectral features for the harmonic component
    spectral_centroid = librosa.feature.spectral_centroid(y=harmonic, sr=sampling_rate)[0]
    spectral_rolloff = librosa.feature.spectral_rolloff(y=harmonic, sr=sampling_rate)[0]
    spectral_flatness = librosa.feature.spectral_flatness(y=harmonic)[0]
    
    sc_mean = np.mean(spectral_centroid)
    sr_mean = np.mean(spectral_rolloff)
    sf_mean = np.mean(spectral_flatness)

    # Threshold values for each feature to determine if it's vocal or instrumental
    centroid_threshold = 1250  # Adjust this value based on your analysis
    rolloff_threshold = 2250  # Adjust this value based on your analysis
    flatness_threshold = 0.001   # Adjust this value based on your analysis

    # Check if any of the features indicate vocals
    is_vocal = (sc_mean > centroid_threshold) or \
            (sr_mean > rolloff_threshold) or \
            (sf_mean > flatness_threshold)
    
    
    if is_vocal:
        print(f"The song is likely to have vocals.\nSC: {sc_mean}\nSR: {sr_mean}\nSF: {sf_mean}")
    else:
        print(f"The song is likely to be instrumental.\nSC: {sc_mean}\nSR: {sr_mean}\nSF: {sf_mean}")
    
    return is_vocal

# get song data based on difficulty chosen
# easy: onset data and/or beat times, very slow paced
# medium: just beat times?, slow paced
# hard: beat times and onset data, medium paced
# expert: beat times and onset data, random bpm, fast paced
# impossible: beat times and onset data, with maximum bpm and speed
def get_song_data(audio_path: str, difficulty: str):    
    match difficulty:
        case "easy":
            return get_pitch_beat(audio_path)
        case "medium":
            return get_pitch_onset(audio_path)
        case "hard":
            pass
        case "expert":
            pass
        case "impossible":
            return get_pitch_all(audio_path)
    
def get_pitch_onset(audio_path):
    y, sr = librosa.load(audio_path)

    # Perform onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    onset_times= onset_times.tolist()

    # Get pitch information using piptrack
    pitches, _ = librosa.piptrack(y=y, sr=sr)

    # Find the closest pitch values to the detected onset times
    pitch_at_onsets = []
    for onset_time in onset_times:
        frame_idx = librosa.time_to_frames(onset_time, sr=sr)
        closest_pitch = pitches[:, frame_idx].max()
        pitch_at_onsets.append(closest_pitch)

    # Create a dictionary of onsets and corresponding pitch values
    onset_pitch_dict = {onset_time: pitch for onset_time, pitch in zip(onset_times, pitch_at_onsets)}

    return onset_pitch_dict

def get_pitch_beat(audio_path):
    y, sr = librosa.load(audio_path)

    # Perform beat tracking
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    beat_times = beat_times.tolist()

    # Get pitch information using piptrack
    pitches, _ = librosa.piptrack(y=y, sr=sr)

    # Find the closest pitch values to the detected onset times
    pitch_at_beats = []
    for onset_time in beat_times:
        frame_idx = librosa.time_to_frames(onset_time, sr=sr)
        closest_pitch = pitches[:, frame_idx].max()
        pitch_at_beats.append(closest_pitch)

    # Create a dictionary of onsets and corresponding pitch values
    beat_pitch_dict = {onset_time: pitch for onset_time, pitch in zip(beat_times, pitch_at_beats)}

    return beat_pitch_dict

def get_pitch_all(audio_path):
    y, sr = librosa.load(audio_path)

    # Perform beat tracking
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    beat_times = beat_times.tolist()

    # Perform onset detection
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    onset_times = onset_times.tolist()

    # Get pitch information using piptrack
    pitches, _ = librosa.piptrack(y=y, sr=sr)

    # Find the closest pitch values to the beat times
    pitch_at_beats = []
    for beat_time in beat_times:
        frame_idx = librosa.time_to_frames(beat_time, sr=sr)
        closest_pitch = pitches[:, frame_idx].max()
        pitch_at_beats.append(closest_pitch)

    # Find the closest pitch values to the onset times
    pitch_at_onsets = []
    for onset_time in onset_times:
        frame_idx = librosa.time_to_frames(onset_time, sr=sr)
        closest_pitch = pitches[:, frame_idx].max()
        pitch_at_onsets.append(closest_pitch)

    # Create dictionaries with both beat times and onset times as keys and corresponding pitch values
    beat_time_pitch_dict = {beat_time: pitch for beat_time, pitch in zip(beat_times, pitch_at_beats)}
    onset_time_pitch_dict = {onset_time: pitch for onset_time, pitch in zip(onset_times, pitch_at_onsets)}

    # Merge both dictionaries and sort by keys
    time_pitch_dict = {**beat_time_pitch_dict, **onset_time_pitch_dict}
    sorted_time_pitch_dict = {k: v for k, v in sorted(time_pitch_dict.items(), key=lambda item: item[0])}

    return sorted_time_pitch_dict

'''
path = 'audio/field.wav'
# audio_data, sampling_rate = librosa.load(path)
data = get_pitch_beat(path)
values_array = np.array(list(data.values()))

# Find the maximum and minimum values
max_value = np.max(values_array)
min_value = np.min(values_array)

print(f"max: {max_value} min: {min_value}")
print(data)

plt.plot(data.keys(), data.values(), marker='o')
plt.xlabel('Time')
plt.ylabel('Pitch')
plt.title('Time vs Pitch in Song')
plt.show()
'''

print(f"Time it took: {time.time() - t1}")