import asyncio
from typing import List

import updater
from db import MongoDBConnection


async def main():
    collection_name: str = "coe"
    zip_file_name: str = "COE Bidding Results.zip"
    zip_url: str = (
        f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"
    )
    key_fields: List[str] = ["month", "bidding_no"]

    db = MongoDBConnection().database
    collection = db[collection_name]

    # Create indexes
    collection.create_index({"month": 1, "vehicle_class": 1});
    collection.create_index({"vehicle_class": 1});
    collection.create_index({"month": 1, "bidding_no": 1});
    collection.create_index({"premium": 1});
    collection.create_index({"bids_success": 1, "bids_received": 1});

    db.client.close()

    return await updater.main(collection_name, zip_file_name, zip_url, key_fields)


def handler(event, context):
    print(f"Event:", event)
    response = asyncio.run(main())
    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    asyncio.run(main())
