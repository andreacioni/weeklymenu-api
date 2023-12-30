import logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, jsonify, json

_logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def create_module(app: Flask):
  scheduler.add_job(log, 'interval', minutes=1)

  app.before_first_request(_start_scheduler)
  app.teardown_appcontext(_stop_scheduler)

def log():
  _logger.info("TEST")

def _start_scheduler(*kargs, **kwargs):
  _logger.info("scheduler starting")
  scheduler.start()

def _stop_scheduler(*kargs, **kwargs):
  _logger.info("scheduler stopping")
  scheduler.shutdown()