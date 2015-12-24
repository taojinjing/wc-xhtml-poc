from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_MaintenanceFlowNumberDialog import Ui_MaintenanceFlowNumberDialog
except:
    Ui_MaintenanceFlowNumberDialog = loadQtUiType(__file__, "ui/MaintenanceFlowNumberDialog")

class MaintenanceFlowNumberDialog(QDialog, Ui_MaintenanceFlowNumberDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.listView_.setColumnWidth(0, 150)
        self.listView_ = QTreeWidgetWrap(self.listView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
