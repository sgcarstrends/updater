import asyncio
from typing import List

import updater
from db import MongoDBConnection


async def main():
    collection_name: str = "cars"
    zip_file_name: str = "Monthly New Registration of Cars by Make.zip"
    zip_url: str = (
        f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"
    )
    key_fields: List[str] = ["month"]

    db = MongoDBConnection().database
    collection = db[collection_name]

    # Create indexes
    collection.create_index({"month": 1, "make": 1})
    collection.create_index({"month": 1})
    collection.create_index({"make": 1})
    collection.create_index({"fuel_type": 1})
    collection.create_index({"make": 1, "fuel_type": 1})
    collection.create_index({"number": 1})

    update_result = await updater.main(
        collection_name, zip_file_name, zip_url, key_fields
    )

    replace_empty_string_with_zero = [
        {"$match": {"number": ""}},
        {"$set": {"number": 0}},
        {
            "$merge": {
                "into": collection_name,
                "on": "_id",
                "whenMatched": "replace",
                "whenNotMatched": "discard",
            }
        },
    ]

    format_values = [
        {
            "$addFields": {
                "make": {
                    "$replaceAll": {"input": "$make", "find": ".", "replacement": ""},
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
                "into": collection_name,
                "on": "_id",
                "whenMatched": "merge",
                "whenNotMatched": "discard",
            }
        },
    ]

    uppercase_make = [
        {"$addFields": {"make": {"$toUpper": "$make"}}},
        {
            "$merge": {
                "into": collection_name,
                "on": "_id",
                "whenMatched": "merge",
                "whenNotMatched": "discard",
            }
        },
    ]

    # collection.aggregate(replace_empty_string_with_zero)
    # collection.aggregate(format_values)
    # collection.aggregate(uppercase_make)

    db.client.close()

    return update_result


def handler(event, context):
    print("Event:", event)
    response = asyncio.run(main())
    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    asyncio.run(main())
