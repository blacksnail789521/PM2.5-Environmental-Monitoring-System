#!/usr/bin/python3
from wsgiref.handlers import CGIHandler
from datamodule import app

CGIHandler().run(app)
