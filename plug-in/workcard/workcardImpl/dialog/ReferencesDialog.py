from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_ReferencesDialog import Ui_ReferencesDialog
except:
    Ui_ReferencesDialog = loadQtUiType(__file__, "ui/ReferencesDialog")

class ReferencesDialog(QDialog, Ui_ReferencesDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.taskListView_ = QTreeWidgetWrap(self.taskListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
