PHASE_ONE_TIME_DAYS = 14
PHASE_TWO_TIME_DAYS = 30
PHASE_THREE_TIME_DAYS = 90

TOLERATE_USERS = ["cracky109", "mamelmamel5", "daisys"]
TOLERATE_GENRES = ["metal", "prog", "alternative"]
REMOVE_GENRES = [
    "german",
    "schlager",
    "pop",
    "elektro",
    "kabarett",
    "party",
    "volksmusik",
    "house",
    "dance",
    "edm",
    "synth",
    "discofox",
]

WHITELIST_SONGS = ["Slipshod"]

from spotify_objects import SpotifyPlaylist

list_todo = SpotifyPlaylist("5f1XnFPwdmCERgXQCanZeq", "#TODO:")
list_42 = SpotifyPlaylist("59Wdcmc6obHTvYXTtEa5gK", "42")
list_43 = SpotifyPlaylist("4TBjcQxCQt44DbHyA9Ah48", "43")
list_prog = SpotifyPlaylist(
    "3tno14fGclax5WaFKzbMmY", "if it sounds proggy, that's because it is"
)
list_soul = SpotifyPlaylist("5ZQwxZ3pIPoVkyYIQDJwiZ", "Soulstice")
list_u2 = SpotifyPlaylist("5QJ2cW7xHcHNJEjuwyfZYw", "u2")
list_swe = SpotifyPlaylist("2Ita6z3IthLSW54M33V1tu", "sverige")

personal_lists = [list_42, list_43, list_prog, list_soul, list_u2, list_swe]
