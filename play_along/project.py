from play_along.db import get_db, init_app
from play_along.blob import (
    blob_sas_url,
    send_audio_to_az_blob,
    delete_audio_from_az_blob,
)

from mssql_python import IntegrityError

from flask import Blueprint, render_template, request, flash
import json
from dotenv import load_dotenv

# YT Downloader
from yt_dlp import YoutubeDL

# Load and get env variables
load_dotenv()

# Global Variables
from play_along.config import AUDIO_DIR

# Initialize Blueprint
bp = Blueprint("project", __name__)


# ENDPOINTS
@bp.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        try:
            url = request.form.get("youtube_url")

            # Verify if track already exists in db
            # Split string to get youtube_id
            youtube_id = url.rsplit("/watch?v=", maxsplit=1)[-1]

            #Query db for track
            songExists = get_track_by_id(youtube_id)

            if not songExists:
                # Download audio track from youtube
                track_info_dict = download_audiotrack(url, download=True)

                # Send audio file to azure blob storage
                blob_name = send_audio_to_az_blob(track_info_dict.get("title", ""))

                # Send info to database
                send_track_info_to_db(track_info_dict, blob_name)
            else:
                flash("Song already exists in DB!", "error")

        except Exception as e:
            print(f"An exception was thrown with the following error: {e}")

    # Query database for track data stored
    track_data = get_all_track_info_from_db()
    return render_template("base.html", track_data=track_data)


@bp.route("/wave/<int:track_id>", methods=["GET", "POST"])
def wave_audio(track_id):
    if request.method == "POST":
        regions = json.loads(request.form.get("regions", "[]"))

        print(regions)

    # Get track info
    conn = get_db()
    cursor = conn.cursor()

    query = (
        f"""SELECT container, blob_name FROM dbo.audio_tracks where id = {track_id}"""
    )
    cursor.execute(query)

    track_data = cursor.fetchall()[0]

    sas_url = blob_sas_url(track_data[0], track_data[1])
    return render_template("waveform.html", url=sas_url)


@bp.route("/test_youtube_id/<string:youtube_id>", methods=["GET"])
def test_youtube_url(youtube_id:str):

    res = get_track_by_id(youtube_id)

    return str(res)


def download_audiotrack(url:str, download:bool = True):
    global AUDIO_DIR

    ydl_opts = {
        "extract_audio": True,
        "format": "bestaudio/best",
        "outtmpl": f"{AUDIO_DIR}/%(title)s.mp3",
        "quiet": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        track_info_dict = ydl.extract_info(url, download=download)

        return track_info_dict


def get_track_by_id(youtube_id: str):
    conn = get_db()
    cursor = conn.cursor()

    query = (
        f"""SELECT COUNT(*) FROM dbo.audio_tracks where youtube_id = '{youtube_id}'"""
    )

    cursor.execute(query)
    res = cursor.fetchall()

    return True if len(res) > 1 else False 


def get_all_track_info_from_db():
    conn = get_db()
    cursor = conn.cursor()

    query = """SELECT id, youtube_id, artist, track_name, track_album, thumbnail FROM dbo.audio_tracks"""
    cursor.execute(query)
    track_data = cursor.fetchall()
    cursor.close()

    return track_data


def get_regions_from_db(youtube_id: str): ...


def send_regions_to_db(regions: json): ...


def send_track_info_to_db(track_info: dict, blob_name: str):

    conn = get_db()
    cursor = conn.cursor()

    # Get info from dict
    youtube_id = track_info.get("id", "")
    artist = track_info.get("artist", "")
    track_name = track_info.get("title", "")
    track_album = track_info.get("album", "")
    thumbnail = track_info.get("thumbnail", "")
    duration_sec = track_info.get("duration", "")

    # Assign info of blob storage
    blob_name = blob_name
    container = "play-along-app-audio-files"
    content_type = "audio/mpeg"

    query = f"""
        INSERT INTO audio_tracks (youtube_id, artist, track_name, track_album, thumbnail, duration_sec, blob_name, container, content_type)
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        (
            youtube_id,
            artist,
            track_name,
            track_album,
            thumbnail,
            duration_sec,
            blob_name,
            container,
            content_type,
        ),
    )
    conn.commit()
    cursor.close()


if __name__ == "__main__":
    main()
