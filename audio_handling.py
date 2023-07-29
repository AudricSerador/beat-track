import librosa
import numpy as np
import time
from collections import OrderedDict

t1 = time.time()
def get_song_data(audio_path: str):
    # Load the audio file
    audio_data, sampling_rate = librosa.load(audio_path)

    # Perform audio analysis and extract beat and onset information
    
    
    tempo, beats = librosa.beat.beat_track(y=audio_data, sr=sampling_rate)
    beat_times = librosa.frames_to_time(beats, sr=sampling_rate)
    beat_data = beat_times.tolist()
    
    
    onset_frames = librosa.onset.onset_detect(y=audio_data, sr=sampling_rate)
    onset_times = librosa.frames_to_time(onset_frames, sr=sampling_rate)
    onset_data = onset_times.tolist()
    
    total_data = beat_data + onset_data
    total_data.sort()
    total_data = list(OrderedDict.fromkeys(total_data))
    # Print the extracted beat and onset information
    print(f"Tempo (BPM): {tempo}")
    
    return total_data # array of beat times in seconds

     #  print(f"Onset Times (seconds): {onset_times}")
     
# print(get_song_data('audio/nights.wav'))
     
print(f"Time it took: {time.time() - t1}")