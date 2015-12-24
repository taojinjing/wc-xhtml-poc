from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 


try:
    from .ui.Ui_AboutDialogBase import Ui_AboutDialogBase
except:
    Ui_AboutDialogBase = loadQtUiType(__file__, "ui/AboutDialogBase")

class AboutDialogBase(QDialog, Ui_AboutDialogBase):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        pluginPath = str(SernaConfig().root().getSafeProperty("vars/ext_plugins"))
        iconpath = pluginPath[1:-1].replace("\\\\","/")+"/s1000d40/icons/infotrustLog.png" 
        self.image0 = QPixmap(iconpath)
        self.textLabel1.setPixmap(self.image0)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
