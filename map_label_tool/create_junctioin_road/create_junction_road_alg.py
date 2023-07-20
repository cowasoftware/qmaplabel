from math import sqrt

import processing
from qgis.core import (QgsApplication, QgsFeature, QgsField, QgsFields,
                       QgsGeometry, QgsPoint, QgsProject, QgsRectangle,
                       QgsSpatialIndex, QgsSymbolLayer, QgsVectorFileWriter,
                       QgsVectorLayer, QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant


def writeResult(fileUrl,cluster_list,junction_line_points,allPoints,dict_point_with_Line,geomSingleType):
    if(len(allPoints)==0):
        return 

    junction_line_fields = QgsFields()
    junction_line_fields.append(QgsField("id", QVariant.Int))
    junction_line_crs = QgsProject.instance().crs()
    junction_line_transform_context = QgsProject.instance().transformContext()
    junction_line_save_options = QgsVectorFileWriter.SaveVectorOptions()
    junction_line_save_options.driverName = "ESRI Shapefile"
    junction_line_save_options.fileEncoding = "UTF-8"
    junction_line_layer = QgsVectorFileWriter.create(
        fileUrl,
        junction_line_fields,
        QgsWkbTypes.MultiLineString,
        junction_line_crs,
        junction_line_transform_context,
        junction_line_save_options
    )
    if junction_line_layer.hasError() != QgsVectorFileWriter.NoError:
        print("Error when creating shapefile: ",  junction_line_layer.errorMessage())

    junction_data_list=[]
     
    for i in range(0,len(cluster_list)):
        pointsIndex = junction_line_points[cluster_list[i]]
        #所有点已经获取到,获取到之后判断是否需要连接每一个点
        #创建方式为起点连向终点
    
        for j in range(0,len(pointsIndex)):
            this_point_1 =allPoints[pointsIndex[j]]
            
            this_point_1_id = this_point_1['id']
            #首先判断是否为起点
            if(this_point_1_id%2==0):
                continue
            for k in range(0,len(pointsIndex)):
                #其次要不和自己点一样
                if(j==k):
                    continue
                this_point_2 =  allPoints[pointsIndex[k]]
                this_point_2_id = this_point_2['id']
                #level问题
                if(this_point_1['level']!=this_point_2['level']):
                    continue
                #接下来 被连接点的level需要和自己一样
                #再次被连接点不能是终点
                if(this_point_2_id%2==1):
                    continue
                #接下来是最难得判断 两个点构成的线段和原来的线段夹角不应垂直
                lineFeature = dict_point_with_Line[this_point_1_id]
                geom =lineFeature.geometry()
                point_second_1=[]
                if geomSingleType:
                    this_Polyline = geom.asPolyline()
                    point_second_1 = this_Polyline[-2]
                else:
                    this_Polyline = geom.asMultiPolyline()
                    point_second_1 = this_Polyline[0][-2]
                #判断角度
                #接近九十度是不可以的
                #准确的说法是连接的线段需要有斜率的差异
                x1 = point_second_1[0]-this_point_1.geometry().asPoint()[0]
                y1 = point_second_1[1]-this_point_1.geometry().asPoint()[1]
                x2 = this_point_2.geometry().asPoint()[0]-this_point_1.geometry().asPoint()[0]
                y2 = this_point_2.geometry().asPoint()[1]-this_point_1.geometry().asPoint()[1]
                cosR = (x1*x2+y1*y2) / (sqrt(x1*x1+y1*y1)*sqrt(x2*x2+y2*y2))
            
                if(abs(cosR)<0.08):
                    continue
                #生成线段
                this_line  =QgsGeometry.fromMultiPolylineXY([[this_point_1.geometry().asPoint(),this_point_2.geometry().asPoint()]])
                junction_line_data = QgsFeature(junction_line_fields)
                junction_line_data.setGeometry(this_line)
                junction_data_list.append(junction_line_data)

    junction_line_layer.addFeatures(junction_data_list)

def writeTempLayer(cluster_list,junction_line_points,allPoints,dict_point_with_Line,geomSingleType):
    vl = QgsVectorLayer("multilinestring?crs=epsg:4326", "junction_line_data", "memory")
    pr = vl.dataProvider()
    pr.addAttributes([QgsField("id", QVariant.Int)])
    vl.updateFields()
    junction_data_list=[]
     
    for i in range(0,len(cluster_list)):
        pointsIndex = junction_line_points[cluster_list[i]]
        #所有点已经获取到,获取到之后判断是否需要连接每一个点
        #创建方式为起点连向终点
    
        for j in range(0,len(pointsIndex)):
            this_point_1 =allPoints[pointsIndex[j]]
            
            this_point_1_id = this_point_1['id']
            #首先判断是否为起点
            if(this_point_1_id%2==0):
                continue
            for k in range(0,len(pointsIndex)):
                #其次要不和自己点一样
                if(j==k):
                    continue
                this_point_2 =  allPoints[pointsIndex[k]]
                this_point_2_id = this_point_2['id']
                #level问题
                if(this_point_1['level']!=this_point_2['level']):
                    continue
                #接下来 被连接点的level需要和自己一样
                #再次被连接点不能是终点
                if(this_point_2_id%2==1):
                    continue
                #接下来是最难得判断 两个点构成的线段和原来的线段夹角不应垂直
                lineFeature = dict_point_with_Line[this_point_1_id]
                geom =lineFeature.geometry()
                point_second_1=[]
                if geomSingleType:
                    this_Polyline = geom.asPolyline()
                    point_second_1 = this_Polyline[-2]
                else:
                    this_Polyline = geom.asMultiPolyline()
                    point_second_1 = this_Polyline[0][-2]
                #判断角度
                #接近九十度是不可以的
                #准确的说法是连接的线段需要有斜率的差异
                x1 = point_second_1[0]-this_point_1.geometry().asPoint()[0]
                y1 = point_second_1[1]-this_point_1.geometry().asPoint()[1]
                x2 = this_point_2.geometry().asPoint()[0]-this_point_1.geometry().asPoint()[0]
                y2 = this_point_2.geometry().asPoint()[1]-this_point_1.geometry().asPoint()[1]
                cosR = (x1*x2+y1*y2) / (sqrt(x1*x1+y1*y1)*sqrt(x2*x2+y2*y2))
            
                if(abs(cosR)<0.08):
                    continue
                #生成线段
                this_line  =QgsGeometry.fromMultiPolylineXY([[this_point_1.geometry().asPoint(),this_point_2.geometry().asPoint()]])
                junction_line_data = QgsFeature()
                junction_line_data.setGeometry(this_line)
                junction_data_list.append(junction_line_data)

    pr.addFeatures(junction_data_list)
    vl.updateExtents()
    QgsProject.instance().addMapLayer(vl)
    


def create_junction_line(layer,tol):
    center_data_features = list(layer.getFeatures())
    if(len(center_data_features)==0 or  center_data_features[0].fieldNameIndex("level")==-1 ):
        return
    #index = QgsSpatialIndex()
    index = QgsSpatialIndex()
    point_list = []
    vl = QgsVectorLayer("point?crs=epsg:4326", "temporary_points", "memory")
    pr = vl.dataProvider()
    pr.addAttributes([QgsField("id", QVariant.Int),QgsField("level", QVariant.String)])
    vl.updateFields() 
    fields = QgsFields()
    fields.append(QgsField("id", QVariant.Int))
    
    
    #建立点对线的id索引 奇数为begin 偶数为end
    dict_point_with_Line = {}
    for i in range(0,len(center_data_features)):
        feature = center_data_features[i]
        # if(feature['level']!='2'):
        #     continue
        geom =feature.geometry()
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geomSingleType:
            this_Polyline = geom.asPolyline()
            this_begin_point = this_Polyline[0]
            this_end_point = this_Polyline[-1]
            begin_point_feature = QgsFeature()
            begin_point_feature.setGeometry(QgsGeometry.fromPointXY(this_begin_point))
            end_point_feature = QgsFeature()
            end_point_feature.setGeometry(QgsGeometry.fromPointXY(this_end_point))
            index.addFeature(begin_point_feature)
            index.addFeature(end_point_feature)
            begin_point_feature.setAttributes([2*i,feature['level']])
            end_point_feature.setAttributes([2*i+1,feature['level']])
            dict_point_with_Line[2*i] = feature
            point_list.append(begin_point_feature)
            dict_point_with_Line[2*i+1] = feature
            point_list.append(end_point_feature)
            
        else:
            this_Polyline = geom.asMultiPolyline()
            this_begin_point = this_Polyline[0][0]
            this_end_point = this_Polyline[0][-1]
            begin_point_feature = QgsFeature()
            begin_point_feature.setGeometry(QgsGeometry.fromPointXY(this_begin_point))
            end_point_feature = QgsFeature()
            end_point_feature.setGeometry(QgsGeometry.fromPointXY(this_end_point))
            index.addFeature(begin_point_feature)
            index.addFeature(end_point_feature)
            begin_point_feature.setAttributes([2*i,feature['level']])
            end_point_feature.setAttributes([2*i+1,feature['level']])
            dict_point_with_Line[2*i] = feature
            point_list.append(begin_point_feature)
            dict_point_with_Line[2*i+1] = feature
            point_list.append(end_point_feature)
    pr.addFeatures(point_list)
    vl.updateExtents()
    

    new_vl = QgsVectorLayer("point?crs=epsg:4326", "Scratch point layer", "memory")
    new_pr = new_vl.dataProvider()
    new_pr.addAttributes([QgsField("id", QVariant.Int),QgsField("level", QVariant.String)])
    new_vl.updateFields() 
    new_point_list =[]
    feas = list(vl.getFeatures())
    for i in range(0,len(point_list)):
        this_point = feas[i]
        geom = this_point.geometry()
        new_box = geom.boundingBox()
        xMin = new_box.xMinimum()
        yMin = new_box.yMinimum()
        xMax = new_box.xMaximum()
        yMax = new_box.yMaximum()
        intersect = index.intersects(QgsRectangle(xMin-tol, yMin-tol, xMax+tol, yMax+tol))
        #intersect = index.intersects(geom.boundingBox())
        if(len(intersect))==1:
            boundary_Point = QgsFeature()
            boundary_Point.setGeometry(geom)
            boundary_Point.setAttributes([this_point['id'],this_point['level']])
            new_point_list.append(boundary_Point)

    new_pr.addFeatures(new_point_list)
    new_vl.updateExtents()
    #目的是找出边界点
    #QgsProject.instance().addMapLayer(new_vl)


    parameter_dictionary={}
    parameter_dictionary["INPUT"]=new_vl
    parameter_dictionary["MIN_SIZE"]=1
    parameter_dictionary["EPS"]=0.001
    parameter_dictionary["OUTPUT"]= 'memory:'
    result = processing.run("native:dbscanclustering", parameter_dictionary)
    layer = result['OUTPUT']
    
    allPoints= list(layer.getFeatures())
    print('allPoints:',len(allPoints))
    junction_line_points={}
    cluster_list =[]
    
    for i in range(0,len(allPoints)):
        pointFeature = allPoints[i]
        
        if(pointFeature['CLUSTER_SIZE']<=6):
            Continue
        else:
            cluster_group = pointFeature['CLUSTER_ID']
            if cluster_group not in junction_line_points.keys():
                junction_line_points[cluster_group]=[i]
                cluster_list.append(cluster_group)
            else:
                junction_line_points[cluster_group].append(i)
    
    
    #方案一 写入到文件
    #writeResult("junction_line_result.shp",cluster_list,junction_line_points,allPoints,dict_point_with_Line,geomSingleType)
    #方案二 写入临时内存
    writeTempLayer(cluster_list,junction_line_points,allPoints,dict_point_with_Line,geomSingleType)



    
