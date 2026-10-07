import os, pytest

from project import download_audiotrack
from play_along.db import (send_track_info_to_db, delete_track_info_from_db)
from play_along.blob import send_audio_to_az_blob

def test_env_loaded():
    assert os.getenv("AZURE_CLIENT_SECRET")


@pytest.fixture(scope="module")
def audio_dict():
    #Song 1
    url = "https://music.youtube.com/watch?v=U_XuO0MuoHE"

    #Test download with Youtube Music Link
    return download_audiotrack(url, True)


def test_download_audiotrack(audio_dict):

    #Check if info obtained from dowloaded track is valid
    assert audio_dict["title"] == "Big Mits"
    assert audio_dict["release_year"] == 2024

@pytest.fixture(scope="module")
def blob_name(audio_dict):
    
    return send_audio_to_az_blob(audio_dict.get("title", ""))

@pytest.fixture(scope="module")
def new_id(app, audio_dict, blob_name):
    
    return send_track_info_to_db(audio_dict, blob_name)

def test_send_track_info_to_db(new_id, blob_name):

    #Test failed attempt
    with pytest.raises(RuntimeError):
        send_audio_to_az_blob(1234)

    assert isinstance(blob_name, str)
    assert isinstance(new_id, int)


def test_delete_track_info_from_db(app, new_id, blob_name):

    #Try to delete audio with an non-existent id
    assert delete_track_info_from_db(99999999, blob_name) == False

    #Delete audio from both db and blob storage
    assert delete_track_info_from_db(new_id, blob_name) == True