from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Footer, Header, Label, ListView, ListItem

from player import Player
from utils import get_valid_playlists
from playlist_manager import download_playlist

class VerticalLayoutExample(App):
    CSS_PATH = "tui.css"
    TITLE = "gababa"
    SUB_TITLE = "yrail my assnt"

    musicplayer = Player()
    playlists = get_valid_playlists()

    BINDINGS = [
        Binding(key="p", action="toggle_play_pause", description="pause/resume"),
        Binding(key="+", action="increase_volume", description="increase volume"),
        Binding(key="-", action="decrease_volume", description="decrease volume"),
        Binding(key="s", action="skip", description="skip"),
        Binding(key="r", action="shuffle", description="shuffle"),
    ]
    
    def action_toggle_play_pause(self) -> None:
        """Toggle between play and pause state."""
        if self.musicplayer.is_paused:
            self.musicplayer.resume()
        else:
            self.musicplayer.pause()

    def action_increase_volume(self) -> None:
        """Increase the volume."""
        new_volume = self.musicplayer.current_volume + 10
        self.musicplayer.set_volume(new_volume)

    def action_decrease_volume(self) -> None:
        """Decrease the volume."""
        new_volume = self.musicplayer.current_volume - 10
        self.musicplayer.set_volume(new_volume)
    
    def action_skip(self) -> None:
        """Skip to the next item."""
        self.musicplayer.skip()
    
    def action_shuffle(self) -> None:
        """Shuffle the playback."""
        self.musicplayer.toggle_shuffle()
    
    def compose(self) -> ComposeResult:
        yield Header()
        """
        yield Horizontal(
            Static("One", classes="box"),
            Static("Two", classes="box"),
            Static("Three", classes="box"),
        )
        """
        yield Footer()
        
if __name__ == "__main__":
    app = VerticalLayoutExample()
    app.musicplayer.add_playlist("playlists/sr")
    app.musicplayer.start()
    app.run()
