from .create_junctioin_road.create_junction_road import *


class HDMapConnectJunctionRoad:
    def __init__(self, iface):
        self.iface = iface
        self.iface.messageBar().pushInfo("CRMAP", 'helloworld')
    def create_junction_road(self):
        self.create_junction_road_dialog = create_junction_road_dialog(self.iface.mainWindow())
        self.create_junction_road_dialog.show()

    

    