from datetime import datetime

from .. import mongo

class BaseDocument(mongo.Document):

  offline_id = mongo.StringField(required=True, regex=r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
  
  owner = mongo.ReferenceField('User', required=True)

  insert_timestamp = mongo.LongField(required=True, default=lambda: int(datetime.utcnow().timestamp()*1000))
  update_timestamp = mongo.LongField(required=True, default=lambda: int(datetime.utcnow().timestamp()*1000))

  meta = {
    'allow_inheritance': True
  }
