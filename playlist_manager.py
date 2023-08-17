import os
from utils import get_video_urls, download_audio, extract_playlist_id

def download_playlist(youtube_playlist_url):
    # Extracting the playlist ID
    playlist_id, playlist_name = extract_playlist_id(youtube_playlist_url)

    # Create 'Playlists' directory if it doesn't exist
    main_folder = 'playlists'
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
    
    # Create subdirectory for this playlist under 'Playlists'
    playlist_folder = os.path.join(main_folder, playlist_name)
    if not os.path.exists(playlist_folder):
        os.makedirs(playlist_folder)

    # Fetch video URLs
    video_urls = get_video_urls(playlist_id)
    print("\nvideo urls:")
    for url in video_urls:
        print(url)

    # Download the audios of the videos as MP3 files
    for url in video_urls:
        download_audio(url, playlist_folder)