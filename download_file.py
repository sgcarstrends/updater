import io
import zipfile
import requests
import os


class DownloadFileOptions:
    def __init__(self, url, destination):
        self.url: str = url
        self.destination: str = destination


async def download_file(url):
    folder_path = "tmp"
    os.makedirs(folder_path, exist_ok=True)
    response = requests.get(url)

    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(folder_path)
        print("Zip file downloaded and extracted successfully!")
    else:
        print("Failed to download the zip file.")
