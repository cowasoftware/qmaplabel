import math
from functools import cmp_to_key

from qgis.core import (QgsApplication, QgsGeometry, QgsPoint, QgsPointXY,
                       QgsProject, QgsRectangle, QgsSpatialIndex,
                       QgsSymbolLayer, QgsWkbTypes)


def distance(pt1,pt2):
    return math.sqrt((pt1[0]-pt2[0])*(pt1[0]-pt2[0])+(pt1[1]-pt2[1])*(pt1[1]-pt2[1]))


def tool_fixing_road_lines_up_down_ids(
    layer,
    tol):
    #获取中心线

    center_data_features = list(layer.getFeatures())
    #index = QgsSpatialIndex()
    index = QgsSpatialIndex(layer.getFeatures())
    tol_1 = tol
    tol=tol*0.0001
    willChange = {}
    for i in range(0,len(center_data_features)):
        feature = center_data_features[i]
        up_ids_index = feature.fieldNameIndex("up_ids")
        down_ids_index = feature.fieldNameIndex("down_ids")
        geom = feature.geometry()
        this_change={}
        up_ids= []
        down_ids=[]
        new_box = geom.boundingBox()
        xMin = new_box.xMinimum()
        yMin = new_box.yMinimum()
        xMax = new_box.xMaximum()
        yMax = new_box.yMaximum()
        intersect = index.intersects(QgsRectangle(xMin-tol_1, yMin-tol_1, xMax+tol_1, yMax+tol_1))
        for j in range(0,len(intersect)):
            if(intersect[j]==i):
                continue
            else:
                geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
                if geomSingleType:
                    this_Polyline = geom.asPolyline()
                    that_feature  =  center_data_features[intersect[j]]
                    that_Polyline =  that_feature.geometry().asPolyline()
                    if(distance(this_Polyline[0],that_Polyline[-1])<tol):
                        #起点和终点一致 更新属性
                        that_id = that_feature["id"]
                        up_ids.append(str(that_id))
                    elif(distance(this_Polyline[-1],that_Polyline[0])<tol):
                        that_id = that_feature["id"]
                        down_ids.append(str(that_id))
                else:
                    this_Polyline = geom.asMultiPolyline()
                    that_feature  =  center_data_features[intersect[j]]
                    that_Polyline =  that_feature.geometry().asMultiPolyline()
                    if(distance(this_Polyline[0][0],that_Polyline[0][-1])<tol):
                        #起点和终点一致 更新属性
                        that_id = that_feature["id"]
                        up_ids.append(str(that_id))
                    elif(distance(this_Polyline[0][-1],that_Polyline[0][0])<tol):
                        that_id = that_feature["id"]
                        down_ids.append(str(that_id))
        this_change[up_ids_index]=",".join(up_ids)
        this_change[down_ids_index]=",".join(down_ids)
        willChange[feature.id()] = this_change
    print(willChange)
    layer.dataProvider().changeAttributeValues(willChange)
          



def tool_fixing_junction_lines_up_down_ids(
		center_layer,
		junction_layer,
        tol
        ):
    center_data_features = list(center_layer.getFeatures())
    index = QgsSpatialIndex(center_layer.getFeatures())
    junction_layer_features= list(junction_layer.getFeatures())
    tol=tol*0.0001
    willChange = {}
    for i in range(0,len(junction_layer_features)):
        feature = junction_layer_features[i]
        up_ids_index = feature.fieldNameIndex("up_ids")
        down_ids_index = feature.fieldNameIndex("down_ids")
        geom = feature.geometry()
        this_change={}
        up_ids= []
        down_ids=[]
        new_box = geom.boundingBox()
        xMin = new_box.xMinimum()
        yMin = new_box.yMinimum()
        xMax = new_box.xMaximum()
        yMax = new_box.yMaximum()
        intersect = index.intersects(QgsRectangle(xMin-tol, yMin-tol, xMax+tol, yMax+tol))
        #intersect = index.intersects(geom.boundingBox())
        for j in range(0,len(intersect)):
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            if geomSingleType:
                this_Polyline = geom.asPolyline()
                that_feature  =  center_data_features[intersect[j]]
                that_Polyline =  that_feature.geometry().asPolyline()
                if(distance(this_Polyline[0],that_Polyline[-1])<tol):
                    #起点和终点一致 更新属性
                    that_id = that_feature["id"]
                    up_ids.append(str(that_id))
                elif(distance(this_Polyline[-1],that_Polyline[0])<tol):
                    that_id = that_feature["id"]
                    down_ids.append(str(that_id))
            else:
                this_Polyline = geom.asMultiPolyline()
                that_feature  =  center_data_features[intersect[j]]
                that_Polyline =  that_feature.geometry().asMultiPolyline()
                if(distance(this_Polyline[0][0],that_Polyline[0][-1])<tol):
                    #起点和终点一致 更新属性
                    that_id = that_feature["id"]
                    up_ids.append(str(that_id))
                elif(distance(this_Polyline[0][-1],that_Polyline[0][0])<tol):
                    that_id = that_feature["id"]
                    down_ids.append(str(that_id))
        this_change[up_ids_index]=",".join(up_ids)
        this_change[down_ids_index]=",".join(down_ids)
        willChange[feature.id()] = this_change
    print(willChange)
    #return willChange
    junction_layer.dataProvider().changeAttributeValues(willChange)
          


