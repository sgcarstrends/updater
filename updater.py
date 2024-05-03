import csv
import json
from download_file import download_file

EXTRACT_PATH = "tmp"

csv_file_path = "tmp/Monthly New Registration of Cars by Make/M03-Car_Regn_by_make.csv"

json_file_path = (
    "tmp/Monthly New Registration of Cars by Make/M03-Car_Regn_by_make.csv.json"
)

csv_data = []


async def update():
    with open(csv_file_path, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            csv_data.append(row)

    json_data = json.dumps(csv_data, indent=4)

    with open(json_file_path, "w") as json_file:
        json_file.write(json_data)

    print("CSV file parsed and converted to JSON successfully!")

    return json_data
