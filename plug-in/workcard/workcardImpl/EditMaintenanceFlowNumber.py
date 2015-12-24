from .ExecutorBase import *
from .dialog.MaintenanceFlowNumberDialog import MaintenanceFlowNumberDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Maintenance Flow Number
##########################################################################
class EditMaintenanceFlowNumber(ExecutorBase):
    def execute(self):
        dialog = MaintenanceFlowNumberDialogImpl(self.qtWidget_,
                 self.sernaDoc_, self.getMaintFlowNumbers(),
                 self.currentMaintFlowNumber())
        if QDialog.Accepted == dialog.exec_loop():
            maintenance_flow_number = dialog.getMaintenanceFlowNumber()
            if maintenance_flow_number:
                self.replaceOrInsert(
                    "maintflow-num", maintenance_flow_number, "crew-type")
    
    def getMaintFlowNumbers(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        maint_flow_numbers = []
        data = self.getMfgModelDash()
        parameters = [("mfg", data.manufacturer_), ("model", data.model_),
                      ("dash", data.dash_)]
        grove = Grove.buildGroveFromFile(
            self.composeUrl("maintflowDef", parameters))
        
        for maint_flow in get_nodes("//maintflow", grove.document()):
            maint_flow_numbers.append((
                get_datum_from_expr("maintflow-num", maint_flow),
                get_datum_from_expr("maintflow-desc", maint_flow)))
        qApp.restoreOverrideCursor()
        return maint_flow_numbers

    def currentMaintFlowNumber(self):
        return get_datum_from_expr("//prelreq/maintflow-num", self.srcDoc_)

##########################################################################

class MaintenanceFlowNumberDialogImpl(MaintenanceFlowNumberDialog):
    def __init__(self, parent, sernaDoc, maintFlowNumbers, current):
        MaintenanceFlowNumberDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc        
        selected_item = None
        for maint_flow_number in maintFlowNumbers:
            text0 = ""
            if maint_flow_number[0]:
                text0 = maint_flow_number[0]
            text1 = ""
            if maint_flow_number[1]:
                text1 = maint_flow_number[1]
            item = QListViewItem(self.listView_, text0, text1)
            if text0 == current:
                selected_item = item
                self.listView_.setSelected(item, True)

        if selected_item:
            self.listView_.ensureItemVisible(selected_item)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#mai-dialog")

    def getMaintenanceFlowNumber(self):
        item = self.listView_.selectedItem()
        if item == None:
            return None
        return str(item.text(0))
