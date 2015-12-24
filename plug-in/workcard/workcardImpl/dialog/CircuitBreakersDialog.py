from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_CircuitBreakersDialog import Ui_CircuitBreakersDialog
except:
    Ui_CircuitBreakersDialog = loadQtUiType(__file__, "ui/CircuitBreakersDialog")

class CircuitBreakersDialog(QDialog, Ui_CircuitBreakersDialog):

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
