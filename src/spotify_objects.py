import datetime
from typing import Dict, List, Union
from spotipy import Spotify


class SpotifyObject:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def printf(self):
        for key, val in self.__dict__.items():
            print(f"{key}: {val}")


class SpotifyPlaylist(SpotifyObject):
    def __init__(self, id: str, name: str):
        super().__init__(id, name)


class SpotifyTrack(SpotifyObject):
    def __init__(
        self,
        id: str,
        name: str,
        artists: List,
        added: datetime.datetime,
        *,
        added_by: Union[Dict, None],
    ):
        super().__init__(id, name)
        self.added = datetime.datetime.strptime(added, "%Y-%m-%dT%H:%M:%SZ")
        self.artist_names = [artist["name"] for artist in artists]
        self.artist = self.artist_names
        self.artist_ids = [artist["id"] for artist in artists]

        if added_by:
            self.added_by = added_by["id"]
            if "user" not in added_by["type"]:
                print("WARNING! Found song added by non user type!")
                print(f"Song: {name} by artist(s) {self.artist_names}")
                print(f"Was added by {self.added_by} of user-type {added_by['type']}")
                print()
            self.added_by_type = added_by["type"]

    def save_artist_genre(self, spotify_client: Spotify):
        all_genres = []
        for id in self.artist_ids:
            if id:
                artist = spotify_client.artist(id)
                genres = artist["genres"]
                all_genres.extend(genres)

        self.genres = all_genres

    def printf(self):
        super().printf()
