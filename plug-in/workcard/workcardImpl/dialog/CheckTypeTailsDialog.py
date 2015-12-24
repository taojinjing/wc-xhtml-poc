from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap, QComboxWrap

try:
    from .ui.Ui_CheckTypeTailsDialog import Ui_CheckTypeTailsDialog
except:
    Ui_CheckTypeTailsDialog = loadQtUiType(__file__, "ui/CheckTypeTailsDialog")

class CheckTypeTailsDialog(QDialog, Ui_CheckTypeTailsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.airplaneTailsListView_ = QTreeWidgetWrap(self.airplaneTailsListView_)
        self.effGroupComboBox_ = QComboxWrap(self.effGroupComboBox_)
        self.checkComboBox_ = QComboxWrap(self.checkComboBox_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
