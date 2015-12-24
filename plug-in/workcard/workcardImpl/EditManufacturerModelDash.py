from .ExecutorBase import *
from .dialog.ManufacturerModelDashDialog import ManufacturerModelDashDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Manufacturer Model Dash
##########################################################################
class EditManufacturerModelDash(ExecutorBase):
    def execute(self):
        dialog = ManufacturerModelDashDialogImpl(
            self.qtWidget_, self.sernaDoc_, self.getMfgModelDashList(),
            self.getMfgModelDash())
        if QDialog.Accepted == dialog.exec_loop():
            mfg_model_dash = dialog.getMfgModelDash()
            if mfg_model_dash:
                self.insertMfgModelDash(mfg_model_dash);
    
    def getMfgModelDashList(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        mfg_model_dash_list = []
        grove = Grove.buildGroveFromFile(self.composeUrl(
            "definitionList", [("param1", "ac-model-def")]))
        for gridrow in get_nodes("//dul:gridrow", grove.document()):
            mfg_model_dash_list.append(
                MfgModelDash(get_datum_from_expr("dul:gridcell[1]", gridrow),
                             get_datum_from_expr("dul:gridcell[2]", gridrow),
                             get_datum_from_expr("dul:gridcell[3]", gridrow)))
        qApp.restoreOverrideCursor()
        return mfg_model_dash_list

    def insertMfgModelDash(self, mfgModelDash):
        batch_cmd = GroveBatchCommand()
        batch_cmd.executeAndAdd(self.replaceText(
            "//prelreq/mfg", self.srcDoc_, mfgModelDash.manufacturer_))
        batch_cmd.executeAndAdd(self.replaceText(
            "//prelreq/model", self.srcDoc_, mfgModelDash.model_))
        batch_cmd.executeAndAdd(self.replaceText(
            "//prelreq/dash", self.srcDoc_, mfgModelDash.dash_))
        self.structEditor_.executeAndUpdate(batch_cmd)


##########################################################################
class ManufacturerModelDashDialogImpl(ManufacturerModelDashDialog):
    def __init__(self, parent, sernaDoc, mfgModelDashList, currentMfg):
        ManufacturerModelDashDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        for data in mfgModelDashList:
            item = QListViewItem(self.listView_, data.manufacturer_,
                                 data.model_, data.dash_)
            if data == currentMfg:
                self.listView_.setSelected(item, True)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#mfg-dialog")

    def getMfgModelDash(self):
        item = self.listView_.selectedItem()
        if not item:
            return None
        return MfgModelDash(str(item.text(0)), str(item.text(1)),
                            str(item.text(2)))
