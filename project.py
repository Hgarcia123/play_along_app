from play_along.db import (
    get_track_info_by_id,
    get_all_track_info_from_db,
    send_regions_to_db,
    send_track_info_to_db,
    get_track_blob_storage,
    check_existing_track,
    get_regions_by_id
)
from play_along.blob import (
    send_audio_to_az_blob,
)

from play_along import create_app

from flask import (
    Blueprint,
    render_template,
    request,
    flash
)

import os, json
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
## HOMEPAGE
@bp.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        try:
            local_path = None
            url = request.form.get("youtube_url")

            # Verify if track already exists in db
            # Split string to get youtube_id
            youtube_id = url.rsplit("/watch?v=", maxsplit=1)[-1]

            # Query db for track
            songExists = check_existing_track(youtube_id)

            if not songExists:
                # Download audio track from youtube
                track_info_dict = download_audiotrack(url, download=True)

                #get local path of file
                local_path = track_info_dict["requested_downloads"][0]["filepath"]

                # Send audio file to azure blob storage
                blob_name = send_audio_to_az_blob(track_info_dict.get("title", ""))

                # Send info to database
                send_track_info_to_db(track_info_dict, blob_name)
            else:
                flash("Song already exists in DB!", "error")

        except Exception as e:
            print(f"An exception was thrown with the following error: {e}")

        finally:
            if local_path and os.path.exists(local_path):
                os.remove(local_path)
                
    # Query database for track data stored
    track_data = get_all_track_info_from_db()
    return render_template("base.html", track_data=track_data)


## WAVEFORM
@bp.route("/wave/<int:track_id>", methods=["GET", "POST"])
def wave_audio(track_id):
    if request.method == "POST":
        regions = json.loads(request.form.get("regions", "[]"))
        send_regions_to_db(regions, track_id)
        return "", 204  # no page reload, nothing to render

    # Get track info
    track_data = get_track_info_by_id(track_id)
    # Get track blob storage info
    sas_url = get_track_blob_storage(track_id)
    # Get previously saved regions of track
    regions = get_regions_by_id(track_id)

    return render_template("waveform.html", url=sas_url, track_data=track_data, regions=regions)


def download_audiotrack(url: str, download: bool = True):
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

#Create app
app = create_app()
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run()
