import json
import re

import requests
from bs4 import BeautifulSoup
from constants import *
from flask import Blueprint, jsonify, request

api = Blueprint("api", __name__)

"""
Ruta para obtener el ID del artista/banda.

Parámetros:
    <string:name> = Nombre del artista/banda.
    <int:page> (opt) = Número de página de resultados.
"""


@api.route("/artist")
def get_artist_list():
    try:
        # Verificar los parámetros de la petición y añadirlos a variables.
        try:
            args = json.loads(json.dumps(request.args))
            if args.get("name") == "":
                raise Exception

            name = args.get("name").title()
            page = (
                1
                if "page" not in args or int(args.get("page")) <= 0
                else int(args.get("page"))
            )
        except:
            return (
                jsonify({"msg": INVALID_PARAMETERS, "status": BAD_REQUEST_STATUS}),
                BAD_REQUEST_STATUS,
            )

        # Realizar la petición y verificar si fue exitosa.
        r = requests.get(f"{SEARCH_ARTIST_URL}?q={name}&page={page}")
        if r.status_code != OK_STATUS:
            return (
                jsonify(
                    {"msg": SERVICE_UNAVAILABLE, "status": SERVICE_UNAVAILABLE_STATUS}
                ),
                SERVICE_UNAVAILABLE_STATUS,
            )

        # Obtener información y verificar que tenga el contenido requerido.
        data = r.json().get("response")
        hits = data.get("sections")[0].get("hits")
        if len(hits) <= 0:
            return (
                jsonify({"msg": ARTIST_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )

        # Filtrar la información de cada artista y añadirla a un arreglo de objetos.
        artists = []
        for i in hits:
            artists.append(
                {
                    "id": i.get("result").get("id"),
                    "image": i.get("result").get("image_url")
                    if "default" not in i.get("result").get("image_url")
                    else None,
                    "name": i.get("result").get("name"),
                    "verified": i.get("result").get("is_verified"),
                }
            )

        return (
            jsonify(
                {
                    "data": artists,
                    "next_page": data.get("next_page"),
                    "status": OK_STATUS,
                }
            ),
            OK_STATUS,
        )
    except:
        return (
            jsonify(
                {"msg": INTERNAL_SERVER_ERROR, "status": INTERNAL_SERVER_ERROR_STATUS}
            ),
            INTERNAL_SERVER_ERROR_STATUS,
        )


"""
Ruta para obtener información sobre el artista/banda.

Parámetro:
    <int:id> = Id del artista/banda.
"""


@api.route("/artist/<int:id>")
def get_artist(id):
    try:
        # Verificar si el parámetro de la petición es válido.
        if id <= 0:
            return (
                jsonify({"msg": INVALID_PARAMETERS, "status": BAD_REQUEST_STATUS}),
                BAD_REQUEST_STATUS,
            )

        # Realizar la petición y verificar si fue exitosa.
        r = requests.get(f"{ARTIST_URL}/{id}")
        if r.status_code == NOT_FOUND_STATUS:
            return (
                jsonify({"msg": ARTIST_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )
        elif r.status_code != OK_STATUS:
            return (
                jsonify(
                    {"msg": SERVICE_UNAVAILABLE, "status": SERVICE_UNAVAILABLE_STATUS}
                ),
                SERVICE_UNAVAILABLE_STATUS,
            )

        # Obtener la información de los artistas.
        data = r.json().get("response").get("artist")

        # Helper para las redes sociales del artista.
        facebook_name, instagram_name, twitter_name = (
            data.get("facebook_name"),
            data.get("instagram_name"),
            data.get("twitter_name"),
        )

        return jsonify(
            {
                "data": {
                    "description": data.get("description_preview")
                    if data.get("description_preview") != ""
                    else None,
                    "id": id,
                    "image": data.get("image_url")
                    if "default" not in data.get("image_url")
                    else None,
                    "name": data.get("name"),
                    "nicknames": data.get("alternate_names")
                    if data.get("alternate_names") != []
                    else None,
                    "social_media": {
                        "facebook": "https://www.facebook.com/" + facebook_name
                        if facebook_name
                        else None,
                        "instagram": "https://www.instagram.com/" + instagram_name
                        if instagram_name
                        else None,
                        "twitter": "https://twitter.com/" + twitter_name
                        if twitter_name
                        else None,
                    }
                    if facebook_name or instagram_name or twitter_name
                    else None,
                    "verified": data.get("is_verified"),
                },
                "status": OK_STATUS,
            }
        )
    except:
        return (
            jsonify(
                {"msg": INTERNAL_SERVER_ERROR, "status": INTERNAL_SERVER_ERROR_STATUS}
            ),
            INTERNAL_SERVER_ERROR_STATUS,
        )


"""
Ruta para obtener una lista de canciónes del artista/banda.

Parámetros:
    <int:id> = Id del artista/banda.
    <int:page> (opt) = Número de página de resultados.
"""


@api.route("/artist/<int:id>/songs")
def get_songs(id):
    try:
        # Verificar los parámetros de la petición y añadirlos a variables.
        try:
            if id <= 0:
                return (
                    jsonify({"msg": ARTIST_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                    NOT_FOUND_STATUS,
                )

            args = json.loads(json.dumps(request.args))
            page = (
                1
                if "page" not in args or int(args.get("page")) <= 0
                else int(args.get("page"))
            )
        except:
            return (
                jsonify({"msg": INVALID_PARAMETERS, "status": BAD_REQUEST_STATUS}),
                BAD_REQUEST_STATUS,
            )

        # Realizar la petición y verificar si fue exitosa.
        r = requests.get(f"{ARTIST_URL}/{id}/songs?sort=popularity&page={page}")
        if r.status_code == NOT_FOUND_STATUS:
            return (
                jsonify({"msg": ARTIST_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )
        elif r.status_code != OK_STATUS:
            return (
                jsonify(
                    {"msg": SERVICE_UNAVAILABLE, "status": SERVICE_UNAVAILABLE_STATUS}
                ),
                SERVICE_UNAVAILABLE_STATUS,
            )

        # Obtener la información de las canciones.
        data = r.json().get("response")

        # Filtrar la información de cada cancion y añadirla a un arreglo de objetos.
        songs = []
        for i in data.get("songs"):
            if i.get("primary_artist").get("id") == id:
                if songs == []:
                    primary_artist = i.get("primary_artist")
                    image = primary_artist.get("image_url")
                    name = primary_artist.get("name")
                    verified = primary_artist.get("is_verified")

                songs.append(
                    {
                        "artists": i.get("artist_names"),
                        "full_title": " ".join(
                            [name, "-", i.get("title_with_featured")]
                        ),
                        "title": i.get("title_with_featured"),
                        "song_id": i.get("id"),
                        "song_image": i.get("song_art_image_url"),
                    }
                )

        return (
            jsonify(
                {
                    "data": {
                        "id": id,
                        "image": image,
                        "name": name,
                        "songs": songs,
                        "verified": verified,
                    },
                    "next_page": data.get("next_page"),
                    "status": OK_STATUS,
                }
            ),
            OK_STATUS,
        )
    except:
        return (
            jsonify(
                {"msg": INTERNAL_SERVER_ERROR, "status": INTERNAL_SERVER_ERROR_STATUS}
            ),
            INTERNAL_SERVER_ERROR_STATUS,
        )


"""
Ruta para obtener información de la canción y sus lyrics.

Parámetro:
    <int:song_id> = Id de la canción.
"""


@api.route("/song/<int:song_id>")
def get_lyrics(song_id):
    try:
        # Verificar el parámetro de la petición y añadirlo a una variable.
        if song_id <= 0:
            return (
                jsonify({"msg": SONG_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )

        # Realizar la petición y verificar si fue exitosa.
        r = requests.get(f"{SONG_URL}/{song_id}")
        if r.status_code == NOT_FOUND_STATUS:
            return (
                jsonify({"msg": SONG_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )
        elif r.status_code != OK_STATUS:
            return (
                jsonify(
                    {"msg": SERVICE_UNAVAILABLE, "status": SERVICE_UNAVAILABLE_STATUS}
                ),
                SERVICE_UNAVAILABLE_STATUS,
            )

        # Obtener la información de la canción.
        data = r.json().get("response").get("song")

        # Obtener información del artista principal.
        primary_artist = data.get("primary_artist")

        # Formatear la información de la canción dentro de un objeto.
        response = {
            "data": {
                "artists": data.get("artist_names"),
                "full_title": " ".join(
                    [
                        primary_artist.get("name"),
                        "-",
                        data.get("title_with_featured"),
                    ]
                ),
                "main_artist": {
                    "id": primary_artist.get("id"),
                    "image": primary_artist.get("image_url"),
                    "name": primary_artist.get("name"),
                    "verified": primary_artist.get("is_verified"),
                },
                "song_id": song_id,
                "song_image": data.get("song_art_image_url"),
                "song_lyrics": [],
                "title": data.get("title_with_featured"),
            },
            "status": OK_STATUS,
        }

        # Realizar la petición del código fuente de los lyrics y verificar si fue exitosa.
        r = requests.get(f"{LYRICS_URL}/{song_id}")
        if r.status_code == NOT_FOUND_STATUS:
            return (
                jsonify({"msg": SONG_NOT_FOUND, "status": NOT_FOUND_STATUS}),
                NOT_FOUND_STATUS,
            )
        elif r.status_code != OK_STATUS:
            return (
                jsonify(
                    {"msg": SERVICE_UNAVAILABLE, "status": SERVICE_UNAVAILABLE_STATUS}
                ),
                SERVICE_UNAVAILABLE_STATUS,
            )

        # Parsear el código fuente para formatear y añadir los párrafos de la letra de la canción al arreglo de lyrics.
        containers = BeautifulSoup(r.content, "html.parser").find_all(
            "div", attrs={"data-lyrics-container": "true"}
        )
        for container in containers:
            content = (
                re.compile(r"<.*?>")
                .sub("", str(container).replace("<br/>", "\n"))
                .replace('"', "'")
                .split("\n")
            )

            for p in content:
                response.get("data").get("song_lyrics").append(p if p != "" else "\n")

        return jsonify(response), OK_STATUS
    except:
        return (
            jsonify(
                {"msg": INTERNAL_SERVER_ERROR, "status": INTERNAL_SERVER_ERROR_STATUS}
            ),
            INTERNAL_SERVER_ERROR_STATUS,
        )
