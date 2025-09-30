import pika
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_rabbitmq_connection():
    """Get RabbitMQ connection."""
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://fiapx_user:fiapx_password@localhost:5672/')
    
    try:
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        return connection
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None

def send_email(to_email: str, subject: str, message: str) -> bool:
    """Send email notification."""
    try:
        smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        if not smtp_user or not smtp_password:
            print("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def get_user_email(user_id: int) -> str:
    """Get user email from auth service."""
    try:
        import requests
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8000')
        
        # This would need to be implemented in the auth service
        # For now, return a default email
        return f"user{user_id}@fiapx.com"
        
    except Exception as e:
        print(f"Error getting user email: {e}")
        return None

def process_notification_message(ch, method, properties, body):
    """Process notification message from queue."""
    try:
        notification = json.loads(body)
        user_id = notification.get('user_id')
        job_id = notification.get('job_id')
        message = notification.get('message')
        notification_type = notification.get('type', 'email')
        
        if not all([user_id, message]):
            print("Invalid notification: missing required fields")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return
        
        print(f"Processing notification for user {user_id}")
        
        if notification_type == 'email':
            user_email = get_user_email(user_id)
            if user_email:
                subject = "FIAP X - Video Processing Update"
                success = send_email(user_email, subject, message)
                
                if success:
                    print(f"Email notification sent to user {user_id}")
                else:
                    print(f"Failed to send email to user {user_id}")
            else:
                print(f"Could not get email for user {user_id}")
        else:
            print(f"Unsupported notification type: {notification_type}")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f"Error processing notification: {e}")
        # Reject message and requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_notification_consumer():
    """Start consuming messages from notification queue."""
    print("Starting notification queue consumer...")
    
    while True:
        try:
            connection = get_rabbitmq_connection()
            if not connection:
                print("Failed to connect to RabbitMQ, retrying in 5 seconds...")
                import time
                time.sleep(5)
                continue
            
            channel = connection.channel()
            channel.queue_declare(queue='notifications', durable=True)
            
            # Set QoS to process one message at a time
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(
                queue='notifications',
                on_message_callback=process_notification_message
            )
            
            print("Waiting for notification messages...")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            print("Stopping notification consumer...")
            break
        except Exception as e:
            print(f"Notification consumer error: {e}")
            import time
            time.sleep(5)