#list 排序 根据内部index为0的数据进行排序
def start_and_end_compare(x,y):
    if(x[0]>y[0]):
        return 1
    else:
        return -1
# 设置value 根据起点进行累加的设置id
def set_link_value1(features_indexs,features,ids_dict,link_value,willChange,link_index):
    for i in range(0,len(features_indexs)):
        fea_index = features_indexs[i]
        feature = features[fea_index]
        fid = feature.id()
        willChange[fid]={link_index:link_value}
        if(fea_index in ids_dict.keys()):
            down_features_index = ids_dict[fea_index]
            set_link_value1(down_features_index,features,ids_dict,link_value+1,willChange,link_index)
# 设置value 根据起点进行累减的设置id
def set_link_value2(features_indexs,features,ids_dict,link_value,willChange,link_index):
    for i in range(0,len(features_indexs)):
        fea_index = features_indexs[i]
        feature = features[fea_index]
        fid = feature.id()
        willChange[fid]={link_index:link_value}
        if(fea_index in ids_dict.keys()):
            down_features_index = ids_dict[fea_index]
            set_link_value2(down_features_index,features,ids_dict,link_value-1,willChange,link_index)


#根据起始点 和上下游字典 获取整条线段的全部link index
def getCompeleteLinesByStartIndex(fea_index,ids_dict,index_dic,these_features):
    if(fea_index in ids_dict.keys()):
        down_feature_index= ids_dict[fea_index]
        index_dic['index_list'].append(down_feature_index[0])
        index_dic['length']=index_dic['length']+1
        getCompeleteLinesByStartIndex(down_feature_index[0],ids_dict,index_dic,these_features)
    else:
        return
#根据link index 获取一整条线段的点集 可以直接转化为polyline
def getLineByIndexs(indexs,features,geomSingleType):
    points_list = []
    for i in range(0,len(indexs)):
        fea= features[indexs[i]]
        geom = fea.geometry()
        if(geom.isEmpty()):
            continue
        if(geomSingleType):
            this_Polyline = geom.asPolyline()
        else:
            this_Polylines = geom.asMultiPolyline()
            this_Polyline = this_Polylines[0]

        if(len(points_list)>0 and distance([this_Polyline[0].x(),this_Polyline[0].y()],[points_list[-1].x(),points_list[-1].y()])>distance([this_Polyline[-1].x(),this_Polyline[-1].y()],[points_list[-1].x(),points_list[-1].y()])):
            this_Polyline.reverse()
        points_list.extend(this_Polyline)

    compolete_line = QgsGeometry.fromPolylineXY(points_list)
    return points_list



#计算 point2 point1 point3构成角 的角度是否大于90°
def cosCal(point1,point2,point3):
    x1 = point2.x()-point1.x()
    y1 = point2.y()-point1.y()
    x2 = point3.x()-point1.x()
    y2 = point3.y()-point1.y()
    value = (x1*x2+y1*y2)
    return value
#j计算向量line1 和line2 的数量积
def cosAngle(line1,line2):
    pt1 = line1[0]
    pt2 = line1[-1]
    pt3 = line2[0]
    pt4 = line2[-1]
    x1 = pt2.x()-pt1.x()
    y1 = pt2.y()-pt1.y()
    x2= pt4.x()-pt3.x()
    y2= pt4.y()-pt3.y()
    value = (x1*x2+y1*y2)/math.sqrt(distance([pt1.x(),pt1.y()],[pt2.x(),pt2.y()])*distance([pt3.x(),pt3.y()],[pt4.x(),pt4.y()]))
    return value
