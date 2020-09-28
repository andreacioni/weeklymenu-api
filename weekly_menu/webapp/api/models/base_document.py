from datetime import datetime

from .. import mongo

class BaseDocument(mongo.Document):

  offline_id = mongo.StringField(required=True, regex=r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
  
  owner = mongo.ReferenceField('User', required=True)

  creation_date = mongo.DateTimeField(required=True, default=datetime.utcnow)
  update_date = mongo.DateTimeField(required=True, default=datetime.utcnow)

  meta = {
    'allow_inheritance': True
  }
