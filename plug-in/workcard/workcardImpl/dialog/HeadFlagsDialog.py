from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_HeadFlagsDialog import Ui_HeadFlagsDialog
except:
    Ui_HeadFlagsDialog = loadQtUiType(__file__, "ui/HeadFlagsDialog")

class HeadFlagsDialog(QDialog, Ui_HeadFlagsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.headFlagList = QTreeWidgetWrap(self.headFlagList)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
