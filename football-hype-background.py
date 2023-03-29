import youtube_dl
import speech_recognition as sr
import yt_dlp
import os
import shutil
import nltk
import yt_dlp.utils
import subprocess
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search
from nltk.sentiment import SentimentIntensityAnalyzer
import sounddevice as sd
import numpy as np
import sys
import wavio
import queue
import time
from pydub import AudioSegment

nltk.download('vader_lexicon')

attacking_keywords = [
    'attack', 'shot', 'shoot', 'chance', 'goal', 'score', 'cross', 'corner', 'opportunity',
    'header', 'free kick', 'penalty', 'assist', 'counterattack', 'break', 'through ball',
    'one-on-one', 'foul', 'possession', 'build-up', 'dangerous', 'in the box', 'finish',
    'goal-bound', 'strike', 'long range', 'volley', 'target', 'pressure', 'offensive',
    'forward', 'clearance', 'threat', 'onside', 'danger', 'goalkeeper save', 'blocked shot',
    'whistle', 'set piece', 'goal line', 'goalmouth', 'scramble', 'last-ditch',
    'tackle', 'rebound', 'narrowly wide', 'post', 'crossbar', 'woodwork', 'close call', 'equalize'
]

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata.copy())

def record_audio(duration, filename):
    q = queue.Queue()

    def callback(indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    # Set the recording settings
    channels = 1
    samplerate = 16000

    try:
        # Open the audio input stream
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            print(f"Recording audio for {duration} seconds...")
            # Record audio for the specified duration
            start_time = time.time()
            # Run a specific part of your code here
            recorded_data = [q.get() for _ in range(int(samplerate / 100 * duration))]
            end_time = time.time()
            print("Time taken:", end_time - start_time)
            print("Recording complete.")

        # Combine the recorded data into a single NumPy array
        audio_array = np.concatenate(recorded_data, axis=0)

        # Convert the NumPy array to an audio file
        wavio.write(filename, audio_array, samplerate, sampwidth=2)
    except Exception as e:
        print("Error occurred:", e)

def transcribe_audio(audio_filename):
    r = sr.Recognizer()

    with sr.AudioFile(audio_filename) as source:
        audio_data = r.record(source)

        try:
            response = r.recognize_google(audio_data, show_all=True)
            if response and response.get('alternative'):
                text = response['alternative'][0]['transcript']
                print("Transcribed text:", text)

                # Check for attacking keywords
                found_keywords = [keyword for keyword in attacking_keywords if keyword in text.lower()]
                print("Found attacking keywords:", ', '.join(found_keywords))

                # Calculate the ratio of total keywords to total words transcribed
                total_words = len(text.split())
                keyword_ratio = len(found_keywords) / total_words
                print("Keyword ratio:", keyword_ratio)

            else:
                print("Could not understand audio")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print("Error occurred:", e)

def main():
    duration = 1 * 60  # Record audio for 27 minutes
    audio_filename = "recorded_audio.wav"

    # Play the YouTube video in the background, e.g., using a web browser
    # You can replace the following line with the actual YouTube URL
    print("Please play the YouTube video in the background and then press Enter")
    input()

    # Record audio from the system
    
    record_audio(duration, audio_filename)

    # Transcribe the recorded audio and analyze it
    transcribe_audio(audio_filename)

if __name__ == "__main__":
    main()

