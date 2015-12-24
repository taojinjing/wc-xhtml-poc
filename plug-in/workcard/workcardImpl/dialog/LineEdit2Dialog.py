from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QComboxWrap

try:
    from .ui.Ui_LineEdit2Dialog import Ui_LineEdit2Dialog
except:
    Ui_LineEdit2Dialog = loadQtUiType(__file__, "ui/LineEdit2Dialog")

class LineEdit2Dialog(QDialog, Ui_LineEdit2Dialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.nhaBox_ = QComboxWrap(self.nhaBox_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
