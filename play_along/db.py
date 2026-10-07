from os import getenv

# from mssql_python import connect
import sqlite3
import click
import time

from .blob import delete_all_audio_from_az_blob, blob_sas_url

from flask import g, current_app, Flask
from dotenv import load_dotenv

load_dotenv()

connection_string = getenv("AZURE_SQL_CONNECTIONSTRING")


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    # Clear blob storage
    delete_all_audio_from_az_blob()


@click.command("init-db")
def init_db_command():
    """DROPS ALL TABLES AND CREATES NEW ONES"""
    init_db()
    click.echo("===DB Initialized===")


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db(retries=5, delay=5):
    last_err = None

    for attempt in range(1, retries + 1):
        try:
            if "db" not in g:
                g.db = sqlite3.connect(
                    current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
                )
                g.db.row_factory = sqlite3.Row

            return g.db

        except Exception as e:
            last_err = e
            print(f"DB connect attempt {attempt} failed: {e}")
            time.sleep(delay)
    raise RuntimeError(f"Could not connect to DB after {retries} attempts: {last_err}")


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


# CRUD LIKE OPERATIONS

## TRACKS

def check_existing_track(youtube_id: str):
    conn = get_db()
    cursor = conn.cursor()

    query = (
        f"""SELECT COUNT(*) FROM audio_tracks where youtube_id = '{youtube_id}'"""
    )


    cursor.execute(query)
    res = cursor.fetchall()

    return True if res[0][0] > 0 else False


def get_track_info_by_id(track_id):
    conn = get_db()
    cursor = conn.cursor()

    query = f"""SELECT artist, track_album, track_name, thumbnail FROM audio_tracks where id = {track_id}"""
    cursor.execute(query)

    track_data = cursor.fetchall()[0]

    return track_data


def get_all_track_info_from_db():
    conn = get_db()
    cursor = conn.cursor()

    query = """SELECT id, youtube_id, artist, track_name, track_album, thumbnail FROM audio_tracks"""
    cursor.execute(query)
    track_data = cursor.fetchall()
    cursor.close()

    return track_data


def get_track_blob_storage(track_id):
    conn = get_db()
    cursor = conn.cursor()

    query = (
        f"""SELECT container, blob_name FROM audio_tracks where id = {track_id}"""
    )
    cursor.execute(query)

    track_data = cursor.fetchall()[0]

    sas_url = blob_sas_url(track_data[0], track_data[1])

    return sas_url


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


## REGIONS


def get_regions_by_id(audio_track_id: int):
    conn = get_db()
    cursor = conn.cursor()

    query = f"""SELECT label, [start], [end], color from loop_regions where audio_track_id = '{audio_track_id}' order by [start] ASC"""

    cursor.execute(query)
    regions = cursor.fetchall()

    regions = [
        {"label": label, "start": start, "end": end, "color": color}
        for label, start, end, color in regions
    ]

    return regions if len(regions) > 0 else []


def send_regions_to_db(regions: list, track_id: int):
    conn = get_db()
    cursor = conn.cursor()
    try:
        if not regions:
            cursor.execute(
                "DELETE FROM loop_regions WHERE audio_track_id = ?", (track_id,)
            )
            conn.commit()
            return

        # UPSERT each region (needs a unique index on audio_track_id + label)
        cursor.executemany(
            """
            INSERT INTO loop_regions (audio_track_id, label, "start", "end", color)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (audio_track_id, label) DO UPDATE SET
                "start" = excluded."start",
                "end"   = excluded."end",
                color   = excluded.color
            """,
            [
                (track_id, r["label"], r["start"], r["end"], r["color"])
                for r in regions
            ],
        )

        # Remove regions that are no longer present (the "NOT MATCHED BY SOURCE" part)
        labels = [r["label"] for r in regions]
        placeholders = ", ".join("?" * len(labels))
        cursor.execute(
            f"""
            DELETE FROM loop_regions
            WHERE audio_track_id = ? AND label NOT IN ({placeholders})
            """,
            [track_id, *labels],
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Failed to insert loop region in DB. Error:\n{e}")
    finally:
        cursor.close()
