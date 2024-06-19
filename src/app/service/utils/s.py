import os
import time
from datetime import datetime

import requests
import boto3
from PyPDF2 import PdfReader, PdfWriter

from app.core.config import settings
from app.core.logger import logging
from botocore.exceptions import NoCredentialsError

logger = logging.getLogger(__name__)

s3_bucket_access_key = settings.MAIL_REPORT_S3_ACCESS_KEY
s3_bucket_secret_key = settings.MAIL_REPORT_S3_SECRET_KEY
region = settings.MAIL_REQUEST_REPORT_BUCKET_REGION
BUCKET = 'mail-attachment-archive'

class S3Utils:
    def __init__(self):
        timestamp = str(int(time.time() * 1000))[:12]
        self.directory = f"{timestamp[:6]}-{timestamp[6:12]}"
        self.full_directory_path = f"/tmp/{self.directory}"
        os.makedirs(self.full_directory_path)

    def download_file_to_temp_directory(self, file_url: str, file_name: str):
        """Download a PDF file from a given URL and save it."""
        logger.info("Download File Started")
        response = requests.get(file_url)
        file_path = os.path.join(self.full_directory_path, file_name)
        with open(file_path, "wb") as f:
            f.write(response.content)
        logger.info(f"Download file completed and file_name is - {file_name}")
        return file_name

    def upload_file_to_s3(self, file_name:str):
        """Upload the file to S3."""
        logger.info(f"Uploading file {file_name} to S3 Bucket")
        s3 = boto3.client(
            "s3",
            aws_access_key_id=s3_bucket_access_key,
            aws_secret_access_key=s3_bucket_secret_key,
            region_name=region,
        )
        object_name = f"mail-attachments/{file_name}"
        try:
            s3.upload_file(f"{self.full_directory_path}/{file_name}", BUCKET, object_name, ExtraArgs={'ACL': 'public-read', 'ContentType': 'application/pdf','ContentDisposition':'inline'})
            logger.info(
                f"File '{file_name}' uploaded to '{BUCKET}/{file_name}' successfully."
            )
            return {"file_location": object_name}
        except FileNotFoundError:
            logger.error(f"The file '{file_name}' was not found.")
        except NoCredentialsError:
            logger.error("Credentials not available or incorrect.")

    def cleanup_temp_directory(self):
        """Clean up the temporary directory and file."""
        logger.info(f"Cleaning up {self.full_directory_path} and file")
        try:
            logger.info(f"Removing {self.directory}")
            if os.path.exists(self.full_directory_path):
                for file in os.listdir(self.full_directory_path):
                    file_path = os.path.join(self.full_directory_path, file)
                    os.remove(file_path)
                os.rmdir(self.full_directory_path)
                logger.info(f"Deleted temporary directory: {self.full_directory_path}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def get_timestamp():
    t = datetime.now()
    time_stamp = t.timestamp()
    return time_stamp


def pdf_concat(input_files, output_stream):
    file_names_to_remove = []
    input_streams = []
    try:
        for input_file in input_files:
            file_name = f'{str(get_timestamp())}.pdf'   
            try:
                input_streams.append(open(input_file, 'rb'))
            except FileNotFoundError:
                re = requests.get(input_file)
            if re.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(re.content)
                input_streams.append(open(file_name,'rb'))
                file_names_to_remove.append(file_name)
        logger.info(f"{len(input_streams)}, {input_streams}")
        writer = PdfWriter()
        for reader in map(PdfReader, input_streams):
            for n in range(len(reader.pages)):
                writer.add_page(reader.pages[n])
        writer.write(output_stream)
    finally:
        for f in input_streams:
            f.close()
        if len(file_names_to_remove)>0:
            for i in file_names_to_remove:
                os.remove(i)
        output_stream.close()