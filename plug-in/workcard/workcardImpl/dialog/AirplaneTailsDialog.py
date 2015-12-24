from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_AirplaneTailsDialog import Ui_AirplaneTailsDialog
except:
    Ui_AirplaneTailsDialog = loadQtUiType(__file__, "ui/AirplaneTailsDialog")

class AirplaneTailsDialog(QDialog, Ui_AirplaneTailsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.airplaneTailsListView_= QTreeWidgetWrap(self.airplaneTailsListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
