from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_DMReferencesDialog import Ui_DMReferencesDialog
except:
    Ui_DMReferencesDialog = loadQtUiType(__file__, "ui/DMReferencesDialog")

class DMReferencesDialog(QDialog, Ui_DMReferencesDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
