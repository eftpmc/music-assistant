import os
import re
import json
from dotenv import load_dotenv
from urllib import request, parse
from pytube import YouTube
from pydub import AudioSegment

from pytube.exceptions import PytubeError
from pydub.exceptions import CouldntDecodeError

# Load the environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment variables
api_key = os.getenv('YOUTUBE_API_KEY')

def get_valid_playlists():
    global api_key
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

def get_songs_in_playlist(playlist_folder):
    """
    Get the songs in a given playlist folder.
    
    :param playlist_folder: The path to the folder containing the playlist.
    :return: A list of tuples where each tuple contains (song_name, song_full_path).
    """
    songs_in_playlist = []
    
    if os.path.exists(playlist_folder):
        files_in_folder = os.listdir(playlist_folder)
        
        for file in files_in_folder:
            if file.endswith('.mp3') and file.strip():
                full_path = os.path.join(playlist_folder, file)
                songs_in_playlist.append((file, full_path))
                
        if not songs_in_playlist:
            print(f"No songs found in the playlist folder: {playlist_folder}")
    else:
        print(f"\nPlaylist folder '{playlist_folder}' not found.")
        
    return songs_in_playlist

def extract_playlist_id(url):
    playlist_id_match = re.search('list=([a-zA-Z0-9_-]+)', url)
    
    if playlist_id_match:
        playlist_id = playlist_id_match.group(1)
        playlist_name = get_playlist_name(playlist_id)
        return playlist_id, playlist_name
    else:
        return None, "invalid url or no playlist id found."
    
def get_playlist_name(playlist_id):
    global api_key
    base_url = 'https://www.googleapis.com/youtube/v3/playlists'
    params = {
        'part': 'snippet',
        'id': playlist_id,
        'key': api_key
    }
    query_string = parse.urlencode(params)
    response = request.urlopen(f'{base_url}?{query_string}')
    result = json.loads(response.read())
    
    # Extract playlist name from the response
    if 'items' in result and result['items']:
        return result['items'][0]['snippet']['title']
    
    return "Unknown Playlist Name"
    
def get_video_urls(playlist_id):
    global api_key
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
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if audio_stream is None:
            print(f"No audio stream found for {video_url}. Skipping download.")
            return

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

    except PytubeError as e:
        print(f"An error occurred while downloading the video {video_url}. Error: {e}")

    except CouldntDecodeError as e:
        print(f"An error occurred while decoding the audio for {video_url}. Error: {e}")

    except Exception as e:
        print(f"An unexpected error occurred while processing {video_url}. Error: {e}")