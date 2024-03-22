"""
This module provides a manager class for interacting with Amazon S3.

Classes:
    - S3Manager: Manager class for Amazon S3 operations.

Dependencies:
    - boto3: AWS SDK for Python.
    - botocore.exceptions.NoCredentialsError: Exception for missing AWS credentials.
    - typing.List: Type representing a list.
    - typing.Optional: Type representing an optional value.

Global Variables:
    - BUCKET_TO_RASPBERRY (str): Name of the S3 bucket for files to Raspberry Pi.
    - BUCKET_FROM_RASPBERRY (str): Name of the S3 bucket for files from Raspberry Pi.
"""


import boto3
from botocore.exceptions import NoCredentialsError
from typing import List, Optional

BUCKET_TO_RASPBERRY = 'files-to-raspberry'
BUCKET_FROM_RASPBERRY = 'files-from-raspberry'


class S3Manager:
    """
    Manager class for interacting with Amazon S3.

    Attributes:
        s3 (boto3.client): Boto3 S3 client instance.

    Methods:
        - __init__: Initializes the S3Manager.
        - upload_file: Uploads a file to S3.
        - download_file: Downloads a file from S3.
        - files_list: Lists files in a S3 bucket.
        - delete_file: Deletes a file from S3.
        - generate_presigned_url: Generates a presigned URL for accessing a file from S3.
    """

    def __init__(self, access_key: str, secret_key: str, region_name: str = 'us-east-1') -> None:
        """
        Initializes the S3Manager.

        Parameters:
            access_key (str): AWS access key.
            secret_key (str): AWS secret key.
            region_name (str): AWS region name (default is 'us-east-1').
        """
        self.s3 = boto3.client('s3', aws_access_key_id=access_key,
                               aws_secret_access_key=secret_key, region_name=region_name)

    def upload_file(self, local_file_path: str, s3_file_key: str, bucket: str) -> None:
        """
        Uploads a file to S3.

        Parameters:
            local_file_path (str): Local file path.
            s3_file_key (str): Key to store the file in S3.
            bucket (str): S3 bucket name.
        """
        try:
            self.s3.upload_file(local_file_path, bucket, s3_file_key)
        except FileNotFoundError:
            print(f"The file {local_file_path} was not found.")
        except NoCredentialsError:
            print("Credentials not available.")

    def download_file(self, s3_file_key: str, local_file_path: str, bucket: str) -> None:
        """
        Downloads a file from S3.

        Parameters:
            s3_file_key (str): Key of the file in S3.
            local_file_path (str): Local file path to save the downloaded file.
            bucket (str): S3 bucket name.
        """
        try:
            self.s3.download_file(bucket, s3_file_key, local_file_path)
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def files_list(self, bucket: str) -> Optional[List[str]]:
        """
        Lists files in a S3 bucket.

        Parameters:
            bucket (str): S3 bucket name.

        Returns:
            Optional[List[str]]: List of file keys in the S3 bucket or None if error occurs.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=bucket)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            return files
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def delete_file(self, s3_file_key: str, bucket: str) -> None:
        """
        Deletes a file from S3.

        Parameters:
            s3_file_key (str): Key of the file in S3.
            bucket (str): S3 bucket name.
        """
        try:
            self.s3.delete_object(Bucket=bucket, Key=s3_file_key)
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def generate_presigned_url(self, s3_file_key: str, bucket: str, expiration_time: int = 60) -> Optional[str]:
        """
        Generates a presigned URL for accessing a file from S3.

        Parameters:
            s3_file_key (str): Key of the file in S3.
            bucket (str): S3 bucket name.
            expiration_time (int): Expiration time for the presigned URL in seconds (default is 60).

        Returns:
            Optional[str]: Presigned URL for accessing the file or None if error occurs.
        """
        try:
            presigned_url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_file_key},
                ExpiresIn=expiration_time
            )
            return presigned_url
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
