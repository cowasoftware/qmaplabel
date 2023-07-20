# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_clip_center(object):
    def setupUi(self, Dialog_clip_center):
        Dialog_clip_center.setObjectName("Dialog_clip_center")
        Dialog_clip_center.resize(640, 300)
        self.btn_break_layer = QtWidgets.QPushButton(Dialog_clip_center)
        self.btn_break_layer.setGeometry(QtCore.QRect(500, 180, 75, 23))
        self.btn_break_layer.setObjectName("btn_break_layer")
        self.label_break = QtWidgets.QLabel(Dialog_clip_center)
        self.label_break.setGeometry(QtCore.QRect(30, 180, 71, 16))
        self.label_break.setObjectName("label_break")
        self.btn_center_layer = QtWidgets.QPushButton(Dialog_clip_center)
        self.btn_center_layer.setGeometry(QtCore.QRect(500, 50, 75, 23))
        self.btn_center_layer.setObjectName("btn_center_layer")
        self.btn_run = QtWidgets.QPushButton(Dialog_clip_center)
        self.btn_run.setGeometry(QtCore.QRect(530, 260, 75, 23))
        self.btn_run.setObjectName("btn_run")
        self.comboBox_road = QtWidgets.QComboBox(Dialog_clip_center)
        self.comboBox_road.setGeometry(QtCore.QRect(120, 50, 341, 22))
        self.comboBox_road.setObjectName("comboBox_road")
        self.label_center = QtWidgets.QLabel(Dialog_clip_center)
        self.label_center.setGeometry(QtCore.QRect(30, 50, 71, 16))
        self.label_center.setObjectName("label_center")
        self.comboBox_break = QtWidgets.QComboBox(Dialog_clip_center)
        self.comboBox_break.setGeometry(QtCore.QRect(120, 180, 341, 22))
        self.comboBox_break.setObjectName("comboBox_break")
        self.listWidget = QtWidgets.QListWidget(Dialog_clip_center)
        self.listWidget.setGeometry(QtCore.QRect(120, 80, 341, 81))
        self.listWidget.setObjectName("listWidget")
        self.btn_add_layer = QtWidgets.QPushButton(Dialog_clip_center)
        self.btn_add_layer.setGeometry(QtCore.QRect(470, 90, 75, 23))
        self.btn_add_layer.setObjectName("btn_add_layer")
        self.btn_remove_layer = QtWidgets.QPushButton(Dialog_clip_center)
        self.btn_remove_layer.setGeometry(QtCore.QRect(470, 120, 75, 23))
        self.btn_remove_layer.setObjectName("btn_remove_layer")
        self.label_junction = QtWidgets.QLabel(Dialog_clip_center)
        self.label_junction.setGeometry(QtCore.QRect(30, 230, 71, 16))
        self.label_junction.setObjectName("label_junction")
        self.comboBox_junction = QtWidgets.QComboBox(Dialog_clip_center)
        self.comboBox_junction.setGeometry(QtCore.QRect(120, 228, 341, 22))
        self.comboBox_junction.setObjectName("comboBox_junction")
        self.checkBox_direction = QtWidgets.QCheckBox(Dialog_clip_center)
        self.checkBox_direction.setGeometry(QtCore.QRect(100, 270, 91, 16))
        self.checkBox_direction.setObjectName("checkBox_direction")

        self.retranslateUi(Dialog_clip_center)
        QtCore.QMetaObject.connectSlotsByName(Dialog_clip_center)

    def retranslateUi(self, Dialog_clip_center):
        _translate = QtCore.QCoreApplication.translate
        Dialog_clip_center.setWindowTitle(_translate("Dialog_clip_center", "裁剪中心线"))
        self.btn_break_layer.setText(_translate("Dialog_clip_center", "选择位置"))
        self.label_break.setText(_translate("Dialog_clip_center", "切割线图层："))
        self.btn_center_layer.setText(_translate("Dialog_clip_center", "选择位置"))
        self.btn_run.setText(_translate("Dialog_clip_center", "确定"))
        self.label_center.setText(_translate("Dialog_clip_center", "被切割图层："))
        self.btn_add_layer.setText(_translate("Dialog_clip_center", "增加图层"))
        self.btn_remove_layer.setText(_translate("Dialog_clip_center", "删除图层"))
        self.label_junction.setText(_translate("Dialog_clip_center", "路口图层："))
        self.checkBox_direction.setText(_translate("Dialog_clip_center", "是否分方向"))
