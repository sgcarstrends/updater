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


async def updater(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> str:
    db = MongoDBConnection().database
    collection = db[collection_name]

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, zip_file_name)
            download_file(zip_url, zip_file_path)

            extracted_file_name = extract_zip_file(zip_file_path, temp_dir)
            destination_path = os.path.join(temp_dir, extracted_file_name)
            print(f"Destination path: {destination_path}")

            csv_data: List[Dict[str, Any]] = []
            with open(destination_path, "r", encoding="utf-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    if "make" in row:
                        row["make"] = row["make"].replace(".", "")
                    csv_data.append(row)

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
            else:
                message = "No new data to insert. The provided data matches the existing records."

            return message

    except Exception as error:
        print(f"An error has occurred: {error}")
        raise


async def main(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> Dict[str, Any]:
    time_now = datetime.datetime.now().isoformat()
    response: Dict[str, str]

    try:
        message = await updater(
            collection_name,
            zip_file_name,
            zip_url,
            key_fields,
        )
        response = {
            "collection": collection_name,
            "message": message,
            "timestamp": time_now,
        }
    except Exception as e:
        response = {
            "collection": collection_name,
            "message": str(e),
            "timestamp": time_now,
        }
    print(response)
    return response
