import io
import json
import os
from pathlib import Path
from typing import Dict

import boto3 as boto3
from minio import Minio

from hmse_simulations.hmse_projects.minio_controller.typing_help import PrefixEndedWithSlash, FilePathInBucket

MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_REGION = os.environ.get("MINIO_REGION")
ROOT_BUCKET = os.environ.get("HMSE_MINIO_ROOT_BUCKET")


class MinIOController:
    def __init__(self):
        endpoint = MINIO_ENDPOINT if MINIO_ENDPOINT else "s3.amazon.com/endpoint"
        self.minio_client = Minio(
            endpoint=endpoint,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            region=MINIO_REGION
        )

    def list_bucket_content(self, name_prefix: PrefixEndedWithSlash, recursive: bool = False):
        return list(self.minio_client.list_objects(ROOT_BUCKET, name_prefix, recursive=recursive))

    def get_json_content(self, file_name: FilePathInBucket):
        response = self.minio_client.get_object(ROOT_BUCKET, file_name,
                                                request_headers={"Content-Type": "application/json"})
        return json.loads(response.data.decode('utf-8'))

    def get_file(self, file_name: FilePathInBucket, output_location: os.PathLike):
        return self.minio_client.fget_object(ROOT_BUCKET, file_name, output_location)

    def get_file_bytes(self, file_name: FilePathInBucket):
        return self.minio_client.get_object(ROOT_BUCKET, file_name)

    def put_file(self, input_file: os.PathLike, bucket_location: FilePathInBucket):
        return self.minio_client.fput_object(ROOT_BUCKET, bucket_location, input_file)

    def put_json_file(self, json_data: Dict, object_location: FilePathInBucket):
        serialized = json.dumps(json_data, indent=2).encode('utf-8')
        return self.minio_client.put_object(ROOT_BUCKET, object_location, io.BytesIO(serialized), len(serialized),
                                            content_type="application/json")

    def delete_file(self, object_location: FilePathInBucket):
        return self.minio_client.remove_object(ROOT_BUCKET, object_location)

    def delete_directory(self, dir_location: PrefixEndedWithSlash):
        files_to_delete = [obj.object_name for obj in self.list_bucket_content(dir_location, recursive=True)]
        for file in files_to_delete:
            self.delete_file(file)

    def upload_directory_to_bucket(self, directory: os.PathLike, bucket_location_root: FilePathInBucket):
        files_to_upload = [str(file) for file in Path(directory).rglob("*")
                           if file.is_file()]
        for file in files_to_upload:
            bucket_file = file.replace("\\", "/")
            location_in_bucket = bucket_file.replace(f"{directory}/", '')
            self.put_file(file, f"{bucket_location_root}/{location_in_bucket}")

    def get_root(self) -> str:
        return ROOT_BUCKET


minio_controller = MinIOController()
