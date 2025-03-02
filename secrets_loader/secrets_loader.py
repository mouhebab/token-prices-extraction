import os
from dotenv import load_dotenv
from typing import List, Tuple
from helpers.utils import get_local_path
 
DEFAULT_KEYS_PATH = get_local_path(__file__,".env")

def load_env(keys_path: str = DEFAULT_KEYS_PATH) -> None:
    """
    Load environment variables from  .env file.
    """
    if not os.path.exists(keys_path):
        raise FileNotFoundError(f".env file not found at: {keys_path}")
    load_dotenv(keys_path)

def get_env_vars(variables: List[str]) -> Tuple[str, ...]:
    """
    Args:
        variables: List of environment variable names to retrieve.

    Returns:
        Tuple of environment variable values in order.
    """
    load_env()
    values = tuple(os.getenv(var) for var in variables)

    if None in values:
        missing = [var for var, val in zip(variables, values) if val is None]
        raise EnvironmentError(f"Missing env variables: {missing}")

    return values