from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_CrewTypeDialog import Ui_CrewTypeDialog
except:
    Ui_CrewTypeDialog = loadQtUiType(__file__, "ui/CrewTypeDialog")

class CrewTypeDialog(QDialog, Ui_CrewTypeDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.crewTypeListView_ = QTreeWidgetWrap(self.crewTypeListView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
