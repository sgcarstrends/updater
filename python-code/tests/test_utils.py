import pytest
from utils.create_unique_key import create_unique_key


@pytest.mark.parametrize(
    "item, key_fields, expected_result",
    [
        (
            {
                "_id": {"$oid": "6635f923c113f9ccd1cea039"},
                "fuel_type": "Petrol",
                "importer_type": "AMD",
                "make": "B.M.W.",
                "month": "2024-03",
                "number": "54",
                "vehicle_type": "Sedan",
            },
            ["month"],
            "2024-03",
        ),
    ],
)
def test_generate_unique_key_for_cars(item, key_fields, expected_result):
    assert create_unique_key(item, key_fields) == expected_result


def test_generate_unique_key_for_coe():
    assert (
        create_unique_key(
            {
                "_id": {"$oid": "663a4e0a3d609a019b87090e"},
                "bidding_no": "2",
                "bids_received": "1,008",
                "bids_success": "690",
                "month": "2024-04",
                "premium": "102001",
                "quota": "690",
                "vehicle_class": "Category B",
            },
            ["month", "bidding_no"],
        )
        == "2024-04-2"
    )


if __name__ == "__main__":
    pytest.main()
