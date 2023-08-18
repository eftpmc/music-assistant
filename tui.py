from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.binding import Binding
from textual.message import Message
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Footer, Header, Label, ListView, ListItem

from player import Player
from utils import get_valid_playlists, get_songs_in_playlist
from playlist_manager import download_playlist

musicplayer = Player()
playlists = get_valid_playlists()

class PlaylistSongHorizontal(Static):
    playlistsList = []
    songsList = []

    def on_list_view_selected( self, event: ListView.Selected ) -> None:
        selectedViewID = event.control.id
        if selectedViewID == "playlists":
            playlistListView = self.query_one("#songs", ListView)
            playlistListView.clear()
            selectedPlaylist = event.item.get_child_by_type(Label).renderable
            playlist_songs = get_songs_in_playlist("playlists/" + str(selectedPlaylist))
            for name, path in playlist_songs:
                playlistListView.append(ListItem(Label(name)))
            self.update()
        else:
            selectedSong = event.item.get_child_by_type(Label).renderable
        
        

    def on_mount(self) -> None:
        playlistsListView = self.query_one("#playlists", ListView)
        songsListView = self.query_one("#songs", ListView)

        for playlistName, playlistPath in playlists:
            playlistsListView.append(ListItem(Label(playlistName)))
            

    def compose(self) -> ComposeResult:
        yield Horizontal(
            ListView(id="playlists", classes="box"),
            ListView(id="songs", classes="box"),
        )

class Status(Static):
    current_status = reactive("No song playing")

    def on_mount(self) -> None:
        self.set_interval(1, self.update_status)

    def update_status(self) -> None:
        self.current_status = musicplayer.current_song + " " + musicplayer.get_current_time()

    def watch_current_status(self) -> None:
        """Called when the current_song attribute changes."""
        self.update(self.current_status)

class MainApp(App):
    CSS_PATH = "tui.css"
    TITLE = "gababa"
    SUB_TITLE = "yrail my assnt"

    BINDINGS = [
        Binding(key="p", action="toggle_play_pause", description="pause/resume"),
        Binding(key="+", action="increase_volume", description="increase volume"),
        Binding(key="-", action="decrease_volume", description="decrease volume"),
        Binding(key="s", action="skip", description="skip"),
        Binding(key="r", action="shuffle", description="shuffle"),
    ]

    current_song = reactive("No song playing")
    
    def action_toggle_play_pause(self) -> None:
        """Toggle between play and pause state."""
        if musicplayer.is_paused:
            musicplayer.resume()
        else:
            musicplayer.pause()

    def action_increase_volume(self) -> None:
        """Increase the volume."""
        new_volume = musicplayer.current_volume + 10
        musicplayer.set_volume(new_volume)

    def action_decrease_volume(self) -> None:
        """Decrease the volume."""
        new_volume = musicplayer.current_volume - 10
        musicplayer.set_volume(new_volume)
    
    def action_skip(self) -> None:
        """Skip to the next item."""
        musicplayer.skip()
    
    def action_shuffle(self) -> None:
        """Shuffle the playback."""
        musicplayer.toggle_shuffle()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield PlaylistSongHorizontal(classes="container")
        yield Status(classes="status")
        yield Footer()
        
if __name__ == "__main__":
    app = MainApp()
    musicplayer.add_playlist("playlists/sr")
    musicplayer.start()
    app.run()