from .change_points_types.change_points_types import *
from .update_attribute import *
from .update_junction_up_down_ids.update_junction_up_down_ids import *
from .update_road_up_down_ids.update_road_up_down_ids import *


class HDMapUpdateAttributes:
    def __init__(self, iface):
        self.iface = iface
        self.iface.messageBar().pushInfo("CRMAP", 'helloworld')
    def update_center_line_up_down_ids(self):
        
        self.update_center_line_up_down_ids_dialog = update_road_up_down_ids()
        self.update_center_line_up_down_ids_dialog.show()
    def update_junction_line_up_down_ids(self):
        
        self.update_junction_line_up_down_ids_dialog = update_junction_up_down_ids()
        self.update_junction_line_up_down_ids_dialog.show()
        


    def update_boundary_points_type(self):
        layer = self.iface.activeLayer()
        if('boundary' not in layer.name()):
            self.iface.messageBar().pushInfo("Question","the activeLayer's name must contain 'road_center'")
            return
        
        self.dia1 = change_points_types_dialog(self.iface,layer)
        self.dia1.show()