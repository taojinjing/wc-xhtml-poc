# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TaskRefDialog.ui'
#
# Created: Sat Oct 25 19:07:51 2008
#      by: The PyQt User Interface Compiler (pyuic) 3.17.4
#
# WARNING! All changes made in this file will be lost!


from qt import *


class TaskRefDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("TasksDialog")



        self.okButton_ = QPushButton(self,"okButton_")
        self.okButton_.setGeometry(QRect(26,236,80,24))
        self.okButton_.setAutoDefault(0)

        self.cancelButton_ = QPushButton(self,"cancelButton_")
        self.cancelButton_.setGeometry(QRect(112,236,80,24))
        self.cancelButton_.setAutoDefault(0)

        self.tasksListView_ = QListView(self,"tasksListView_")
        self.tasksListView_.addColumn(self.__tr("Tasks"))
        self.tasksListView_.setGeometry(QRect(11,11,170,210))
        self.tasksListView_.setSelectionMode(QListView.Single)
        self.tasksListView_.setAllColumnsShowFocus(1)
        self.tasksListView_.setResizeMode(QListView.AllColumns)

        self.languageChange()

        self.resize(QSize(203,271).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelButton_,SIGNAL("clicked()"),self.reject)
        self.connect(self.okButton_,SIGNAL("clicked()"),self.accept)
        self.connect(self.tasksListView_,SIGNAL("selectionChanged()"),self.selectionChanged)

        self.setTabOrder(self.tasksListView_,self.okButton_)
        self.setTabOrder(self.okButton_,self.cancelButton_)


    def languageChange(self):
        self.setCaption(self.__tr("Add/Change Tasks"))
        self.okButton_.setText(self.__tr("&Ok"))
        self.okButton_.setAccel(QKeySequence(self.__tr("Alt+O")))
        self.cancelButton_.setText(self.__tr("&Cancel"))
        self.cancelButton_.setAccel(QKeySequence(self.__tr("Alt+C")))
        self.tasksListView_.header().setLabel(0,self.__tr("Tasks"))


    def help(self):
        print("TasksDialog.help(): Not implemented yet")

    def edit(self):
        print("TasksDialog.edit(): Not implemented yet")

    def selectionChanged(self):
        print("TasksDialog.selectionChanged(): Not implemented yet")

    def remove(self):
        print("TasksDialog.remove(): Not implemented yet")

    def add(self):
        print("TasksDialog.add(): Not implemented yet")

    def __tr(self,s,c = None):
        return qApp.translate("TasksDialog",s,c)
