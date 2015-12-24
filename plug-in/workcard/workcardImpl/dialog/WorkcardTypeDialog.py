from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_WorkcardTypeDialog import Ui_WorkcardTypeDialog
except:
    Ui_WorkcardTypeDialog = loadQtUiType(__file__, "ui/WorkcardTypeDialog")

class WorkcardTypeDialog(QDialog, Ui_WorkcardTypeDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.workcardTypeListView_ = QTreeWidgetWrap(self.workcardTypeListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
