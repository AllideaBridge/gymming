import logging

import boto3
from botocore.exceptions import ClientError


class ImageService:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.BUCKET_NAME = 'gymming'

    def upload_image(self, entity, id, file, prefix):
        s3_key = f'{entity}/{id}/{prefix}'
        try:
            self.s3.upload_fileobj(file, self.BUCKET_NAME, s3_key)
            return s3_key
        except Exception as e:
            print(f"Error uploading file: {e}")
            return {'error': 'File upload failed'}, 500

    def get_presigned_url(self, s3_key):
        try:
            # 파일 존재 여부 확인
            self.s3.head_object(Bucket=self.BUCKET_NAME, Key=s3_key)

            presigned_url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=3600  # URL 유효 기간 (1시간)
            )
            return presigned_url
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            else:
                logging.error(f"Error generating presigned URL: {e}")
                return None
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return None

    def delete_image(self, entity=None, id=None, prefix=None, s3_key=None):
        try:
            if s3_key is None:
                s3_key = f'{entity}/{id}/{prefix}'

            self.s3.delete_object(Bucket=self.BUCKET_NAME, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "NoSuchKey":
                return False
            else:
                raise e
