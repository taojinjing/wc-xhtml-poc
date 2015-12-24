from .ExecutorBase import *
from .dialog.ZonesPanelsDialog import ZonesPanelsDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Zones and Panels
##########################################################################
class EditZonesPanels(ExecutorBase):
    def execute(self):        
        zone_panels_list = self.getZonesPanels()
        if not self.isValidWorkcardTaskList(zone_panels_list, "Zones and Panels"):
            return 
        dialog = ZonesPanelsDialogImpl(self.qtWidget_, self.sernaDoc_,
                                       zone_panels_list)
        if QDialog.Accepted == dialog.exec_loop():
            zones_panels = dialog.getZonesPanels()
            self.replaceOrInsert("zones-panels", zones_panels,
                    "forecasts configurations checks maintflow-num crew-type")
    
    def getZonesPanels(self):
        zones_panels = []
        current_zones = self.getCurrentZones()
        tasks = self.getTasks("ZonesPanels")
        for task in tasks:
            task_key = get_attribute(task, "key")
            for zone_node in get_nodes(".//zone", task):
                zone_num = get_datum_from_expr("zn-num", zone_node)
                zone_desc = get_datum_from_expr("zn-desc", zone_node)
                panel_nodes = get_nodes(".//panel", zone_node)
                if len(panel_nodes) == 0:
                    is_selected = (task_key, zone_num) in current_zones
                    zones_panels.append(ZonesPanelsData(
                        task_key, zone_num, zone_desc, is_selected))
                else:
                    for panel_node in panel_nodes:
                        panel_num = get_datum_from_expr("pnl-num", panel_node)
                        panel_desc = get_datum_from_expr("pnl-desc",panel_node)
                        is_selected = (task_key, zone_num, panel_num) \
                                      in current_zones
                        zp_data = ZonesPanelsData(task_key, zone_num, 
                                  zone_desc, is_selected,
                                  panel_num, panel_desc)
                        zones_panels.append(zp_data)
        return zones_panels

    def getCurrentZones(self):
        zones = []
        zone_nodes = get_nodes("//prelreq/zones-panels/zone-panel",
                               self.srcDoc_)
        for zone_node in zone_nodes:
            task_key = get_datum_from_expr("source-key", zone_node)
            zone_num = get_datum_from_expr("zn-num", zone_node)
            panel_num = get_datum_from_expr("pnl-num", zone_node)
            if panel_num:
                zones.append((task_key, zone_num, panel_num))
            else:
                zones.append((task_key, zone_num))
        return zones
    
#############################################################################

class ZonesPanelsData:
    def __init__(self, taskKey, zoneNum, zoneDesc, isSelected,
                 panelNum = "", panelDesc = ""):
        self.taskKey_ = taskKey
        self.zoneNum_ = zoneNum
        self.zoneDesc_ = zoneDesc
        self.panelNum_ = panelNum
        self.panelDesc_ = panelDesc
        self.isSelected_ = isSelected

#############################################################################

class ZonesPanelsDialogImpl(ZonesPanelsDialog):
    def __init__(self, parent, sernaDoc, list):
        ZonesPanelsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        iffristChild = False
        for data in list:
            taskKey = ""
            if data.taskKey_:
                taskKey = data.taskKey_
            zoneNum = ""
            if data.zoneNum_:
                zoneNum = data.zoneNum_
            zoneDesc = ""
            if data.zoneDesc_:
                zoneDesc = data.zoneDesc_
            panelNum = ""
            if data.panelNum_:
                panelNum = data.panelNum_
            panelDesc = ""
            if data.panelDesc_:
                panelDesc = data.panelDesc_
            listitem = QListViewItem(self.listView_, taskKey,
                       zoneNum,  zoneDesc, panelNum, panelDesc)
            
            self.listView_.setSelected(listitem, data.isSelected_, True)
            if listitem == self.listView_.firstChild() and data.isSelected_:
                iffristChild = True
        if iffristChild:
            self.listView_.firstChild().setSelected(True)
            iffristChild = False
        else:
            self.listView_.firstChild().setSelected(False)
                
    def selectionChanged(self):
        if not self.processSignal_:
            return
        cur = self.listView_.currentItem()
        if not self.listView_.isSelected(cur):
            return
        deselectitems = []
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item) and  cur != item and \
               cur.text(1) == item.text(1) and cur.text(3) == item.text(3):
                deselectitems.append(item) 
                #QMessageBox.warning(self, "Warning",
                #"You have selected duplicated item with the same 'Zone Number'.")
                #return;
            item = item.nextSibling(item, self.listView_.invisibleRootItem())

        self.processSignal_ = False
        for item in deselectitems:
            self.listView_.setSelected(item, False, True)
        self.processSignal_ = True

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#zon-dialog")

    def getZonesPanels(self):
        checked_zones = []
        zones_panels = []
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item):
                if (item.text(1),item.text(3))  in checked_zones:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated zone will be skiped:\n source-key:" + 
                     str(item.text(0)) + "\n zone number:" +  str(item.text(1)) +
                     "\n panel number:" + str(item.text(3)))
                    item = item.nextSibling(item, self.listView_.invisibleRootItem())
                    continue;
                children = [("source-key", str(item.text(0))),
                            ("zn-num", str(item.text(1)))]
                if item.text(3):
                    children.append(("pnl-num", str(item.text(3))))
                zones_panels.append(("zone-panel", children))
                checked_zones.append((item.text(1),item.text(3)))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())
        
        return zones_panels        
