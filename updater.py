import csv
import datetime
import os
from zipfile import ZipFile
from pymongo import MongoClient
from download_file import download_file
from utils.create_unique_key import create_unique_key
from typing import List, Dict, Any

EXTRACT_PATH = "tmp"

csv_data: List[Dict[str, Any]] = []


async def update(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> str:
    client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
    db = client[os.environ.get("MONGODB_DB_NAME", "local-lta-datasets")]
    collection = db[collection_name]

    try:
        zip_file_path = os.path.join(EXTRACT_PATH, zip_file_name)
        await download_file(zip_url, zip_file_path)

        extracted_file_name = extract_zip_file(zip_file_path, EXTRACT_PATH)
        destination_path = os.path.join(EXTRACT_PATH, extracted_file_name)
        print(f"Destination path: {destination_path}")

        with open(destination_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                csv_data.append(row)

        existing_data = collection.find({})

        existing_data_map = {
            create_unique_key(item, key_fields): item for item in existing_data
        }
        new_data_to_insert = [
            item
            for item in csv_data
            if create_unique_key(item, key_fields) not in existing_data_map
        ]

        if new_data_to_insert:
            result = collection.insert_many(new_data_to_insert)
            message = f"{len(result.inserted_ids)} document(s) inserted"
        else:
            message = (
                "No new data to insert. The provided data matches the existing records."
            )

        return message

    except Exception as error:
        print(f"An error has occurred: {error}")
        raise


def extract_zip_file(zip_file_path: str, extract_to_path: str) -> str:
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to_path)
        for entry in zip_ref.infolist():
            if not entry.is_dir():
                return entry.filename


async def main(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> Dict[str, Any]:
    message = await update(
        collection_name=collection_name,
        zip_file_name=zip_file_name,
        zip_url=zip_url,
        key_fields=key_fields,
    )

    response = {
        "status": 200,
        "collection": collection_name,
        "message": message,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    print(response)

    return response
