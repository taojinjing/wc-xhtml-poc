from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_DemoteStepDialog import Ui_DemoteStepDialog
except:
    Ui_DemoteStepDialog = loadQtUiType(__file__, "ui/DemoteStepDialog")

class DemoteStepDialog(QDialog, Ui_DemoteStepDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.addButtonGroup()

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
    
    def addButtonGroup(self):
        self.buttonGroup1.addButton(self.radioButton1, 1)
        self.buttonGroup1.addButton(self.radioButton2, 2)
        self.buttonGroup1.addButton(self.radioButton3, 3)
