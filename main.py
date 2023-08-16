import os
from dotenv import load_dotenv
import re
import json
from urllib import request, parse
from pytube import YouTube
from pydub import AudioSegment
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem

from player import Player

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

musicplayer = None

menu = ConsoleMenu("music buddy", "let me guess tiny, a dime bag?")

playermenu = ConsoleMenu("play music")
playermenu_item = SubmenuItem("play music", playermenu, menu=menu)

def musicplayer_start():
   global musicplayer
   musicplayer.start()

musicplayer_start_function = FunctionItem("start", musicplayer_start)
playermenu.append_item(musicplayer_start_function)

def musicplayer_pause():
   global musicplayer
   if musicplayer.is_paused == True:
       musicplayer.resume()
   else:
       musicplayer.pause()

musicplayer_pause_function = FunctionItem("pause/resume", musicplayer_pause)
playermenu.append_item(musicplayer_pause_function)

def musicplayer_skip():
   global musicplayer
   musicplayer.skip()

musicplayer_skip_function = FunctionItem("skip", musicplayer_skip)
playermenu.append_item(musicplayer_skip_function)

def musicplayer_volume(args):
   volume_level = input(args)
   global musicplayer
   musicplayer.set_volume(float(volume_level))

musicplayer_volume_function = FunctionItem("volume", musicplayer_volume, ["volume (0.0-1.0): "])
playermenu.append_item(musicplayer_volume_function)

def musicplayer_shuffle():
   global musicplayer
   musicplayer.toggle_shuffle()

musicplayer_shuffle_function = FunctionItem("shuffle", musicplayer_shuffle)
playermenu.append_item(musicplayer_shuffle_function)

def musicplayer_fade(args):
   fade_time_input = input(args)
   fade_time = max(0, min(10, fade_time_input))
   global musicplayer
   musicplayer.fade_duration = float(fade_time)

musicplayer_fade_function = FunctionItem("fade", musicplayer_volume, ["fade in seconds (0.0-10.0): "])
playermenu.append_item(musicplayer_fade_function)

def musicplayer_stop():
   global musicplayer
   musicplayer.stop()

musicplayer_stop_function = FunctionItem("stop", musicplayer_stop)
playermenu.append_item(musicplayer_stop_function)

viewplaylistsmenu = ConsoleMenu("view playlists")
viewplaylists_item = SubmenuItem("view playlists", viewplaylistsmenu, menu=menu)

addplaylistsmenu = ConsoleMenu("add playlists")
addplaylists_item = SubmenuItem("add playlists", addplaylistsmenu, menu=menu)

def addyoutubeplaylist(args):
    youtube_url = input(args)
    download_playlist(youtube_url)

addplaylists_function = FunctionItem("add a youtube playlist", addyoutubeplaylist, ["youtube playlist url: "])
addplaylistsmenu.append_item(addplaylists_function)

menu.append_item(playermenu_item)
menu.append_item(viewplaylists_item)
menu.append_item(addplaylists_item)

def selectplaylist(playlist_path):
    print(playlist_path)
    global musicplayer
    musicplayer = Player(playlist_path)
    print(musicplayer.play_list)

if __name__ == "__main__":
    valid_playlists = get_valid_playlists()
    for i, (playlist_name, playlist_path) in enumerate(valid_playlists, 1):
        playlistmenu = ConsoleMenu(playlist_name)
        playlistsubmenu = SubmenuItem(playlist_name, playlistmenu, menu=menu)
        viewplaylistsmenu.append_item(playlistsubmenu)

        selectplaylist_function = FunctionItem("select playlist", selectplaylist, [playlist_path])
        playlistmenu.append_item(selectplaylist_function)
        selectplaylist(playlist_path)

    menu.show()