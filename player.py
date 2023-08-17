import os
import vlc
import time
import random

class Player:
    def __init__(self):
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()
        self.MediaList = self.Instance.media_list_new()
        self.MediaListPlayer = self.Instance.media_list_player_new()
        self.MediaListPlayer.set_media_list(self.MediaList)
        self.MediaListPlayer.set_media_player(self.player)

        self.play_list = []  # Initialize empty queue
        self.original_play_list = []  # For storing the initial playlist when shuffle is disabled
        self.index = 0
        self.is_shuffle_enabled = False
        self.is_paused = False
        self.is_playing = False
        self.current_volume = 50

    def add_song(self, song_path):
        """
        Adds a single song to the end of the queue
        """
        if song_path.endswith('.mp3'):
            self.play_list.append(song_path)
            self.original_play_list.append(song_path)
            print(f"Added {song_path} to the queue")
        else:
            print(f"Invalid file format: {song_path}")

    def add_playlist(self, folder_path):
        """
        Adds all songs in the given folder to the end of the queue
        """
        playlist = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.mp3')]
        self.play_list.extend(playlist)
        self.original_play_list.extend(playlist)
        print(f"Added {len(playlist)} songs from {folder_path} to the queue")

    def start(self):
        if not self.is_playing:
            self.is_playing = True
            self.set_volume(self.current_volume)
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

    def stop(self):
        self.player.stop()
        print("Music Stopped")
        self.is_playing = False

    def set_volume(self, volume_level):
        volume = max(0, min(100, volume_level))
        self.current_volume = int(volume)
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