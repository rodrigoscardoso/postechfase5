from flask import Blueprint, request, jsonify, send_file, current_app
from src.models.video_job import db, VideoJob, JobStatus
from src.services.queue_service import publish_video_job
import os
import uuid
from werkzeug.utils import secure_filename
import requests

video_bp = Blueprint('video', __name__)

ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def verify_token(token):
    """Verify token with auth service."""
    try:
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
        response = requests.post(f'{auth_service_url}/api/auth/verify', 
                               json={'token': token}, 
                               timeout=5)
        if response.status_code == 200:
            return response.json().get('user')
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def token_required(f):
    """Decorator to require valid JWT token."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        user = verify_token(token)
        if not user:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        return f(user, *args, **kwargs)
    return decorated

@video_bp.route('/upload', methods=['POST'])
@token_required
def upload_video(current_user):
    """Upload video for processing."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Supported: mp4, avi, mov, mkv, wmv, flv, webm'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Create video job record
        video_job = VideoJob(
            user_id=current_user['id'],
            original_filename=filename,
            file_path=file_path,
            status=JobStatus.PENDING
        )
        
        db.session.add(video_job)
        db.session.commit()
        
        # Publish job to queue
        publish_video_job(video_job.id)
        
        return jsonify({
            'message': 'Video uploaded successfully and queued for processing',
            'job_id': video_job.id,
            'status': video_job.status.value
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@video_bp.route('/jobs', methods=['GET'])
@token_required
def list_jobs(current_user):
    """List user's video processing jobs."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        jobs = VideoJob.query.filter_by(user_id=current_user['id'])\
                            .order_by(VideoJob.created_at.desc())\
                            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs.items],
            'total': jobs.total,
            'pages': jobs.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/jobs/<int:job_id>', methods=['GET'])
@token_required
def get_job(current_user, job_id):
    """Get specific job details."""
    try:
        job = VideoJob.query.filter_by(id=job_id, user_id=current_user['id']).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({'job': job.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/jobs/<int:job_id>/download', methods=['GET'])
@token_required
def download_result(current_user, job_id):
    """Download processed video result."""
    try:
        job = VideoJob.query.filter_by(id=job_id, user_id=current_user['id']).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status != JobStatus.COMPLETED:
            return jsonify({'error': 'Job not completed yet'}), 400
        
        if not job.zip_file_path or not os.path.exists(job.zip_file_path):
            return jsonify({'error': 'Result file not found'}), 404
        
        return send_file(
            job.zip_file_path,
            as_attachment=True,
            download_name=f"frames_{job.original_filename}_{job.id}.zip"
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get user's processing statistics."""
    try:
        total_jobs = VideoJob.query.filter_by(user_id=current_user['id']).count()
        completed_jobs = VideoJob.query.filter_by(user_id=current_user['id'], status=JobStatus.COMPLETED).count()
        processing_jobs = VideoJob.query.filter_by(user_id=current_user['id'], status=JobStatus.PROCESSING).count()
        failed_jobs = VideoJob.query.filter_by(user_id=current_user['id'], status=JobStatus.FAILED).count()
        
        return jsonify({
            'total_jobs': total_jobs,
            'completed_jobs': completed_jobs,
            'processing_jobs': processing_jobs,
            'failed_jobs': failed_jobs,
            'success_rate': round((completed_jobs / total_jobs * 100) if total_jobs > 0 else 0, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

