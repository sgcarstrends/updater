import pandas as pd
from download_file import download_file

EXTRACT_PATH = "/tmp"


async def read_csv_file(file_path: str):
    df = pd.read_csv(file_path)
    csv_dicts = df.to_dict("records")
    return csv_dicts


async def update(
    collection_name,
    zipFileName,
    zip_url,
):
    zip_file_path = f"{EXTRACT_PATH}/{collection_name}.zip"
    destination_path = await download_file(zip_url, zip_file_path)
    print(destination_path)
    return destination_path
