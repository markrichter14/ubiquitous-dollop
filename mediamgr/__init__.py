from flask import Flask
from mediamgr.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from mediamgr import routes
