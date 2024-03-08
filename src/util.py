import base64
import datetime
import logging
import os
import random
from typing import Dict, List, Union

import requests
import yaml
from spotipy import Spotify

from definitions import PHASE_ONE_TIME_DAYS, PHASE_THREE_TIME_DAYS, PHASE_TWO_TIME_DAYS
from spotify_objects import SpotifyCredentials, SpotifyPlaylist, SpotifyTrack


def setup_credentials(cred_file=".spotipy-cred.yml") -> SpotifyCredentials:
    creds = SpotifyCredentials(
        client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
        client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
        refresh_token=os.environ.get("SPOTIPY_REFRESH_TOKEN"),
    )

    read_from_env_success = True
    for key, val in creds.__dict__.items():
        if not val:
            logging.info(f"Could not read env variable for {key}")
            read_from_env_success = False

    if read_from_env_success:
        logging.info("Using credentials from environment.")
        return creds

    logging.info("Couldn't find environment variables.")
    logging.info(f"Attempting to read credentials from file {cred_file}.")

    if os.path.exists(cred_file):
        with open(cred_file) as cred_file:
            _creds = yaml.safe_load(cred_file)
            for k, v in _creds.items():
                os.environ[k] = v

        creds = SpotifyCredentials(
            client_id=os.environ.get("SPOTIPY_CLIENT_ID"),
            client_secret=os.environ.get("SPOTIPY_CLIENT_SECRET"),
            redirect_uri=os.environ.get("SPOTIPY_REDIRECT_URI"),
            refresh_token=os.environ.get("SPOTIPY_REFRESH_TOKEN"),
        )
        return creds
    else:
        raise FileNotFoundError(f"Couldn't find {cred_file}.")


def refresh_access_token(creds: SpotifyCredentials) -> str:
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": creds.refresh_token,
    }
    auth_header = {
        "Authorization": "Basic "
        + base64.b64encode(
            (creds.client_id + ":" + creds.client_secret).encode()
        ).decode()
    }
    print("posting...")
    response = requests.post(
        "https://accounts.spotify.com/api/token", data=payload, headers=auth_header
    )
    print(response)
    return response.json().get("access_token")


def login_to_spotify():
    creds = setup_credentials()
    new_access_token = refresh_access_token(creds)

    # Set up Spotipy
    print("Setting up Spotify object")
    sp = Spotify(auth=new_access_token)
    return sp


def gather_playlist_tracks(
    spotify_client: Spotify, list_id: str, *, lim: int = 100, max_iterations: int = 100
) -> List:
    logging.debug("Gathering playlist tracks...")
    playlist_tracks = []
    for i in range(max_iterations):
        pl_tr = spotify_client.playlist_tracks(
            playlist_id=list_id, limit=lim, offset=i * lim, additional_types=("track",)
        )
        if len(pl_tr["items"]) == 0:
            break
        playlist_tracks.append(pl_tr)

    return playlist_tracks


def filter_tracks(
    playlist_tracks: List, *, spotify_client: Union[Spotify, None] = None
) -> List[SpotifyTrack]:

    logging.debug("Filtering tracks...")
    all_tracks = []

    for group in playlist_tracks:
        for item in group["items"]:
            if item["track"]:
                _track = SpotifyTrack(
                    id=item["track"]["id"],
                    name=item["track"]["name"],
                    artists=item["track"]["artists"],
                    added=item["added_at"],
                    added_by=item["added_by"],
                )

                if spotify_client:
                    _track.save_artist_genre(spotify_client)

                all_tracks.append(_track)

    return all_tracks


def delete_song_from_personal_playlist(
    spotify_client: Spotify,
    track: SpotifyTrack,
    playlist_id: str,
    *,
    dangerrun: bool = False,
):
    #     spotipy.playlist_remove_all_occurrences_of_items(playlist_id, items, snapshot_id=None)
    artists = [artist for artist in track.artist]
    artists_str = ", ".join(artists)
    logging.info(f"Song '{track.name}' by '{artists_str}' will be deleted.")
    if not dangerrun:
        logging.info("Dry-run. Skip deletion.\n\n")
    else:
        spotify_client.playlist_remove_all_occurrences_of_items(playlist_id, [track.id])
    pass


def find_song_in_personal_playlist(
    track: SpotifyTrack, personal_songs: Dict[str, List[SpotifyTrack]]
) -> int:
    """
    Search all personal playlists if the given track is present in one of them.
    """
    other_occurrences = 0
    for key, songs in personal_songs.items():
        for song in songs:
            if not song or not song.id:
                if song.name == "Slipshod":
                    continue
                song.printf()
                raise Exception(
                    f"Error Found None type song in playlist {key}, {song.__dict__=}"
                )

            if song.id == track.id:
                other_occurrences += 1

    return other_occurrences


def handle_songs(
    spotify_client: Spotify,
    todo_tracks: List[SpotifyTrack],
    personal_songs: Dict[str, List[SpotifyTrack]],
    todo_list_id: str,
    dangerrun: bool = False,
):
    """
    If a song from the TODO list is already present in any
    of the personal playlists, remove it from the TODO list.
    """
    now = datetime.datetime.now()
    for track in todo_tracks:
        delta = now - track.added
        if delta.days >= PHASE_ONE_TIME_DAYS:
            # check if song is present in personal playlist
            # if so: delete from todo
            # and continue loop
            n_occurrences = find_song_in_personal_playlist(track, personal_songs)
            if n_occurrences:
                logging.info(
                    f"Song {track.name} is present in {n_occurrences} other playlists."
                )
                delete_song_from_personal_playlist(
                    spotify_client, track, todo_list_id, dangerrun=dangerrun
                )
                continue

        if delta.days > PHASE_TWO_TIME_DAYS:
            # Send notification to review songs
            pass

        if delta.days > PHASE_THREE_TIME_DAYS:
            # delete song from todo playlist
            # and continue loop w/ next track
            logging.info(f"Found old song: {track.name} by {track.artist}.")
            delete_song_from_personal_playlist(
                spotify_client, track, todo_list_id, dangerrun=False
            )
            continue


def prepare_personal_songs(
    spotify_client: Spotify, playlists: List[SpotifyPlaylist]
) -> Dict:
    all_songs = {}

    for playlist in playlists:
        playlist_tracks = gather_playlist_tracks(spotify_client, playlist.id)
        all_songs[playlist.name] = filter_tracks(playlist_tracks)
    return all_songs


def insert_random_insult():
    insults = [
        "absolute toaster",
        "knobhead",
        "utter idiot",
        "witless dishcloth",
        "muppet",
        "infantile pillock",
        "insufferable oaf",
        "blithering idiot",
    ]
    return random.choice(insults)
