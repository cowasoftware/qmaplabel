# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog_ChangePointsType(object):
    def setupUi(self, Dialog_ChangePointsType):
        Dialog_ChangePointsType.setObjectName("Dialog_ChangePointsType")
        Dialog_ChangePointsType.resize(298, 445)
        self.btn_start_change = QtWidgets.QPushButton(Dialog_ChangePointsType)
        self.btn_start_change.setGeometry(QtCore.QRect(20, 20, 75, 23))
        self.btn_start_change.setObjectName("btn_start_change")
        self.btn_save = QtWidgets.QPushButton(Dialog_ChangePointsType)
        self.btn_save.setGeometry(QtCore.QRect(30, 370, 75, 23))
        self.btn_save.setObjectName("btn_save")
        self.btn_endDraw = QtWidgets.QPushButton(Dialog_ChangePointsType)
        self.btn_endDraw.setGeometry(QtCore.QRect(190, 370, 75, 23))
        self.btn_endDraw.setObjectName("btn_endDraw")
        self.scrollArea = QtWidgets.QScrollArea(Dialog_ChangePointsType)
        self.scrollArea.setGeometry(QtCore.QRect(40, 100, 221, 251))
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 219, 249))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.label = QtWidgets.QLabel(Dialog_ChangePointsType)
        self.label.setGeometry(QtCore.QRect(30, 70, 54, 12))
        self.label.setObjectName("label")
        self.btn_draw_tool = QtWidgets.QPushButton(Dialog_ChangePointsType)
        self.btn_draw_tool.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.btn_draw_tool.setObjectName("btn_draw_tool")

        self.retranslateUi(Dialog_ChangePointsType)
        QtCore.QMetaObject.connectSlotsByName(Dialog_ChangePointsType)

    def retranslateUi(self, Dialog_ChangePointsType):
        _translate = QtCore.QCoreApplication.translate
        Dialog_ChangePointsType.setWindowTitle(_translate("Dialog_ChangePointsType", "更改边界线类型"))
        self.btn_start_change.setText(_translate("Dialog_ChangePointsType", "开始绘制"))
        self.btn_save.setText(_translate("Dialog_ChangePointsType", "保存结果"))
        self.btn_endDraw.setText(_translate("Dialog_ChangePointsType", "结束绘制"))
        self.label.setText(_translate("Dialog_ChangePointsType", "修改类型："))
        self.btn_draw_tool.setText(_translate("Dialog_ChangePointsType", "绘制工具"))
