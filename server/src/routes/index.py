from flask import Blueprint, render_template, jsonify
from database import SessionLocal, Monitor
import logging
from sqlalchemy.orm import joinedload

index_bp = Blueprint('index', __name__)
logger = logging.getLogger(__name__)

@index_bp.route('/')
def index():
    session = SessionLocal()
    try:
        # Query for monitors and their associated metric types
        monitors = session.query(Monitor).options(
            joinedload(Monitor.metric_types)
        ).all()

        # Create a structured dictionary of monitors and their metrics
        metrics_data = {}
        monitor_names = set()

        for monitor in monitors:
            monitor_names.add(monitor.name)
            metrics_data[monitor.name] = [metric_type.name for metric_type in monitor.metric_types]

        return render_template('index.html',
                               monitor_names=sorted(monitor_names),
                               metrics_data=metrics_data)
    except Exception as e:
        logger.error(f"Error in index: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()