import os
import argparse
import logging

from weekly_menu import app, db, api

LOG_MAX_SIZE = 10000000
LOG_BACKUP_COUNT = 3

#Parsing arguments
parser = argparse.ArgumentParser('{} - v.{}'.format(app.name, app.version))
parser.add_argument('host',
                    help='host')
parser.add_argument('port',
                    type=int,
                    help='host')
parser.add_argument('--mongodb_uri',
                    required=True,
                    help='the uri of the MongoDB database')
parser.add_argument('--log_file',
                    default=None,
                    help='if defined, indicates the file used by the application to log')
parser.add_argument('-l', '--log_level',
                    metavar='log_level',
                    default='WARN',
                    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                    help='file containing the configuration for autobot istance')

args = parser.parse_args()

# Sutup logger
if args.log_file is None:
    logging.basicConfig(
        level=logging.getLevelName(args.log_level)
    )
else:
    logging.basicConfig(
        handlers=[logging.handlers.RotatingFileHandler(args.log_file, maxBytes=LOG_MAX_SIZE, backupCount=LOG_BACKUP_COUNT)], 
        level=logging.getLevelName(args.log_level)
    )

#Setup connection to MongoDB
db.connect(args.mongodb_uri)

#Setup and serve API
api.serve(args.host, args.port, False)