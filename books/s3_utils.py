import boto3
import os
import logging
from botocore.exceptions import NoCredentialsError, ClientError
from django.conf import settings
from dotenv import load_dotenv
from urllib.parse import urljoin

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_s3_client():
    """
    Create and return an S3 client with the appropriate credentials
    """
    try:
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
            region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        )
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}")
        return None

def get_s3_url(key):
    """
    Generate the URL for a file in S3
    
    Args:
        key: The S3 key (path/filename)
        
    Returns:
        str: The URL of the file
    """
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    base_url = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    
    if base_url:
        # Use custom domain if configured
        return urljoin(f"https://{base_url}/", key)
    else:
        # Default to standard S3 URL
        return f"https://{bucket_name}.s3.amazonaws.com/{key}"

def upload_file_to_s3(file, key, content_type=None, acl='public-read'):
    """
    Upload a file to S3
    
    Args:
        file: The file object to upload
        key: The S3 key (path/filename) to use
        content_type: The content type of the file (optional)
        acl: The ACL to apply to the object (default: public-read)
        
    Returns:
        str: The URL of the uploaded file, or None if upload fails
    """
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME not set")
        return None
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
            
        # Determine content type if not provided
        if not content_type and hasattr(file, 'content_type'):
            content_type = file.content_type
            
        extra_args = {'ACL': acl}
        if content_type:
            extra_args['ContentType'] = content_type
        
        s3_client.upload_fileobj(
            file,
            bucket_name,
            key,
            ExtraArgs=extra_args
        )
        
        # Generate the URL for the uploaded file
        return get_s3_url(key)
    
    except NoCredentialsError:
        logger.error("AWS credentials not available")
        return None
    except ClientError as e:
        logger.error(f"AWS client error uploading to S3: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error uploading to S3: {str(e)}")
        return None

def delete_file_from_s3(key):
    """
    Delete a file from S3
    
    Args:
        key: The S3 key of the file to delete
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    if not bucket_name:
        logger.error("AWS_STORAGE_BUCKET_NAME not set")
        return False
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return False
            
        s3_client.delete_object(
            Bucket=bucket_name,
            Key=key
        )
        logger.info(f"Successfully deleted {key} from S3 bucket {bucket_name}")
        return True
    
    except ClientError as e:
        logger.error(f"AWS client error deleting from S3: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error deleting from S3: {str(e)}")
        return False

def check_file_exists(key):
    """
    Check if a file exists in S3
    
    Args:
        key: The S3 key of the file to check
        
    Returns:
        bool: True if file exists, False otherwise
    """
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return False
            
        s3_client.head_object(
            Bucket=bucket_name,
            Key=key
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        logger.error(f"Error checking if file exists in S3: {str(e)}")
        return False

def get_presigned_url(key, expiration=3600):
    """
    Generate a presigned URL to share an S3 object
    
    Args:
        key: The S3 key of the file
        expiration: Time in seconds for the URL to remain valid (default: 1 hour)
        
    Returns:
        str: The presigned URL or None if failed
    """
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
            
        return s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': key
            },
            ExpiresIn=expiration
        )
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None