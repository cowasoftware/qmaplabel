# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_update_road_up_down_ids(object):
    def setupUi(self, Dialog_update_road_up_down_ids):
        Dialog_update_road_up_down_ids.setObjectName("Dialog_update_road_up_down_ids")
        Dialog_update_road_up_down_ids.resize(640, 300)
        self.label_center = QtWidgets.QLabel(Dialog_update_road_up_down_ids)
        self.label_center.setGeometry(QtCore.QRect(60, 70, 71, 16))
        self.label_center.setObjectName("label_center")
        self.comboBox_road = QtWidgets.QComboBox(Dialog_update_road_up_down_ids)
        self.comboBox_road.setGeometry(QtCore.QRect(140, 70, 341, 22))
        self.comboBox_road.setObjectName("comboBox_road")
        self.btn_center_layer = QtWidgets.QPushButton(Dialog_update_road_up_down_ids)
        self.btn_center_layer.setGeometry(QtCore.QRect(510, 70, 75, 23))
        self.btn_center_layer.setObjectName("btn_center_layer")
        self.btn_run = QtWidgets.QPushButton(Dialog_update_road_up_down_ids)
        self.btn_run.setGeometry(QtCore.QRect(500, 190, 75, 23))
        self.btn_run.setObjectName("btn_run")

        self.retranslateUi(Dialog_update_road_up_down_ids)
        QtCore.QMetaObject.connectSlotsByName(Dialog_update_road_up_down_ids)

    def retranslateUi(self, Dialog_update_road_up_down_ids):
        _translate = QtCore.QCoreApplication.translate
        Dialog_update_road_up_down_ids.setWindowTitle(_translate("Dialog_update_road_up_down_ids", "更新中心线上下游节点"))
        self.label_center.setText(_translate("Dialog_update_road_up_down_ids", "中心线图层："))
        self.btn_center_layer.setText(_translate("Dialog_update_road_up_down_ids", "选择位置"))
        self.btn_run.setText(_translate("Dialog_update_road_up_down_ids", "确定"))
