from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_MajorZoneDialog import Ui_MajorZoneDialog
except:
    Ui_MajorZoneDialog = loadQtUiType(__file__, "ui/MajorZoneDialog")

class MajorZoneDialog(QDialog, Ui_MajorZoneDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.majorZoneListView_ = QTreeWidgetWrap(self.majorZoneListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
