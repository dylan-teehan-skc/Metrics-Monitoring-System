from flask import Blueprint, jsonify, render_template
from database import SessionLocal, Monitor
import logging

monitors_bp = Blueprint('monitors', __name__)
logger = logging.getLogger(__name__)

@monitors_bp.route('/monitors', methods=['GET'])
def get_monitors():
    session = SessionLocal()
    try:
        monitors = session.query(Monitor).all()
        return render_template('monitors.html', monitors=monitors)
    except Exception as e:
        logger.error(f"Error in get_monitors: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()

@monitors_bp.route('/monitors', methods=['POST'])
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