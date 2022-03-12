from os import getenv

SEARCH_ARTIST_URL = getenv("SEARCH_ARTIST_URL")
ARTIST_URL = getenv("ARTIST_URL")
SONG_URL = getenv("SONG_URL")
LYRICS_URL = getenv("LYRICS_URL")
OK_STATUS = 200
BAD_REQUEST_STATUS = 400
NOT_FOUND_STATUS = 404
INTERNAL_SERVER_ERROR_STATUS = 500
SERVICE_UNAVAILABLE_STATUS = 503
INVALID_PARAMETERS = "Invalid parameters."
ARTIST_NOT_FOUND = "Artist not found."
SONG_NOT_FOUND = "Song not found."
INTERNAL_SERVER_ERROR = "An internal server error ocurred."
SERVICE_UNAVAILABLE = (
    "This service is not available, please try again in a few minutes."
)
