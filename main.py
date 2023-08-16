import os
from dotenv import load_dotenv
import re
import json
from urllib import request, parse
from pytube import YouTube
import vlc
import time
import random
from consolemenu import ConsoleMenu

from consolemenu.items import FunctionItem, SubmenuItem, CommandItem

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

def get_valid_playlists():
    main_folder = 'playlists'
    valid_playlists = []
    
    if os.path.exists(main_folder):
        playlists = os.listdir(main_folder)
        
        for playlist in playlists:
            if 'invalid' not in playlist and playlist.strip():
                full_path = os.path.join(main_folder, playlist)
                valid_playlists.append((playlist, full_path))
    else:
        print("\nNo playlists directory found.")
        
    return valid_playlists

def music_player(playlist_folder):
    player = Player(playlist_folder)
    while True:
        user_input = prompt("\nEnter command (start, resume, shuffle, pause, skip, volume, fade, quit): ", 
                            completer=commands_completer,
                            validator=CommandValidator(),
                            validate_while_typing=True)

        if user_input == "start":
            player.start()
        elif user_input == "resume":
            player.resume()
        elif user_input == "shuffle":
            player.toggle_shuffle()
        elif user_input == "pause":
            player.pause()
        elif user_input == "skip":
            player.skip()
        elif user_input == "volume":
            volume_level = prompt("Enter volume (0.0-1.0): ", validator=VolumeValidator())
            player.set_volume(float(volume_level))
            print(f"Volume set to {float(volume_level)*100}%")
        elif user_input == "fade":
            fade_time = prompt("Enter fade time (0.0-10.0): ", validator=FadeValidator())
            player.fade_duration = float(fade_time)
            print(f"Fade time set to {fade_time} seconds.")
        elif user_input == "quit":
            player.stop()
            break
        else:
            print("Invalid command!")

def download_playlist(youtube_playlist_url):
    # Extracting the playlist ID
    playlist_id = extract_playlist_id(youtube_playlist_url)

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
        self.is_paused = False
        self.is_playing = False
        self.current_volume = 100
        self.fade_duration = 3
        print(self.play_list)

    def start(self):
        if not self.is_playing:
            self.is_playing = True
            self.play()
            print("Music Started")
        else:
            print("Music already playing")

    def play(self):
        if not self.play_list:
            print("No songs to play!")
            return

        self.player.set_media(vlc.Media(self.play_list[self.index]))
        self.player.play()
        self.fade_in()
        
    def resume(self):
        if self.is_paused:
            self.player.play()
            print("Resumed")
            self.is_paused = False
        else:
            print("Nothing to resume")

    def pause(self):
        self.player.pause()
        print("Paused")
        self.is_paused = True

    def skip(self):
        self.index += 1
        if self.index >= len(self.play_list):
            self.index = 0
        self.player.set_media(vlc.Media(self.play_list[self.index]))
        self.player.play()
        print("Skipped to the next track")

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

menu = ConsoleMenu("music buddy", "let me guess tiny, a dime bag?")

viewplaylistsmenu = ConsoleMenu("view playlists")
viewplaylists_item = SubmenuItem("view playlists", viewplaylistsmenu, menu=menu)

addplaylistsmenu = ConsoleMenu("add playlists")
addplaylists_item = SubmenuItem("add playlists", addplaylistsmenu, menu=menu)

def addyoutubeplaylist(args):
    youtube_url = input(args)
    download_playlist(youtube_url)

addplaylists_function = FunctionItem("add a youtube playlist", addyoutubeplaylist, ["youtube playlist url: "])

menu.append_item(viewplaylists_item)
menu.append_item(addplaylists_item)

addplaylistsmenu.append_item(addplaylists_function)

if __name__ == "__main__":
    valid_playlists = get_valid_playlists()
    for i, (playlist_name, playlist_path) in enumerate(valid_playlists, 1):
        print(f"{i}. {playlist_name} ({playlist_path})")
        playlistmenu = ConsoleMenu(playlist_name)
        playlistsubmenu = SubmenuItem(playlist_name, playlistmenu, menu=menu)
        viewplaylistsmenu.append_item(playlistsubmenu)
    menu.show()