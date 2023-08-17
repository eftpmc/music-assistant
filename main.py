import os
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem

from player import Player
from utils import get_valid_playlists
from playlist_manager import download_playlist


musicplayer = Player()

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

def add_playlist(playlist_path):
    global musicplayer
    musicplayer.add_playlist(playlist_path)

if __name__ == "__main__":
    valid_playlists = get_valid_playlists()
    for i, (playlist_name, playlist_path) in enumerate(valid_playlists, 1):
        playlistmenu = ConsoleMenu(playlist_name)
        playlistsubmenu = SubmenuItem(playlist_name, playlistmenu, menu=menu)
        viewplaylistsmenu.append_item(playlistsubmenu)

        addplaylist_function = FunctionItem("add playlist to queue", add_playlist, [playlist_path])
        playlistmenu.append_item(addplaylist_function)

    menu.show()
    #download_playlist("https://music.youtube.com/playlist?list=PLUdUiRdpouHqNxa2792wQUZnhafK6xPqE")