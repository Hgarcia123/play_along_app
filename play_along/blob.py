from datetime import datetime, timedelta, timezone
import uuid
from pathlib import Path

#Global Variable
from play_along.config import AUDIO_DIR

#Azure Services
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

ACCOUNT = "playalongappsa001"
ACCOUNT_URL = f"https://{ACCOUNT}.blob.core.windows.net"

credential = DefaultAzureCredential()

#Cretate BlobServiceClient object
blob_service_client = BlobServiceClient(ACCOUNT_URL, credential)


def send_audio_to_az_blob(audio_file_path:str):
    try:
        audio_file_path = Path(AUDIO_DIR + "/" + audio_file_path + ".mp3")
        blob_name = f"{uuid.uuid4()}.mp3"

        blob = blob_service_client.get_blob_client(container="play-along-app-audio-files", blob=blob_name)

        print("\nUploading to Azure Storage as blob:\n\t" + blob_name)

        # Upload the created file
        with audio_file_path.open("rb") as data:
            blob.upload_blob(data)

            return blob_name

    except Exception as e:
        raise RuntimeError(f"Could not connect to storage account with error: {e}")

def delete_audio_from_az_blob(blob_name:str):
    blob = blob_service_client.get_blob_client(container="play-along-app-audio-files", blob=blob_name)

    print(f"Deleting blob '{blob_name}' from Azure Storage")

    blob.delete_blob(delete_snapshots='include')

def blob_sas_url(container:str, blob_name:str, minutes:int = 60):
    start = datetime.now(timezone.utc) - timedelta(minutes=5)
    expiry = datetime.now(timezone.utc) + timedelta(minutes=minutes)

    delegation_key = blob_service_client.get_user_delegation_key(start, expiry)

    token = generate_blob_sas(
        account_name=ACCOUNT,
        container_name=container,
        blob_name=blob_name,
        user_delegation_key=delegation_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry,
        start=start
    )

    return f"{ACCOUNT_URL}/{container}/{blob_name}?{token}"
