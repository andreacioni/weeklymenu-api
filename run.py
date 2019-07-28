import os
import argparse
import logging

from flask_mongoengine import MongoEngine

from weekly_menu import webapp, name as app_name, version as app_version

LOG_MAX_SIZE = 10000000
LOG_BACKUP_COUNT = 3

#Parsing arguments
parser = argparse.ArgumentParser('{} - v.{}'.format(app_name, app_version))
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

#Setup and run application
app = webapp.create_app('config')
app.run(host=app.config['API_HOST'], port=app.config['API_PORT'])