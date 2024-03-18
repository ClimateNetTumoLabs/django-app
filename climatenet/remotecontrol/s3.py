import boto3
from botocore.exceptions import NoCredentialsError

BUCKET_TO_RASPBERRY = 'files-to-raspberry'
BUCKET_FROM_RASPBERRY = 'files-from-raspberry'


class S3Manager:
    def __init__(self, access_key, secret_key, region_name='us-east-1'):
        self.s3 = boto3.client('s3', aws_access_key_id=access_key,
                               aws_secret_access_key=secret_key, region_name=region_name)

    def upload_file(self, local_file_path, s3_file_key, bucket):
        try:
            self.s3.upload_file(local_file_path, bucket, s3_file_key)
            print(f"File {local_file_path} uploaded to S3 bucket {bucket} as {s3_file_key}")
        except FileNotFoundError:
            print(f"The file {local_file_path} was not found.")
        except NoCredentialsError:
            print("Credentials not available.")

    def download_file(self, s3_file_key, local_file_path, bucket):
        try:
            self.s3.download_file(bucket, s3_file_key, local_file_path)
            print(f"File {s3_file_key} downloaded from S3 bucket {bucket} to {local_file_path}")
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def list_files(self, bucket):
        try:
            response = self.s3.list_objects_v2(Bucket=bucket)
            files = [obj['Key'] for obj in response.get('Contents', [])]
            print(f"Files in S3 bucket {bucket}: {files}")
            return files
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def delete_file(self, s3_file_key, bucket):
        try:
            self.s3.delete_object(Bucket=bucket, Key=s3_file_key)
            print(f"File {s3_file_key} deleted from S3 bucket {bucket}")
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def generate_presigned_url(self, s3_file_key, bucket, expiration_time=60):
        try:
            presigned_url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_file_key},
                ExpiresIn=expiration_time
            )
            print(f"Presigned URL generated for file {s3_file_key}: {presigned_url}")
            return presigned_url
        except NoCredentialsError:
            print("Credentials not available.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
