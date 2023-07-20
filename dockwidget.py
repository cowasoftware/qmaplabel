# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import operator
import os
import sys
import time
#from .core import cpp
from builtins import str

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qgis.core import QgsApplication, QgsProject, QgsSymbolLayer
from qgis.PyQt import QtGui, QtWidgets, uic
from qgis.PyQt.QtWidgets import QProgressBar

from .algorithm import *
from .select_tool import DrawPolygonTool, PointSelectTool

FORM_CLASS, _ = uic.loadUiType(
  os.path.join(os.path.dirname(__file__), 'asset/dockwidget.ui'))

from enum import Enum


class JunctionType(Enum):
  LaneChange, Bump, CrossRoad, CrossWalk = 1,2,3,4
def ActiveLayer(iface, name):
  layers = QgsProject.instance().mapLayersByName(name)
  if layers == None or len(layers) == 0:
    iface.messageBar().pushWarning("CRMAP", '未找到预定义%s层'%name)
    return
  iface.setActiveLayer(layers[0])
  return layers[0]

class SeclectTools:
  def __init__(self, iface):
    self.iface = iface
    self.point_tools = PointSelectTool(self.iface)
    self.line_tools = PointSelectTool(self.iface)
    self.edit_polygon = DrawPolygonTool(self.iface)

  def asNormal(self):
    self.iface.mapCanvas().setMapTool(None)
    self.iface.actionPan().trigger()
  def asLink(self, cbk):
    cursor = QCursor(QPixmap(["16 16 3 1",
                              "      c None",
                              ".     c #FF0000",
                              "+     c #FFFFFF",
                              "                ",
                              "       +.+      ",
                              "      ++.++     ",
                              "     +.....+    ",
                              "    +.     .+   ",
                              "   +.   .   .+  ",
                              "  +.    .    .+ ",
                              " ++.    .    .++",
                              " ... ...+... ...",
                              " ++.    .    .++",
                              "  +.    .    .+ ",
                              "   +.   .   .+  ",
                              "   ++.     .+   ",
                              "    ++.....+    ",
                              "      ++.++     ",
                              "       +.+      "]))
    #cursor.setShape(Qt.SizeHorCursor)
    self.iface.mapCanvas().setCursor(cursor)
    self.iface.mapCanvas().setMapTool(self.point_tools)
    self.point_tools.set(cbk, 6)
  def asPoint(self, cbk):
    cursor = QCursor()
    cursor.setShape(Qt.CrossCursor)
    self.iface.mapCanvas().setCursor(cursor)
    self.iface.mapCanvas().setMapTool(self.point_tools)
    self.point_tools.set(cbk)
  def asJunctionCreate(self, cbk):
    self.edit_polygon.activate()
    self.iface.mapCanvas().setMapTool(self.edit_polygon)
    self.edit_polygon.set(cbk)
###############roads#################

