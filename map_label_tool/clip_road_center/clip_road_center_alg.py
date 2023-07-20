from functools import cmp_to_key
from math import sqrt

from qgis.core import *
from qgis.PyQt.QtCore import QVariant


def distance(pt1,pt2):
    return sqrt((pt1.x()-pt2.x())*(pt1.x()-pt2.x())+(pt1.y()-pt2.y())*(pt1.y()-pt2.y()))

def start_and_end_compare(x,y):
    if(x[0]>y[0]):
        return 1
    else:
        return -1
#判断line1是line2的一部分
def is_ovelap_lines(line1,line2):
    points = list(line1.vertices())
    for i in range(0,len(points)):
        dis = line2.distance(QgsGeometry.fromPointXY( QgsPointXY(points[i].x(),points[i].y())))
        if(dis>0.001):
            return False
    return True
  

def clip_center_and_fill_link(layer_break, layer_center,junction_layer,if_direction):
    tol = 1
    crs = layer_center.crs()
    if(crs.isGeographic()):
        tol = 0.0001
    center_data_features = list(layer_center.getFeatures())
    break_line_features = list(layer_break.getFeatures())
    junction_features = list(junction_layer.getFeatures())
    
    layer_name = layer_center.name()
    
    #虚拟线判断
    if(len(center_data_features)==0 or len(break_line_features)==0):
        return
    #is_visual_index 为true默认是center 否则是boundary
    
    order_index = center_data_features[0].fieldNameIndex("order")
    break_line_index = QgsSpatialIndex(layer_break.getFeatures())
    center_line_index = QgsSpatialIndex(layer_center.getFeatures())
    junction_index = QgsSpatialIndex(junction_layer.getFeatures())
    dic_break_fid_fea= {}
    dic_center_fid_fea= {}
    dict_junction_fid_fea={}
    for i in range(0,len(break_line_features)):
        dic_break_fid_fea[break_line_features[i].id()]=break_line_features[i]
    for i in range(0,len(center_data_features)):
        dic_center_fid_fea[center_data_features[i].id()]=center_data_features[i]
    for i in range(0,len(junction_features)):
        dict_junction_fid_fea[junction_features[i].id()]=junction_features[i]
    
    new_line_features=[]
    #junction内部features
    junction_line_features=[]
    for i in range(0,len(center_data_features)):
        fea = center_data_features[i]
        geom =fea.geometry()
        if(geom.isEmpty() or geom.isNull()):
            continue
        will_clip_Point =[]
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geomSingleType:
            line = geom.asPolyline()
        else:
            multiLine = geom.asMultiPolyline()
            line = multiLine[0]
            for j in range(0,len(multiLine)):
                temp_geom1 = QgsGeometry.fromPolylineXY(line)
                temp_geom2 = QgsGeometry.fromPolylineXY(multiLine[j])
                tempdis1 = temp_geom1.length()
                tempdis2 = temp_geom2.length()
                if(tempdis2>tempdis1):
                    line = multiLine[j]
        #并不是每根线都要处理的 这里进行过滤
        #面内部的要做额外特殊处理这里可以认为
        is_in_junction = False

        start_point_geom = QgsGeometry.fromPointXY(line[0])
        end_point_geom = QgsGeometry.fromPointXY(line[-1])
        new_box = geom.boundingBox()
        xMin = new_box.xMinimum()
        yMin = new_box.yMinimum()
        xMax = new_box.xMaximum()
        yMax = new_box.yMaximum()
        intersect = break_line_index.intersects(QgsRectangle(xMin-tol*0.1, yMin-tol*0.1, xMax+tol*0.1, yMax+tol*0.1))
        is_overlap_line = False
        for j in range(0,len(intersect)):
            near_break_line = dic_break_fid_fea[intersect[j]]
            geom1 = near_break_line.geometry()
            geom1 = geom1.simplify(0.000001)
            extend_geom = geom1.extendLine(0.001*tol , 0.001*tol)
        if (is_overlap_line):
            intersect1 = center_line_index.intersects(QgsRectangle(xMin-tol*0.1, yMin-tol*0.1, xMax+tol*0.1, yMax+tol*0.1))
            #这是该boundary 附近的boundary
            for j in range(0,len(intersect1)):
                if(intersect1[j] == i):
                    continue
                center_line_feature = dic_center_fid_fea[intersect1[j]]
                line_geom =center_line_feature.geometry().extendLine(0.001*tol , 0.001*tol)
                #print(center_line_feature.id())
                if(geom.intersects(line_geom)):
                    interGeom = line_geom.nearestPoint(geom)
                    point = interGeom.asPoint()
                    will_clip_Point.append(point)
            #此外添加额外break的相交点
            for j in range(0,len(intersect)):
                near_break_line = dic_break_fid_fea[intersect[j]]
                geom1 = near_break_line.geometry()
                geom1 = geom1.simplify(0.000001)
                extend_geom = geom1.extendLine(0.001*tol , 0.001*tol)
        else:
            for j in range(0,len(intersect)):
                near_break_line = dic_break_fid_fea[intersect[j]]
                geom1 = near_break_line.geometry()
                geom1 = geom1.simplify(0.000001)
                extend_geom = geom1.extendLine(0.001*tol , 0.001*tol)
                # breaklines 和line 不是重合的 
                if(extend_geom.intersects(geom)):
                    #找到附近的center 
                    intersect1 = center_line_index.intersects(extend_geom.boundingBox())
                    #遍历判断
                    #下面是分方向的代码 这里暂时不用
                    if(if_direction):
                        direction = 0 
                        for k in range(0,len(intersect1)):
                            center_line_feature = dic_center_fid_fea[intersect1[k]]
                            if(extend_geom.intersects(center_line_feature.geometry())):
                            #这是被切割的线段然后获取方向
                                if geomSingleType:
                                    this_line = center_line_feature.geometry().asPolyline()
                                else:
                                    this_multiLine = center_line_feature.geometry().asMultiPolyline()
                                    this_line = this_multiLine[0]
                                det_k = this_line[-1].y()- this_line[0].y()
                                if(det_k>0):
                                    direction = direction+1
                                else:
                                    direction = direction-1
                        det_res = line[-1].y()- line[0].y()
                        if(direction * det_res <0):
                            continue
                    interGeom =extend_geom.intersection(geom)
                    if QgsWkbTypes.isSingleType(interGeom.wkbType()) and interGeom.type()==QgsWkbTypes.GeometryType.PointGeometry:
                        intersect_geom = extend_geom.nearestPoint(geom)
                        point = interGeom.asPoint()
                        #这个点满足两个条件 1 ：处于breaklines上 2 不在line 的边缘 3：breaklines 和line 不重合
                        geom1 = near_break_line.geometry()
                        geom1 = geom1.simplify(0.000001)
                        if(intersect_geom.distance(geom1)<tol*0.001 and intersect_geom.distance(start_point_geom)>tol*0.1 and intersect_geom.distance(end_point_geom)>tol*0.1):
                            #有的排除
                            if(is_in_junction):
                                this_box = geom.boundingBox()
                                this_box.buffered(0.001)
                                temp_intersect = junction_index.intersects(this_box)
                                if(len(temp_intersect)>0):
                                    junction_fid = temp_intersect[0]
                                    junction_fea = dict_junction_fid_fea[junction_fid]
                                    if interGeom.intersects(junction_fea.geometry()):
                                        will_clip_Point.append(point)
                            else:
                                will_clip_Point.append(point)
                    elif not QgsWkbTypes.isSingleType(interGeom.wkbType()) and interGeom.type()==QgsWkbTypes.GeometryType.PointGeometry:
                        points = interGeom.asMultiPoint()
                        for i in range(0,len(points)):
                            point = points[i]
                            point_geom =QgsGeometry.fromPointXY(point)
                            geom1 = near_break_line.geometry()
                            geom1 = geom1.simplify(0.000001)
                            if(point_geom.distance(geom1)<tol*0.001 and point_geom.distance(start_point_geom)>tol*0.1 and point_geom.distance(end_point_geom)>tol*0.1):
                                if(is_in_junction):
                                    this_box = point_geom.boundingBox()
                                    this_box.buffered(0.001)
                                    temp_intersect = junction_index.intersects(this_box)
                                    if(len(temp_intersect)>0):
                                        junction_fid = temp_intersect[0]
                                        junction_fea = dict_junction_fid_fea[junction_fid]
                                        if interGeom.intersects(junction_fea.geometry()):
                                            will_clip_Point.append(point)
                                else:
                                    will_clip_Point.append(point)
        print(fea.id(),will_clip_Point)
        will_add_clip=[]
        will_add_clips=[]
        for j in range(0,len(line)-1):
            will_add_clip.append(line[j])
            temp_link = [line[j],line[j+1]]
            temp_geom = QgsGeometry.fromPolylineXY(temp_link)
            this_intersect_point_list =[]
            for k in range(0,len(will_clip_Point)):
                if(temp_geom.distance(QgsGeometry.fromPointXY(will_clip_Point[k]))<tol*0.0001):
                    dis = distance(line[j],will_clip_Point[k])
                    pt = QgsPointXY(will_clip_Point[k].x(),will_clip_Point[k].y())
                    this_intersect_point_list.append([dis,pt])
            this_intersect_point_list.sort(key = cmp_to_key(start_and_end_compare))
                
            for l in range(0,len(this_intersect_point_list)):
                will_add_clip.append(this_intersect_point_list[l][1])
                will_add_clips.append(will_add_clip.copy())
                will_add_clip=[this_intersect_point_list[l][1]]  
            
        will_add_clip.append(line[-1])
        will_add_clips.append(will_add_clip.copy())

        for j in range(0,len(will_add_clips)):
            geom = QgsGeometry.fromPolylineXY(will_add_clips[j])
            if(geom.length()<0.001*tol):
                continue
            geom.simplify(tol*0.001)
            if(len(line)<2):
                continue
            will_add_fea = QgsFeature()
            temp_attributes = fea.attributes()
            if(order_index>-1):
                temp_attributes[order_index] = len(new_line_features)+1
            will_add_fea.setAttributes(temp_attributes)
            will_add_fea.setGeometry(geom)
            new_line_features.append(will_add_fea)
    

    ids =[] 
    for i in range(0,len(center_data_features)):
        id = center_data_features[i].id()
        ids.append(id)
    res = layer_center.dataProvider().deleteFeatures(ids)
    layer_center.dataProvider().addFeatures(new_line_features)
    layer_center.updateExtents()
  