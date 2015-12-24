from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap, QComboxWrap

try:
    from .ui.Ui_InsertReferenceDialog import Ui_InsertReferenceDialog
except:
    Ui_InsertReferenceDialog = loadQtUiType(__file__, "ui/InsertReferenceDialog")

class InsertReferenceDialog(QDialog, Ui_InsertReferenceDialog):

    def __init__(self, widget,name = None, modal = 0, fl = 0):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.listView_ = QTreeWidgetWrap(self.listView_)
        self.treeView_ = QTreeWidgetWrap(self.treeView_)
        self.filterComboBox_ = QComboxWrap(self.filterComboBox_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
