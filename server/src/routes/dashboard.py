from flask import Blueprint, jsonify, render_template, request
from database import SessionLocal, MetricValue, MetricType, Monitor
from sqlalchemy.orm import joinedload
import logging

dashboard_bp = Blueprint('dashboard', __name__)
logger = logging.getLogger(__name__)

@dashboard_bp.route('/dashboard', methods=['GET'])
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

        # Get the unit from the first metric if available
        unit = metrics[0].metric_type.unit if metrics else ''

        return render_template(
            'dashboard.html',
            metrics=metrics,
            monitor_type=monitor_type,
            metric_name=metric_name,
            unit=unit
        )
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@dashboard_bp.route('/api/metric/latest', methods=['GET'])
def latest_metric():
    session = SessionLocal()
    monitor_type = request.args.get('monitor')
    metric_name = request.args.get('metric')
    try:
        # Fetch the latest metric value
        metric = session.query(MetricValue).join(MetricType).join(Monitor) \
            .filter(Monitor.name == monitor_type, MetricType.name == metric_name) \
            .order_by(MetricValue.timestamp.desc()).first()

        if metric:
            return jsonify({'value': metric.value, 'unit': metric.metric_type.unit})
        else:
            return jsonify({'error': 'Metric not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching latest metric: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@dashboard_bp.route('/api/metric/minmax', methods=['GET'])
def minmax_metric():
    session = SessionLocal()
    monitor_type = request.args.get('monitor')
    metric_name = request.args.get('metric')
    try:
        # Fetch the last 12 trading weeks' data
        metrics = session.query(MetricValue).join(MetricType).join(Monitor) \
            .filter(Monitor.name == monitor_type, MetricType.name == metric_name) \
            .order_by(MetricValue.timestamp.desc()).limit(12 * 5 * 7).all()  # Assuming 5 trading days per week

        if metrics:
            values = [metric.value for metric in metrics]
            min_value = min(values)
            max_value = max(values)
            return jsonify({'min': min_value, 'max': max_value})
        else:
            return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        logger.error(f"Error fetching min/max metric: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()
