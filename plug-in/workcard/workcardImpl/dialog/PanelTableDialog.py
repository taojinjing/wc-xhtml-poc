from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QButtonGroupWrap


try:
    from .ui.Ui_PanelTableDialog import Ui_PanelTableDialog
except:
    Ui_PanelTableDialog = loadQtUiType(__file__, "ui/PanelTableDialog")

class PanelTableDialog(QDialog, Ui_PanelTableDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.addButtonGroup()
        self.groupBox_ =  QButtonGroupWrap(self.groupBox_)
       
    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
    
    def addButtonGroup(self):
        self.groupBox_.addButton(self.radioButton1, 0)
        self.groupBox_.addButton(self.radioButton2, 1)
        self.groupBox_.addButton(self.radioButton3, 2)
        self.groupBox_.addButton(self.radioButton4, 3)
        self.groupBox_.addButton(self.radioButton5, 4)
        self.groupBox_.addButton(self.radioButton6, 5)
        self.groupBox_.addButton(self.radioButton7, 6)
        self.groupBox_.addButton(self.radioButton8, 7)
        self.groupBox_.addButton(self.radioButton9, 8)
        self.groupBox_.addButton(self.radioButton10, 9)
        self.groupBox_.addButton(self.radioButton11, 10)
        self.groupBox_.addButton(self.radioButton12, 11)
        self.groupBox_.addButton(self.radioButton13, 12)
        self.groupBox_.addButton(self.radioButton14, 13)
        self.groupBox_.addButton(self.radioButton15, 14)
        self.groupBox_.addButton(self.radioButton16, 15)
        self.groupBox_.addButton(self.radioButton17, 16)
        self.groupBox_.addButton(self.radioButton18, 17)
        self.groupBox_.addButton(self.radioButton19, 18)
        self.groupBox_.addButton(self.radioButton20, 19)
        self.groupBox_.addButton(self.radioButton21, 20)
        self.groupBox_.addButton(self.radioButton22, 21)
        self.groupBox_.addButton(self.radioButton23, 22)
        self.groupBox_.addButton(self.radioButton24, 23)
