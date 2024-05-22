import asyncio
from typing import List

import updater


async def main():
    collection_name: str = "coe"
    zip_file_name: str = "COE Bidding Results.zip"
    zip_url: str = (
        f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"
    )
    key_fields: List[str] = ["month", "bidding_no"]

    response = await updater.main(
        collection_name=collection_name,
        zip_url=zip_url,
        zip_file_name=zip_file_name,
        key_fields=key_fields,
    )

    return response


def handler(event, context):
    print(f"Event:", event)
    response = asyncio.run(main())
    return {"statusCode": 200, "body": response}


if __name__ == "__main__":
    asyncio.run(main())
