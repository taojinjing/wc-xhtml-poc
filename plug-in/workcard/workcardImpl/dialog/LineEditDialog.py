from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_LineEditDialog import Ui_LineEditDialog
except:
    Ui_LineEditDialog = loadQtUiType(__file__, "ui/LineEditDialog")

class LineEditDialog(QDialog, Ui_LineEditDialog):
    
    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
       
        
    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
