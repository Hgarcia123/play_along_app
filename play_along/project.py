from flask import (
    Flask, render_template, request
)
import os
from yt_dlp import YoutubeDL
from play_along.db import get_db

app = Flask(__name__)

output_path = './play_along/audio_files'

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

def get_audiotrack(url:str):
    global output_path

    ydl_opts = {
        'extract_audio': True,
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.mp3',
        'quiet': False
    }

    with YoutubeDL(ydl_opts) as ydl:
        track_info_dict = ydl.extract_info(url, download=True)

        return track_info_dict

def send_track_info_to_db(track_info:dict):
        
        conn = get_db()
        cursor = conn.cursor()

        #Get info from dict
        artist = track_info.get('artist', "")
        track_name = track_info.get('title', "")
        track_audio = "PLACEHOLDER"
        thumbnail = track_info.get('thumbnail', "")

        query = f"""
            INSERT INTO audio_tracks (artist, track_name, track_audio, thumbnail)
            VALUES(?, ?, ?, ?)
        """

        cursor.execute(query, (artist, track_name, track_audio, thumbnail))
        conn.commit()


if __name__ == '__main__':
    main()
