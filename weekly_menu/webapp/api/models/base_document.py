from .. import mongo

class BaseDocument(mongo.Document):

  offline_id = mongo.StringField(required=True)
  
  owner = mongo.ReferenceField('User', required=True)

  meta = {
    'allow_inheritance': True
  }
