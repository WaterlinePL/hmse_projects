import tempfile
from typing import List, Dict

import numpy as np
from werkzeug.datastructures import FileStorage

from hmse_simulations.hmse_projects.hmse_hydrological_models.hydrus import hydrus_utils
from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow import modflow_utils
from hmse_simulations.hmse_projects.hmse_hydrological_models.modflow.modflow_metadata import ModflowMetadata
from hmse_simulations.hmse_projects.project_dao import project_dao
from hmse_simulations.hmse_projects.project_exceptions import ProjectSimulationNotFinishedError
from hmse_simulations.hmse_projects.project_metadata import ProjectMetadata
from hmse_simulations.hmse_projects.shape_utils import generate_random_html_color
from hmse_simulations.hmse_projects.typing_help import ProjectID, HydrusID, ShapeID, WeatherID


def get(project_id: ProjectID) -> ProjectMetadata:
    return project_dao.read_metadata(project_id)


def get_all_project_names() -> List[ProjectID]:
    return project_dao.read_all_names()


def save_or_update_metadata(metadata: ProjectMetadata) -> None:
    project_dao.save_or_update_metadata(metadata)


def delete(project_id: ProjectID) -> None:
    project_dao.delete_project(project_id)


def download_project(project_id: ProjectID):
    if not project_dao.read_metadata(project_id).finished:
        raise ProjectSimulationNotFinishedError()
    return project_dao.download_project(project_id)


def is_finished(project_id: ProjectID) -> bool:
    return project_dao.read_metadata(project_id).finished


def add_hydrus_model(project_id: ProjectID, hydrus_model: FileStorage) -> HydrusID:
    metadata = project_dao.read_metadata(project_id)
    hydrus_id = hydrus_model.filename[:-4]  # .zip file

    with tempfile.TemporaryDirectory() as validation_dir:
        hydrus_utils.validate_model(hydrus_model, validation_dir)
        project_dao.add_hydrus_model(project_id, hydrus_id, validation_dir)
        metadata.add_hydrus_model(hydrus_id)
        project_dao.save_or_update_metadata(metadata)
        return hydrus_id


def delete_hydrus_model(project_id: ProjectID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_hydrus_model(hydrus_id)
    project_dao.delete_hydrus_model(project_id, hydrus_id)
    project_dao.save_or_update_metadata(metadata)


def set_modflow_model(project_id: ProjectID, modflow_model: FileStorage) -> ModflowMetadata:
    metadata = project_dao.read_metadata(project_id)

    if metadata.modflow_metadata:
        project_dao.delete_modflow_model(project_id, metadata.modflow_metadata.modflow_id)

    modflow_id = modflow_model.filename[:-4]  # .zip file
    with tempfile.TemporaryDirectory() as validation_dir:
        model_metadata, rch_shapes = modflow_utils.extract_metadata(modflow_model, validation_dir)
        project_dao.add_modflow_model(project_id, modflow_id, validation_dir)
        metadata.set_modflow_metadata(model_metadata)
        project_dao.save_or_update_metadata(metadata)
        project_dao.add_modflow_rch_shapes(project_id, rch_shapes)
        return model_metadata


def delete_modflow_model(project_id: ProjectID):
    metadata = project_dao.read_metadata(project_id)
    modflow_id = metadata.modflow_metadata.modflow_id
    metadata.remove_modflow_metadata()
    project_dao.delete_modflow_model(project_id, modflow_id)
    project_dao.save_or_update_metadata(metadata)


def add_weather_file(project_id: ProjectID, weather_file: FileStorage) -> WeatherID:
    metadata = project_dao.read_metadata(project_id)
    weather_id = weather_file.filename[:-4]  # .csv file
    metadata.add_weather_file(weather_id)
    project_dao.add_weather_file(project_id, weather_id, weather_file)
    project_dao.save_or_update_metadata(metadata)
    return weather_id


def delete_weather_file(project_id: ProjectID, weather_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_weather_file(weather_id)
    project_dao.delete_weather_file(project_id, weather_id)
    project_dao.save_or_update_metadata(metadata)


def wipe_all_shapes(project_id: ProjectID) -> None:
    metadata = project_dao.read_metadata(project_id)
    for shape_id in metadata.shapes:
        project_dao.delete_shape(project_id, shape_id)


def get_all_shapes(project_id: ProjectID) -> Dict[ShapeID, np.ndarray]:
    metadata = project_dao.read_metadata(project_id)
    shapes = {}
    for shape_id in metadata.shapes.keys():
        shapes[shape_id] = project_dao.get_shape(project_id, shape_id).tolist()
    return shapes


def add_rch_shapes(project_id: ProjectID):
    rch_shapes = project_dao.get_rch_shapes(project_id)
    for shape_id, mask in rch_shapes.items():
        project_dao.save_or_update_shape(project_id, shape_id, mask)
    return {
        "shapeIds": {shape_id: generate_random_html_color() for shape_id in rch_shapes.keys()},
        "shapeMasks": {shape_id: mask.tolist() for shape_id, mask in rch_shapes.items()},
    }


def save_or_update_shape(project_id: ProjectID, shape_id: ShapeID, shape_mask: np.ndarray, color: str,
                         new_shape_id: ShapeID) -> None:
    metadata = project_dao.read_metadata(project_id)
    if metadata.contains_shape(shape_id) and shape_id != new_shape_id:
        project_dao.delete_shape(project_id, shape_id)
        current_shape_mapping = metadata.shapes_to_hydrus.get(shape_id)

        if current_shape_mapping is not None:
            if isinstance(current_shape_mapping, float):
                metadata.map_shape_to_manual_value(new_shape_id, current_shape_mapping)
            else:
                metadata.map_shape_to_hydrus(new_shape_id, current_shape_mapping)
            metadata.remove_shape_mapping(shape_id)
        metadata.remove_shape_metadata(shape_id)

    metadata.add_shape_metadata(new_shape_id, color)
    project_dao.save_or_update_shape(project_id, new_shape_id, shape_mask)
    project_dao.save_or_update_metadata(metadata)


def delete_shape(project_id: ProjectID, shape_id: ShapeID) -> None:
    project_dao.delete_shape(project_id, shape_id)


def map_shape_to_hydrus(project_id: ProjectID, shape_id: ShapeID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_shape_to_hydrus(shape_id, hydrus_id)
    project_dao.save_or_update_metadata(metadata)


def map_shape_to_manual_value(project_id: ProjectID, shape_id: ShapeID, value: float):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_shape_to_manual_value(shape_id, value)
    project_dao.save_or_update_metadata(metadata)


def map_hydrus_to_weather_file(project_id: ProjectID, hydrus_id: HydrusID, weather_id: WeatherID):
    metadata = project_dao.read_metadata(project_id)
    metadata.map_hydrus_to_weather(hydrus_id, weather_id)
    project_dao.save_or_update_metadata(metadata)


def remove_shape_mapping(project_id: ProjectID, shape_id: ShapeID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_shape_mapping(shape_id)
    project_dao.save_or_update_metadata(metadata)


def remove_weather_hydrus_mapping(project_id: ProjectID, hydrus_id: HydrusID):
    metadata = project_dao.read_metadata(project_id)
    metadata.remove_hydrus_weather_mapping(hydrus_id)
    project_dao.save_or_update_metadata(metadata)
