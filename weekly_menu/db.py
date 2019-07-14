import logging
import os
from pymongo import MongoClient

class MongoDB(object):
    _logger = logging.getLogger(__name__)
    _mongo_client = None

    def __init__(self, url: str):
        self._logger.info("Connecting to MongoDD instance at: %s", url)
        self._mongo_client = MongoClient(url)
        
        self.test_connection()  
    
    def test_connection(self) -> bool:
        self._mongo_client.admin.command('ismaster')

    def get_client(self) -> MongoClient:
        return self._mongo_client