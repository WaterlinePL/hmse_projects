import io
import json
import os
from pathlib import Path
from typing import Dict

from minio import Minio

from hmse_simulations.hmse_projects.minio_controller.typing_help import PrefixEndedWithSlash, FilePathInBucket

MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_SECURE = os.environ.get("MINIO_SECURE")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
ROOT_BUCKET = os.environ.get("HMSE_MINIO_ROOT_BUCKET")


class MinIOController:
    def __init__(self):
        self.minio_client = Minio(
            endpoint=MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            region='us-east-1'
        )

    def list_bucket_content(self, name_prefix: PrefixEndedWithSlash, recursive: bool = False):
        return list(self.minio_client.list_objects(ROOT_BUCKET, name_prefix, recursive=recursive))

    def get_json_content(self, file_name: FilePathInBucket):
        response = self.minio_client.get_object(ROOT_BUCKET, file_name,
                                                request_headers={"Content-Type": "application/json"})
        return json.loads(response.data.decode('utf-8'))

    def get_file(self, file_name: FilePathInBucket, output_location: os.PathLike):
        return self.minio_client.fget_object(ROOT_BUCKET, file_name, output_location)

    def put_file(self, input_file: os.PathLike, bucket_location: FilePathInBucket):
        return self.minio_client.fput_object(ROOT_BUCKET, bucket_location, input_file)

    def put_json_file(self, json_data: Dict, object_location: FilePathInBucket):
        serialized = json.dumps(json_data, indent=2).encode('utf-8')
        return self.minio_client.put_object(ROOT_BUCKET, object_location, io.BytesIO(serialized), len(serialized),
                                            content_type="application/json")

    def delete_file(self, object_location: FilePathInBucket):
        return self.minio_client.remove_object(ROOT_BUCKET, object_location)

    def delete_directory(self, dir_location: FilePathInBucket):
        files_to_delete = [obj.object_name for obj in self.list_bucket_content(dir_location, recursive=True)]
        for file in files_to_delete:
            self.delete_file(file)

    def upload_directory_to_bucket(self, directory: os.PathLike, bucket_location_root: FilePathInBucket):
        files_to_upload = [str(file) for file in Path(directory).rglob("*")
                           if file.is_file()]
        for file in files_to_upload:
            bucket_file = file.replace("\\", "/")
            self.put_file(file, f"{bucket_location_root}/{bucket_file}")


minio_controller = MinIOController()