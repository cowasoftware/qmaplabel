from qgis.core import *

from .clip_road_center.clip_road_center import *


class HDMapClipCenter:
    def __init__(self, iface):
        self.iface = iface

    def clip_center_and_fill_link(self):
        
        self.clip_dialog = clip_road_center(self.iface.mainWindow(),self.iface)
        self.clip_dialog.show()
