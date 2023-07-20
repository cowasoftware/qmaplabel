# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_create_junction_road(object):
    def setupUi(self, Dialog_create_junction_road):
        Dialog_create_junction_road.setObjectName("Dialog_create_junction_road")
        Dialog_create_junction_road.resize(640, 300)
        self.btn_run = QtWidgets.QPushButton(Dialog_create_junction_road)
        self.btn_run.setGeometry(QtCore.QRect(490, 190, 75, 23))
        self.btn_run.setObjectName("btn_run")
        self.label_center = QtWidgets.QLabel(Dialog_create_junction_road)
        self.label_center.setGeometry(QtCore.QRect(50, 70, 71, 16))
        self.label_center.setObjectName("label_center")
        self.comboBox_road = QtWidgets.QComboBox(Dialog_create_junction_road)
        self.comboBox_road.setGeometry(QtCore.QRect(130, 70, 341, 22))
        self.comboBox_road.setObjectName("comboBox_road")
        self.btn_center_layer = QtWidgets.QPushButton(Dialog_create_junction_road)
        self.btn_center_layer.setGeometry(QtCore.QRect(500, 70, 75, 23))
        self.btn_center_layer.setObjectName("btn_center_layer")

        self.retranslateUi(Dialog_create_junction_road)
        QtCore.QMetaObject.connectSlotsByName(Dialog_create_junction_road)

    def retranslateUi(self, Dialog_create_junction_road):
        _translate = QtCore.QCoreApplication.translate
        Dialog_create_junction_road.setWindowTitle(_translate("Dialog_create_junction_road", "创建路口线段"))
        self.btn_run.setText(_translate("Dialog_create_junction_road", "确定"))
        self.label_center.setText(_translate("Dialog_create_junction_road", "中心线图层："))
        self.btn_center_layer.setText(_translate("Dialog_create_junction_road", "选择位置"))
