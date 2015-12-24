from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_DrawingsDialog import Ui_DrawingsDialog
except:
    Ui_DrawingsDialog = loadQtUiType(__file__, "ui/DrawingsDialog")

class DrawingsDialog(QDialog, Ui_DrawingsDialog):

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
