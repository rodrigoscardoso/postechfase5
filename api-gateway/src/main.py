import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from src.routes.gateway import gateway_bp
import redis

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = 'api_gateway_secret_key'
app.config['AUTH_SERVICE_URL'] = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8000')
app.config['VIDEO_PROCESSOR_URL'] = os.getenv('VIDEO_PROCESSOR_URL', 'http://video-processor:8000')

# Initialize Redis for caching
try:
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379')
    app.config['REDIS_CLIENT'] = redis.from_url(redis_url)
    app.config['REDIS_CLIENT'].ping()
    print("Redis connection established")
except Exception as e:
    print(f"Redis connection failed: {e}")
    app.config['REDIS_CLIENT'] = None

# Register blueprints
app.register_blueprint(gateway_bp, url_prefix='/api')

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({'message': 'FIAP X Video Processor API Gateway', 'version': '1.0.0'}), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'version': '1.0.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
