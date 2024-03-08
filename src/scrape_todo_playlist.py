import sys

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from args import parse_args
from definitions import list_todo, personal_lists
from util import (
    filter_tracks,
    gather_playlist_tracks,
    handle_songs,
    login_to_spotify,
    prepare_personal_songs,
)


def main():
    args = parse_args()
    dangerrun = args.danger_run

    sp = login_to_spotify()

    # according to https://stackoverflow.com/questions/51442226/spotipy-user-playlist-remove-tracks-issue
    # token = spotipy.util.prompt_for_user_token(
    #     "cracky109",
    #     scope="playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative",
    # )
    # sp = spotipy.Spotify(auth=token)

    playlist_tracks = gather_playlist_tracks(sp, list_todo.id)
    todo_tracks = filter_tracks(playlist_tracks)

    all_songs = prepare_personal_songs(sp, personal_lists)

    handle_songs(sp, todo_tracks, all_songs, list_todo.id, dangerrun=dangerrun)
    return 0


if __name__ == "__main__":
    sys.exit(main())
