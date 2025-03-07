from flask import Blueprint, jsonify, request
from database import SessionLocal, Monitor, MetricType, MetricValue
import logging
from datetime import datetime

metrics_bp = Blueprint('metrics', __name__)
logger = logging.getLogger(__name__)

@metrics_bp.route('/v1.0/metrics', methods=['POST'])
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
        system_id = data.get('metadata', {}).get('system_id')

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
                        timestamp=timestamp,
                        system_id=system_id
                    )
                    session.add(metric_value)
                    logger.debug(f"Added metric value: {metric_name}={value} {unit} (system_id: {system_id})")

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