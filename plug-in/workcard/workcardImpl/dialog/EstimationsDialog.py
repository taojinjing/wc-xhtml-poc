from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QComboxWrap

try:
    from .ui.Ui_EstimationsDialog import Ui_EstimationsDialog
except:
    Ui_EstimationsDialog = loadQtUiType(__file__, "ui/EstimationsDialog")

class EstimationsDialog(QDialog, Ui_EstimationsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.comboSkill1 =  QComboxWrap(self.comboSkill1)
        self.comboSkill2 =  QComboxWrap(self.comboSkill2)
        self.comboSkill3 =  QComboxWrap(self.comboSkill3)
        self.comboSkill4 =  QComboxWrap(self.comboSkill4)
        self.comboSkill5 =  QComboxWrap(self.comboSkill5)
        self.comboSkill6 =  QComboxWrap(self.comboSkill6)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
    
