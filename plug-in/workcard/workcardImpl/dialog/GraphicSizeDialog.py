from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_GraphicSizeDialog import Ui_GraphicSizeDialog
except:
    Ui_GraphicSizeDialog = loadQtUiType(__file__, "ui/GraphicSizeDialog")

class GraphicSizeDialog(QDialog, Ui_GraphicSizeDialog):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        pluginPath = str(SernaConfig().root().getSafeProperty("vars/ext_plugins"))
        iconpath = pluginPath[1:-1].replace("\\\\","/")+"/s1000d40/icons/warning.png" 
        self.image0 = QPixmap(iconpath)
        self.fitWarningIcon_.setPixmap(self.image0)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
