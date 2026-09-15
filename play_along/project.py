from play_along.db import get_db, init_app
from play_along.blob import blob_sas_url, send_audio_to_az_blob, delete_audio_from_az_blob

from mssql_python import IntegrityError

from flask import (
    Blueprint, render_template, request, flash
)
import json
from dotenv import load_dotenv

#YT Downloader
from yt_dlp import YoutubeDL

#Load and get env variables
load_dotenv()

#Global Variables
from play_along.config import AUDIO_DIR

#Initialize Blueprint
bp = Blueprint('project', __name__)


#ENDPOINTS

@bp.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':

        url = request.form.get('youtube_url')

        #Call function get_audiotrack
        track_info_dict = get_audiotrack(url)

        #Send audio file to azure blob storage
        blob_name = send_audio_to_az_blob(track_info_dict.get('title', ""))

        #Send info to database
        send_track_info_to_db(track_info_dict, blob_name)

    #Query database for track data stored
    track_data = get_track_info_from_db()
    return render_template('base.html', track_data=track_data)

@bp.route("/wave/<int:track_id>", methods=['GET', 'POST'])
def wave_audio(track_id):
    if request.method == 'POST':
        regions = json.loads(request.form.get('regions', '[]'))

        print(regions)

    #Get track info
    conn = get_db()
    cursor = conn.cursor()
  
    query = f"""SELECT container, blob_name FROM dbo.audio_tracks where id = {track_id}"""
    cursor.execute(query)

    track_data = cursor.fetchall()[0]

    sas_url = blob_sas_url(track_data[0], track_data[1])
    return render_template('waveform.html', url=sas_url)


def get_audiotrack(url:str):
    global AUDIO_DIR

    ydl_opts = {
        'extract_audio': True,
        'format': 'bestaudio/best',
        'outtmpl': f'{AUDIO_DIR}/%(title)s.mp3',
        'quiet': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        track_info_dict = ydl.extract_info(url, download=True)

        return track_info_dict

def get_track_info_from_db():

    conn = get_db()
    cursor = conn.cursor()
  
    query = """SELECT id, youtube_id, artist, track_name, track_album, thumbnail FROM dbo.audio_tracks"""
    cursor.execute(query)
    track_data = cursor.fetchall()
    cursor.close()

    return track_data



def get_regions_from_db(youtube_id:str):
    ...

def send_regions_to_db(regions:json):
    ...

def send_track_info_to_db(track_info:dict, blob_name:str):

    try:
        conn = get_db()
        cursor = conn.cursor()
            
        #Get info from dict
        youtube_id = track_info.get('id', "")
        artist = track_info.get('artist', "")
        track_name = track_info.get('title', "")
        track_album = track_info.get('album', "")
        thumbnail = track_info.get('thumbnail', "")
        duration_sec = track_info.get('duration', "")

        #Assign info of blob storage
        blob_name = blob_name
        container = "play-along-app-audio-files"
        content_type = "audio/mpeg"

        query = f"""
            INSERT INTO audio_tracks (youtube_id, artist, track_name, track_album, thumbnail, duration_sec, blob_name, container, content_type)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query, (youtube_id, artist, track_name, track_album, thumbnail, duration_sec, blob_name, container, content_type))
        conn.commit()
        cursor.close()

    except IntegrityError as e:
        flash('Song already exists in DB!', 'error')
        print(f'Could not save song song to DB with error: {e}')

        #Delete blob that was uploaded to az storage
        delete_audio_from_az_blob(blob_name=blob_name)


if __name__ == '__main__':
    main()