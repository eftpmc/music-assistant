import os
import vlc
import time
import random

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
        volume = max(0, min(1, volume_level))
        self.current_volume = int(volume * 100)
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