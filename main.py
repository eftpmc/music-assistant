import os
from dotenv import load_dotenv
import re
import json
import pygame
import random
from urllib import request, parse
from pytube import YouTube
from pydub import AudioSegment
from pydub.playback import play

# Load the environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment variables
api_key = os.getenv('YOUTUBE_API_KEY')

def extract_playlist_id(url):
    playlist_id_match = re.search('list=([a-zA-Z0-9_-]+)', url)
    if playlist_id_match:
        return playlist_id_match.group(1)
    else:
        return "invalid url or no playlist id found."

def get_video_urls(api_key, playlist_id):
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    video_urls = []
    
    params = {
        'part': 'snippet',
        'maxResults': '50',
        'playlistId': playlist_id,
        'key': api_key
    }
    
    while True:
        query_string = parse.urlencode(params)
        response = request.urlopen(f'{base_url}?{query_string}')
        result = json.loads(response.read())
        
        for item in result['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_urls.append(video_url)
            
        if 'nextPageToken' in result:
            params['pageToken'] = result['nextPageToken']
        else:
            break
    
    return video_urls

def download_audio(video_url, folder_path):
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    title = yt.title.replace("/", " ").replace("\\", " ")
    mp3_filename = f"{title}.mp3"
    full_path = os.path.join(folder_path, mp3_filename)
    
    if not os.path.exists(full_path):
        audio_file = audio_stream.download(output_path=folder_path)
        base, ext = os.path.splitext(audio_file)
        sound = AudioSegment.from_file(audio_file, format=ext.replace('.', ''))
        sound.export(full_path, format='mp3')
        
        os.remove(audio_file)
        print(f"downloaded: {full_path}")
    else:
        print(f"file {full_path} already exists. skipping download.")

class Player:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.play_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3')]
        self.index = 0
        self.shuffle = False
        self.volume = 1  # Default volume (0.0 to 1.0)
        print(self.play_list)

    def play(self):
        if not self.play_list:
            print("No songs to play!")
            return

        song = AudioSegment.from_file(self.play_list[self.index])
        
        # Apply fade in and fade out
        song = song.fade_in(2000).fade_out(2000)  # 2 seconds fade in/out
        
        # Set volume
        song = song - (1 - self.volume) * 50  # 50 here is an arbitrary number for volume control
        
        # Play the song
        play(song)
        
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))  # Ensure volume is between 0.0 and 1.0
        print(f"Volume set to {self.volume * 100}%")

    def stop(self):
        # Simpleaudio doesn't provide a stop function, so we move to the next track to effectively stop the current one
        self.skip()

    def skip(self):
        self.index += 1
        if self.index >= len(self.play_list):
            self.index = 0
        self.play()

    def enable_shuffle(self):
        self.shuffle = True
        random.shuffle(self.play_list)

    def disable_shuffle(self):
        self.shuffle = False
        self.play_list = sorted(self.play_list)

    def toggle_shuffle(self):
        if self.shuffle:
            self.disable_shuffle()
        else:
            self.enable_shuffle()

if __name__ == "__main__":
    # Taking YouTube playlist URL as input from the user
    youtube_playlist_url = input("enter the youtube playlist url: ")

    # Extracting the playlist ID
    playlist_id = extract_playlist_id(youtube_playlist_url)
    print("playlist id:", playlist_id)

    # Create 'Playlists' directory if it doesn't exist
    main_folder = 'playlists'
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    # Create subdirectory for this playlist under 'Playlists'
    playlist_folder = os.path.join(main_folder, playlist_id)
    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)

    # Fetch video URLs
    video_urls = get_video_urls(api_key, playlist_id)
    print("\nvideo urls:")
    for url in video_urls:
        print(url)

    # Download the audios of the videos as MP3 files
    for url in video_urls:
        download_audio(url, playlist_folder)
    
    player = Player(playlist_folder)
    while True:
        command = input("\nenter command (play, shuffle, stop, skip, volume, quit): ").strip().lower()
        if command == "play":
            player.play()
        elif command == "shuffle":
            player.toggle_shuffle()
        elif command == "stop":
            player.stop()
        elif command == "skip":
            player.skip()
        elif command == "volume":
            volume_level = float(input("enter volume (0.0-1.0): "))
            player.set_volume(volume_level)
        elif command == "quit":
            player.stop()
            break
        else:
            print("invalid command!")
