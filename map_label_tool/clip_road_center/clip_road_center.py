import os
import re

from PyQt5.QtWidgets import QDialog, QFileDialog
from qgis.core import QgsProject

from ...utils import *
from ..update_attribute import *
from .clip_road_center_alg import *
from .clip_road_center_ui import *


class clip_road_center(QDialog):
    def __init__(self,parent=None,iface=None):
        super().__init__(parent)
        self.iface = iface
        self.ui_data = Ui_Dialog_clip_center()
        #self.setWindowFlags(QtCore.Qt.WindowType.Tool)
        self.ui_data.setupUi(self)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        for i in range(0,len(QgsProject.instance().mapLayers().keys())):
            id = list(QgsProject.instance().mapLayers().keys())[i]
            vectorlayer = QgsProject.instance().mapLayers()[id]
            self.ui_data.comboBox_break.addItem(vectorlayer.source())
            self.ui_data.comboBox_road.addItem(vectorlayer.source())
            self.ui_data.comboBox_junction.addItem(vectorlayer.source())
        self.ui_data.comboBox_break.setAcceptDrops(True)
        self.ui_data.comboBox_road.setAcceptDrops(True)
        self.ui_data.comboBox_junction.setAcceptDrops(True)
        self.ui_data.comboBox_break.setEditable(True)
        self.ui_data.comboBox_road.setEditable(True)
        self.ui_data.comboBox_junction.setEditable(True)
        self.ui_data.comboBox_break.setCurrentIndex(-1)
        self.ui_data.comboBox_road.setCurrentIndex(-1)
        self.ui_data.comboBox_junction.setCurrentIndex(-1)
        self.ui_data.comboBox_break.installEventFilter(QEventHandler(self))
        self.ui_data.comboBox_road.installEventFilter(QEventHandler(self))
        self.ui_data.comboBox_junction.installEventFilter(QEventHandler(self))
        self.ui_data.btn_center_layer.clicked.connect(self.btn_choose_center_data)
        self.ui_data.btn_break_layer.clicked.connect(self.btn_choose_break_data)
        self.ui_data.btn_add_layer.clicked.connect(self.btn_add_layer)
        self.ui_data.btn_remove_layer.clicked.connect(self.btn_remove_layer)
        self.ui_data.btn_run.clicked.connect(self.btn_run)
        self.ui_data.listWidget.setAcceptDrops(True)
        self.ui_data.btn_center_layer.hide()
        self.ui_data.comboBox_road.currentTextChanged.connect(self.btn_add_layer)
    
    def btn_choose_center_data(self):
        center_data =  QFileDialog.getOpenFileName(None, "中心线", "./",'*.shp') 
        self.ui_data.comboBox_road.setCurrentText(center_data[0])
    def btn_choose_break_data(self):
        junction_data  =  QFileDialog.getOpenFileName(None, "路口线", "./",'*.shp') 
        self.ui_data.comboBox_break.setCurrentText(junction_data[0])
    def btn_run(self):
        items_count = self.ui_data.listWidget.count()
        break_layer = QgsVectorLayer(self.ui_data.comboBox_break.currentText(),"break_layer","ogr")
        junction_layer = QgsVectorLayer(self.ui_data.comboBox_junction.currentText(),"junction_layer","ogr")
        if_break = self.ui_data.checkBox_direction.isChecked()
        for i in range(0,items_count):
            center_layer_url = self.ui_data.listWidget.item(i).text()
            if("hd_center" in center_layer_url): 
                center_layer = QgsVectorLayer(center_layer_url,"hd_center","ogr")
            elif ("hd_boundary" in center_layer_url):
                center_layer = QgsVectorLayer(center_layer_url,"hd_boundary","ogr")
            else:
                center_layer = QgsVectorLayer(center_layer_url,"line_layer","ogr")
            #判断路口的type 和 check
            # boundary_multi_list = is_multipart_geometry(center_layer)
            # if(len(boundary_multi_list)>0):
            #     idtext = ",".join(boundary_multi_list)
            #     self.iface.messageBar().pushMessage(center_layer_url+"存在多部件,fid为:"+idtext, Qgis.MessageLevel.Critical, 5)
            #     continue
            if(center_layer.geometryType()!= QgsWkbTypes.GeometryType.LineGeometry):
                continue
            clip_center_and_fill_link(break_layer,center_layer,junction_layer,if_break)
    def btn_add_layer(self):
        if(os.path.isfile(self.ui_data.comboBox_road.currentText())):
            self.ui_data.listWidget.addItem(self.ui_data.comboBox_road.currentText()) 
            self.ui_data.comboBox_road.setCurrentIndex(-1)
    def btn_remove_layer(self):
        
        self.ui_data.listWidget.takeItem(self.ui_data.listWidget.currentIndex().row())
class QEventHandler1(QtCore.QObject):
    def eventFilter(self, obj, event):
        """
        处理窗体内出现的事件，如果有需要则自行添加if判断语句；
        目前已经实现将拖到控件上文件的路径设置为控件的显示文本；
        """
        if event.type() == QtCore.QEvent.DragEnter:
            event.accept()
        if event.type() == 60:
            md = event.mimeData()
            if('application/qgis.layertreemodeldata' in md.formats()):
                qgslayerres = md.retrieveData('application/qgis.layertreemodeldata',QVariant(QgsLayerTreeModel).type())
                print(qgslayerres)
                str1 = str(qgslayerres, encoding='utf-8')
                print(str1)
                result1 = GetMiddleStr1(str1,"source=\"","\"")
                for i in result1:
                    url = str(i.group())[8:-1]
                    obj.addItem(url)
                    
        return super().eventFilter(obj, event)



def GetMiddleStr1(content,startStr,endStr):
    patternStr = r'%s(.+?)%s'%(startStr,endStr)
    p = re.compile(patternStr,re.IGNORECASE)
    m= re.finditer(p,content)
    return m