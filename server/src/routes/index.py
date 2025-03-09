from flask import Blueprint, render_template, jsonify, request
from database import SessionLocal, Monitor
import logging
from sqlalchemy.orm import joinedload
import time

index_bp = Blueprint('index', __name__)
logger = logging.getLogger(__name__)

# In-memory storage for shutdown status
shutdown_status = {
    "shutdown_requested_at": None,
    "client_id": None
}

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

@index_bp.route('/api/shutdown-client', methods=['POST'])
def shutdown_client():
    """Request client shutdown"""
    try:
        client_id = request.args.get('client_id')  # Optional client ID
        
        # Set shutdown status
        shutdown_status["shutdown_requested_at"] = time.time()
        shutdown_status["client_id"] = client_id
        
        logger.info(f"Shutdown requested for client {client_id if client_id else 'all'}")
        return jsonify({"success": True, "message": "Shutdown request queued"}), 200
        
    except Exception as e:
        logger.error(f"Error requesting shutdown: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@index_bp.route('/api/cancel-shutdown', methods=['POST'])
def cancel_shutdown():
    """Cancel a pending shutdown request"""
    try:
        client_id = request.args.get('client_id')
        logger.info(f"Received shutdown cancellation request from client {client_id}")
        logger.info(f"Current shutdown status: {shutdown_status}")
        
        # Only cancel if it matches the pending shutdown
        if shutdown_status["client_id"] == client_id or shutdown_status["client_id"] is None:
            shutdown_status["shutdown_requested_at"] = None
            shutdown_status["client_id"] = None
            logger.info(f"Shutdown cancelled for client {client_id if client_id else 'all'}")
        else:
            logger.info(f"Ignoring cancellation - client ID mismatch (request: {client_id}, pending: {shutdown_status['client_id']})")
            
        logger.info(f"Updated shutdown status: {shutdown_status}")
        return jsonify({"success": True, "message": "Shutdown cancelled"}), 200
        
    except Exception as e:
        logger.error(f"Error cancelling shutdown: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@index_bp.route('/api/check-shutdown', methods=['GET'])
def check_shutdown():
    try:
        # Get the last check timestamp from the request
        last_check = float(request.args.get('last_check', 0))
        
        # Check if shutdown was requested after the last check
        should_shutdown = (shutdown_status["shutdown_requested_at"] is not None and 
                         shutdown_status["shutdown_requested_at"] > last_check)
        
        if should_shutdown:
            # Reset the timestamp after sending
            shutdown_status["shutdown_requested_at"] = None
            logger.info("Shutdown request processed")
            
        return jsonify({
            "should_shutdown": should_shutdown,
            "server_time": time.time()
        })
    except Exception as e:
        logger.error(f"Error in check_shutdown: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500