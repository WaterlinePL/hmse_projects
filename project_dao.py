# Interface
import os
import tempfile
from typing import List

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.minio_controller.minio_controller import minio_controller
from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.typing_help import ProjectID, ModflowID, HydrusID, WeatherID, ShapeID


class ProjectDao:

    def read_metadata(self, project_id: ProjectID) -> ProjectMetadata:
        metadata_dict = minio_controller.get_json_content(f"projects/{project_id}/metadata.json")
        return ProjectMetadata(**metadata_dict)

    def read_all_metadata(self) -> List[ProjectMetadata]:
        return [self.read_metadata(project_id) for project_id in self.read_all_names()]

    def read_all_names(self) -> List[str]:
        return [obj.object_name.split('/')[-1] for obj in minio_controller.list_bucket_content("projects/")]

    def save_or_update_metadata(self, metadata: ProjectMetadata) -> None:
        minio_controller.put_json_file(metadata.__dict__, f"projects/{metadata.project_id}/metadata.json")

    def delete_project(self, project_id: ProjectID) -> None:
        minio_controller.delete_directory(f"projects/{project_id}/")

    def download_project(self, project_id: ProjectID) -> FileStorage:
        minio_controller.get_file(f"projects/{project_id}/{project_id}.zip")

    def add_hydrus_model(self, project_id: ProjectID,
                         hydrus_id: HydrusID,
                         validated_model_path: os.PathLike) -> None:
        minio_controller.upload_directory_to_bucket(validated_model_path,
                                                    f"projects/{project_id}/hydrus/{hydrus_id}")  # TODO: test

    def add_modflow_model(self, project_id: ProjectID,
                          modflow_id: ModflowID,
                          validated_model_path: os.PathLike) -> None:
        minio_controller.upload_directory_to_bucket(validated_model_path,
                                                    f"projects/{project_id}/modflow/{modflow_id}")  # TODO: test

    def delete_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID) -> None:
        minio_controller.delete_directory(f"projects/{project_id}/hydrus/{hydrus_id}/")

    def delete_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID) -> None:
        minio_controller.delete_directory(f"projects/{project_id}/modflow/{modflow_id}/")

    def add_weather_file(self, project_id: ProjectID, weather_id: WeatherID, weather_file: FileStorage) -> None:
        minio_controller.put_file(weather_file, f"projects/{project_id}/weather/{weather_id}.csv")

    def delete_weather_file(self, project_id: ProjectID, weather_file_id: WeatherID) -> None:
        minio_controller.delete_file(f"projects/{project_id}/weather/{weather_file_id}.csv")

    def save_or_update_shape(self,
                             project_id: ProjectID,
                             shape_id: ShapeID,
                             shape_mask: np.ndarray) -> None:
        with tempfile.NamedTemporaryFile() as tmp:
            np.save(tmp, shape_mask)
            minio_controller.put_file(tmp.name, f"projects/{project_id}/shapes/{shape_id}.npy")

    def get_rch_shapes(self, project_id: ProjectID):
        rch_shapes = {}
        rch_paths = [obj.object_name for obj in
                     minio_controller.list_bucket_content(f"projects/{project_id}/rch-shapes/")]
        for rch_shape_bucket_path in rch_paths:
            shape_id = rch_shape_bucket_path.split("/")[-1]
            rch_shapes[shape_id] = self.get_shape(project_id, shape_id)

    def delete_rch_shapes(self, project_id: ProjectID):
        minio_controller.delete_directory(f"projects/{project_id}/rch-shapes")

    def get_shape(self, project_id: ProjectID, shape_id: ShapeID) -> np.ndarray:
        with tempfile.NamedTemporaryFile() as tmp:
            minio_controller.get_file(f"projects/{project_id}/shapes/{shape_id}.npy", tmp.name)
            return np.load(tmp.name)

    def delete_shape(self, project_id: ProjectID, shape_id: ShapeID) -> None:
        minio_controller.delete_file(f"projects/{project_id}/shapes/{shape_id}.npy")

    def add_modflow_rch_shapes(self, project_id: ProjectID, rch_shapes: List[np.ndarray]):
        for i, mask in enumerate(rch_shapes):
            shape_id = f"rch-shape-{i + 1}.npy"
            self.save_or_update_shape(project_id, shape_id, mask)


project_dao = ProjectDao()
