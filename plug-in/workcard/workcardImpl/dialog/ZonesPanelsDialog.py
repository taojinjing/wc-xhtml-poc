from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_ZonesPanelsDialog import Ui_ZonesPanelsDialog
except:
    Ui_ZonesPanelsDialog = loadQtUiType(__file__, "ui/ZonesPanelsDialog")

class ZonesPanelsDialog(QDialog, Ui_ZonesPanelsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.listView_ = QTreeWidgetWrap(self.listView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
