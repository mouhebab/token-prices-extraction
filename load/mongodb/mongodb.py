from pymongo import MongoClient, UpdateOne
import logging
import pandas as pd
import numpy as np
from typing import Any, Dict, List,Tuple, Optional
import requests
import yaml
from helpers.utils import load_yaml_file,load_file,get_local_path
from pathlib import Path
from pymongo.errors import BulkWriteError


import json
from bson import BSON

def get_mongo_connection_config(db_configs: Dict) -> Tuple[str, str]:
    """Extract Mongo host and db name from config."""
    try:
        mongo = db_configs["Mongo"]["Mongo_Config"]
        return mongo["host_url"], mongo["db_name"]
    except KeyError as e:
        raise ValueError(f"Missing MongoDB config key: {e}")

def get_collection_config(db_configs: Dict, collection_key: str) -> Tuple[str, List[str]]:
    """Get collection name and primary key(s) for a given collection key."""
    try:
        collection_cfg = db_configs["Mongo"]["Mongo_Collections"][collection_key]
        return collection_cfg["collection_name"], collection_cfg["primary_key"]
    except KeyError as e:
        raise ValueError(f"Missing collection config for key: {collection_key}") from e

    

def initialize_mongo_db(host:str, database_name:str)-> Tuple[MongoClient, Any]:
    try:
        client = MongoClient(host)
        db = client[database_name]
        return client,db
    except Exception as e:
        logging.error(f"Error in initiating Mongo client: {e}")    
    return None,None


# def bulk_upsert_mongodb(host:str, database_name:str, collection_name:str, data:List, unique_keys:List) -> Any:
#     try:
#         client, db = initialize_mongo_db(host, database_name)
#         if client is None or db is None:
#             logging.error("Failed to connect to MongoDB.")
#             return None
#         else: 
#             logging.debug('Connected to mongoDB successfully')
            

#         collection = db[collection_name]

        
#         bulk_operations = [
#             UpdateOne(
#                 {key: record[key] for key in unique_keys if key in record}, 
#                 {"$setOnInsert": record},
#                 upsert=True
#             )
#             for record in data
#         ]

#         result = None
#         if bulk_operations:
#             result = collection.bulk_write(bulk_operations, ordered=False)
#             logging.info(f"[bulk_upsert_mongodb]: {result.upserted_count} Document Inserted")
#             if result.upserted_count > 0:
#                 logging.info("MongoDB: Data inserted successfully!")
#             else: 
#                 logging.info("MongoDB: No new data to be inserted!")
#         return result
    
            
    
#     except Exception as e:
#         logging.error(f"MongoDB: Error in bulk upsert operation: {e}")
#         return None

#     finally:
#         if client:
#             client.close()
#             logging.debug("MongoDB: Client closed!") 



# def bulk_insert_mongodb(host: str,database_name: str, collection_name: str, 
#                         data: List[Dict[str, Any]], unique_keys: Optional[List[str]] ) -> None:
#     client = MongoClient(host)
#     db = client[database_name]
#     collection = db[collection_name]

#     # try:
#     #     index_fields = [(key, 1) for key in unique_keys]
#     #     collection.create_index(index_fields, unique=True)
#     #     logging.info(f"[bulk_insert_mongodb] Ensured unique index on {unique_keys}")
#     # except Exception as e:
#     #     logging.warning(f"[bulk_insert_mongodb] Index creation failed or already exists: {e}")

#     try:
#         result = collection.insert_many(data, ordered=False)
#         logging.info(f"[bulk_insert_mongodb] Inserted {len(result.inserted_ids)} documents.")
#     except BulkWriteError as e:
#         inserted = e.details.get("nInserted", 0)
#         skipped = len(e.details.get("writeErrors", []))
#         logging.warning(f"[bulk_insert_mongodb] Inserted {inserted}, skipped {skipped} duplicates.")
#     except Exception as e:
#         logging.error(f"[bulk_insert_mongodb] Unexpected error: {e}")
#     finally:
#         client.close()
#         logging.debug("[bulk_insert_mongodb] MongoDB client closed.")


# def debug_problematic_documents(data: List[Dict[str, Any]], output_path: str = "problematic_documents.json") -> None:
#     problematic = []

