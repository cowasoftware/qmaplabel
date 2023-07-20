# -*- coding: utf-8 -*-

import json
import os.path
from builtins import object

from qgis.PyQt.QtCore import (QCoreApplication, QRect, QSettings, Qt,
                              QTranslator, qVersion)
from qgis.PyQt.QtGui import QIcon, QKeySequence
from qgis.PyQt.QtWidgets import (QAction, QLabel, QLineEdit, QMenu, QShortcut,
                                 QWidget)

from .asset import resources
from .dockwidget import HDMapDockWidget, HDMapProcess
from .map_label_tool.clip_center_class import HDMapClipCenter
from .map_label_tool.create_junction_road_class import HDMapConnectJunctionRoad
from .map_label_tool.update_attribute_class import HDMapUpdateAttributes


class HDMap(object):
  def __init__(self, iface):
    """Constructor.

    :param iface: An interface instance that will be passed to this class
      which provides the hook by which you can manipulate the QGIS
      application at run time.
    :type iface: QgsInterface
    """
    # Save reference to the QGIS interface
    self.iface = iface

    # initialize plugin directory
    self.plugin_dir = os.path.dirname(__file__)

    # initialize locale
    locale = QSettings().value('locale/userLocale')[0:2]
    locale_path = os.path.join(
      self.plugin_dir,
      'i18n',
      'SmoothLine_{}.qm'.format(locale))

    if os.path.exists(locale_path):
      self.translator = QTranslator()
      self.translator.load(locale_path)

      if qVersion() > '4.3.3':
        QCoreApplication.installTranslator(self.translator)

    self.pluginIsActive = False
    self.dockwidget = None
    self.process = HDMapProcess(self.iface)
    self.process1 = HDMapUpdateAttributes(self.iface)
    self.process2 = HDMapClipCenter(self.iface)
    self.process3 = HDMapConnectJunctionRoad(self.iface)
  def initGui(self):
    """Create the menu entries and toolbar icons inside the QGIS GUI."""
    
    self.action = QAction(QIcon(':/COWA/icon.png'), '图形界面', self.iface.mainWindow())
    self.action.setEnabled(True)
    self.action.triggered.connect(self.run)

    # Add toolbar button and menu item
    self.iface.pluginToolBar().addAction(self.action)
    self.iface.pluginMenu().addAction(self.action)
    



   
    

    self.toolbar1 = self.iface.addToolBar("convert_data")
    self.update_boundary_points_type = QAction(QIcon(":/COWA/change_points_type.png"),"修改points_type", self.iface.mainWindow())
    self.update_boundary_points_type.triggered.connect(self.process1.update_boundary_points_type)
    self.toolbar1.addAction(self.update_boundary_points_type)
    
    self.toolbar = self.iface.addToolBar("COWA HDMAP")
    
    self.link_road = QAction(QIcon(":/COWA/link_road.png"),"添加关联车道", self.iface.mainWindow())
    self.link_road.triggered.connect(self.process.OnLaneLinkSelect)
    self.toolbar.addAction(self.link_road)

    self.link_road2 = QAction(QIcon(":/COWA/bidirection.jpg"),"添加双向车道", self.iface.mainWindow())
    self.link_road2.triggered.connect(self.process.OnLaneLinkSelect2)
    self.toolbar.addAction(self.link_road2)
    
    self.lane_change = QAction(QIcon(":/COWA/lane_change.png"), "添加变道区", self.iface.mainWindow())
    self.lane_change.triggered.connect(self.process.OnLaneChangeCreate)
    self.toolbar.addAction(self.lane_change)

    self.crossroad = QAction(QIcon(":/COWA/crossroad.jpg"), "添加路口区域", self.iface.mainWindow())
    self.crossroad.triggered.connect(self.process.OnCrossRoadCreate)
    self.toolbar.addAction(self.crossroad)


    self.limit_speed = QAction(QIcon(":/COWA/speed.jpg"), "添加限速", self.iface.mainWindow())
    #self.limit_speed.triggered.connect(self.process.OnLaneChangeCreate)
    self.toolbar.addAction(self.limit_speed)

    self.parrel = QAction(QIcon(":/COWA/parrel.jpg"), "添加平行线", self.iface.mainWindow())
    self.parrel.triggered.connect(self.process.OnAddParrelLine)
    self.parrel.setShortcut("CTRL+ALT+C") 
    self.toolbar.addAction(self.parrel)


    self.dir_change = QAction(QIcon(":/COWA/changedir.jpg"), "调整方向", self.iface.mainWindow())
    self.dir_change.triggered.connect(self.process.OnDirChange)
    self.toolbar.addAction(self.dir_change)

    self.add_left = QAction(QIcon(":/COWA/left.jpg"), "左转", self.iface.mainWindow())
    self.add_left.triggered.connect(self.process.OnAddLeft)
    self.add_left.setShortcut("L") 
    self.toolbar.addAction(self.add_left)

    self.add_right = QAction(QIcon(":/COWA/right.jpg"), "右转", self.iface.mainWindow())
    self.add_right.triggered.connect(self.process.OnAddRight)
    self.add_right.setShortcut("R") 
    self.toolbar.addAction(self.add_right)

    self.add_forward = QAction(QIcon(":/COWA/forward.jpg"), "直行", self.iface.mainWindow())
    self.add_forward.triggered.connect(self.process.OnAddForward)
    self.add_forward.setShortcut("CTRL+T") 
    self.toolbar.addAction(self.add_forward)

    self.add_uturn = QAction(QIcon(":/COWA/uturn.jpg"), "掉头", self.iface.mainWindow())
    self.add_uturn.triggered.connect(self.process.OnAddUturn)
    self.add_uturn.setShortcut("U") 
    self.toolbar.addAction(self.add_uturn)

    self.no_dir = QAction(QIcon(":/COWA/no_dir.jpg"), "删除方向", self.iface.mainWindow())
    self.no_dir.triggered.connect(self.process.OnDelDir)
    self.toolbar.addAction(self.no_dir)


    self.add_car = QAction(QIcon(":/COWA/car.jpg"), "机动车道", self.iface.mainWindow())
    self.add_car.triggered.connect(self.process.OnSetCar)
    self.add_car.setShortcut("CTRL+2") 
    self.toolbar.addAction(self.add_car)

    self.add_bike = QAction(QIcon(":/COWA/bike.jpg"), "非机动车道", self.iface.mainWindow())
    self.add_bike.triggered.connect(self.process.OnSetBike)
    self.add_bike.setShortcut("CTRL+3") 
    self.toolbar.addAction(self.add_bike)

    self.add_sidewalk = QAction(QIcon(":/COWA/sidewalk.jpg"), "人行道", self.iface.mainWindow())
    self.add_sidewalk.triggered.connect(self.process.OnSetSidewalk)
    self.add_sidewalk.setShortcut("CTRL+4") 
    self.toolbar.addAction(self.add_sidewalk)


    self.split_line = QAction(QIcon(":/COWA/split.jpg"), "切割车道线", self.iface.mainWindow())
    self.split_line.triggered.connect(self.process.OnSplitLine)
    self.toolbar.addAction(self.split_line)
    menuBar = self.iface.mainWindow().menuBar()
    
    
    #环卫云地图
    self.sanitation_cloud_menu = QMenu(self.iface.mainWindow())
    self.sanitation_cloud_menu.setTitle("地图工具")
    self.update_center_line_up_down_ids = QAction(QIcon(":/COWA/update_up_down_ids.png"),"更新中心线上下游节点", self.iface.mainWindow())
    self.update_center_line_up_down_ids.triggered.connect(self.process1.update_center_line_up_down_ids)
    self.sanitation_cloud_menu.addAction(self.update_center_line_up_down_ids)
    self.update_junction_line_up_down_ids = QAction(QIcon(":/COWA/update_up_down_ids.png"),"更新路口线上下游节点", self.iface.mainWindow())
    self.update_junction_line_up_down_ids.triggered.connect(self.process1.update_junction_line_up_down_ids)
    self.sanitation_cloud_menu.addAction(self.update_junction_line_up_down_ids)
    self.clip_center_and_fill_link = QAction(QIcon(":/COWA/clip_lines.png"), "裁剪线图层", self.iface.mainWindow())
    self.clip_center_and_fill_link.triggered.connect(self.process2.clip_center_and_fill_link)
    self.sanitation_cloud_menu.addAction(self.clip_center_and_fill_link)
    self.create_junction_road = QAction(QIcon(":/COWA/create_junction_lines.png"), "创建路口道路", self.iface.mainWindow())
    self.create_junction_road.triggered.connect(self.process3.create_junction_road)
    self.sanitation_cloud_menu.addAction(self.create_junction_road)
    menuBar.addMenu(self.sanitation_cloud_menu)
    
    
    
  
    
  def onClosePlugin(self):
    # disconnects
    self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
    # self.dockwidget = None
    self.pluginIsActive = False

  def unload(self):
    """Removes the plugin menu item and icon from QGIS GUI."""
    self.iface.pluginMenu().removeAction(self.action)
    self.iface.pluginToolBar().removeAction(self.action)

    del self.toolbar
    del self.toolbar1

    
    self.sanitation_cloud_menu.deleteLater()
   


  def run(self):
    """Run method that loads and starts the plugin"""
    if not self.pluginIsActive:
      self.pluginIsActive = True

      if self.dockwidget == None:
        self.dockwidget = HDMapDockWidget(self.iface, self.process)

      # connect to provide cleanup on closing of dockwidget
      self.dockwidget.closingPlugin.connect(self.onClosePlugin)

      # show the dockwidget
      self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
      self.dockwidget.show()

