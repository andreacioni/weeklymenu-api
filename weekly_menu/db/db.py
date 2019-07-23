import logging
import os
from pymongo import MongoClient

logger = logging.getLogger(__name__)
mongo_client = None

def connect(url: str):
    global mongo_client
    logger.debug("Connecting to MongoDD instance at: %s", url)
    mongo_client = MongoClient(url)
    test_connection()
    logger.info("Connected to MongoDD instance")

def test_connection() -> bool:
    global mongo_client
    try:
        mongo_client.admin.command('ismaster')
        return True
    except Exception as e:
        logger.error(e)
        return False

def get_client() -> MongoClient:
    global mongo_client
    return mongo_client