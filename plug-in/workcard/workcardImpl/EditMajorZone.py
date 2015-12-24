from .ExecutorBase import *
from .dialog.MajorZoneDialog import MajorZoneDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Major Zone
##########################################################################
class EditMajorZone(ExecutorBase):
    def execute(self):
        dialog = MajorZoneDialogImpl(self.qtWidget_, self.sernaDoc_,
                                     self.getMajorZoneList(),
                                     self.getCurrentMajorZone())
        if QDialog.Accepted == dialog.exec_loop():
            major_zone = dialog.getMajorZone()
            if major_zone:
                self.insertMajorZone(major_zone);
    
    def getMajorZoneList(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        major_zone_list = []
        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        data = self.getMfgModelDash()
        parameters = [("param1", "major-zone-def"), ("param3", carrier_code),
                      ("param4", data.manufacturer_), ("param5", data.model_),
                      ("param6", data.dash_)]
        grove = Grove.buildGroveFromFile(
            self.composeUrl("definitionList", parameters))
        
        for gridrow in get_nodes("//dul:gridrow", grove.document()):
            major_zone_list.append(MajorZone(
                get_datum_from_expr("dul:gridcell[1]", gridrow),
                get_datum_from_expr("dul:gridcell[2]", gridrow)))
        qApp.restoreOverrideCursor()
        return major_zone_list

    def getCurrentMajorZone(self):
        return get_datum_from_expr("//prelreq/major-zone", self.srcDoc_)
        
    def insertMajorZone(self, majorZone):
        self.structEditor_.executeAndUpdate(self.replaceText(
            "//prelreq/major-zone", self.srcDoc_, majorZone))

############################################################################

class MajorZone:
    def __init__(self, num, desc):
        self.num_ = num
        self.description_ = desc
        
############################################################################

class MajorZoneDialogImpl(MajorZoneDialog):
    def __init__(self, parent, sernaDoc, majorZoneList, currentMajorZone):
        MajorZoneDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc        
        selected_item = None
        for major_zone in majorZoneList:
            item = QListViewItem(self.majorZoneListView_,
                                 major_zone.num_, major_zone.description_)
            if major_zone.num_ == currentMajorZone:
                selected_item = item
                self.majorZoneListView_.setSelected(item, True)
                
        if selected_item:
            self.majorZoneListView_.ensureItemVisible(selected_item)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#maj-dialog")

    def getMajorZone(self):
        item = self.majorZoneListView_.selectedItem()
        if item == None:
            return None
        return str(item.text(0))
