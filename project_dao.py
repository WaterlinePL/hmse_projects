# Interface
import json
import logging
import os
import shutil
from typing import List

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.typing_help import ProjectID, ModflowID, HydrusID, WeatherID, ShapeID

WORKSPACE_PATH = 'workspace'
METADATA_FILENAME = 'metadata.json'


class ProjectDao:

    def __init__(self):
        os.makedirs(WORKSPACE_PATH, exist_ok=True)

    def read_metadata(self, project_id: ProjectID) -> ProjectMetadata:
        with open(os.path.join(WORKSPACE_PATH, project_id, METADATA_FILENAME), 'r') as handle:
            metadata = ProjectMetadata(**json.load(handle))
            if isinstance(metadata.modflow_metadata, dict):
                metadata.modflow_metadata = ModflowMetadata(**metadata.modflow_metadata)
            return metadata

    def read_all_metadata(self) -> List[ProjectMetadata]:
        return [self.read_metadata(project_id) for project_id in self.read_all_names()]

    def read_all_names(self) -> List[str]:
        return os.listdir(WORKSPACE_PATH)

    def save_or_update_metadata(self, metadata: ProjectMetadata) -> None:
        project_path = os.path.join(WORKSPACE_PATH, metadata.project_id)
        os.makedirs(project_path, exist_ok=True)
        with open(os.path.join(project_path, METADATA_FILENAME), 'w') as handle:
            json.dump(metadata.to_json_response(), handle, indent=2, default=lambda o: o.__dict__)
            os.makedirs(os.path.join(ProjectDao.get_project_path(metadata.project_id), 'modflow'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.get_project_path(metadata.project_id), 'hydrus'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.get_project_path(metadata.project_id), 'weather'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.get_project_path(metadata.project_id), 'shapes'), exist_ok=True)
            os.makedirs(os.path.join(ProjectDao.get_rch_shapes_path(metadata.project_id)), exist_ok=True)

    def delete_project(self, project_id: ProjectID) -> None:
        try:
            shutil.rmtree(ProjectDao.get_project_path(project_id))
        except OSError as e:
            logging.error(f"Error occurred during deleting project {project_id}: {str(e)}")

    def download_project(self, project_id: ProjectID) -> str:
        return shutil.make_archive(base_name=os.path.join(ProjectDao.get_project_path(project_id), project_id),
                                   format='zip',
                                   root_dir=ProjectDao.get_simulation_path(project_id))

    def add_hydrus_model(self, project_id: ProjectID,
                         hydrus_id: HydrusID,
                         validated_model_path: os.PathLike) -> None:
        hydrus_model_dir = ProjectDao.get_hydrus_model_path(project_id, hydrus_id)
        os.makedirs(hydrus_model_dir)
        for hydrus_file in os.listdir(validated_model_path):
            validated_file_path = os.path.join(validated_model_path, hydrus_file)
            shutil.move(validated_file_path, hydrus_model_dir)

    def add_modflow_model(self, project_id: ProjectID,
                          modflow_id: ModflowID,
                          validated_model_path: os.PathLike) -> None:
        modflow_model_dir = ProjectDao.get_modflow_model_path(project_id, modflow_id)
        os.makedirs(modflow_model_dir)
        for modflow_file in os.listdir(validated_model_path):
            validated_file_path = os.path.join(validated_model_path, modflow_file)
            shutil.move(validated_file_path, modflow_model_dir)

    def delete_hydrus_model(self, project_id: ProjectID, hydrus_id: HydrusID) -> None:
        shutil.rmtree(ProjectDao.get_hydrus_model_path(project_id, hydrus_id))

    def delete_modflow_model(self, project_id: ProjectID, modflow_id: ModflowID) -> None:
        shutil.rmtree(ProjectDao.get_modflow_model_path(project_id, modflow_id))
        rch_shapes_path = ProjectDao.get_rch_shapes_path(project_id)
        shutil.rmtree(rch_shapes_path)
        os.makedirs(rch_shapes_path)

    def add_weather_file(self, project_id: ProjectID, weather_id: WeatherID, weather_file: FileStorage) -> None:
        os.makedirs(os.path.join(ProjectDao.get_project_path(project_id), 'weather'), exist_ok=True)
        weather_file.save(f"{ProjectDao.get_weather_model_path(project_id, weather_id)}")

    def delete_weather_file(self, project_id: ProjectID, weather_file_id: WeatherID) -> None:
        os.remove(ProjectDao.get_weather_model_path(project_id, weather_file_id))

    def save_or_update_shape(self,
                             project_id: ProjectID,
                             shape_id: ShapeID,
                             shape_mask: np.ndarray) -> None:
        os.makedirs(os.path.join(ProjectDao.get_project_path(project_id), 'shapes'), exist_ok=True)
        np.save(ProjectDao.get_shape_path(project_id, shape_id), shape_mask)

    def get_rch_shapes(self, project_id: ProjectID):
        return {shape_id[:-4]: np.load(ProjectDao.get_rch_shape_filepath(project_id, shape_id[:-4]))
                for shape_id in os.listdir(ProjectDao.get_rch_shapes_path(project_id))}

    def get_shape(self, project_id: ProjectID, shape_id: ShapeID) -> np.ndarray:
        return np.load(ProjectDao.get_shape_path(project_id, shape_id))

    def delete_shape(self, project_id: ProjectID, shape_id: ShapeID) -> None:
        os.remove(ProjectDao.get_shape_path(project_id, shape_id))

    def add_modflow_rch_shapes(self, project_id: ProjectID, rch_shapes: List[np.ndarray]):
        os.makedirs(os.path.join(ProjectDao.get_project_path(project_id), 'rch_shapes'), exist_ok=True)
        for i, mask in enumerate(rch_shapes):
            shape_id = f"rch_shape_{i + 1}"
            np.save(ProjectDao.get_rch_shape_filepath(project_id, shape_id), mask)

    @staticmethod
    def get_project_path(project_id: ProjectID):
        return os.path.join(WORKSPACE_PATH, project_id)

    @staticmethod
    def get_modflow_model_path(project_id: ProjectID, modflow_id: ModflowID):
        return os.path.join(ProjectDao.get_project_path(project_id), 'modflow', modflow_id)

    @staticmethod
    def get_hydrus_model_path(project_id: ProjectID, hydrus_id: HydrusID):
        return os.path.join(ProjectDao.get_project_path(project_id), 'hydrus', hydrus_id)

    @staticmethod
    def get_weather_model_path(project_id: ProjectID, weather_id: WeatherID):
        return os.path.join(ProjectDao.get_project_path(project_id), 'weather', f"{weather_id}.csv")

    @staticmethod
    def get_shape_path(project_id: ProjectID, shape_id: ShapeID):
        return os.path.join(ProjectDao.get_project_path(project_id), 'shapes', f"{shape_id}.npy")

    @staticmethod
    def get_rch_shapes_path(project_id: ProjectID):
        return os.path.join(ProjectDao.get_project_path(project_id), 'rch_shapes')

    @staticmethod
    def get_rch_shape_filepath(project_id: ProjectID, shape_id: ShapeID):
        return os.path.join(ProjectDao.get_rch_shapes_path(project_id), f"{shape_id}.npy")

    @staticmethod
    def get_simulation_path(project_id: ProjectID):
        return os.path.join(ProjectDao.get_project_path(project_id), "simulation")


project_dao = ProjectDao()
