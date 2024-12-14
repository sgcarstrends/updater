import csv
import datetime
import json
import os
import re
import tempfile
import time
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from pymongo.results import InsertManyResult

from db import MongoDBConnection
from download_file import download_file
from utils.calculate_checksum import calculate_checksum
from utils.create_unique_key import create_unique_key
from utils.extract_zip_file import extract_zip_file
from utils.redis_cache import get_cached_checksum, cache_checksum

load_dotenv()


def read_csv_data(file_path: str) -> List[Dict[str, Any]]:
    csv_data = []
    with open(file_path, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(process_csv_row(row))
    return csv_data


def process_csv_row(row) -> Dict[str, Any]:
    if "make" in row:
        row["make"] = row["make"].replace(".", "")
    # Convert string values to numbers if possible
    for key, value in row.items():
        if re.match(r"\b\d+(?:,\d+)?\b", value):
            row[key] = 0 if value == "" else value
            try:
                value = str(int(value.replace(",", "")))
                row[key] = float(value) if "." in value else int(value)
            except ValueError:
                pass
    return row


async def updater(
    collection_name: str, zip_file_name: str, zip_url: str, key_fields: List[str]
) -> Tuple[InsertManyResult | None, str]:
    db = MongoDBConnection().database
    collection = db[collection_name]

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, zip_file_name)
            download_file(zip_url, zip_file_path)

            extracted_file_name = extract_zip_file(zip_file_path, temp_dir)
            destination_path = os.path.join(temp_dir, extracted_file_name)
            print(f"Destination path: {destination_path}")

            checksum = calculate_checksum(destination_path)
            print(f"Checksum (SHA-256) of extracted file: {checksum}")

            cached_checksum = await get_cached_checksum(extracted_file_name)
            if cached_checksum is None:
                print("No cached checksum found. This might be the first run.")
                await cache_checksum(extracted_file_name, checksum)
                print(
                    f"Checksum for {extracted_file_name} cached. Checksum: {checksum}"
                )
            elif cached_checksum == checksum:
                return (
                    None,
                    f"File have not been changed since last update. Checksum: {checksum}",
                )

            await cache_checksum(extracted_file_name, checksum)
            print("Checksum has been changed.")

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
                message = f"{len(result.inserted_ids)} document(s) inserted in {round((end - start) * 1000)}ms"
                return result, message
            else:
                message = "No new data to insert. The provided data matches the existing records."
                return None, message

    except Exception as error:
        raise Exception(f"An error has occurred: {error}")
    finally:
        db.client.close()


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

    print(json.dumps(response, indent=4))
    return response
