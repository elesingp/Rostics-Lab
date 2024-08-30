import matplotlib.pyplot as plt
from tools.imports import sns
import os
from common_paths import *

graphics_show = True
visualization_paths = get_visualize_paths(
    data_dict['data'], 
    data_dict['data_test_before'], 
    data_dict['data_control_before'],
    data_dict['data_test_after'], 
    data_dict['data_control_after'],
    self.config, 
    graphics_show
)