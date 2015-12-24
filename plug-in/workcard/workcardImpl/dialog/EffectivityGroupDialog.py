from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_EffectivityGroupDialog import Ui_EffectivityGroupDialog
except:
    Ui_EffectivityGroupDialog = loadQtUiType(__file__, "ui/EffectivityGroupDialog")

class EffectivityGroupDialog(QDialog, Ui_EffectivityGroupDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.listView_ = QTreeWidgetWrap(self.listView_)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
