from .ExecutorBase import *
from .dialog.CrewTypeDialog import CrewTypeDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Crew Type
##########################################################################
class EditCrewType(ExecutorBase):
    def execute(self):
        crew_type_selection_list = self.getCrewTypeList()
        dialog = CrewTypeDialogImpl(self.qtWidget_, self.sernaDoc_,
                                    crew_type_selection_list)
        if QDialog.Accepted == dialog.exec_loop():
            crew_type = dialog.getCrewType()
            if crew_type:
                self.insertCrewType(crew_type);
    
    def getCrewTypeList(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        crew_type_selection_list = []
        grove = Grove.buildGroveFromFile(
            self.composeUrl("definitionList", [("param1", "crew-def")]))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        current_crew_type = self.getCrewType()
        
        for gridrow in gridrows:
            crew_type = get_datum_from_expr("dul:gridcell[1]", gridrow)
            crew_desc = get_datum_from_expr("dul:gridcell[2]", gridrow)
            crew = (crew_type, crew_desc)
            selected = crew_type == current_crew_type
            crew_type_selection_list.append((crew, selected))
        qApp.restoreOverrideCursor()
        return crew_type_selection_list

    def getCrewType(self):
        crew_type = get_datum_from_expr("//prelreq/crew-type", self.srcDoc_)
        return crew_type
        
    def insertCrewType(self, crew_type):
        self.structEditor_.executeAndUpdate(
            self.replaceText("//prelreq/crew-type", self.srcDoc_, crew_type))
    
##########################################################################

class CrewTypeDialogImpl(CrewTypeDialog):
    def __init__(self, parent, sernaDoc, crew_type_selection_list):
        CrewTypeDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc        
        for crew_type_selection in crew_type_selection_list:
            crew = crew_type_selection[0]
            item = QListViewItem(self.crewTypeListView_, crew[0], crew[1])
            self.crewTypeListView_.setSelected(item, crew_type_selection[1], True)

    def getCrewType(self):
        item = self.crewTypeListView_.selectedItem()
        if item == None:
            return None
        return str(item.text(0))

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#cre-dialog")
