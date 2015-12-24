from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_ChecksDialog import Ui_ChecksDialog
except:
    Ui_ChecksDialog = loadQtUiType(__file__, "ui/ChecksDialog")

class ChecksDialog(QDialog, Ui_ChecksDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.checksListView_ = QTreeWidgetWrap(self.checksListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
