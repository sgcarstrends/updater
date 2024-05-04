import asyncio
import csv
import datetime
import os
from zipfile import ZipFile
from pymongo import MongoClient

from download_file import download_file

EXTRACT_PATH = "tmp"

csv_file_path = "tmp/Monthly New Registration of Cars by Make/M03-Car_Regn_by_make.csv"

json_file_path = (
    "tmp/Monthly New Registration of Cars by Make/M03-Car_Regn_by_make.csv.json"
)

csv_data = []


async def update(collection_name, zip_file_name, zip_url, key_fields):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["local-lta-datasets"]
    collection = db[collection_name]

    try:
        zip_file_path = os.path.join(EXTRACT_PATH, zip_file_name)
        await download_file(zip_url, zip_file_path)  # You'll need to define this

        extracted_file_name = extract_zip_file(zip_file_path, EXTRACT_PATH)
        destination_path = os.path.join(EXTRACT_PATH, extracted_file_name)
        print(f"Destination path: {destination_path}")

        with open(destination_path, "r", encoding="utf-8") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                csv_data.append(row)

        existing_data = collection.find({})

        def create_unique_key(item, key_fields):
            return "-".join(str(item[field]) for field in key_fields if item.get(field))

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

    except Exception as error:  # Use Exception for a broader error catch
        print(f"An error has occurred: {error}")
        raise


def extract_zip_file(zip_file_path, extract_to_path):
    with ZipFile(zip_file_path, "r") as zip_ref:
        zip_ref.extractall(extract_to_path)
        for entry in zip_ref.infolist():
            if not entry.is_dir():
                return entry.filename
    return ""


async def main():
    zip_file_name = "Monthly New Registration of Cars by Make.zip"
    zip_url = f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"  # Replace with the actual URL
    collection_name = "cars"

    message = await update(
        collection_name=collection_name,
        zip_file_name=zip_file_name,
        zip_url=zip_url,
        key_fields=["month"],
    )

    response = {
        "status": 200,
        "collection": collection_name,
        "message": message,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    print(response)

    return response


if __name__ == "__main__":
    asyncio.run(main())
