import os
from dotenv import load_dotenv
import re
import json
from urllib import request, parse
from pytube import YouTube
import vlc
import time
import random
import tkinter as tk

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

def view_playlists():
    main_folder = 'playlists'
    if os.path.exists(main_folder):
        playlists = os.listdir(main_folder)
        if playlists:
            print("\nExisting Playlists:")
            for i, playlist in enumerate(playlists, 1):
                print(f"{i}. {playlist}")
        else:
            print("\nNo playlists found.")
    else:
        print("\nNo playlists directory found.")

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

def on_option1_selected():
    print("Option 1 selected")

def on_option2_selected():
    print("Option 2 selected")

def on_exit_selected():
    print("Exiting...")
    root.quit()

def play_music():
    print("Music Playing")

def pause_music():
    print("Music Paused")

def shuffle_music():
    print("Music Shuffled")

def skip_music():
    print("Music Skipped")

# Create the main window
root = tk.Tk()
root.title("Music Buddy")

# Set the size of the window
root.geometry("500x200")

# Disable resizing the window
root.resizable(False, False)

# Load the GIF image file
bg_image = tk.PhotoImage(file="background.gif")

# Use a Label to display the image, the label acts as a background
bg_label = tk.Label(root, image=bg_image)
bg_label.place(relwidth=1, relheight=1)  # Make the label cover the whole window

# Music Section
music_frame = tk.Frame(root, bg="lightgrey", bd=2)
music_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.5)

# Now Playing Section
now_playing_frame = tk.Frame(root, bg="lightgrey", bd=2)
now_playing_frame.place(relx=0.05, rely=0.65, relwidth=0.9, relheight=0.3)

now_playing_label = tk.Label(now_playing_frame, text="Now Playing: Song Title", font=("Arial", 16))
now_playing_label.pack()

play_button = tk.Button(now_playing_frame, text="Play", command=play_music)
play_button.pack(side=tk.LEFT, padx=10)

pause_button = tk.Button(now_playing_frame, text="Pause", command=pause_music)
pause_button.pack(side=tk.LEFT, padx=10)

shuffle_button = tk.Button(now_playing_frame, text="Shuffle", command=shuffle_music)
shuffle_button.pack(side=tk.LEFT, padx=10)

skip_button = tk.Button(now_playing_frame, text="Skip", command=skip_music)
skip_button.pack(side=tk.LEFT, padx=10)

# Create a menubar
menubar = tk.Menu(root)

# Create a menu and add it to the menubar
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)

# Add options to the menu
filemenu.add_command(label="Option 1", command=on_option1_selected)
filemenu.add_command(label="Option 2", command=on_option2_selected)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=on_exit_selected)

# Attach the menubar to the main window
root.config(menu=menubar)

if __name__ == "__main__":
    # Run the main loop
    root.mainloop()