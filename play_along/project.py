from flask import (
    Flask, render_template, request, send_from_directory
)
import os
from yt_dlp import YoutubeDL
from play_along.db import get_db, init_app

app = Flask(__name__)

AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'audio_files')

init_app(app)

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        #TODO: Validate URL with regex
        url = request.form.get('youtube_url')

        #TODO: Call function get_audiotrack
        track_info_dict = get_audiotrack(url)

        #Send info to database
        send_track_info_to_db(track_info_dict)

    return render_template('base.html')

@app.route("/test_wave")
def wave_audio():
    return render_template('waveform.html')

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)


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

def send_track_info_to_db(track_info:dict):
        
        conn = get_db()
        cursor = conn.cursor()

        #Get info from dict
        youtube_id = track_info.get('id', "")
        artist = track_info.get('artist', "")
        track_name = track_info.get('title', "")
        track_audio = "PLACEHOLDER"
        thumbnail = track_info.get('thumbnail', "")

        query = f"""
            INSERT INTO audio_tracks (youtube_id, artist, track_name, track_audio, thumbnail)
            VALUES(?, ?, ?, ?)
        """

        cursor.execute(query, (youtube_id, artist, track_name, track_audio, thumbnail))
        conn.commit()


if __name__ == '__main__':
    main()
