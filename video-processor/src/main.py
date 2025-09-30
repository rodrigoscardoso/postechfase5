import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from src.models.video_job import db
from src.routes.video import video_bp
from src.routes.health import health_bp
from src.services.queue_consumer import start_queue_consumer
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = 'video_processor_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://fiapx_user:fiapx_password@localhost:5432/fiapx_videos')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/app/storage/uploads'
app.config['OUTPUT_FOLDER'] = '/app/storage/outputs'

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(video_bp, url_prefix='/api/video')
app.register_blueprint(health_bp, url_prefix='/api')

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create storage directories
    os.makedirs('/app/storage/uploads', exist_ok=True)
    os.makedirs('/app/storage/outputs', exist_ok=True)
    os.makedirs('/app/storage/temp', exist_ok=True)
    
    with app.app_context():
        db.create_all()
    
    # Start queue consumer in background thread
    consumer_thread = threading.Thread(target=start_queue_consumer, daemon=True)
    consumer_thread.start()
    
    app.run(host='0.0.0.0', port=8000, debug=False)
