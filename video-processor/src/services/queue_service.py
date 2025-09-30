import pika
import json
import os
from typing import Optional

def get_rabbitmq_connection():
    """Get RabbitMQ connection."""
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://fiapx_user:fiapx_password@localhost:5672/')
    
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        return connection
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None

def setup_queues():
    """Setup RabbitMQ queues."""
    connection = get_rabbitmq_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        # Declare video processing queue
        channel.queue_declare(queue='video_processing', durable=True)
        
        # Declare notification queue
        channel.queue_declare(queue='notifications', durable=True)
        
        connection.close()
        return True
    except Exception as e:
        print(f"Error setting up queues: {e}")
        return False

def publish_video_job(job_id: int) -> bool:
    """Publish video processing job to queue."""
    connection = get_rabbitmq_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        message = {
            'job_id': job_id,
            'action': 'process_video'
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='video_processing',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        connection.close()
        print(f"Published video job {job_id} to queue")
        return True
    except Exception as e:
        print(f"Error publishing video job: {e}")
        return False

def publish_notification(user_id: int, job_id: int, message: str, notification_type: str = 'email') -> bool:
    """Publish notification to queue."""
    connection = get_rabbitmq_connection()
    if not connection:
        return False
    
    try:
        channel = connection.channel()
        
        notification = {
            'user_id': user_id,
            'job_id': job_id,
            'message': message,
            'type': notification_type
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='notifications',
            body=json.dumps(notification),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        connection.close()
        print(f"Published notification for user {user_id}")
        return True
    except Exception as e:
        print(f"Error publishing notification: {e}")
        return False

