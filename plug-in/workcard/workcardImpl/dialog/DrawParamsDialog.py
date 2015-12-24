from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTextEditWrap, QComboxWrap

try:
    from .ui.Ui_DrawParamsDialog import Ui_DrawParamsDialog
except:
    Ui_DrawParamsDialog = loadQtUiType(__file__, "ui/DrawParamsDialog")

class DrawParamsDialog(QDialog, Ui_DrawParamsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.commentEdit_ = QTextEditWrap(self.commentEdit_)
        self.typeEdit_ = QComboxWrap(self.typeEdit_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
