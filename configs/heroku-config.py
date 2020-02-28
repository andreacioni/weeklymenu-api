import os

#Flask
DEBUG=os.getenv('DEBUG', False)

API_HOST=os.getenv('API_HOST','localhost')
API_PORT=os.getenv('API_PORT',8080)

JSON_SORT_KEYS=os.getenv('JSON_SORT_KEYS',False)

#MongoDb
MONGODB_SETTINGS={
    'host': os.getenv('MONGO_HOST', 'mongomock://localhost:27017/test?socketTimeoutMS=1000')
}

#JWT
SECRET_KEY=os.getenv('SECRET_KEY','NONE')