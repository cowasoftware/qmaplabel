# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
import sys, os, operator, logging, math
from xml.sax.handler import all_features
logger = logging.getLogger()
import shapely.geometry

from qgis.core import *
from qgis.PyQt import QtGui, uic, QtWidgets, QtCore
from qgis.PyQt.QtCore import *



def frange(x, y, jump):
  while x < y:
    yield float(x)
    x += jump

def GetFeature(layer, filter = None):
  project = QgsProject.instance()
  layers = project.mapLayersByName(layer)
  if layers == None or len(layers) == 0:
    self.iface.messageBar().pushWarning("CRMAP", '未找到预定义{}层'.format(layer))
    return
  layer = layers[0]
  if filter == None:
    return layer.getFeatures()
  request = QgsFeatureRequest().setFilterExpression(filter)
  return layer.getFeatures(request)

def AsList(feature):
  if type(feature) == QgsGeometry:
    g = feature
  else:
    g = feature.geometry()
  if g.wkbType() == QgsWkbTypes.MultiLineString:
    l = [(p.x(), p.y()) for p in list(g.get())[0]]
  elif g.wkbType() == QgsWkbTypes.MultiLineStringZ:
    l = [(p.x(), p.y(), p.z()) for p in list(g.get())[0]]
  elif g.wkbType() == QgsWkbTypes.Polygon:
    l = [(p.x(), p.y()) for p in g.get().vertices()]
  elif g.wkbType() == QgsWkbTypes.PolygonZ or g.wkbType() == QgsWkbTypes.Polygon25D:
    l = [(p.x(), p.y(), p.z()) for p in g.get().vertices()]
  elif g.wkbType() == QgsWkbTypes.LineString25D:
    l = [(p.x(), p.y(), p.z()) for p in g.get().vertices()]
  elif g.wkbType() == 1002 or g.wkbType() == 2:
    l = [(p.x(), p.y(), p.z()) for p in g.get()]
  else:
    print(g.wkbType(), " not supprot")
  return l
def AsLineString(feature, revert = False):
  #l = AsList(feature)
  #if revert: l.reverse()
  l = [(786468.8845299111, 3381626.7104727556), (786493.6553648652, 3381608.322306931), (786461.286114281, 3381571.545975281), (786444.87353652, 3381592.0616974826), (786468.8845299111, 3381626.7104727556)]
  return shapely.geometry.LineString(l)


def CreateRoad(f1, f2,layer, remove = True, bidirection = False):
  project = QgsProject.instance()
  if(layer.name()!='roads'):
    return

  
  
  def Align(g1, g2):
    ps = AsList(g2)
    d, point1, index1, direction = g1.closestSegmentWithContext(QgsPointXY(ps[0][0], ps[0][1]))
    d, point2, index2, direction = g1.closestSegmentWithContext(QgsPointXY(ps[-1][0], ps[-1][1]))
    if index1 > index2:
      point1, index1, point2, index2 = point2, index2, point1, index1
    path = [(point1.x(), point1.y())]
    path.extend(AsList(g1)[index1:index2])
    path.append((point2.x(), point2.y()))
    return path
  g1, g2 = f1.geometry(), f2.geometry()
  l1, l2 = Align(g1, g2), Align(g2, g1)
  if len(l1) < len(l2): l1, l2, g1, g2 = l2, l1, g2, g1
  line = []
  for i in l1:
    d, point1, index1, direction = g2.closestSegmentWithContext(QgsPointXY(i[0], i[1]))
    x, y = point1.x() + i[0], point1.y() + i[1]
    line.append((x / 2, y / 2))
  path = [QgsPoint(*i) for i in line]
  def CreateFeature(layer, path):
    feature = QgsFeature()
    feature.setFields(layer.fields())
    feature.setGeometry(QgsGeometry.fromPolyline(path))
    feature.setAttribute("type", 7)
    return feature
  
  layer.startEditing()
  layer.addFeature(CreateFeature(layer, path))
  if bidirection:
    path.reverse()
    layer.addFeature(CreateFeature(layer, path))
  layer.updateExtents()
  
