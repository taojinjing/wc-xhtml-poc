from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap, QButtonGroupWrap

try:
    from .ui.Ui_CautionsWarningsDialog import Ui_CautionsWarningsDialog
except:
    Ui_CautionsWarningsDialog = loadQtUiType(__file__, "ui/CautionsWarningsDialog")

class CautionsWarningsDialog(QDialog, Ui_CautionsWarningsDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        self.addButtonGroup()
        self.listView_ = QTreeWidgetWrap(self.listView_)
        self.listView_.setSorting(True)
        self.filterGroup_ = QButtonGroupWrap(self.filterGroup_)
        
    def addButtonGroup(self):
        self.filterGroup_.addButton(self.radioButton17, 1)
        self.filterGroup_.addButton(self.warnRadioButton_, 2)
        self.filterGroup_.addButton(self.cauRadioButton_, 3)
        self.filterGroup_.addButton(self.noteRadioButton_, 4)
        self.filterGroup_.addButton(self.textRadioButton_, 5)
        
    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
