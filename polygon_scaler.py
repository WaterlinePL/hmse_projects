from typing import Tuple

import numpy as np

from config import app_config


def scale_polygon(polygon_arr: np.ndarray, original_shape: Tuple[int, int]) -> np.ndarray:
    polygon_arr[:, 0] = polygon_arr[:, 0] / (original_shape[1] - 1) * app_config.get_config().grid_width
    polygon_arr[:, 1] = polygon_arr[:, 1] / (original_shape[0] - 1) * app_config.get_config().grid_height
    polygon_arr.round()
    return polygon_arr.astype(int)
