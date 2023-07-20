import html
import re

from PyQt5 import QtCore
from qgis.core import QgsLayerDefinition, QgsLayerTreeModel, QgsLayerTreeNode
from qgis.PyQt.QtCore import QByteArray, QMimeData, QVariant


class QEventHandler(QtCore.QObject):
    def eventFilter(self, obj, event):
        """
        处理窗体内出现的事件，如果有需要则自行添加if判断语句；
        目前已经实现将拖到控件上文件的路径设置为控件的显示文本；
        """
        if event.type() == QtCore.QEvent.DragEnter:
            event.accept()
        if event.type() == QtCore.QEvent.Drop:
            md = event.mimeData()
            print(md.formats())
            
            if('application/qgis.layertreemodeldata' in md.formats()):
                qgslayerres = md.retrieveData('application/qgis.layertreemodeldata',QVariant(QgsLayerTreeModel).type())
                print(qgslayerres)

                str1 = str(qgslayerres, encoding='utf-8')
                str1 = html.unescape(str1)
                print(str1)
                #print(str2)
                result1 = GetMiddleStr(str1,"source=\"","\"")
                for i in result1:
                    url = str(i.group())[8:-1]
                    obj.setCurrentText(url)
                    
        return super().eventFilter(obj, event)


def GetMiddleStr(content,startStr,endStr):
    patternStr = r'%s(.+?)%s'%(startStr,endStr)
    p = re.compile(patternStr,re.IGNORECASE)
    m= re.finditer(p,content)
    return m


    