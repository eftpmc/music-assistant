import os
from dotenv import load_dotenv
import re
import json
from urllib import request, parse
from pytube import YouTube
import vlc
import time
import random

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
        print(f"downloaded: {full_path}")
    else:
        print(f"file {full_path} already exists. skipping download.")

class Player:
    def __init__(self, folder_path):
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.MediaList = self.Instance.media_list_new()
        self.MediaListPlayer = self.Instance.media_list_player_new()
        self.MediaListPlayer.set_media_list(self.MediaList)
        self.MediaListPlayer.set_media_player(self.player)
        
        self.folder_path = folder_path
        self.original_play_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3')]
        self.play_list = self.original_play_list.copy()
        self.index = 0
        self.is_shuffle_enabled = False
        self.current_volume = 100
        self.fade_duration = 0
        self.player = vlc.MediaPlayer()
        print(self.play_list)
        
    def play(self):
        if not self.play_list:
            print("No songs to play!")
            return
        self.player.set_media(vlc.Media(self.play_list[self.index]))
        self.player.play()
        self.fade_in()

    def fade_in(self):
        fade_steps = int(self.fade_duration * 10)
        for step in range(fade_steps):
            time.sleep(self.fade_duration / fade_steps)
            volume = int((step + 1) / fade_steps * self.current_volume)
            self.player.audio_set_volume(volume)

    def fade_out(self):
        fade_steps = int(self.fade_duration * 10)
        for step in range(fade_steps):
            time.sleep(self.fade_duration / fade_steps)
            volume = int((fade_steps - step - 1) / fade_steps * self.current_volume)
            self.player.audio_set_volume(volume)
        self.stop()

    def set_volume(self, volume_level):
        self.current_volume = int(volume_level * 100)
        self.player.audio_set_volume(self.current_volume)
        
    def stop(self):
        self.player.stop()
        print("Stopped")

    def skip(self):
        self.fade_out()
        self.index += 1
        if self.index >= len(self.play_list):
            self.index = 0
        self.play()

    def enable_shuffle(self):
        random.shuffle(self.play_list)
        self.is_shuffle_enabled = True
        print("Shuffle enabled")

    def disable_shuffle(self):
        self.play_list = self.original_play_list.copy()
        self.is_shuffle_enabled = False
        print("Shuffle disabled")

    def toggle_shuffle(self):
        if self.is_shuffle_enabled:
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
        command = input("\nenter command (play, shuffle, stop, skip, volume, fade, quit): ").strip().lower()
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
            if 0.0 <= volume_level <= 1.0:
                player.set_volume(volume_level)
                print(f"Volume set to {volume_level*100}%")
            else:
                print("Invalid volume level! Enter a value between 0.0 and 1.0.")
        elif command == "fade":
            fade_time = float(input("enter fade time (0.0-10.0): "))
            if 0.0 <= fade_time <= 10.0:
                player.fade_duration = fade_time
                print(f"Fade time set to {fade_time} seconds.")
            else:
                print("Invalid fade time! Enter a value between 0.0 and 10.0 seconds.")
        elif command == "quit":
            player.stop()
            break
        else:
            print("invalid command!")
