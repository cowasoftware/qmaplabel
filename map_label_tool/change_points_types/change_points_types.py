import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QAction, QButtonGroup, QDialog, QFileDialog,
                             QMainWindow, QMessageBox, QRadioButton,
                             QScrollArea, QVBoxLayout)
from qgis.core import (QgsApplication, QgsExpression, QgsFeature,
                       QgsFeatureRequest, QgsField, QgsFields, QgsGeometry,
                       QgsPoint, QgsProject, QgsSpatialIndex,
                       QgsVectorFileWriter, QgsVectorLayer, QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant

from .change_points_types_ui import *
from .RectangleMapTool import *


class change_points_types_dialog(QDialog):
    def __init__(self, iface,layer,parent=None):
        super().__init__(parent)
        self.dict_points_type_list = [ 
            0,1,2,3,4,5,6,7,8
        ]
        self.setWindowFlags(QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.dict_points_type_name = [
            "未知","黄虚","白虚","黄实","白实","双黄","马路牙子","空白","栅栏"
        ]
        self.iface = iface
        self.layer = layer
        self.ui_data = Ui_Dialog_ChangePointsType()
        self.ui_data.setupUi(self)
        vLayout = QVBoxLayout()
        self.Button_Group = QButtonGroup()
        for i in range(0,len(self.dict_points_type_list)):
            radio =  QRadioButton(self.dict_points_type_name[i]+":"+ str(self.dict_points_type_list[i]),self.ui_data.scrollAreaWidgetContents)
            vLayout.addWidget(radio)
            self.Button_Group.addButton(radio)
            if(i==0):
                radio.setChecked(True)
        vLayout.addStretch(1)
        self.ui_data.scrollAreaWidgetContents.setLayout(vLayout)
        self.ui_data.btn_start_change.clicked.connect(self.btn_start_change_void)
        self.ui_data.btn_endDraw.clicked.connect(self.end_draw)
        self.ui_data.btn_save.clicked.connect(self.save_result)
        self.ui_data.btn_draw_tool.clicked.connect(self.draw_tool)
        self.drawPolygonEvent =  RectangleMapTool(self.iface.mapCanvas())
        self.drawPolygonEvent.rectangleCreated.connect(self.draw_result_trigger)
        self.isEdit=False
        self.update_line_ids=[]
        #记录发生变化率的lineid 即可 line 全部更新
        
        #self.temp_dir.show()
    def draw_tool(self):
        self.iface.mapCanvas().setMapTool(self.drawPolygonEvent)
        
    def draw_result_trigger(self,polygon):
        willChange = {}
        check_text = self.Button_Group.checkedButton().text()
        value = int(check_text.split(":")[1])
        intersect_ids = self.points_indexs.intersects(polygon)
        
        for i in range(0,len(intersect_ids)):
            willChange[intersect_ids[i]]={1:value}
        #修改这些id 为value
        #对于相交id而言 需要找到对应的lineid  根据line id 记录返回的number数字

        request = QgsFeatureRequest()
        request.setFilterFids(intersect_ids)
        res = list(self.newVl.getFeatures(request))
        
        #第一步只记录id
        for feature in res:
            line_id = feature['line_id']
            if(line_id not in self.update_line_ids):
                self.update_line_ids.append(line_id)
        
        self.newVl.dataProvider().changeAttributeValues(willChange)
        self.newVl.updateExtents()
        self.newVl.triggerRepaint()
        self.iface.mapCanvas().refresh()

        
    def btn_start_change_void(self):
        if(self.isEdit):
            self.iface.messageBar().pushInfo("CRMAP", 'already in the editing state')
            return
        self.isEdit=True
        #生成临时点图层
        EPSGID = self.layer.crs().authid()
        create_string = "point?"
        create_string= create_string+ "crs="+EPSGID
        self.newVl = QgsVectorLayer(create_string, "temporary_points", "memory")
        pr = self.newVl.dataProvider()
        pr.addAttributes([
            QgsField("id", QVariant.Int),
            QgsField("type", QVariant.Int),
            QgsField("line_id",QVariant.Int),
            QgsField("points_order",QVariant.Int)
        ])
        self.newVl.updateFields() 
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        fields.append(QgsField("type", QVariant.Int))
        fields.append(QgsField("line_id", QVariant.Int))
        fields.append(QgsField("points_order", QVariant.Int))
        will_add_point_features=[]
        feas = list(self.layer.getFeatures())
        order_index = feas[0].fieldNameIndex("pnt_types")
        if(order_index==-1):
            return 
        for i in range(0,len(feas)):
            feature = feas[i]
            geom = feature.geometry()
            line = None
            if(QgsWkbTypes.isMultiType(geom.wkbType())):
                multi_line = geom.asMultiPolyline()
                line = multi_line[0]
            else:
                line = geom.asPolyline()
            pnt_types = feature['pnt_types']
            
            pnts_value_list = analyse_pnt_types(pnt_types)
            if(len(pnts_value_list)!=len(line)):
                for j in range(0,len(line)):
                    will_add_point_fea = QgsFeature()
                    will_add_point_fea.setGeometry(QgsGeometry.fromPointXY(line[j]))
                    will_add_point_fea.setAttributes([len(will_add_point_features),0,feature.id(),j])
                    will_add_point_features.append(will_add_point_fea)
            else:
                for j in range(0,len(line)):
                    will_add_point_fea = QgsFeature()
                    will_add_point_fea.setGeometry(QgsGeometry.fromPointXY(line[j]))
                    will_add_point_fea.setAttributes([len(will_add_point_features),pnts_value_list[j],feature.id(),j])
                    will_add_point_features.append(will_add_point_fea)
        pr.addFeatures(will_add_point_features)
        self.newVl.updateExtents()
        self.newVl.loadNamedStyle(":/COWA/boundaray_points_type.qml")
        QgsProject.instance().addMapLayer(self.newVl)
        
        self.iface.mapCanvas().setMapTool(self.drawPolygonEvent)
        
        self.points_indexs = QgsSpatialIndex(self.newVl.getFeatures())
        
    def save_result(self):
        if (len(self.update_line_ids)==0):
            return
        willChange={} 
        for i in range(0,len(self.update_line_ids)):
            
            id = self.update_line_ids[i]
            request = QgsFeatureRequest()
            request.setFilterFid(id)
            res = list(self.layer.getFeatures(request))
            line_feature = res[0]
            print("id:",line_feature['id'])
            #这是要修改的listtype
            if(QgsWkbTypes.isMultiType(line_feature.geometry().wkbType())):
                multi_line = line_feature.geometry().asMultiPolyline()
                line = multi_line[0]
            else:
                line = line_feature.geometry().asPolyline()
            
            line_feature_pnt_types_list = analyse_pnt_types(line_feature['pnt_types'])
            
            if(len(line_feature_pnt_types_list)!=len(line)):
                line_feature_pnt_types_list = [0]*len(line)

            exp1 = QgsExpression("line_id = "+ str(id))
            request1 = QgsFeatureRequest(exp1)
            res1 = list(self.newVl.getFeatures(request1))
            for j  in range(0,len(res1)):
                point_fea = res1[j]
                order = res1[j]['points_order']
                line_feature_pnt_types_list[order]=point_fea['type']
                
            line_feature_pnt_types_str = convert_pnt_types(line_feature_pnt_types_list)
            pnt_types_index = line_feature.fieldNameIndex("pnt_types")
            willChange[id]={pnt_types_index:line_feature_pnt_types_str}
        self.layer.dataProvider().changeAttributeValues(willChange)
        self.layer.updateExtents()
        self.layer.triggerRepaint()
        self.iface.mapCanvas().refresh()        
        self.update_line_ids=[]
        

    def end_draw(self):
        if(self.isEdit):
            self.isEdit=False
        else:
            return
        QgsProject.instance().removeMapLayer(self.newVl)
        self.iface.mapCanvas().refresh()
        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())

    def closeEvent(self, event):
        # 创建一个消息盒子（提示框）
        if(len(self.update_line_ids)>0):
            quitMsgBox = QMessageBox()
            # 设置提示框的标题
            quitMsgBox.setWindowTitle('确认提示')
            # 设置提示框的内容
            quitMsgBox.setText('尚未保存编辑，是否保存？')
            # 设置按钮标准，一个yes一个no
            quitMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            # 获取两个按钮并且修改显示文本
            buttonY = quitMsgBox.button(QMessageBox.Yes)
            buttonY.setText('确定')
            buttonN = quitMsgBox.button(QMessageBox.No)
            buttonN.setText('取消')
            quitMsgBox.exec_()
            if quitMsgBox.clickedButton() == buttonY:
                self.save_result()
        if(self.isEdit):
            quitMsgBox = QMessageBox()
            # 设置提示框的标题
            quitMsgBox.setWindowTitle('确认提示')
            # 设置提示框的内容
            quitMsgBox.setText('尚未结束编辑，是否结束？')
            # 设置按钮标准，一个yes一个no
            quitMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            # 获取两个按钮并且修改显示文本
            buttonY = quitMsgBox.button(QMessageBox.Yes)
            buttonY.setText('确定')
            buttonN = quitMsgBox.button(QMessageBox.No)
            buttonN.setText('取消')
            quitMsgBox.exec_()
            # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
            if quitMsgBox.clickedButton() == buttonY:
                self.isEdit=False
                QgsProject.instance().removeMapLayer(self.newVl)
                self.iface.mapCanvas().refresh()
                self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())
        self.iface.mapCanvas().unsetMapTool(self.iface.mapCanvas().mapTool())
def analyse_pnt_types(pnt_types):
    result = []
    if (str(pnt_types)=="Null" or str(pnt_types)=="" or str(pnt_types)=="NULL"):
        return result
    pnt_types_list = pnt_types.split(",")
    for i in range(0,int(len(pnt_types_list)/2)):
        list1 = [int(pnt_types_list[i*2+1])]*int(pnt_types_list[i*2])
        result.extend(list1)
    return result
    
def convert_pnt_types(pnt_types_list):

    result_list=[]
    for i in range(0,len(pnt_types_list)):
        if(len(result_list)==0 or result_list[-1]!=pnt_types_list[i]):
            result_list.append(1)
            result_list.append(pnt_types_list[i])
        else:
            result_list[-2] = result_list[-2] + 1
    for i in range(0,len(result_list)):
        result_list[i]=str(result_list[i])
    return ",".join(result_list)
       
   
        
        
    
   
    