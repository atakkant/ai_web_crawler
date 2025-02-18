from typing import List, Set


def is_complete_repo(repo: dict, required_keys: List[str]) -> dict:
    normalized_dict = {}
    for field in required_keys:
        normalized_dict[field] = repo.get(field, None)
    
    return normalized_dict

def is_duplicate_repo(repo: dict, seen_names: Set[str]) -> bool:
    return repo["name"] in seen_names