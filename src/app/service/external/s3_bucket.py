import boto3

from app.core.config import settings
from app.core.logger import logging

logger = logging.getLogger(__name__)

s3_bucket_access_key = settings.S3_BUCKET_ACCESS_KEY
s3_bucket_secret_key = settings.S3_BUCKET_SECRET_KEY
region = settings.S3_BUCKET_REGION
BUCKET = settings.S3_BUCKET



class S3Utils:
    
    def upload_image_to_s3(self, name: str, file):
            """Upload the file to S3."""
            logger.info(f'Uploading file {file} to S3 Bucket')
            s3 = boto3.client(
                    's3',
                    aws_access_key_id=s3_bucket_access_key,
                    aws_secret_access_key=s3_bucket_secret_key,
                    region_name=region,
            )
            obj_name = f'menu-card/{name}-{file.filename}'.replace(' ', '-')
            try:
                
                #     s3.upload_fileobj(file.file, BUCKET, obj_name, ExtraArgs={'ACL': 'public-read'})
                    s3.upload_fileobj(file.file,BUCKET, obj_name, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png', 'ContentDisposition': 'attachment'})

                    logger.info(
                            f"File '{file}' uploaded to 'https://{BUCKET}.s3.amazonaws.com/{obj_name}' successfully."
                    )
                    url = f'https://{BUCKET}.s3.amazonaws.com/{obj_name}'
                    return url
            except FileNotFoundError:
                    logger.error(f"The file '{file}' was not found.")
                    
    def upload_qr_image_to_s3(self, name: str, file):
            """Upload the image to S3."""
            logger.info(f'Uploading file {file} to S3 Bucket')
            s3 = boto3.client(
                    's3',
                    aws_access_key_id=s3_bucket_access_key,
                    aws_secret_access_key=s3_bucket_secret_key,
                    region_name=region,
            )
            obj_name = f'menu-card/qr-{name}'.replace(' ', '-')
            try:
                
                #     s3.upload_fileobj(file.file, BUCKET, obj_name, ExtraArgs={'ACL': 'public-read'})
                    s3.upload_fileobj(file,BUCKET, obj_name, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png', 'ContentDisposition': 'attachment'})

                    logger.info(
                            f"File '{file}' uploaded to 'https://{BUCKET}.s3.amazonaws.com/{obj_name}' successfully."
                    )
                    url = f'https://{BUCKET}.s3.amazonaws.com/{obj_name}'
                    return url
            except FileNotFoundError:
                    logger.error(f"The file '{file}' was not found.")

    def delete_image_from_s3(self, file_url):
            """Delete the attachment file from S3"""
            try:
                    obj_name = file_url.split('/')[-1]
                    s3 = boto3.client(
                            's3',
                            aws_access_key_id=s3_bucket_access_key,
                            aws_secret_access_key=s3_bucket_secret_key,
                            region_name=region,
                    )
                    s3.delete_object(Bucket=BUCKET, Key=obj_name)
                    logger.info(f'The file {obj_name} deleted successfully from S3 bucket')

            except Exception as e:
                    logger.error(f'Error during deleting: {e}')
