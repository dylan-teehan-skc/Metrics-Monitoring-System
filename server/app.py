from flask import Flask, jsonify, request, render_template, url_for
from database import SessionLocal, Monitor, MetricType, MetricValue
import os
from sqlalchemy.orm import joinedload
import logging
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = app.logger

@app.route('/')
def index():
    session = SessionLocal()
    try:
        # Query for available monitors and metrics
        monitors = session.query(Monitor).all()
        metrics = session.query(MetricType).all()

        # Extract unique monitor names and metric names
        monitor_names = {monitor.name for monitor in monitors}
        metric_names = {metric.name for metric in metrics}

        return render_template('index.html', monitor_names=monitor_names, metric_names=metric_names)
    except Exception as e:
        logger.error(f"Error in index: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@app.route('/monitors', methods=['GET'])
def get_monitors():
    session = SessionLocal()
    try:
        monitors = session.query(Monitor).all()
        return jsonify([{
            "id": monitor.id,
            "name": monitor.name
        } for monitor in monitors])
    except Exception as e:
        logger.error(f"Error in get_monitors: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@app.route('/monitors', methods=['POST'])
def create_monitor():
    session = SessionLocal()
    try:
        data = request.json
        logger.debug(f"Creating monitor with data: {data}")
        new_monitor = Monitor(name=data['name'])
        session.add(new_monitor)
        session.commit()
        return jsonify({
            "id": new_monitor.id,
            "name": new_monitor.name
        }), 201
    except Exception as e:
        session.rollback()
        logger.error(f"Error in create_monitor: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@app.route('/metrics', methods=['POST'])
def post_metrics():
    session = SessionLocal()
    try:
        data = request.json
        logger.info(f"Received metrics data: {data}")

        if not isinstance(data, dict):
            raise ValueError("Invalid data format: expected dictionary")
        if 'data' not in data:
            raise ValueError("Missing 'data' key in request")

        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        metrics_data = data['data']

        for monitor_name, metrics in metrics_data.items():
            logger.debug(f"Processing monitor: {monitor_name}")

            # Find or create monitor
            monitor = session.query(Monitor).filter_by(name=monitor_name).first()
            if not monitor:
                logger.debug(f"Creating new monitor: {monitor_name}")
                monitor = Monitor(name=monitor_name)
                session.add(monitor)
                session.commit()

            if not isinstance(metrics, dict):
                logger.warning(f"Skipping invalid metrics format for {monitor_name}: {metrics}")
                continue

            for metric_name, metric_data in metrics.items():
                logger.debug(f"Processing metric: {metric_name} = {metric_data}")

                try:
                    # Extract value and unit
                    if isinstance(metric_data, dict):
                        value = metric_data.get('value')
                        unit = metric_data.get('unit', 'unknown')
                    else:
                        value = metric_data
                        unit = 'unknown'

                    # Validate and convert value
                    if value is None:
                        logger.warning(f"Skipping metric {metric_name}: no value provided")
                        continue

                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        logger.warning(f"Skipping metric {metric_name}: invalid value {value}")
                        continue

                    # Find or create metric type
                    metric_type = session.query(MetricType).filter_by(
                        name=metric_name,
                        monitor_id=monitor.id
                    ).first()

                    if not metric_type:
                        logger.debug(f"Creating new metric type: {metric_name}")
                        metric_type = MetricType(
                            name=metric_name,
                            unit=unit,
                            monitor=monitor
                        )
                        session.add(metric_type)
                        session.commit()

                    # Create metric value
                    metric_value = MetricValue(
                        metric_type=metric_type,
                        value=value,
                        timestamp=timestamp
                    )
                    session.add(metric_value)
                    logger.debug(f"Added metric value: {metric_name}={value} {unit}")

                except Exception as e:
                    logger.error(f"Error processing metric {metric_name}: {str(e)}")
                    continue

        session.commit()
        return jsonify({"message": "Metrics saved successfully"}), 201

    except Exception as e:
        session.rollback()
        logger.error(f"Error processing metrics: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route('/dashboard', methods=['GET'])
def dashboard():
    session = SessionLocal()
    monitor_type = request.args.get('monitor')
    metric_name = request.args.get('metric')
    try:
        # Filter metrics based on user selection
        query = session.query(MetricValue).join(MetricType).join(Monitor)
        if monitor_type:
            query = query.filter(Monitor.name == monitor_type)
        if metric_name:
            query = query.filter(MetricType.name == metric_name)
        
        metrics = query.options(
            joinedload(MetricValue.metric_type).joinedload(MetricType.monitor)
        ).all()
        
        return render_template('dashboard.html', metrics=metrics, monitor_type=monitor_type, metric_name=metric_name)
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()