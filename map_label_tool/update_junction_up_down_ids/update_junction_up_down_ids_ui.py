# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_update_junction_up_down_ids(object):
    def setupUi(self, Dialog_update_junction_up_down_ids):
        Dialog_update_junction_up_down_ids.setObjectName("Dialog_update_junction_up_down_ids")
        Dialog_update_junction_up_down_ids.setEnabled(True)
        Dialog_update_junction_up_down_ids.resize(640, 300)
        self.label_junction = QtWidgets.QLabel(Dialog_update_junction_up_down_ids)
        self.label_junction.setGeometry(QtCore.QRect(20, 30, 71, 16))
        self.label_junction.setObjectName("label_junction")
        self.label_center = QtWidgets.QLabel(Dialog_update_junction_up_down_ids)
        self.label_center.setGeometry(QtCore.QRect(20, 90, 71, 16))
        self.label_center.setObjectName("label_center")
        self.btn_junction_layer = QtWidgets.QPushButton(Dialog_update_junction_up_down_ids)
        self.btn_junction_layer.setGeometry(QtCore.QRect(490, 30, 75, 23))
        self.btn_junction_layer.setObjectName("btn_junction_layer")
        self.btn_center_layer = QtWidgets.QPushButton(Dialog_update_junction_up_down_ids)
        self.btn_center_layer.setGeometry(QtCore.QRect(490, 90, 75, 23))
        self.btn_center_layer.setObjectName("btn_center_layer")
        self.btn_run = QtWidgets.QPushButton(Dialog_update_junction_up_down_ids)
        self.btn_run.setGeometry(QtCore.QRect(500, 240, 75, 23))
        self.btn_run.setObjectName("btn_run")
        self.comboBox_junction = QtWidgets.QComboBox(Dialog_update_junction_up_down_ids)
        self.comboBox_junction.setGeometry(QtCore.QRect(110, 30, 341, 22))
        self.comboBox_junction.setObjectName("comboBox_junction")
        self.comboBox_road = QtWidgets.QComboBox(Dialog_update_junction_up_down_ids)
        self.comboBox_road.setGeometry(QtCore.QRect(110, 90, 341, 22))
        self.comboBox_road.setObjectName("comboBox_road")

        self.retranslateUi(Dialog_update_junction_up_down_ids)
        QtCore.QMetaObject.connectSlotsByName(Dialog_update_junction_up_down_ids)

    def retranslateUi(self, Dialog_update_junction_up_down_ids):
        _translate = QtCore.QCoreApplication.translate
        Dialog_update_junction_up_down_ids.setWindowTitle(_translate("Dialog_update_junction_up_down_ids", "更新路口线上下游节点"))
        self.label_junction.setText(_translate("Dialog_update_junction_up_down_ids", "路口线图层："))
        self.label_center.setText(_translate("Dialog_update_junction_up_down_ids", "中心线图层："))
        self.btn_junction_layer.setText(_translate("Dialog_update_junction_up_down_ids", "选择位置"))
        self.btn_center_layer.setText(_translate("Dialog_update_junction_up_down_ids", "选择位置"))
        self.btn_run.setText(_translate("Dialog_update_junction_up_down_ids", "确定"))
