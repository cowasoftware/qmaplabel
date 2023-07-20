import re

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QAction, QButtonGroup, QDialog, QFileDialog,
                             QMainWindow, QMessageBox, QRadioButton,
                             QScrollArea, QVBoxLayout)
from qgis.core import (QgsApplication, QgsExpression, QgsFeature,
                       QgsFeatureRequest, QgsField, QgsFields, QgsGeometry,
                       QgsLayerTree, QgsLayerTreeModel, QgsPoint, QgsProject,
                       QgsSpatialIndex, QgsVectorFileWriter, QgsVectorLayer,
                       QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant

from ...utils import *
from ..update_attribute import *
from .update_junction_up_down_ids_ui import *


class update_junction_up_down_ids(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.ui_data = Ui_Dialog_update_junction_up_down_ids()
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.ui_data.setupUi(self)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        for i in range(0,len(QgsProject.instance().mapLayers().keys())):
            id = list(QgsProject.instance().mapLayers().keys())[i]
            vectorlayer = QgsProject.instance().mapLayers()[id]
            self.ui_data.comboBox_junction.addItem(vectorlayer.source())
            self.ui_data.comboBox_road.addItem(vectorlayer.source())
        self.ui_data.comboBox_junction.setAcceptDrops(True)
        self.ui_data.comboBox_road.setAcceptDrops(True)
        self.ui_data.comboBox_junction.setEditable(True)
        self.ui_data.comboBox_road.setEditable(True)
        self.ui_data.comboBox_junction.installEventFilter(QEventHandler(self))
        self.ui_data.comboBox_road.installEventFilter(QEventHandler(self))
        self.ui_data.btn_center_layer.clicked.connect(self.btn_choose_center_data)
        self.ui_data.btn_junction_layer.clicked.connect(self.btn_choose_junction_data)
        self.ui_data.btn_run.clicked.connect(self.btn_run)
    def btn_choose_center_data(self):
        center_data =  QFileDialog.getOpenFileName(None, "中心线", "./",'*.shp') 
        self.ui_data.comboBox_road.setCurrentText(center_data[0])
    def btn_choose_junction_data(self):
        junction_data  =  QFileDialog.getOpenFileName(None, "路口线", "./",'*.shp') 
        self.ui_data.comboBox_junction.setCurrentText(junction_data[0])
    def btn_run(self):
        center_layer = QgsVectorLayer(self.ui_data.comboBox_road.currentText(),"center_layer","ogr")
        junction_layer = QgsVectorLayer(self.ui_data.comboBox_junction.currentText(),"junction_layer","ogr")
        tool_fixing_junction_lines_up_down_ids(center_layer,junction_layer,0.0001)
        
# python
# class QEventHandler(QtCore.QObject):
#     def eventFilter(self, obj, event):
#         """
#         处理窗体内出现的事件，如果有需要则自行添加if判断语句；
#         目前已经实现将拖到控件上文件的路径设置为控件的显示文本；
#         """
#         if event.type() == QtCore.QEvent.DragEnter:
#             event.accept()
#         if event.type() == QtCore.QEvent.Drop:
#             md = event.mimeData()
#             if('application/qgis.layertreemodeldata' in md.formats()):
#                 qgslayerres = md.retrieveData('application/qgis.layertreemodeldata',QVariant(QgsLayerTreeModel).type())
#                 print(qgslayerres)
#                 str1 = str(qgslayerres, encoding='utf-8')
#                 print(str1)
#                 result1 = GetMiddleStr(str1,"source","\" ")
#                 for i in result1:
#                     url = str(i.group())[8:-2]
#                     obj.setCurrentText(url)
                    
#         return super().eventFilter(obj, event)



# def GetMiddleStr(content,startStr,endStr):
#     patternStr = r'%s(.+?)%s'%(startStr,endStr)
#     p = re.compile(patternStr,re.IGNORECASE)
#     m= re.finditer(p,content)
#     return m
    