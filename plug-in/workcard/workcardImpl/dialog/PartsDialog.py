from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_PartsDialog import Ui_PartsDialog
except:
    Ui_PartsDialog = loadQtUiType(__file__, "ui/PartsDialog")

class PartsDialog(QDialog, Ui_PartsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.partsListView_ = QTreeWidgetWrap(self.partsListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
