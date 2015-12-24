from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_ToolsDialog import Ui_ToolsDialog
except:
    Ui_ToolsDialog = loadQtUiType(__file__, "ui/ToolsDialog")

class ToolsDialog(QDialog, Ui_ToolsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.toolsListView_ = QTreeWidgetWrap(self.toolsListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
