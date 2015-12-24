from .ExecutorBase import *
from .dialog.WorkcardTypeDialog import WorkcardTypeDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Workcard Type
##########################################################################
class EditWorkcardType(ExecutorBase):
    def execute(self):
        workcard_type_list = self.getWorkcardTypeList()
        dialog = WorkcardTypeDialogImpl(self.qtWidget_, self.sernaDoc_,
                                        workcard_type_list)
        if QDialog.Accepted == dialog.exec_loop():
            workcard_type = dialog.getWorkcardType()
            if workcard_type:
                self.insertWorkcardType(workcard_type);
    
    def getWorkcardTypeList(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        workcard_type_list = []
        grove = Grove.buildGroveFromFile(
            self.composeUrl("definitionList", [("param1", "wctype-def")]))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        current_workcard_type = get_datum_from_expr("//prelreq/wctype",
                                                    self.srcDoc_)
        for gridrow in gridrows:
            workcard_type = get_datum_from_expr("dul:gridcell[1]", gridrow)
            workcard_type_description = get_datum_from_expr(
                "dul:gridcell[2]", gridrow)
            workcard = (workcard_type, workcard_type_description)
            selected = workcard_type == current_workcard_type
            workcard_type_list.append((workcard, selected))
        qApp.restoreOverrideCursor()
        return workcard_type_list

    def insertWorkcardType(self, workcard_type):
        self.structEditor_.executeAndUpdate(
            self.replaceText("//prelreq/wctype", self.srcDoc_, workcard_type))
    
##########################################################################

class WorkcardTypeDialogImpl(WorkcardTypeDialog):
    def __init__(self, parent, sernaDoc, workcard_type_selection_list):
        WorkcardTypeDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc        
        for workcard_type_selection in workcard_type_selection_list:
            workcard = workcard_type_selection[0]
            if workcard[0] != "E":
                item = QListViewItem(self.workcardTypeListView_,
                                     workcard[0], workcard[1])
                selected = workcard_type_selection[1]
                self.workcardTypeListView_.setSelected(item, selected)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#wct-dialog")

    def getWorkcardType(self):
        item = self.workcardTypeListView_.selectedItem()
        if item == None:
            return None
        return str(item.text(0))
