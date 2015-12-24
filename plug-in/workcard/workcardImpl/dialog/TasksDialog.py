from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_TasksDialog import Ui_TasksDialog
except:
    Ui_TasksDialog = loadQtUiType(__file__, "ui/TasksDialog")

class TasksDialog(QDialog, Ui_TasksDialog):

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
