from pathlib import Path
import yaml
import logging
from typing import Dict,List,Any,Type,Set
import json
import bson

def get_local_path(base_file: str, relative_path: str) -> Path:
    return Path(base_file).parent.joinpath(relative_path)

def load_yaml_file(base_file: str, relative_path: str) -> Dict:
    path = get_local_path(base_file, relative_path)

    if not path.exists():
        logging.error(f"YAML file not found: {path}")
        raise FileNotFoundError(path)

    with path.open("r") as f:
        return yaml.safe_load(f)
    
def load_file(base_file: str, relative_path: str) -> Dict:
    path = get_local_path(base_file, relative_path)

    if not path.exists():
        logging.error(f"file not found: {path}")
        raise FileNotFoundError(path)

    with path.open("r") as file:
        return file.read()
    

def load_json(file_path: str) -> dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"[load_json] Error loading JSON file: {e}")
        return {}
    
def stringify_large_ints(obj, path_prefix=""):
    if isinstance(obj, dict):
        return {
            k: str(v) if isinstance(v, int) and abs(v) > 2**63 - 1 else stringify_large_ints(v, f"{path_prefix}.{k}" if path_prefix else k)
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [stringify_large_ints(i, path_prefix) for i in obj]
    return obj

def prepare_for_mongo(data):
    return [stringify_large_ints(doc) for doc in data]


def format_token_addresses_as_tuple(token_addresses: List[str]) -> str:
    if len(token_addresses) == 1:
        return f"('{token_addresses[0]}')"
    return str(tuple(token_addresses))


def get_value_tokens_list(data: List[Dict]) -> List[str]:
    value_in_tokens = {doc['value_in_token'] for doc in data if 'value_in_token' in doc}
    return list(value_in_tokens)

def get_path_tokens_list(data: List[Dict]) -> List[str]:
    path_tokens = set()
    for doc in data:
        tokens = doc.get('path_tokens', [])
        path_tokens.update(tokens)
    return list(path_tokens)