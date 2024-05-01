import requests
import os


class DownloadFileOptions:
    def __init__(self, url, destination):
        self.url: str = url
        self.destination: str = destination


async def download_file(options: DownloadFileOptions):
    response = requests.get(options.url, stream=True)
    if response.status_code == 200:
        filename = os.path.join(options.destination, os.path.basename(options.url))
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"File downloaded and saved as {options.destination}")
    else:
        print(f"Error while downloading {options.url}")
