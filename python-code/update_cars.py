import asyncio
from typing import List, Dict, Any

from pymongo import ASCENDING, IndexModel
from pymongo.collection import Collection

import updater
from db import MongoDBConnection


async def create_indexes(collection: Collection) -> None:
    indexes = [
        IndexModel([("month", ASCENDING), ("make", ASCENDING)]),
        IndexModel([("month", ASCENDING)]),
        IndexModel([("make", ASCENDING)]),
        IndexModel([("fuel_type", ASCENDING)]),
        IndexModel([("make", ASCENDING), ("fuel_type", ASCENDING)]),
        IndexModel([("number", ASCENDING)]),
    ]
    collection.create_indexes(indexes)


async def run_aggregations(collection: Collection) -> None:
    aggregations = [
        [
            {"$match": {"number": ""}},
            {"$set": {"number": 0}},
            {
                "$merge": {
                    "into": collection.name,
                    "on": "_id",
                    "whenMatched": "replace",
                    "whenNotMatched": "discard",
                }
            },
        ],
        [
            {
                "$addFields": {
                    "make": {
                        "$replaceAll": {
                            "input": {
                                "$replaceAll": {
                                    "input": "$make",
                                    "find": ".",
                                    "replacement": "",
                                }
                            },
                            "find": "-",
                            "replacement": " ",
                        }
                    },
                    "vehicle_type": {
                        "$replaceAll": {
                            "input": "$vehicle_type",
                            "find": "/ ",
                            "replacement": "/",
                        }
                    },
                }
            },
            {
                "$merge": {
                    "into": collection.name,
                    "on": "_id",
                    "whenMatched": "merge",
                    "whenNotMatched": "discard",
                }
            },
        ],
        [
            {"$addFields": {"make": {"$toUpper": "$make"}}},
            {
                "$merge": {
                    "into": collection.name,
                    "on": "_id",
                    "whenMatched": "merge",
                    "whenNotMatched": "discard",
                }
            },
        ],
    ]

    for aggregation in aggregations:
        collection.aggregate(aggregation)


async def main() -> Dict[str, Any]:
    collection_name: str = "cars"
    zip_file_name: str = "Monthly New Registration of Cars by Make.zip"
    zip_url: str = (
        f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"
    )
    key_fields: List[str] = ["month"]

    db = MongoDBConnection().database
    collection = db[collection_name]

    await create_indexes(collection)

    message = await updater.main(collection_name, zip_file_name, zip_url, key_fields)

    if message["inserted_count"] > 0:
        print("Running aggregation...")
        await run_aggregations(collection)
        print("Aggregation complete.")

    db.client.close()

    return message


def handler(event, context):
    print("Event:", event)
    response = asyncio.run(main())
    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    asyncio.run(main())
