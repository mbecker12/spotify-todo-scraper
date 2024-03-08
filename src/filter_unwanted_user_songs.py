import argparse
import os
import sys

import spotipy
import yaml
from spotipy.oauth2 import SpotifyClientCredentials

from definitions import REMOVE_GENRES, TOLERATE_GENRES, TOLERATE_USERS, personal_lists
from util import (
    delete_song_from_personal_playlist,
    filter_tracks,
    gather_playlist_tracks,
    insert_random_insult,
    setup_credentials,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dry-run",
    help="Don't delete track from playlist. Only print track information.",
    action="store_true",
)
parser.add_argument(
    "--danger-run",
    help="Delete track from playlist.",
    action="store_true",
)


def main():
    args = parser.parse_args()
    dangerrun = args.danger_run
    if args.dry_run:
        dangerrun = False

    if not os.environ.get("SPOTIPY_CLIENT_ID"):
        setup_credentials()

    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    token = spotipy.util.prompt_for_user_token(
        "cracky109",
        scope="playlist-modify-public playlist-modify-private playlist-read-private playlist-read-collaborative",
    )
    sp = spotipy.Spotify(auth=token)

    for playlist in personal_lists:
        if "prog" not in playlist.name:
            continue
        playlist_tracks = gather_playlist_tracks(sp, playlist.id)

        playlist_tracks = filter_tracks(playlist_tracks, spotify_client=sp)
        for track in playlist_tracks:
            track_matched_bad_genre = False
            track_matched_allowed_genre = False

            if track.added_by not in TOLERATE_USERS:
                print(f"Warning! Song {track.name} by artists {track.artist_names}")
                print(
                    f"Was added by untolerated user {track.added_by} and comes from genre {track.genres}."
                )
                print()

                delete_song_from_personal_playlist(
                    sp, track, playlist.id, dangerrun=dangerrun
                )

            for genre in track.genres:
                for allowed_genre in TOLERATE_GENRES:
                    if (allowed_genre in genre) or (genre in allowed_genre):
                        track_matched_allowed_genre = True
                        break
                if track_matched_allowed_genre:
                    break

                for forbidden_genre in REMOVE_GENRES:
                    if (forbidden_genre in genre) or (genre in forbidden_genre):
                        track_matched_bad_genre = True
                        break

            if track_matched_bad_genre:
                if track_matched_allowed_genre:
                    continue
                genres_str = ", ".join([genre for genre in track.genres])
                print(f"Detected sacrilegious song from genre {genres_str},")
                print(f"added by the {insert_random_insult()} {track.added_by}:")
                delete_song_from_personal_playlist(
                    sp, track, playlist.id, dangerrun=dangerrun
                )

    return 0


if __name__ == "__main__":
    sys.exit(main())
