from flask import Blueprint, jsonify, request
from database import SessionLocal, Monitor, MetricType, MetricValue
import logging
from datetime import datetime

gauge_bp = Blueprint('gauge', __name__)
logger = logging.getLogger(__name__)

@gauge_bp.route('/v1.0/view/gauge/<monitor_name>/<metric_name>', methods=['GET'])
def view_gauge(monitor_name, metric_name):
    session = SessionLocal()
    try:
        # Get the initial data
        query = session.query(MetricValue)\
            .join(MetricType)\
            .join(Monitor)\
            .filter(Monitor.name == monitor_name)\
            .filter(MetricType.name == metric_name)\
            .order_by(MetricValue.timestamp.desc())\
            .limit(1)

        latest_metric = query.first()

        if not latest_metric:
            return "No data found", 404

        metric_type = latest_metric.metric_type
        value = latest_metric.value
        unit = metric_type.unit
        min_val = 0
        max_val = 100

        # Determine appropriate min/max values
        if unit.lower() in ['%', 'percent', 'percentage']:
            min_val = 0
            max_val = 100
        else:
            historical_max = session.query(MetricValue)\
                .join(MetricType)\
                .filter(MetricType.id == metric_type.id)\
                .order_by(MetricValue.value.desc())\
                .first()
            if historical_max:
                max_val = historical_max.value * 1.2  # 20% buffer

        # Convert initial data into JSON (used for JS)
        initial_data = {
            "monitor": monitor_name,
            "metric": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": latest_metric.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "min": min_val,
            "max": max_val
        }

        # HTML with JavaScript to update the gauge dynamically
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{monitor_name} - {metric_name} Gauge</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <h1>{monitor_name} - {metric_name} ({unit})</h1>
            <div id="gauge-container"></div>
            <p>Last updated: <span id="last-updated">{initial_data['timestamp']}</span></p>

            <script>
                let gaugeData = {initial_data};  // Initial data

                function createGauge(data) {{
                    let fig = {{
                        data: [{{
                            type: "indicator",
                            mode: "gauge+number",
                            value: data.value,
                            title: {{ text: data.monitor + " - " + data.metric }},
                            gauge: {{
                                axis: {{ range: [data.min, data.max] }},
                                bar: {{ color: "darkblue" }},
                                steps: [
                                    {{ range: [data.min, data.max * 0.6], color: "lightgreen" }},
                                    {{ range: [data.max * 0.6, data.max * 0.8], color: "yellow" }},
                                    {{ range: [data.max * 0.8, data.max], color: "red" }}
                                ]
                            }}
                        }}]
                    }};
                    Plotly.newPlot("gauge-container", fig.data, {{}});
                }}

                function updateGauge() {{
                    fetch("/v1.0/gauge/{monitor_name}/{metric_name}")
                        .then(response => response.json())
                        .then(data => {{
                            if (data.error) {{
                                console.error("Error fetching data:", data.error);
                                return;
                            }}
                            let update = {{
                                value: [data.value]
                            }};
                            Plotly.restyle("gauge-container", update);
                            document.getElementById("last-updated").innerText = data.timestamp;
                        }})
                        .catch(error => console.error("Error updating gauge:", error));
                }}

                createGauge(gaugeData);  // Create the initial gauge

                setInterval(updateGauge, 5000);  // Auto-update every 5 seconds
            </script>
        </body>
        </html>
        """

    except Exception as e:
        return f"Error displaying gauge: {str(e)}", 500
    finally:
        session.close()

@gauge_bp.route('/v1.0/gauge/<monitor_name>/<metric_name>', methods=['GET'])
def get_gauge_data(monitor_name, metric_name):
    session = SessionLocal()
    try:
        # Get the latest metric value for the specified monitor and metric
        query = session.query(MetricValue)\
            .join(MetricType)\
            .join(Monitor)\
            .filter(Monitor.name == monitor_name)\
            .filter(MetricType.name == metric_name)\
            .order_by(MetricValue.timestamp.desc())\
            .limit(1)

        latest_metric = query.first()

        if not latest_metric:
            return jsonify({"error": f"No data found for {monitor_name}/{metric_name}"}), 404

        # Get the metric type to retrieve unit and other metadata
        metric_type = latest_metric.metric_type

        # Prepare the response
        response = {
            "monitor": monitor_name,
            "metric": metric_name,
            "value": latest_metric.value,
            "unit": metric_type.unit,
            "timestamp": latest_metric.timestamp,
            # Default gauge boundaries
            "min": 0,
            "max": 100
        }

        # If the unit is percentage, we know the range is 0-100
        if metric_type.unit.lower() in ['%', 'percent', 'percentage']:
            response["min"] = 0
            response["max"] = 100
        else:
            # For other metrics, calculate based on historical data
            historical_max = session.query(MetricValue)\
                .join(MetricType)\
                .filter(MetricType.id == metric_type.id)\
                .order_by(MetricValue.value.desc())\
                .first()

            if historical_max:
                # Set max to slightly above the historical maximum
                response["max"] = historical_max.value * 1.2  # 20% buffer

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error retrieving gauge data: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@gauge_bp.route('/v1.0/gauge', methods=['GET'])
def get_available_gauges():
    """Return a list of available monitor/metric combinations for gauge visualization"""
    session = SessionLocal()
    try:
        # Get all monitor/metric combinations that have data
        result = session.query(Monitor.name.label('monitor'),
                              MetricType.name.label('metric'),
                              MetricType.unit)\
            .join(MetricType)\
            .join(MetricValue)\
            .distinct()\
            .all()

        gauges = []
        for row in result:
            gauges.append({
                "monitor": row.monitor,
                "metric": row.metric,
                "unit": row.unit
            })

        return jsonify({"gauges": gauges})

    except Exception as e:
        logger.error(f"Error retrieving available gauges: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()