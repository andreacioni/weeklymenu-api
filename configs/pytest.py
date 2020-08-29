#Flask
DEBUG=False

API_HOST='localhost'
API_PORT=8080

JSON_SORT_KEYS=False
JWT_ACCESS_TOKEN_EXPIRES=60

#MongoDb
MONGODB_SETTINGS={
    'host': 'mongomock://localhost:27017/test?socketTimeoutMS=1000'
}

#JWT
SECRET_KEY='NONE'