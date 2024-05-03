import boto3
from dotenv import load_dotenv

from updater import update

load_dotenv()


COLLECTION_NAME: str = "cars"
ZIP_FILE_NAME: str = "Monthly New Registration of Cars by Make.zip"
ZIP_URL: str = (
    f"https://datamall.lta.gov.sg/content/dam/datamall/datasets/Facts_Figures/Vehicle Registration/{ZIP_FILE_NAME}"
)

print(f"ZIP_URL {ZIP_URL}")


async def main():
    result = await update()

    if __name__ == "__main__":
        # Create a DynamoDB table
        my_table = create_dynamodb_table("cars")

        # Put the item into the table
        put_item_into_table(my_table, result)


def create_dynamodb_table(table_name):
    # Create a DynamoDB resource
    dynamodb = boto3.resource("dynamodb")

    # Create the table
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
            {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"},  # String data type
            {
                "AttributeName": "timestamp",
                "AttributeType": "N",  # Number data type
            },
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

    # Wait until the table exists
    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

    print(f"DynamoDB Table {table_name} created")

    return table


def put_item_into_table(table, item_data):
    # Put an item into the DynamoDB table
    table.put_item(Item=item_data)
