from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QButtonGroupWrap

try:
    from .ui.Ui_MainfuncDialog import Ui_MainfuncDialog
except:
    Ui_MainfuncDialog = loadQtUiType(__file__, "ui/MainfuncDialog")

class MainfuncDialog(QDialog, Ui_MainfuncDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.addButtonGroup()
        self.actionGroup_ = QButtonGroupWrap(self.actionGroup_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
    
    def addButtonGroup(self):
        self.actionGroup_.addButton(self.radioButton1, 0)
        self.actionGroup_.addButton(self.radioButton2, 1)
