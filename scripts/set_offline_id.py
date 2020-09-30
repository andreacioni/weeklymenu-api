import os
import ssl
import argparse
import pymongo
import bson
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('mongo_url',
                    help='URL')
parser.add_argument('db_name',
                    help='Database name')
parser.add_argument('--user',
                    default='everyone',
                    help='Filter by owner')
args = parser.parse_args()

client = pymongo.MongoClient(args.mongo_url, ssl_cert_reqs=ssl.CERT_NONE)
db = client.get_database(args.db_name)

apply_to = ['shopping_lists', 'recipes', 'menu', 'ingredients']

for coll_name in apply_to:
  print('Setting offline_id to:', coll_name, 'owner:', args.user)

  if(args.user == 'everyone'):
    documents = db[coll_name].find({'offline_id': None})
  else:
    documents = db[coll_name].find({'offline_id': None, 'owner': bson.ObjectId(args.user)})

  for doc in documents:
    print('Update doc', doc['_id'])
    db[coll_name].update_one({'_id': doc['_id']}, {'$set': {'offline_id': str(uuid.uuid4())}})
    print('Updated document', doc['_id'])


