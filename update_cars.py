from updater import update
from urllib.parse import quote

COLLECTION_NAME: str = "cars"
ZIP_FILE_NAME: str = "Monthly New Registration of Cars by Make.zip"
ZIP_URL: str = quote(
    f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{ZIP_FILE_NAME}"
)

print(ZIP_URL)


async def main():
    result = await update(
        COLLECTION_NAME,
        ZIP_FILE_NAME,
        ZIP_URL,
    )
    print(result)
