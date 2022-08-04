from abc import ABC, abstractmethod
from typing import Dict

import numpy as np

HydrusModelName = str


class MaskDao(ABC):

    @abstractmethod
    def wipe_all_masks(self, project_name: str):
        ...

    @abstractmethod
    def read_all_for_project(self, project_name: str) -> Dict[HydrusModelName, np.ndarray]:
        ...

    @abstractmethod
    def read(self, project_name: str, hydrus_model_name: HydrusModelName) -> np.ndarray:
        ...

    @abstractmethod
    def save_or_update(self, project_name: str, hydrus_model_name: HydrusModelName, mask: np.ndarray) -> None:
        ...

    @abstractmethod
    def delete(self, project_name: str, hydrus_model_name: HydrusModelName) -> None:
        ...

    @abstractmethod
    def __get_mask_path(self, project_name: str, hydrus_model_name: HydrusModelName) -> str:
        ...


mask_dao = MaskDao()
