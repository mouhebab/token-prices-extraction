import logging
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Tuple, Optional
from helpers.utils import load_file,format_token_addresses_as_tuple
from secrets_loader.secrets_loader import load_env,get_env_vars
from extract.flipside_api_handler import extract_flipsidecrypto_data


load_env()
flipside_api_key = get_env_vars(['flipside_key'])[0]




def extract_tokens(query_path: str, token_addresses: List[str], api_key: str = flipside_api_key) -> List[Dict[str, Any]]:

    try:
        query = load_file(__file__,query_path)

        token_tuple_str = format_token_addresses_as_tuple(token_addresses)
        params = {'TOKEN_ADDRESSES': token_tuple_str}

        token_data = extract_flipsidecrypto_data(query, params, api_key=api_key)

        logging.info(f"[extract_tokens] {len(token_data)} rows fetched from query: {query_path}")
        return token_data

    except Exception as e:
        logging.error(f"[extract_tokens] Error fetching token data: {type(e).__name__}: {e}")
        return []

def main(token_addresses: List[str], mode: str = "prices") -> List[Dict[str, Any]]:
    """
        mode: 'prices' or 'infos'
    """
    if mode == "prices":
        query_path = "params/queries/query_token_prices.sql"
    elif mode == "infos":
        query_path = "params/queries/query_tokens_info.sql"
    else:
        raise ValueError(f"Unknown mode '{mode}'. Supported modes: 'prices', 'infos'.")

    return extract_tokens(query_path, token_addresses)