#返回0 垂足起点
#返回1 垂足重点
#返回-1 起点之前
#返回-2 终点之前
#返回-3 之间
#均为起点之前和均为终点之前就不是一组
#0 -1  -1 -2也不为一组
#存在3 或者-1 -2就是一组 或者 0 1 是一组
#判断点和线段的关系
def isPointInLine(point,line):
    cos1 = cosCal(line[0],point,line[-1])
    cos2 = cosCal(line[-1],point,line[0])
    #说明刚好在边界
    if(cos1==0):
        return 1
    if(cos2==0):
        return 2
    if(cos1<0):
        return 3
    if(cos2<0):
        return 4
    if(cos1>0 and cos2>0):
        return 5
    
#中垂线判断id 线段重点在内部
def same_Group_line1(line1,line2): 
    line1_begin_point = line1[0]
    line1_end_point = line1[-1]
    center_point = QgsPointXY(0.5*(line1_begin_point.x() + line1_end_point.x()),0.5*(line1_begin_point.y()+line1_end_point.y()))
    #均为锐角或者均为钝角
    cos1  = cosAngle([center_point,line1_begin_point],[center_point,line2[0]])
    cos2  = cosAngle([center_point,line1_end_point],[center_point,line2[-1]])
    if(cos1*cos2>=0):
        return True
    else:
        return False
    


# 判断两条线是否为并行线 true是 false不是
def same_Group_line(line1,line2):
    line1_begin_point = line1[0] 
    line1_end_point=  line1[-1]
    line1_begin_point_value = isPointInLine(line1_begin_point,line2)
    line1_end_point_value = isPointInLine(line1_end_point,line2)

    if(line1_begin_point_value ==5 or line1_end_point_value ==5):
        return True
    elif(line1_begin_point_value *line1_end_point_value==12):
        return True
    elif(line1_begin_point_value *line1_end_point_value==4):
        return True
    elif(line1_begin_point_value *line1_end_point_value==6):
        return True
    else:
        return False
# 二维向量里查找某个值是否存在
def find_index(group,find_value):
    for i in range(0,len(group)):
        son_group = group[i]
        for j in range(0,len(son_group)):
            value = son_group[j]
            if(value==find_value):
                return True
    return False

def continuous_query_model(
    Index,
    models,
    used,
    pt,
    left,
    tol,
    dst 
    ):

    intersects = Index.intersects(QgsRectangle(pt.x()-tol, pt.y()-tol, pt.x()+tol, pt.y()+tol))
    dis_query = 9999
    pos_query = -1
    for i in range(0,len(intersects)):
        v = intersects[i]
        if used[v]:
            continue
        vertexs = list(models[v].geometry().vertices())
        if(len(vertexs)==0):
            continue
        if left==1:
            d = vertexs[-1].distance(pt)
        else:
            d = vertexs[0].distance(pt)
        if d < dis_query:
            dis_query = d
            pos_query = v
    if (pos_query>=0 and dis_query<=tol):
        used[pos_query] = True
        next_line = models[pos_query].geometry()
        next_vertexs = list(next_line.vertices())
        if(len(next_vertexs)==0):
            return
        if(left == 1):
            np = next_vertexs[0]
            dst.insert(0,next_line)
            continuous_query_model(Index,models,used,np,left,tol,dst)
        else:
            np = next_vertexs[-1]
            dst.append(next_line)
            continuous_query_model(Index,models,used,np,left,tol,dst)
   

    