class HDMapProcess:
  def __init__(self, iface):
    self.iface = iface
    self.select_tools = SeclectTools(self.iface)

  lastProcess = [None, None]
  def OnAddParrelLinePoint(self, p, center):
    f = self.iface.activeLayer().selectedFeatures()
    if len(f) != 1: 
      self.select_tools.asNormal()
      self.iface.messageBar().pushInfo("CRMAP", 'Nothing can be done')
      return
    if self.lastProcess[0] != f[0].id():
      self.lastProcess[0] = f[0].id()
      self.lastProcess[1] = None
      print('Process', self.lastProcess[0])
    self.lastProcess[1] = ParallelOffset(f[0], center.get(), self.iface.activeLayer(), self.lastProcess[1])
    self.iface.mapCanvas().refresh()
  def OnAddParrelLine(self):
    l = self.iface.activeLayer()
    f = l.selectedFeatures()
    if len(f) != 1: 
      self.select_tools.asNormal()
      return
    self.select_tools.asPoint(self.OnAddParrelLinePoint)

  def OnDirChangePoint(self, p):
    if p == None:
      self.iface.messageBar().pushWarning("CRMAP", '未找到车道线')
      return
    feature = None
    for i in p:
      if i[0]['type'] >= 7:
        feature = i[0]
        break
    RevertRoad(feature,self.iface.activeLayer())
    self.iface.mapCanvas().refresh()
  def OnDirChange(self):
    if ActiveLayer(self.iface, 'roads') == None: return
    self.select_tools.asPoint(self.OnDirChangePoint)
    
  def OnLaneLink(self, p):
    if p == None:
      self.iface.messageBar().pushWarning("CRMAP", '未找到车道线')
      return
    features = []
    for i in p:
      if i[0]['type'] >= 7: continue
      features.append(i[0])
    if len(features) < 2:
      self.iface.messageBar().pushWarning("CRMAP", '未找到足够的车道线')
      print('未找到足够的车道线', features)
      return
    l1, l2 = features[0], features[1]
    CreateRoad(l1, l2,self.iface.activeLayer(), bidirection = self.bidirection)
    self.iface.mapCanvas().refresh()
  def OnLaneLinkSelect(self):
    self.bidirection = False
    if ActiveLayer(self.iface, 'roads') == None: return
    self.select_tools.asLink(self.OnLaneLink)
  def OnLaneLinkSelect2(self):
    self.bidirection = True
    if ActiveLayer(self.iface, 'roads') == None: return
    self.select_tools.asLink(self.OnLaneLink)
  
  #junction
  def OnLaneChangeDone(self, feature):
    feature.setAttribute('type', JunctionType.LaneChange.value)
    return True # return to the save feature by tools
  def OnLaneChangeCreate(self):
    if ActiveLayer(self.iface, 'junctions') == None: return
    self.select_tools.asJunctionCreate(self.OnLaneChangeDone)

  def OnCrossRoadCreateDone(self, feature):
    feature.setAttribute('type', JunctionType.CrossRoad.value)
    return True # return to the save feature by tools
  def OnCrossRoadCreate(self):
    if ActiveLayer(self.iface, 'junctions') == None: return
    self.select_tools.asJunctionCreate(self.OnCrossRoadCreateDone)

  # 车道方向
  def OnSetDir(self, p):
    layer = self.iface.activeLayer()
    if layer.name() not in ['roads', 'trafficlights']:
      self.iface.messageBar().pushWarning("CRMAP", '图层不对')
      return
    if p == None:
      self.iface.messageBar().pushWarning("CRMAP", '未找到车道线或红绿灯')
      return
    feature = None
    for i in p:
      if layer.name() =='roads' and i[0]['type'] >= 7:
        feature = i[0]
        break
      if layer.name() =='trafficlights' and i[0]['type'] in ["auxline", "light"]:
        feature = i[0]
        break 
    if feature == None:
      return
      
    if self._dir == "DEL": v = ''
    else:
      if type(feature['turn']) == type(self._dir): 
        v = feature['turn'] + '+' + self._dir
      else:
        v = self._dir

    layer.startEditing()

    field_idx = layer.dataProvider().fieldNameIndex('turn')
    layer.changeAttributeValue(feature.id(), field_idx, v)
    self.iface.mapCanvas().refresh()
  def OnAddLeft(self):
    self._dir = 'LEFT'
    self.select_tools.asPoint(self.OnSetDir)
  def OnAddRight(self):
    self._dir = 'RIGHT'
    self.select_tools.asPoint(self.OnSetDir)
  def OnAddForward(self):
    self._dir = 'FORWARD'
    self.select_tools.asPoint(self.OnSetDir)
  def OnAddUturn(self):
    self._dir = 'UTURN'
    self.select_tools.asPoint(self.OnSetDir)
  def OnDelDir(self):
    #if ActiveLayer(self.iface, 'roads') == None: return
    self._dir = 'DEL'
    self.select_tools.asPoint(self.OnSetDir)

  # 车道类型
  def OnSetType(self, p):
    layer = self.iface.activeLayer()
    if layer.name() not in ['roads']:
      self.iface.messageBar().pushWarning("CRMAP", '图层不对')
      return
    if p == None:
      self.iface.messageBar().pushWarning("CRMAP", '未找到车道线')
      return
    feature = None
    for i in p:
      if layer.name() =='roads' and i[0]['type'] >= 7:
        feature = i[0]
        break
    if feature == None:
      return
      

    layer.startEditing()
    field_idx = layer.dataProvider().fieldNameIndex('lane_type')
    layer.changeAttributeValue(feature.id(), field_idx, self._type)
    self.iface.mapCanvas().refresh()
  def OnSetCar(self):
    self._type = 2
    self.select_tools.asPoint(self.OnSetType)
  def OnSetBike(self):
    self._type = 3
    self.select_tools.asPoint(self.OnSetType)
  def OnSetSidewalk(self):
    self._type = 4
    self.select_tools.asPoint(self.OnSetType)

  def OnSplitLinePoint(self, p, center):
    if p == None:
      self.iface.messageBar().pushWarning("CRMAP", '未找到车道线')
      return
    feature = None
    for i in p:
      if i[0]['type'] <= 7:
        feature = i[0]
        break
    if feature == None: feature = p[0][0]
    SplitLane(feature, center.get(),self.iface.activeLayer())
    self.iface.mapCanvas().refresh()
  def OnSplitLine(self):
    if ActiveLayer(self.iface, 'roads') == None: return
    self.select_tools.asPoint(self.OnSplitLinePoint)
  

class HDMapDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

  closingPlugin = pyqtSignal()

  def __init__(self, iface, process, parent=None):
    self.process = process
    super(HDMapDockWidget, self).__init__(parent)

    self.setupUi(self)

    self.iface = iface

    main_layout = QtWidgets.QVBoxLayout(self.fra_main)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    self.frame_top = QtWidgets.QFrame(self.fra_main)
    frame_top_layout = QtWidgets.QFormLayout(self.frame_top)
    self.frame_bottom = QtWidgets.QFrame(self.fra_main)
    frame_bottom_layout = QtWidgets.QFormLayout(self.frame_bottom)

    self.btn_lane_points = QtWidgets.QPushButton("添加道路中心线")
    self.btn_lane_points.pressed.connect(self.OnBtnCenter)
    frame_bottom_layout.addRow(self.btn_lane_points)

    self.lbl_data_layer = QtWidgets.QLabel('边界车道宽度:')
    self.lane_width = QtWidgets.QDoubleSpinBox()
    self.lane_width.setRange(2, 6)
    self.lane_width.setSingleStep(0.1)
    self.lane_width.setValue(3.5)
    frame_bottom_layout.addRow(self.lbl_data_layer, self.lane_width)

    self.btn_merge = QtWidgets.QPushButton('合并车道线')
    self.btn_merge.pressed.connect(self.onBtnMerge)
    frame_bottom_layout.addRow(self.btn_merge)

    self.btn_parrel_other = QtWidgets.QPushButton('平行于另外一边')
    self.btn_parrel_other.pressed.connect(self.OnBtnParrel)
    frame_bottom_layout.addRow(self.btn_parrel_other)

    self.btn_lane_link = QtWidgets.QPushButton('删除自动车道')
    self.btn_lane_link.pressed.connect(self.OnBtnDel)
    frame_bottom_layout.addRow(self.btn_lane_link)

    frame_bottom_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.addWidget(self.frame_top)
    main_layout.addWidget(self.frame_bottom)
    main_layout.addSpacerItem(
      QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Minimum,
                  QtWidgets.QSizePolicy.Expanding))
    
    self.btn_gen_map = QtWidgets.QPushButton('生成地图')
    self.btn_gen_map.pressed.connect(self.OnBtnConvert)
    frame_bottom_layout.addRow(self.btn_gen_map)

  def closeEvent(self, event):
    self.closingPlugin.emit()
    event.accept()

  def getAllLayerName(self):
    layers_name = []

    return layers_name

  def OnBtnCenter(self):
    l = self.iface.activeLayer()
    f = l.selectedFeatures()
    if len(f) != 1 or 'Road' != f[0]['type']: 
      self.iface.messageBar().pushWarning("CRMAP", '未选择道路区域')
      return

    r = JunctionRoad(f[0])
    line = r.CreateCenterLine()

  def onBtnMerge(self):
    f = self.iface.activeLayer().selectedFeatures()
    if len(f) <= 1 or self.iface.activeLayer().name() not in ['roads']: 
      self.iface.messageBar().pushInfo("CRMAP", 'Nothing can be done')
    MergeLine(f,self.iface.activeLayer())
    self.iface.mapCanvas().refresh()
  def OnBtnParrel(self):
    l = self.iface.activeLayer()
    if l.name() != 'roads':
      self.iface.messageBar().pushWarning("CRMAP", '图层不对')
      return
    lines = l.selectedFeatures()
    g = lines[0].geometry()
    dists = []
    for junction in GetFeature('junctions', "type = 'Road'"):
      s = g.intersection(junction.geometry())
      if s and AsLineString(s).length > 5:
        r = JunctionRoad(junction)
        r.ParallelOther(lines)

  def OnBtnDel(self):
    pass

  def OnBtnConvert(self):
    import os
    import threading

    import requests
    files = []
    project = QgsProject()
    for (k, v) in QgsProject.instance().mapLayers().items():
      if v.name() in ['车道', '马路牙', '停止线', '红绿灯', '人行道', '停车位', '地面标识', '行驶轨迹', 'roads', 'trafficlights', 'junctions', 'park']:
        uri = v.dataProvider().uri().uri()
        if 'gpkg' not in uri: continue
        file = uri.split('|')[0].strip()
        if file not in files: files.append(file)
        layer = QgsVectorLayer(uri.strip().replace("'",''), v.name(), "ogr")
        if not layer.isValid(): 
          logger.error(uri)
          continue
        project.addMapLayer(layer, True)
        project.setCrs(layer.crs())
    workdir = QgsProject.instance().absolutePath()
    project.write(os.path.join(workdir, "tmp.qgz"))
    del project
    files.append(os.path.join(workdir, "tmp.qgz"))

    self.btn_gen_map.setEnabled(False)
    self.thread_convert = threading.Thread(target=self.AsyncConvert, args=(workdir, files))
    self.thread_convert.run()

  def AsyncConvert(self, workdir, files):
    import os

    import requests
    def HdmapConvert(uploads, output):
      files = []
      for i in uploads:
        if i[-5:] == '.gpkg':
          files.append(('gpkg', (os.path.basename(i), open(i, 'rb'), "application/binary")))
        if i[-4:] == '.qgz':
          files.append(('qgis', (os.path.basename(i), open(i, 'rb'), "application/binary")))

      try: r = requests.post('http://map.cowarobot.com/basemap/v1/convert', files=files)
      except:
        self.iface.messageBar().pushMessage("Error", "Error Connection")
        return "Error Connection"
      if r.status_code == 200:
        with open(output, 'wb') as f: 
          f.write(r.content)
          f.close()
        self.iface.messageBar().pushMessage("OK", "hdmap.bin saved", level=Qgis.Info)
        return
      open(output.replace('.bin', '.error.log'), 'wb').write(r.content)
      self.iface.messageBar().pushMessage("Error", "Error %d: %s"%(r.status_code, r.content), level=Qgis.Critical)
    HdmapConvert(files, os.path.join(workdir, "hdmap.bin"))
    self.btn_gen_map.setEnabled(True)