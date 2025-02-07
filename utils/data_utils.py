from typing import List, Set


def is_complete_venue(venue: dict, required_keys: List[str]) -> dict:
    normalized_dict = {}
    for field in required_keys:
        normalized_dict[field] = venue.get(field, None)
    
    return normalized_dict

def is_duplicate_venue(venue: dict, seen_names: Set[str]) -> bool:
    return venue["name"] in seen_names