#     for i, doc in enumerate(data):
#         try:
#             BSON.encode(doc)  # attempt BSON serialization
#         except Exception as e:
#             logging.warning(f"[debug_mongo_doc] Document at index {i} is invalid: {e}")
#             problematic.append({"index": i, "error": str(e), "document": doc})

#     if problematic:
#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(problematic, f, ensure_ascii=False, indent=2, default=str)
#         logging.info(f"[debug_mongo_doc] Saved {len(problematic)} problematic documents to {output_path}")
#     else:
#         logging.info("[debug_mongo_doc] No problematic documents found.")


# def bulk_insert_mongodb(host: str, database_name: str, collection_name: str, 
#                         data: List[Dict[str, Any]], unique_keys: Optional[List[str]]) -> None:
#     client = MongoClient(host)
#     db = client[database_name]
#     collection = db[collection_name]

#     try:
#         result = collection.insert_many(data, ordered=False)
#         logging.info(f"[bulk_insert_mongodb] Inserted {len(result.inserted_ids)} documents.")
#     except Exception as e:
#         logging.error(f"[bulk_insert_mongodb] Unexpected error: {e}")
#         logging.info("[bulk_insert_mongodb] Attempting to log problematic documents...")
#         logging.debug(debug_problematic_documents(data))
#     finally:
#         client.close()
#         logging.debug("[bulk_insert_mongodb] MongoDB client closed.")

def bulk_insert_mongodb(
    host: str,
    database_name: str,
    collection_name: str,
    data: List[Dict[str, Any]],
    unique_keys: Optional[List[str]] = None
) -> None:
    """
    Inserts a batch of documents into MongoDB.
    If unique_keys are provided, they are used to build the _id field to enforce uniqueness.
    """
    client = MongoClient(host)
    db = client[database_name]
    collection = db[collection_name]

    # Set _id if primary key(s) are provided
    if unique_keys:
        data = [
            {**doc, "_id": doc.get(unique_keys[0])} if len(unique_keys) == 1
            else {**doc, "_id": "_".join(str(doc.get(k)) for k in unique_keys)}
            for doc in data
        ]

    try:
        result = collection.insert_many(data, ordered=False)
        logging.info(f"[bulk_insert_mongodb] Inserted {len(result.inserted_ids)} documents.")
    except BulkWriteError as e:
        inserted = e.details.get("nInserted", 0)
        skipped = len(e.details.get("writeErrors", []))
        logging.warning(f"[bulk_insert_mongodb] Inserted {inserted}, skipped {skipped} duplicates.")
    except Exception as e:
        logging.error(f"[bulk_insert_mongodb] Unexpected error: {e}")
    finally:
        client.close()
        logging.debug("[bulk_insert_mongodb] MongoDB client closed.")

        

def load_to_mongo(data: List[Dict], collection_key: str) -> None:
    """Loads data to MongoDB for a specified collection."""
    db_params_path = get_local_path(__file__,"params/mongodb_params.yaml")
    db_configs = load_yaml_file(__file__,db_params_path)

    host, db_name = get_mongo_connection_config(db_configs)
    collection_name, primary_keys = get_collection_config(db_configs, collection_key)

    bulk_insert_mongodb(host, db_name, collection_name, data, primary_keys)


def read_from_mongodb(host: str, db_name: str, collection_name: str) -> Optional[List[Dict]]:
    
    try:
        client, db = initialize_mongo_db(host, db_name)
        if client is None or db is None:
            logging.error("MongoDB: Failed to connect.")
            return None
        else:
            logging.debug("MongoDB: Connected successfully.")

        data = list(db[collection_name].find())
        logging.info(f"MongoDB: Loaded {len(data)} records from '{collection_name}'.")
        return data

    except Exception as e:
        logging.error(f"MongoDB: Error reading from collection '{collection_name}': {e}")
        return None

    finally:
        if 'client' in locals() and client:
            client.close()
            logging.debug("MongoDB: Client closed.")
            

def load_from_mongo(collection_key: str) -> Optional[List[Dict]]:
    """Loads data from MongoDB for a specified collection."""
    db_params_path = get_local_path(__file__, "params/mongodb_params.yaml")
    db_configs = load_yaml_file(__file__, db_params_path)

    host, db_name = get_mongo_connection_config(db_configs)
    collection_name, _ = get_collection_config(db_configs, collection_key)

    return read_from_mongodb(host, db_name, collection_name)



