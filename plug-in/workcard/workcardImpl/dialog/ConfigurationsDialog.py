from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_ConfigurationsDialog import Ui_ConfigurationsDialog
except:
    Ui_ConfigurationsDialog = loadQtUiType(__file__, "ui/ConfigurationsDialog")

class ConfigurationsDialog(QDialog, Ui_ConfigurationsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.configurationsListView_ = QTreeWidgetWrap(self.configurationsListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
