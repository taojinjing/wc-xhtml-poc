from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_LoginCMSDialogBase import Ui_LoginCMSDialogBase
except:
    Ui_LoginCMSDialogBase = loadQtUiType(__file__, "ui/LoginCMSDialogBase")

class LoginCMSDialogBase(QDialog, Ui_LoginCMSDialogBase):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
