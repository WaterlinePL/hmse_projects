from typing import Tuple

import numpy as np

from config import app_config


def scale_polygon(polygon_arr: np.ndarray, original_shape: Tuple[int, int]) -> np.ndarray:
    width_scale = app_config.get_config().grid_width / original_shape[0]
    height_scale = app_config.get_config().grid_height / original_shape[1]
    polygon_arr[:, 0] = polygon_arr[:, 0] * height_scale
    polygon_arr[:, 1] = polygon_arr[:, 1] * width_scale
    return polygon_arr.astype(int)