def SplitLane(fline, point,layer):
  if(layer.name()!="roads"):
    return
  line = fline.geometry()
  d, p, index, direction = line.closestSegmentWithContext(QgsPointXY(point.x(), point.y()))

  first = []
  secnond = []
  points = AsList(fline)
  for i in range(0, len(points)):
    if i < index: first.append(points[i])
    else: secnond.append(points[i])    
  first.append((p.x(), p.y()))
  secnond.insert(0, (p.x(), p.y()))

  #project = QgsProject.instance()
  #layer = project.mapLayersByName('roads')[0]
  layer.startEditing()
  path = [QgsPoint(*i) for i in first]
  layer.changeGeometry(fline.id(), QgsGeometry.fromPolyline(path))
  feature = QgsFeature()
  feature.setFields(layer.fields())
  feature.setAttribute("type", fline["type"])
  path = [QgsPoint(*i) for i in secnond]
  feature.setGeometry(QgsGeometry.fromPolyline(path))
  layer.addFeature(feature)
  layer.updateExtents()

def ParallelOffset(fline, point, layer, last_id):
  line = fline.geometry()
  d, p, index, direction = line.closestSegmentWithContext(QgsPointXY(point.x(), point.y()))
  d = math.sqrt(d)
  if direction > 0: d = -d
  path = line.offsetCurve(d, index - 1, QgsGeometry.JoinStyleBevel, 0)
  if path.isMultipart():
    lines = [(i, i.length()) for i in path.constGet()]
    lines.sort(key=lambda x: x[1])
    path = lines[-1][0].clone()

  layer.startEditing()
  if last_id != None and layer.getFeature(last_id).isValid():
    print('chane', last_id)
    layer.changeGeometry(last_id, path)
  else:
    feature = QgsFeature()
    feature.setFields(layer.fields())
    feature.setAttribute("type", fline["type"])
    feature.setGeometry(path)
    layer.addFeatures([feature])
    last_id=feature.id()
    print("last_id:",last_id)
  layer.updateExtents()
  return last_id
  
def RevertRoad(feature,layer):
  if(layer.name()!='roads'):
    return
  l = AsList(feature)
  l.reverse()

  project = QgsProject.instance()
  #layer = project.mapLayersByName('roads')[0]
  
  f = QgsFeature(feature)
  layer.startEditing()
  layer.deleteFeature(feature.id())
  f.setGeometry(QgsGeometry.fromPolyline([QgsPoint(*i) for i in l]))
  layer.addFeature(f)
  layer.updateExtents()

def MergeLineWithReturn(features,layer):
  all_features = [i for i in features]
  last_feature = all_features[0]
  all_points = AsList(last_feature)
  all_features.remove(last_feature)
  while all_features:
    found = False
    for feature in all_features:
      geometry = feature.geometry()
      points = AsList(geometry)
    
      d, p, index, direction = geometry.closestSegmentWithContext(QgsPointXY(all_points[0][0], all_points[0][1]))
      if index > len(points) / 2 and d < 0.5:
        all_points = points[0:index] + all_points
        found = True
        all_features.remove(feature)
        break

      d, p, index, direction = geometry.closestSegmentWithContext(QgsPointXY(all_points[-1][0], all_points[-1][1]))
      if index < len(points) / 2 and d < 0.5:
        all_points = all_points + points[index:]
        last_feature = feature
        found = True
        all_features.remove(feature)
        break
    if found == False:
      break


  #project = QgsProject.instance()
  #layer = project.mapLayersByName('roads')[0]
  
  f = QgsFeature(last_feature)
  layer.startEditing()

  for feature in features: 
    if feature not in all_features: layer.deleteFeature(feature.id())
  f.setGeometry(QgsGeometry.fromPolyline([QgsPoint(*i) for i in all_points]))
  layer.addFeature(f)
  layer.updateExtents()
  return all_features
def MergeLine(features,layer):
  while len(features) > 1:
    features = MergeLineWithReturn(features,layer)