import requests


async def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(destination, "wb") as f:
            for chunk in response.iter_content(1024):  # Download in chunks
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)

        print(f"File downloaded to: {destination}")
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
