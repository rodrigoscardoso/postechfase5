import pika
import json
import os
import subprocess
import uuid
import zipfile
from datetime import datetime
from src.models.video_job import db, VideoJob, JobStatus
from src.services.queue_service import get_rabbitmq_connection, publish_notification
from flask import current_app

def process_video_frames(job_id: int) -> bool:
    """Process video and extract frames."""
    try:
        # Get job from database
        job = VideoJob.query.get(job_id)
        if not job:
            print(f"Job {job_id} not found")
            return False
        
        # Update status to processing
        job.status = JobStatus.PROCESSING
        job.progress = 10
        db.session.commit()
        
        # Create temp directory for frames
        temp_dir = f"/app/storage/temp/{uuid.uuid4()}"
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extract frames using ffmpeg
            frame_pattern = os.path.join(temp_dir, "frame_%04d.png")
            
            cmd = [
                'ffmpeg',
                '-i', job.file_path,
                '-vf', 'fps=1',
                '-y',
                frame_pattern
            ]
            
            job.progress = 30
            db.session.commit()
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"FFmpeg error: {result.stderr}")
            
            job.progress = 70
            db.session.commit()
            
            # Count extracted frames
            frame_files = [f for f in os.listdir(temp_dir) if f.endswith('.png')]
            job.frame_count = len(frame_files)
            
            if len(frame_files) == 0:
                raise Exception("No frames were extracted from the video")
            
            # Create ZIP file
            output_dir = "/app/storage/outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            zip_filename = f"frames_{job.id}_{uuid.uuid4().hex[:8]}.zip"
            zip_path = os.path.join(output_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for frame_file in frame_files:
                    frame_path = os.path.join(temp_dir, frame_file)
                    zipf.write(frame_path, frame_file)
            
            job.progress = 90
            job.zip_file_path = zip_path
            db.session.commit()
            
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
            
            # Clean up original video file
            if os.path.exists(job.file_path):
                os.remove(job.file_path)
            
            # Update job status
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.completed_at = datetime.utcnow()
            db.session.commit()
            
            # Send notification
            message = f"Video processing completed! {job.frame_count} frames extracted from {job.original_filename}"
            publish_notification(job.user_id, job.id, message)
            
            print(f"Successfully processed job {job_id}: {job.frame_count} frames extracted")
            return True
            
        except Exception as e:
            # Clean up temp directory on error
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
            
    except Exception as e:
        # Update job status to failed
        job = VideoJob.query.get(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.session.commit()
            
            # Send error notification
            message = f"Video processing failed for {job.original_filename}: {str(e)}"
            publish_notification(job.user_id, job.id, message)
        
        print(f"Error processing job {job_id}: {e}")
        return False

def process_video_message(ch, method, properties, body):
    """Process video processing message from queue."""
    try:
        message = json.loads(body)
        job_id = message.get('job_id')
        
        if not job_id:
            print("Invalid message: missing job_id")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print(f"Processing video job {job_id}")
        
        # Process the video
        success = process_video_frames(job_id)
        
        if success:
            print(f"Successfully processed job {job_id}")
        else:
            print(f"Failed to process job {job_id}")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing message: {e}")
        # Reject message and requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_queue_consumer():
    """Start consuming messages from video processing queue."""
    print("Starting video processing queue consumer...")
    
    # Setup queues first
    from src.services.queue_service import setup_queues
    setup_queues()
    
    while True:
        try:
            connection = get_rabbitmq_connection()
            if not connection:
                print("Failed to connect to RabbitMQ, retrying in 5 seconds...")
                import time
                time.sleep(5)
                continue
            
            channel = connection.channel()
            channel.queue_declare(queue='video_processing', durable=True)
            
            # Set QoS to process one message at a time
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(
                queue='video_processing',
                on_message_callback=process_video_message
            )
            
            print("Waiting for video processing messages...")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            print("Stopping consumer...")
            break
        except Exception as e:
            print(f"Consumer error: {e}")
            import time
            time.sleep(5)

