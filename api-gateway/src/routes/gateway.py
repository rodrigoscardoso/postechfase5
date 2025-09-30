from flask import Blueprint, request, jsonify, current_app
import requests
import json

gateway_bp = Blueprint('gateway', __name__)

def forward_request(service_url, endpoint, method='GET', data=None, files=None, headers=None):
    """Forward request to microservice."""
    try:
        url = f"{service_url}{endpoint}"
        
        # Prepare headers
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Forward Authorization header if present
        auth_header = request.headers.get('Authorization')
        if auth_header:
            request_headers['Authorization'] = auth_header
        
        # Make request based on method
        if method == 'GET':
            response = requests.get(url, headers=request_headers, timeout=30)
        elif method == 'POST':
            if files:
                response = requests.post(url, files=files, data=data, headers=request_headers, timeout=30)
            else:
                if data:
                    request_headers['Content-Type'] = 'application/json'
                response = requests.post(url, json=data, headers=request_headers, timeout=30)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=request_headers, timeout=30)
        elif method == 'DELETE':
            response = requests.delete(url, headers=request_headers, timeout=30)
        else:
            return {'error': 'Unsupported method'}, 405
        
        return response.json() if response.content else {}, response.status_code
        
    except requests.exceptions.Timeout:
        return {'error': 'Service timeout'}, 504
    except requests.exceptions.ConnectionError:
        return {'error': 'Service unavailable'}, 503
    except Exception as e:
        return {'error': f'Gateway error: {str(e)}'}, 500

# Authentication routes
@gateway_bp.route('/auth/register', methods=['POST'])
def register():
    """Forward registration to auth service."""
    data = request.get_json()
    result, status = forward_request(
        current_app.config['AUTH_SERVICE_URL'],
        '/api/auth/register',
        method='POST',
        data=data
    )
    return jsonify(result), status

@gateway_bp.route('/auth/login', methods=['POST'])
def login():
    """Forward login to auth service."""
    data = request.get_json()
    result, status = forward_request(
        current_app.config['AUTH_SERVICE_URL'],
        '/api/auth/login',
        method='POST',
        data=data
    )
    return jsonify(result), status

@gateway_bp.route('/auth/verify', methods=['POST'])
def verify_token():
    """Forward token verification to auth service."""
    data = request.get_json()
    result, status = forward_request(
        current_app.config['AUTH_SERVICE_URL'],
        '/api/auth/verify',
        method='POST',
        data=data
    )
    return jsonify(result), status

@gateway_bp.route('/auth/profile', methods=['GET'])
def get_profile():
    """Forward profile request to auth service."""
    result, status = forward_request(
        current_app.config['AUTH_SERVICE_URL'],
        '/api/auth/profile',
        method='GET'
    )
    return jsonify(result), status

# Video processing routes
@gateway_bp.route('/video/upload', methods=['POST'])
def upload_video():
    """Forward video upload to video processor service."""
    try:
        # Handle file upload
        files = {}
        if 'video' in request.files:
            files['video'] = request.files['video']
        
        result, status = forward_request(
            current_app.config['VIDEO_PROCESSOR_URL'],
            '/api/video/upload',
            method='POST',
            files=files
        )
        return jsonify(result), status
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gateway_bp.route('/video/jobs', methods=['GET'])
def list_jobs():
    """Forward jobs list request to video processor service."""
    # Forward query parameters
    query_params = request.args.to_dict()
    endpoint = '/api/video/jobs'
    if query_params:
        query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
        endpoint += f"?{query_string}"
    
    result, status = forward_request(
        current_app.config['VIDEO_PROCESSOR_URL'],
        endpoint,
        method='GET'
    )
    return jsonify(result), status

@gateway_bp.route('/video/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Forward job details request to video processor service."""
    result, status = forward_request(
        current_app.config['VIDEO_PROCESSOR_URL'],
        f'/api/video/jobs/{job_id}',
        method='GET'
    )
    return jsonify(result), status

@gateway_bp.route('/video/jobs/<int:job_id>/download', methods=['GET'])
def download_result(job_id):
    """Forward download request to video processor service."""
    try:
        url = f"{current_app.config['VIDEO_PROCESSOR_URL']}/api/video/jobs/{job_id}/download"
        
        # Forward Authorization header
        headers = {}
        auth_header = request.headers.get('Authorization')
        if auth_header:
            headers['Authorization'] = auth_header
        
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            # Stream the file response
            from flask import Response
            return Response(
                response.iter_content(chunk_size=8192),
                content_type=response.headers.get('Content-Type'),
                headers={
                    'Content-Disposition': response.headers.get('Content-Disposition'),
                    'Content-Length': response.headers.get('Content-Length')
                }
            )
        else:
            return jsonify(response.json() if response.content else {'error': 'Download failed'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@gateway_bp.route('/video/stats', methods=['GET'])
def get_stats():
    """Forward stats request to video processor service."""
    result, status = forward_request(
        current_app.config['VIDEO_PROCESSOR_URL'],
        '/api/video/stats',
        method='GET'
    )
    return jsonify(result), status

# Health check aggregation
@gateway_bp.route('/health/all', methods=['GET'])
def health_check_all():
    """Check health of all services."""
    services = {
        'auth-service': current_app.config['AUTH_SERVICE_URL'],
        'video-processor': current_app.config['VIDEO_PROCESSOR_URL']
    }
    
    health_status = {}
    overall_healthy = True
    
    for service_name, service_url in services.items():
        try:
            result, status = forward_request(service_url, '/api/health', method='GET')
            health_status[service_name] = {
                'status': 'healthy' if status == 200 else 'unhealthy',
                'details': result
            }
            if status != 200:
                overall_healthy = False
        except Exception as e:
            health_status[service_name] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            overall_healthy = False
    
    return jsonify({
        'overall_status': 'healthy' if overall_healthy else 'unhealthy',
        'services': health_status
    }), 200 if overall_healthy else 503

