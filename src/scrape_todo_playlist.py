from unittest import result
import spotipy
import sys
import os
from spotipy.oauth2 import SpotifyClientCredentials
from definitions import personal_lists, list_todo
from util import (
    gather_playlist_tracks,
    filter_tracks,
    prepare_personal_songs,
    handle_songs,
    setup_credentials
)
import logging
from args import parse_args

def main():
    args = parse_args()
    dangerrun = args.danger_run

    setup_credentials()

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager, auth_manager=client_credentials_manager)

    # according to https://stackoverflow.com/questions/51442226/spotipy-user-playlist-remove-tracks-issue
    token = spotipy.util.prompt_for_user_token(
        "cracky109",
        scope="playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative"
    )
    sp = spotipy.Spotify(auth=token)

    playlist_tracks = gather_playlist_tracks(sp, list_todo.id)
    todo_tracks = filter_tracks(playlist_tracks)

    all_songs = prepare_personal_songs(sp, personal_lists)

    handle_songs(sp, todo_tracks, all_songs, list_todo.id, dangerrun=dangerrun)
    return 0


if __name__ == "__main__":
    sys.exit(main())
