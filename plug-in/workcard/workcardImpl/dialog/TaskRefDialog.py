from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_TaskRefDialog import Ui_TaskRefDialog
except:
    Ui_TaskRefDialog = loadQtUiType(__file__, "ui/TaskRefDialog")

class TaskRefDialog(QDialog, Ui_TaskRefDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.tasksListView_= QTreeWidgetWrap(self.tasksListView_)
         
    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
