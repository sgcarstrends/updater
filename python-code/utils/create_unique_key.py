from typing import Dict, Any, List


def create_unique_key(item: Dict[str, Any], key_fields: List[str]) -> str:
    return "-".join(str(item[field]) for field in key_fields if item.get(field))
