#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from datamodule import app

CGIHandler().run(app)
