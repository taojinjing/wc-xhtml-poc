from SernaApi import * 
from PyQt4.QtCore import * 
from PyQt4.QtGui import * 
from qt import QTreeWidgetWrap

try:
    from .ui.Ui_RefdmDialogBase import Ui_RefdmDialogBase
except:
    Ui_RefdmDialogBase = loadQtUiType(__file__, "ui/RefdmDialogBase")

class RefdmDialogBase(QDialog, Ui_RefdmDialogBase):

    def __init__(self, widget):
        QDialog.__init__(self, widget)
        self.setupUi(self)
        pluginPath = str(SernaConfig().root().getSafeProperty("vars/ext_plugins"))
        iconpath = pluginPath[1:-1].replace("\\\\","/")+"/s1000d40/icons/dmc.png" 
        self.image0 = QPixmap(iconpath)
        self.uriTextLabel.setPixmap(self.image0)
        self.listView_.setColumnWidth(0, 300)
        self.listView_ = QTreeWidgetWrap(self.listView_)
        self.imageView_ = QTreeWidgetWrap(self.imageView_)
        self.connect(self.collectionsListView_,SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),self.currentCollectionChanged)
        self.connect(self.listView_.getActualObj(),SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),self.currentRefChanged)
        self.connect(self.collectionsListView_,SIGNAL("itemExpanded(QTreeWidgetItem*)"),self.collectionExpanded)
        self.connect(self.collectionsListView_,SIGNAL("itemCollapsed(QTreeWidgetItem*)"),self.collectionCollapsed)
        self.connect(self.modelic_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.sdc_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.chapnum_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.discode_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.incode_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.itemloc_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.sect_,SIGNAL("returnPressed()"),self.focusNext)
        self.connect(self.subject_,SIGNAL("returnPressed()"),self.focusNext)

    def exec_loop(self):
        return self.exec_()

    def setCaption(self, caption):
        return self.setWindowTitle(caption)

    def help(self):
        return
