import math
from logic.networkmodel import DxNetworkModel, NetworkModel
from pandas import read_csv

from logic.postprocessingsettings import PostProcessingSettings

class NetworkPostProcessor:
    def __init__(self, settings: PostProcessingSettings):
        self.settings = settings
        if self.settings.loadfile_name is not None:
            self.load_data = read_csv(self.settings.loadfile_name)
    
    def set_load_values(self, network: DxNetworkModel, hour: int=0):
        if not network.is_three_phase:
            raise Exception("Initializing load files from separate file currently supported for three-phase networks")
        if self.load_data is None:
            raise Exception("NetworkPostProcessor needs a valid load file upon initialization")
        for load_name in self.load_data.columns:
            try:
                load_obj = network.load_name_map[load_name]
            except:
                continue
            try:
                magnitude = self.load_data[load_name][hour]
            except:
                continue
            angle = math.atan(load_obj.Q/load_obj.P)
            load_obj.P = magnitude * math.cos(angle)
            load_obj.Q = magnitude * math.sin(angle)