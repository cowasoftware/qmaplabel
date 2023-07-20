from __future__ import print_function
from __future__ import absolute_import
from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import operator

def FindClicked(iface, mouse_pt, layer, width):
  if type(layer) is not QgsVectorLayer:
    return
  #print(iface.mapCanvas().mapUnitsPerPixel(), width)
  #width = width / iface.mapCanvas().mapUnitsPerPixel()
  rect = QgsRectangle(mouse_pt.x() - width,
                      mouse_pt.y() - width,
                      mouse_pt.x() + width,
                      mouse_pt.y() + width)

  center = QgsGeometry.fromPointXY(QgsPointXY(mouse_pt.x(), mouse_pt.y()))

  request = QgsFeatureRequest(rect)
  feats = layer.getFeatures(request)
  
  dists_d = {}
  for feat in feats:
    dist = feat.geometry().distance(center)
    if dist > width:
      continue
    dists_d[feat] = dist
        
  if len(dists_d) == 0:
    if iface:
      iface.messageBar().pushInfo("CRMAP",
        'Nothing can be selected, perhaps you have not activated the correct layer or select EPSG of map')  # TODO: softcode
    return [], center
  
  sorted_dists = sorted(list(dists_d.items()), key=operator.itemgetter(1))
  #print(sorted_dists[0][0].fields())
  #print(sorted_dists[0][0].geometry())
  return sorted_dists, center

class PointSelectTool(QgsMapTool):
  def __init__(self, iface, callback = None):
    self.iface = iface
    self.callback = callback
    self.width = 0.5
    super(PointSelectTool, self).__init__(self.iface.mapCanvas())

  def canvasReleaseEvent(self, event):
    layer = self.iface.activeLayer()
    self.mouse_pt = self.toLayerCoordinates(layer, event.pos())
    p, center = FindClicked(self.iface, self.mouse_pt, layer, self.width)
    # self.iface.messageBar().pushInfo("CRMAP", str(p))
    if event.button() == Qt.LeftButton:
      if self.callback is not None:
        if self.callback.__code__.co_argcount == 2: self.callback(p)
        else: self.callback(p, center)
  def set(self, cbk, width = 0.5):
    self.callback = cbk
    self.width = width
  
