import requests
import zipfile
import io
import csv
import json
from pymongo import MongoClient


def lambda_handler(event, context):
    # -------- Step 1: Download the .zip File --------
    zip_file_url = "https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/Monthly New Registration of Cars by Make.zip"
    response = requests.get(zip_file_url)

    # -------- Step 2: Extract the .csv File in Memory --------
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        for file_info in zip_ref.infolist():
            if file_info.filename.endswith(".csv"):
                with zip_ref.open(
                    file_info
                ) as csv_file:  # Assumes 'data.csv' is in the zip root
                    csv_data = []
                    csv_reader = csv.DictReader(io.TextIOWrapper(csv_file))
                    for row in csv_reader:
                        csv_data.append(row)

    # -------- Step 3: Convert CSV to JSON --------
    json_data = json.dumps(csv_data)

    # -------- Step 4: Connect to MongoDB --------
    client = MongoClient(
        "mongodb://localhost:27017/"
    )  # Replace this with connection details for MongoDB Atlas or DocumentDB
    db = client["local-lta-datasets"]
    collection = db["cars"]

    # -------- Step 5: Comparison  --------
    existing_data = collection.find({}, {"month": 1})
    existing_data_set = {item["month"] for item in existing_data}

    new_items = [item for item in json_data if item["month"] not in existing_data_set]

    # -------- Step 6: Insert New Items --------
    if new_items:
        collection.insert_many(new_items)
        print(f"Inserted {len(new_items)} records")
    else:
        print("No new records")

    return {"statusCode": 200, "body": "Data successfully written to MongoDB!"}


if __name__ == "__main__":
    lambda_handler(None, None)
