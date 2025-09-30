from flask import Blueprint, jsonify
from src.models.video_job import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'unhealthy',
        'service': 'video-processor',
        'database': db_status,
        'version': '1.0.0'
    }), 200 if db_status == 'healthy' else 503