def tool_update_cliper_link_id(center_layer,break_lines_layer,tol,input_road_name):

    
    center_data_features = list(center_layer.getFeatures())
    break_lines_features = list(break_lines_layer.getFeatures())

    if(len(center_data_features)==0 or len(break_lines_features)==0 or  center_data_features[0].fieldNameIndex("link")==-1 or  center_data_features[0].fieldNameIndex("name")==-1):
        return
    #获取当前图层是简单几何还是复杂几何
    temp_geom = center_data_features[0].geometry()
    geomSingleType = QgsWkbTypes.isSingleType(temp_geom.wkbType())
    del temp_geom

    break_single_type = QgsWkbTypes.isSingleType(break_lines_features[0].geometry().wkbType())
    
   
        
    
    old_break_lines_id_index_dic={}
    break_lines_id_index_dic={}
    index = QgsSpatialIndex(center_layer.getFeatures())
    old_break_lines_index = QgsSpatialIndex(break_lines_layer.getFeatures())
    break_lines_index = QgsSpatialIndex()
    for i in range(0,len(break_lines_features)):
        old_break_lines_id_index_dic[break_lines_features[i].id()]= break_lines_features[i]
    
    res_break_lines_feas = []
    
    used = [False] * len(break_lines_features)
    while (False in used):
        pos = used.index(False)
        used[pos]=True
        #拿到第0个
        geo = break_lines_features[pos].geometry()
        vertexs = list(geo.vertices())
        if(len(vertexs)==0):
            continue
        p1 = vertexs[0]
        p2 = vertexs[-1] 
        left_lines = []
        continuous_query_model(old_break_lines_index,break_lines_features,used,p1,1,tol,left_lines)
        right_lines = []
        continuous_query_model(old_break_lines_index,break_lines_features,used,p2,0,tol,right_lines)
        new_geo=[]
        for i in range(0,len(left_lines)):
            left_geo= left_lines[i]
            line = left_geo.asMultiPolyline()[0]
            new_geo.extend(line)
            new_geo.pop()
        line = geo.asMultiPolyline()[0]
        new_geo.extend(line)
        for i in range(0,len(right_lines)):
            right_geo= right_lines[i]
            line = right_geo.asMultiPolyline()[0]
            new_geo.pop()
            new_geo.extend(line)
        break_lines_features[pos].setGeometry(QgsGeometry.fromMultiPolylineXY([new_geo]))
        res_break_lines_feas.append(break_lines_features[pos])
        
        break_lines_id_index_dic[break_lines_features[pos].id()] = break_lines_features[pos]
        break_lines_index.addFeature(break_lines_features[pos])
    


    name_lines_dic={}
    all_raod_names_list=[]
    willChange={}
    
    link_index = center_data_features[0].fieldNameIndex("link")
    for i in range(0,len(center_data_features)):
        road_name = center_data_features[i]['name']
        if(road_name not in name_lines_dic.keys()):
            name_lines_dic[road_name]=[center_data_features[i]] 
            all_raod_names_list.append(road_name)
        else:
            name_lines_dic[road_name].append(center_data_features[i])
    print(input_road_name)
    #判断路名有效性
    for i in range(0,len(all_raod_names_list)):
        this_road_name=all_raod_names_list[i]
        these_features = name_lines_dic[this_road_name]
        if((input_road_name in all_raod_names_list) and this_road_name!=input_road_name):
            continue
        #对level进行分类
        max_level = 0 
        max_level_features_index=[]
        else_level_features_index=[]
        for j in range(0,len(these_features)):
            level = these_features[j]['level']
            if(level>max_level):
                max_level=level
        for j in range(0,len(these_features)):
            level = these_features[j]['level']
            if(level==max_level):
                max_level_features_index.append(j)
            else:
                else_level_features_index.append(j)
        #获取 前后 breaklines
        
        center_break_lines_dic={}
        for j in range(0,len(these_features)):
            fea =  these_features[j]
            new_box = fea.geometry().boundingBox()
            xMin = new_box.xMinimum()
            yMin = new_box.yMinimum()
            xMax = new_box.xMaximum()
            yMax = new_box.yMaximum()
            intersect = break_lines_index.intersects(QgsRectangle(xMin-tol, yMin-tol, xMax+tol, yMax+tol))
            if(len(intersect)==0):
                continue
            for k in range(0,len(intersect)):
                break_id = intersect[k]
                break_line_fea = break_lines_id_index_dic[break_id]
                if(break_line_fea.geometry().distance(fea.geometry())<tol):
                    if( fea.id() not in center_break_lines_dic.keys()):
                        center_break_lines_dic[fea.id()]=[str(break_id)]
                    else:
                        center_break_lines_dic[fea.id()].append(str(break_id))
            if(fea.id() not in center_break_lines_dic.keys()):
                continue
            center_break_lines_dic[fea.id()].sort()
            center_break_lines_dic[fea.id()] = ",".join(center_break_lines_dic[fea.id()])
        
        MIN_X = 9999
        MIN_Y = 9999
        MAX_X = -1
        MAX_Y = -1
        #构建一个fid 和index的对应
        dict_fid_index ={}
        for j in range(0,len(these_features)):
            fid = these_features[j].id()
            dict_fid_index[fid]=j
        print(dict_fid_index)
        #同名线段拿到之后开始处理 
        #找到线段方向
        #裁剪后只剩下短的部分 先划分为多个部分
        #对每一根线找到相邻线，那么没有相邻的便能够得到结果 构建上下游关系
        down_ids_dic={}
        #记录所有id的上游
        up_ids_dic={}
        startBoundaryLinesIndex=[]
        startBoundaryLinesGeometry=[]
        endBoundaryLinesIndex=[]
        
        for j  in range(0,len(these_features)):
            if( j in else_level_features_index):
                continue
            this_feature = these_features[j]
            this_geom = this_feature.geometry()
            if(this_geom.isEmpty()):
                continue
            this_index = j
            new_box = this_geom.boundingBox()
            
            xMin = new_box.xMinimum()
            yMin = new_box.yMinimum()
            xMax = new_box.xMaximum()
            yMax = new_box.yMaximum()

            if(xMin<MIN_X):
                MIN_X=xMin
            if(yMin<MIN_Y):
                MIN_Y=yMin
            if(xMax>MAX_X):
                MAX_X=xMax
            if(yMax>MAX_Y):
                MAX_Y=yMax

            intersect = index.intersects(QgsRectangle(xMin-tol, yMin-tol, xMax+tol, yMax+tol))
            isStart = True
            isEnd =True
            #记录所有id的下游
            #记录所有边界

            for k in range(0,len(intersect)):
                if(intersect[k] not in dict_fid_index.keys() or j==dict_fid_index[intersect[k]] or these_features[dict_fid_index[intersect[k]]]['level']!=max_level):
                    continue
                if geomSingleType:
                    #this_Polyline 当前线段
                    #that_polyline 当前线段首尾相连的线段
                    #找不到自然没有上下游
                    this_Polyline = this_geom.asPolyline()
                    that_feature  =  these_features[dict_fid_index[intersect[k]]]
                    that_Polyline =  that_feature.geometry().asPolyline()
                    if(distance(this_Polyline[0],that_Polyline[-1])<tol):
                        isStart=False
                        #起点和终点一致 更新属性
                        #this_polyline是下游
                        #that_polyline是上游
                        #所以intersect[k]是fid
                        that_index = dict_fid_index[intersect[k]]
                        if(this_index not in up_ids_dic.keys()):
                            up_ids_dic[this_index]=[that_index]  
                        else:
                            up_ids_dic[this_index].append(that_index)

                    if(distance(this_Polyline[-1],that_Polyline[0])<tol):
                        #下游
                        isEnd=False
                        that_index = dict_fid_index[intersect[k]]
                        if(this_index not in down_ids_dic.keys()):
                            down_ids_dic[this_index]=[that_index]
                        else:
                            down_ids_dic[this_index].append(that_index)
                else:
                    this_Polyline = this_geom.asMultiPolyline()
                    that_feature  =  these_features[dict_fid_index[intersect[k]]]
                    that_Polyline =  that_feature.geometry().asMultiPolyline()
                    if(distance(this_Polyline[0][0],that_Polyline[0][-1])<tol):
                        isStart=False
                        that_index = dict_fid_index[intersect[k]]
                        if(this_index not in up_ids_dic.keys()):
                            up_ids_dic[this_index]=[that_index]  
                        else:
                            up_ids_dic[this_index].append(that_index)  
                    if(distance(this_Polyline[0][-1],that_Polyline[0][0])<tol):
                        isEnd=False
                        that_index = dict_fid_index[intersect[k]]
                        if(this_index not in down_ids_dic.keys()):
                            down_ids_dic[this_index]=[that_index]
                        else:
                            down_ids_dic[this_index].append(that_index)

            #这是一个大组，需要尝试分为更小组，连在一起获取连缀。如果有分支则取其中一条，那么每一条原始的数据就能够拿到
            #再用算法划分为n组 
            if (isStart):
                startBoundaryLinesIndex.append(this_index)
            if (isEnd):
                endBoundaryLinesIndex.append(this_index)
        start_index_feas_dic = {}
        for j in range(0,len(startBoundaryLinesIndex)):
            this_index=startBoundaryLinesIndex[j]
            indexs_dic = {'index_list':[this_index],'length':1}
            getCompeleteLinesByStartIndex(this_index,down_ids_dic,indexs_dic,these_features)
            line_geometry = getLineByIndexs(indexs_dic['index_list'],these_features,geomSingleType)
            start_index_feas_dic[this_index] = {'line_geometry':line_geometry,'length':indexs_dic['length'],'end_index':indexs_dic['index_list'][-1]}
            startBoundaryLinesGeometry.append(line_geometry)
        same_Group_line_index =[]
        print(startBoundaryLinesIndex)
        for j in range(0,len(startBoundaryLinesIndex)):
            if(find_index(same_Group_line_index,startBoundaryLinesIndex[j])):
                continue
            this_group=[startBoundaryLinesIndex[j]]
            polyline1= startBoundaryLinesGeometry[j]
            for k in range(0,len(startBoundaryLinesIndex)):
                if(k==j):
                    continue
                polyline2 = startBoundaryLinesGeometry[k]
                if(same_Group_line(polyline1,polyline2) or same_Group_line(polyline2,polyline1)):
                    this_group.append(startBoundaryLinesIndex[k])
            same_Group_line_index.append(this_group)

        #对same Group line 的线段进行判别 ： 1 ：每个获取1 条 进行左下到右上的排序
        #   2 ：对于自身 进行两个方向的排序， 先做1 
        same_Group_line_index_dic_sort_list = []
        del_X =MAX_X - MIN_X
        del_Y =MAX_Y - MIN_Y
        right_direction_start_index=[]
        left_direction_start_index=[]
        for j in range(0,len(same_Group_line_index)):
            value_indexs = same_Group_line_index[j]
            #exam_fea = these_features[value_indexs[0]]
            points_list = start_index_feas_dic[value_indexs[0]]['line_geometry']
            compelete_line = QgsGeometry.fromPolylineXY(points_list)
            center_point = compelete_line.centroid()
            pt = center_point.asPoint()
            if(del_X>del_Y):
                this_dis = distance([pt.x(),pt.y()],[MIN_X,pt.y()])
            else:
                this_dis = distance([pt.x(),pt.y()],[pt.x(),MIN_Y])
            same_Group_line_index_dic_sort_list.append([this_dis,value_indexs])
            for k in range(0,len(value_indexs)):
                points_list = start_index_feas_dic[value_indexs[k]]['line_geometry']
                if(del_X<del_Y):
                    if(distance([points_list[0].x(),points_list[0].y()],[points_list[0].x(),MIN_Y])<distance([points_list[-1].x(),points_list[-1].y()],[points_list[-1].x(),MIN_Y])):
                        right_direction_start_index.append(value_indexs[k])
                    else:
                        left_direction_start_index.append(value_indexs[k])
                else:
                    if(distance([points_list[0].x(),points_list[0].y()],[MIN_X,points_list[0].y()])<distance([points_list[-1].x(),points_list[-1].y()],[MIN_X,points_list[-1].y()])):
                        right_direction_start_index.append(value_indexs[k])
                    else:
                        left_direction_start_index.append(value_indexs[k])
        same_Group_line_index_dic_sort_list.sort(key = cmp_to_key(start_and_end_compare))
        num = 1 
        for j in range(0,len(same_Group_line_index_dic_sort_list)):
            value_indexs = same_Group_line_index_dic_sort_list[j][1]
            max_num =0
            if(len(right_direction_start_index)>0):
                for k in range(0,len(value_indexs)):
                    fea_index = value_indexs[k]
                    if(fea_index in right_direction_start_index):
                        set_link_value1([fea_index],these_features,down_ids_dic,num,willChange,link_index)
                        for l in range(0,len(endBoundaryLinesIndex)):
                            end_index = endBoundaryLinesIndex[l]
                            
                            line1=None
                            line2=None
                            if(geomSingleType):
                                line1  = these_features[fea_index].geometry().asPolyline()
                                line2 =  these_features[end_index].geometry().asPolyline()
                            else:
                                mulline1  = these_features[fea_index].geometry().asMultiPolyline()
                                mulline2 =  these_features[end_index].geometry().asMultiPolyline()
                                line1 = mulline1[0]
                                line2 = mulline2[0]
                            if(same_Group_line(line1,line2) or same_Group_line(line2,line1)):
                                
                                set_link_value1([end_index],these_features,up_ids_dic,num,willChange,link_index)
                        if(start_index_feas_dic[fea_index]['length']>max_num):
                            max_num = start_index_feas_dic[fea_index]['length']
            else:
                for k in range(0,len(value_indexs)):
                    fea_index = value_indexs[k]
                    set_link_value1([fea_index],these_features,down_ids_dic,num,willChange,link_index)
            num = num + max_num

        del num
        del down_ids_dic
        del up_ids_dic
        #以上处理的全都是 最大level的features 案例
        #接下来处理的是 所有的features
        for j in range(0,len(these_features)):

            this_fea = these_features[j]
            this_geom = this_fea.geometry()
            new_box = this_geom.boundingBox()
            
            xMin = new_box.xMinimum()
            yMin = new_box.yMinimum()
            xMax = new_box.xMaximum()
            yMax = new_box.yMaximum()
            #line 边上的线 ，line2 中间的线 line2的中垂线和line1 必有交点 line2 的中点 投影到line1 上面必在line1上
            intersect = index.intersects(QgsRectangle(xMin-0.001, yMin-0.001, xMax+0.001, yMax+0.001))
            for k in range(0,len(intersect)):
                if(intersect[k] not in dict_fid_index.keys() or these_features[j].id() not in center_break_lines_dic.keys()  or intersect[k] not in center_break_lines_dic.keys() or j==dict_fid_index[intersect[k]] or intersect[k] not in  willChange.keys() or these_features[dict_fid_index[intersect[k]]]['level']!=max_level):
                    continue
                if(center_break_lines_dic[these_features[j].id()]==center_break_lines_dic[intersect[k]]):
                    willChange[this_fea.id()]=willChange[intersect[k]]
                    break
               
            
        del these_features
        del this_road_name
        del dict_fid_index


    center_layer.dataProvider().changeAttributeValues(willChange)

    center_layer.updateExtents()

