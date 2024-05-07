import asyncio
import updater
from typing import List


async def main():
    collection_name: str = "coe"
    zip_file_name: str = "COE Bidding Results.zip"
    zip_url: str = (
        f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{zip_file_name}"
    )
    key_fields: List[str] = ["month", "bidding_no"]

    await updater.main(
        collection_name=collection_name,
        zip_url=zip_url,
        zip_file_name=zip_file_name,
        key_fields=key_fields,
    )


if __name__ == "__main__":
    asyncio.run(main())
