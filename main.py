from extract.extract_tokens import main as extract_tokens_main
from load.mongodb.mongodb import load_to_mongo,load_from_mongo
from helpers.utils import prepare_for_mongo,get_value_tokens_list,get_path_tokens_list
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


def main():
    TOKENS_PRICES_COLLECTION_KEY = "Tokens_prices"
    TOKENS_INFO_COLLECTION_KEY = "Tokens_info"
    DECODED_DATA_COLLECTION_KEY = "transactions_routes_decoded"

    setup_logging()
    logging.info("ETL Pipeline Started")


    try:
            decoded_data = load_from_mongo(DECODED_DATA_COLLECTION_KEY)
            tokens_value_list = get_value_tokens_list(decoded_data)
            tokens_path_list = get_path_tokens_list(decoded_data)

            logging.info(f"Extracting token prices for {len(tokens_value_list)} tokens.")
            prices = extract_tokens_main(tokens_value_list, mode="prices")

            logging.info(f"Extracting token infos for {len(tokens_path_list)} tokens.")
            infos = extract_tokens_main(tokens_path_list, mode="infos")

            logging.info("Loading extracted data into MongoDB.")
            load_to_mongo(prepare_for_mongo(prices), TOKENS_PRICES_COLLECTION_KEY)
            load_to_mongo(infos, TOKENS_INFO_COLLECTION_KEY)

            logging.info("ETL Pipeline Completed Successfully.")

    except Exception as e:
        logging.exception("ETL Pipeline Failed.")
        raise

if __name__ == "__main__":
    main()