def tool_update_cliper_link_id_by_break(center_layer,break_lines_layer,tol,input_road_name):
    center_data_features = list(center_layer.getFeatures())
    break_lines_features = list(break_lines_layer.getFeatures())

    if(len(center_data_features)==0 or len(break_lines_features)==0 or  center_data_features[0].fieldNameIndex("link")==-1 or  center_data_features[0].fieldNameIndex("name")==-1):
        return
    #获取当前图层是简单几何还是复杂几何
    temp_geom = center_data_features[0].geometry()
    geomSingleType = QgsWkbTypes.isSingleType(temp_geom.wkbType())
    del temp_geom
    break_single_type = QgsWkbTypes.isSingleType(break_lines_features[0].geometry().wkbType())
    old_break_lines_id_index_dic={}
    break_lines_id_index_dic={}
    index = QgsSpatialIndex(center_layer.getFeatures())
    old_break_lines_index = QgsSpatialIndex(break_lines_layer.getFeatures())
    break_lines_index = QgsSpatialIndex()
    for i in range(0,len(break_lines_features)):
        old_break_lines_id_index_dic[break_lines_features[i].id()]= break_lines_features[i]
    res_break_lines_feas = []
    used = [False] * len(break_lines_features)
    while (False in used):
        pos = used.index(False)
        used[pos]=True
        #拿到第0个
        geo = break_lines_features[pos].geometry()
        vertexs = list(geo.vertices())
        if(len(vertexs)==0):
            continue
        p1 = vertexs[0]
        p2 = vertexs[-1] 
        left_lines = []
        continuous_query_model(old_break_lines_index,break_lines_features,used,p1,1,tol,left_lines)
        right_lines = []
        continuous_query_model(old_break_lines_index,break_lines_features,used,p2,0,tol,right_lines)
        new_geo=[]
        for i in range(0,len(left_lines)):
            left_geo= left_lines[i]
            line = left_geo.asMultiPolyline()[0]
            new_geo.extend(line)
            new_geo.pop()
        line = geo.asMultiPolyline()[0]
        new_geo.extend(line)
        for i in range(0,len(right_lines)):
            right_geo= right_lines[i]
            line = right_geo.asMultiPolyline()[0]
            new_geo.pop()
            new_geo.extend(line)
        break_lines_features[pos].setGeometry(QgsGeometry.fromMultiPolylineXY([new_geo]))
        res_break_lines_feas.append(break_lines_features[pos])
        
        break_lines_id_index_dic[break_lines_features[pos].id()] = break_lines_features[pos]
        break_lines_index.addFeature(break_lines_features[pos])
    link_index = center_data_features[0].fieldNameIndex("link")
    name_lines_dic={}
    all_raod_names_list=[]
    willChange={}
    for i in range(0,len(center_data_features)):
        road_name = center_data_features[i]['name']
        if(road_name not in name_lines_dic.keys()):
            name_lines_dic[road_name]=[center_data_features[i]] 
            all_raod_names_list.append(road_name)
        else:
            name_lines_dic[road_name].append(center_data_features[i])
    print(input_road_name)
    #找到这个name所有的line 及相关break 根据break进行排序
    #生成了index结果
    for i in range(0,len(all_raod_names_list)):
        this_road_name=all_raod_names_list[i]
        these_features = name_lines_dic[this_road_name]
        if((input_road_name in all_raod_names_list) and this_road_name!=input_road_name):
            continue
        #对level进行分类
        max_level = 0 
        max_level_features_index=[]
        else_level_features_index=[]
        #根据maxlevel针对breakline进行排序罢了
        break_ids=[]
        for j in range(0,len(these_features)):
            level = these_features[j]['level']
            if(level>max_level):
                max_level=level
        for j in range(0,len(these_features)):
            level = these_features[j]['level']
            if(level==max_level):
                max_level_features_index.append(j)
            else:
                else_level_features_index.append(j)
        center_break_lines_dic={}
        MIN_X = 9999
        MIN_Y = 9999
        MAX_X = -1
        MAX_Y = -1
        for j in range(0,len(these_features)):
            fea =  these_features[j]
            new_box = fea.geometry().boundingBox()
            xMin = new_box.xMinimum()
            yMin = new_box.yMinimum()
            xMax = new_box.xMaximum()
            yMax = new_box.yMaximum()
            if(xMin<MIN_X):
                MIN_X=xMin
            if(yMin<MIN_Y):
                MIN_Y=yMin
            if(xMax>MAX_X):
                MAX_X=xMax
            if(yMax>MAX_Y):
                MAX_Y=yMax
            intersect = break_lines_index.intersects(QgsRectangle(xMin-tol, yMin-tol, xMax+tol, yMax+tol))
            if(len(intersect)==0):
                continue
            for k in range(0,len(intersect)):
                break_id = intersect[k]
                break_line_fea = break_lines_id_index_dic[break_id]
                if(break_line_fea.geometry().distance(fea.geometry())<tol):
                    if( fea.id() not in center_break_lines_dic.keys()):
                        center_break_lines_dic[fea.id()]=[str(break_id)]
                    else:
                        center_break_lines_dic[fea.id()].append(str(break_id))
                    if(break_id not in break_ids):
                        break_ids.append(break_id)
            if(fea.id() not in center_break_lines_dic.keys()):
                continue
            center_break_lines_dic[fea.id()].sort()
            center_break_lines_dic[fea.id()] = ",".join(center_break_lines_dic[fea.id()])
        #break全部找到之后 对break进行排序
        #进行一个排序 由下到上的排序？
        del_X = MAX_X - MIN_X
        del_Y = MAX_Y - MIN_Y
        #break排序方式如何更新
        break_id_order_result=[]
        for j in range(0,len(break_ids)):
            break_line = break_lines_id_index_dic[break_ids[j]]
            compelete_line = break_line.geometry()
            center_point = compelete_line.centroid()
            pt = center_point.asPoint()
            this_dis = 0
            if(del_X>del_Y):
                this_dis = distance([pt.x(),pt.y()],[MIN_X,pt.y()])
            else:
                this_dis = distance([pt.x(),pt.y()],[pt.x(),MIN_Y])
            break_id_order_result.append([this_dis,break_ids[j]])
        break_id_order_result.sort(key = cmp_to_key(start_and_end_compare))
        need_link_values =[]
        temp_willChange={}
        for j in range(0,len(these_features)):
            fea =  these_features[j]
            compelete_line = fea.geometry()
            center_point = compelete_line.centroid()
            vertexs = list(compelete_line.vertices())
            if(len(vertexs)==0):
                continue
            p1 = QgsGeometry.fromPointXY(QgsPointXY(vertexs[0]))
            p2 = QgsGeometry.fromPointXY(QgsPointXY(vertexs[-1])) 
            sum = 10000
            addk1 = -1
            for k in range(0,len(break_id_order_result)-1):
                current_break_id = break_id_order_result[k][1]
                next_break_id = break_id_order_result[k+1][1]
                current_break_line = break_lines_id_index_dic[current_break_id]
                next_break_line = break_lines_id_index_dic[next_break_id]
                current_break_geo = current_break_line.geometry()
                next_break_geo = next_break_line.geometry()
                if(p1.distance(current_break_geo) + p2.distance(next_break_geo) <=tol or p1.distance(next_break_geo) + p2.distance(current_break_geo) <=tol ):
                    temp_willChange[fea.id()] = {link_index:k+1}
                    if(k+1 not in need_link_values):
                        need_link_values.append(k+1)
                    break
                else:
                    dis1 = p1.distance(current_break_geo) + p2.distance(next_break_geo)
                    dis2 = p1.distance(next_break_geo) + p2.distance(current_break_geo)
                    if(dis1<sum):
                        sum = dis1
                        temp_willChange[fea.id()] = {link_index:k+1}
                        addk1 = k+1
                    if(dis2<sum):
                        sum = dis2
                        temp_willChange[fea.id()] = {link_index:k+1}
                        addk1 = k+1
                if(k == len(break_id_order_result)-2):
                    if(addk1 != - 1 and addk1 not in need_link_values):
                        need_link_values.append(addk1)
            
        #对于他来说这个link 也有变动？ 也就是link标记不对时 对应的值进行变动
        need_link_values.sort()
        dict_corr={}
        new_need_link_value=need_link_values.copy()
        for k in range(0,len(new_need_link_value)):
            new_need_link_value[k] = k+1
        for k in range(0,len(new_need_link_value)):
            dict_corr[need_link_values[k]] = new_need_link_value[k]
        print(dict_corr)
        print(temp_willChange)
        for k in temp_willChange.keys():
            if(temp_willChange[k][link_index] in list(dict_corr.keys())):
                temp_willChange[k][link_index] = dict_corr[temp_willChange[k][link_index]]
                
        willChange.update(temp_willChange)
        
    center_layer.dataProvider().changeAttributeValues(willChange)
    center_layer.updateExtents()

            #line 和break的对应已经保存
        
        
