import requests


def download_file(url: str, destination: str) -> None:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors

        with open(destination, "wb") as f:
            for chunk in response.iter_content(1024):  # Download in chunks
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)

        print(f"File downloaded to: {destination}")

    except requests.exceptions.HTTPError as e:
        print(
            f"Download failed: HTTP Error - {e.response.status_code} {e.response.reason}"
        )
    except requests.exceptions.Timeout as e:
        print("Download failed: Request timed out.")
    except requests.exceptions.RequestException as e:  # Fallback for other errors
        print(f"Download failed: {e}")
