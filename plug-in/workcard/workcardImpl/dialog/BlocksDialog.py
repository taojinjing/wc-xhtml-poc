from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QComboxWrap


try:
    from .ui.Ui_BlocksDialog import Ui_BlocksDialog
except:
    Ui_BlocksDialog = loadQtUiType(__file__, "ui/BlocksDialog")

class BlocksDialog(QDialog, Ui_BlocksDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.comboLabel1 = QComboxWrap(self.comboLabel1)
        self.comboLabel2 = QComboxWrap(self.comboLabel2)
        self.comboLabel3 = QComboxWrap(self.comboLabel3)
        self.comboLabel4 = QComboxWrap(self.comboLabel4)
        self.comboLabel5 = QComboxWrap(self.comboLabel5)
        self.comboLabel6 = QComboxWrap(self.comboLabel6)
        self.comboSkill1 = QComboxWrap(self.comboSkill1)
        self.comboSkill2 = QComboxWrap(self.comboSkill2)
        self.comboSkill3 = QComboxWrap(self.comboSkill3)
        self.comboSkill4 = QComboxWrap(self.comboSkill4)
        self.comboSkill5 = QComboxWrap(self.comboSkill5)
        self.comboSkill6 = QComboxWrap(self.comboSkill6)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
