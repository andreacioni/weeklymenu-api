import os

JSON_SORT_KEYS=os.getenv('JSON_SORT_KEYS',False)

#MongoDb
MONGODB_SETTINGS={
    'host': os.getenv('MONGO_HOST', None)
}

#JWT
SECRET_KEY=os.getenv('SECRET_KEY','NONE')
JWT_ACCESS_TOKEN_EXPIRES=os.getenv('JWT_ACCESS_TOKEN_EXPIRES',3600)

#Log
LOG_LEVEL=os.getenv('LOG_LEVEL', None)
LOG_FILE=os.getenv('LOG_FILE', None)
LOG_MAX_SIZE = os.getenv('LOG_MAX_SIZE', 10000000)
LOG_BACKUP_COUNT = os.getenv('LOG_BACKUP_COUNT', 3)