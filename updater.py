import csv
import datetime
import os
import tempfile
import time
from typing import List, Dict, Any

from dotenv import load_dotenv

from db import MongoDBConnection
from download_file import download_file
from utils.create_unique_key import create_unique_key
from utils.extract_zip_file import extract_zip_file

load_dotenv()


def read_csv_data(file_path: str) -> List[Dict[str, Any]]:
    csv_data = []
    with open(file_path, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(row)
    return csv_data


async def updater(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> tuple[Any, str] | tuple[None, str]:
    db = MongoDBConnection().database
    collection = db[collection_name]

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, zip_file_name)
            download_file(zip_url, zip_file_path)

            extracted_file_name = extract_zip_file(zip_file_path, temp_dir)
            destination_path = os.path.join(temp_dir, extracted_file_name)
            print(f"Destination path: {destination_path}")

            csv_data: List[Dict[str, Any]] = read_csv_data(destination_path)

            existing_data_map = {
                create_unique_key(item, key_fields): item
                for item in collection.find({})
            }
            new_data_to_insert = [
                item
                for item in csv_data
                if create_unique_key(item, key_fields) not in existing_data_map
            ]

            if new_data_to_insert:
                start = time.time()
                result = collection.insert_many(new_data_to_insert)
                end = time.time()
                db.client.close()
                message = f"{len(result.inserted_ids)} document(s) inserted in {round((end - start) * 1000)}ms"
                return result, message
            else:
                message = "No new data to insert. The provided data matches the existing records."
                return None, message

    except Exception as error:
        print(f"An error has occurred: {error}")
        raise


async def main(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> Dict[str, Any]:
    timestamp = datetime.datetime.now().isoformat()

    try:
        result, message = await updater(
            collection_name,
            zip_file_name,
            zip_url,
            key_fields,
        )
        inserted_count = len(result.inserted_ids) if result else 0
    except Exception as e:
        inserted_count = 0
        message = str(e)

    response = {
        "collection": collection_name,
        "inserted_count": inserted_count,
        "message": message,
        "timestamp": timestamp,
    }

    print(response)
    return response
