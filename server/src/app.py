import os
from flask import Flask
from routes.monitors import monitors_bp
from routes.metrics import metrics_bp
from routes.dashboard import dashboard_bp
from routes.index import index_bp
from routes.gauge import gauge_bp 
import logging

# Initialize Flask app
app = Flask(__name__)

# Register Blueprints
app.register_blueprint(index_bp)
app.register_blueprint(monitors_bp)
app.register_blueprint(metrics_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(gauge_bp) 

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = app.logger