class DrawPolygonTool(QgsMapTool):
  def __init__(self, iface, isPolygon = True):
    QgsMapTool.__init__(self, iface.mapCanvas())
    self.iface = iface
    self.canvas = iface.mapCanvas()
    self.isPolygon = isPolygon
    # Create an empty rubber band
    if self.isPolygon:
      self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry ) # BMF for reference: Polygon > rubberband interior is filled in
    else:
      self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry ) #BMF Line > interior not filled (what we want for EntryLines)
    # Create an empty list for vertex marker
    self.vertexMarkers = []
    # Create an empty list to store the new vertices
    self.captureList = []
    self.cursor = QCursor(QPixmap(["16 16 3 1",
                          "      c None",
                          ".     c #000000",
                          "+     c #ffffff",
                          "                ",
                          "       +.+      ",
                          "      ++.++     ",
                          "     +.....+    ",
                          "    +.  .  .+   ",
                          "   +.   .   .+  ",
                          "  +.    .    .+ ",
                          " ++.    .    .++",
                          " ... ...+... ...",
                          " ++.    .    .++",
                          "  +.    .    .+ ",
                          "   +.   .   .+  ",
                          "   ++.  .  .+   ",
                          "    ++.....+    ",
                          "      ++.++     ",
                          "       +.+      "]))
    self.isAvoidingIntersection = False
    self.cbk = None

  def canvasPressEvent(self, event):
    self.rubberBand.setColor(QColor(255, 0, 0, 150))
    self.rubberBand.setWidth(1)
    #self.rubberBand.show()
    
    # Captures the clicked coordinate and transform
    mapCoordinates = self.toMapCoordinates(event.pos())
    # Check if it's a normal or a right click
    if(event.button() == Qt.RightButton):
      self.finishFeature(mapCoordinates)
    else:
      self.addVertex(mapCoordinates)
  def canvasMoveEvent(self, event):
    self.moveVertex(self.toMapCoordinates(event.pos()))
    pass
  def canvasReleaseEvent(self, event):
    pass
  def activate(self):
    QgsMapTool.activate(self)
    self.canvas.setCursor(self.cursor)
  def deactivate(self):
    try:
        self.emit(SIGNAL("deactivated()"))
    except:
        pass
    pass
  def isZoomTool(self):
    return False
  def isTransient(self):
    return False
  def isEditTool(self):
    return True

  def addVertex(self, pt):
    self.captureList.append(pt)
    self.rubberBand.addPoint(pt)
    m = QgsVertexMarker(self.canvas)
    m.setCenter(pt)
    self.vertexMarkers.append(m)
  def moveVertex(self, pt):
    if self.rubberBand.numberOfVertices() > 1:
      self.rubberBand.movePoint(pt)
  def set(self, cbk):
    self.cbk = cbk
  def finishFeature(self, pt):
    layer = self.iface.activeLayer()
    if len(self.captureList) == 0:
      self.clearMapCanvas()
      selected, center = FindClicked(self.iface, pt, layer, 1)
        
      if len(selected) > 0:
        s = selected[0][0]
        self.cbk(s)
      return
    if self.isPolygon:
      if not len(self.captureList) >= 3:
        QMessageBox.critical(self.canvas,"Not enough vertices", "Cannot close a polygon feature until it has at least three vertices.")
        self.clearMapCanvas()
        return
      if layer.wkbType() % 1000 == QgsWkbTypes.Polygon:
        geometry = QgsGeometry().fromPolygonXY([self.captureList])
      elif layer.wkbType() % 1000 == QgsWkbTypes.LineString:
        geometry = QgsGeometry().fromPolyline([QgsPoint(p.x(), p.y()) for p in self.captureList])

      # Handle avoiding intersections
      if self.isAvoidingIntersection:
        layer.removePolygonIntersections(geometry)

        # We need to check if the removePolygonIntersections method has changed the new
        # geometry to a multipolygon. If yes, we cannot add the new geometry to the
        # PostGIS layer, since this will break the geometry constraints in PostGIS
        if layer.wkbType() == QGis.WKBPolygon and geometry.isMultipart():
          # Throw the same error like qgsmaptooladdfeature.cpp
          QMessageBox.critical(self.canvas,
                                QCoreApplication.translate("ImprovedPolygonCapturing", "Error"),
                                QCoreApplication.translate("ImprovedPolygonCapturing", "The feature could not be added because removing the polygon intersections would change the geometry type"))
          self.clearMapCanvas()
          # Cancel the operation
          return

    # Handle linestrings
    elif not self.isPolygon:
      # Check if there are enough vertices to create a line string
      if not len(self.captureList) >= 2:
        QMessageBox.critical(self.canvas,
                              QCoreApplication.translate("ImprovedPolygonCapturing", "Not enough vertices"),
                              QCoreApplication.translate("ImprovedPolygonCapturing", "Cannot close a line feature until it has at least two vertices."))
        self.clearMapCanvas()
        return

      # Create a geometry from the point list considering the
      # layer geometry type.
      if self.layer.wkbType() == QgsWkbTypes.LineGeometry:
        geometry = QgsGeometry().fromPolyline(self.captureList)
      elif self.layer.wkbType() == QgsWkbTypes.WKBMultiLineString:
        geometry = QgsGeometry().fromMultiPolyline([self.captureList])


    else:
      self.clearMapCanvas()
      return

    # print "New geometry is " + str(geometry.exportToWkt())

    # Add the new geometry to the layers topological point to ensure topological editing
    # see also the announcing for version 1.0 http://blog.qgis.org/node/123
    #layer.addTopologicalPoints(geometry)

    # Create a new feature and set the geometry to it
    feature = QgsFeature()
    feature.setGeometry(geometry)    
    feature.setFields(layer.fields())
    

    # saveFeature = True
    # try:
    #   saveFeature = self.iface.openFeatureForm(layer, feature, True)
    # except AttributeError:
    #   pass

    # Add the new feature to the layer
    if self.cbk and self.cbk(feature):
      print("save feature", feature)
      layer.startEditing()

      layer.addFeature(feature)
      layer.updateExtents()

    # Clear and refresh the canvas in any case
    self.clearMapCanvas()

  def clearMapCanvas(self):
    """
    Clears the map canvas and in particular the rubberband.
    A warning is thrown when the markers are removed.
    """
    # Reset the capture list
    self.captureList = []

    # Reset the rubber band

    # Create an empty rubber band
    if self.isPolygon:
      self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
    else:
      self.rubberBand.reset(QgsWkbTypes.LineGeometry)

    # Delete also all vertex markers
    for marker in self.vertexMarkers:
      self.canvas.scene().removeItem(marker)
      del marker

    self.canvas.refresh()