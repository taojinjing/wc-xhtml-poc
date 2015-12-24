from .ExecutorBase import *
from .dialog.CircuitBreakersDialog import CircuitBreakersDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Circuit Breakers
##########################################################################
class EditCircuitBreakers(ExecutorBase):
    def execute(self):
        cbreakers = self.getCircuitBreakers()
        if not self.isValidWorkcardTaskList(cbreakers, "Circuit Breakers"):
            return 
        dialog = CircuitBreakersDialogImpl(self.qtWidget_, self.sernaDoc_,
                                           cbreakers)
        if QDialog.Accepted == dialog.exec_loop():
            circuit_breakers = dialog.getCircuitBreakers()
            self.replaceOrInsert("circuit-breakers", circuit_breakers,
                "parts tools references drawings zones-panels forecasts "
                "configurations checks maintflow-num crew-type")
    
    def getCircuitBreakers(self):
        list = []
        current_breakers = self.getCurrentCircuitBreakers()
        for task in self.getTasks("Info", "circuit-breakers"):
            task_key = get_attribute(task, "key")

            for zone_node in get_nodes(".//zone", task):
                zone_num = get_datum_from_expr("zn-num", zone_node)

                for cb_panel_node in get_nodes(".//cbpnl", zone_node):
                    cb_panel = get_datum_from_expr("cbpnl-num", cb_panel_node)

                    for cb_node in get_nodes(".//cb", cb_panel_node):
                        cb_num = get_datum_from_expr("cb-num", cb_node)
                        cb_state = get_datum_from_expr("cb-state", cb_node)
                        is_selected = (task_key, zone_num, cb_panel, cb_num) \
                                      in current_breakers
                        cb_data = CircuitBreakersData(task_key, zone_num,
                                  cb_panel, cb_num, cb_state, is_selected)
                        list.append(cb_data)
        return list

    def getCurrentCircuitBreakers(self):
        circuit_breakers = []
        circuit_breaker_nodes = get_nodes(
            "//prelreq/circuit-breakers/circuit-breaker", self.srcDoc_)
        for cb_node in circuit_breaker_nodes:
            task_key = get_datum_from_expr("source-key", cb_node)
            zone_num = get_datum_from_expr("zn-num", cb_node)
            cb_panel = get_datum_from_expr("cbpnl-num", cb_node)
            cb_num = get_datum_from_expr("cb-num", cb_node)
            circuit_breakers.append((task_key, zone_num, cb_panel, cb_num))            
        return circuit_breakers

#############################################################################

class CircuitBreakersData:
    def __init__(self, taskKey, zoneNum, cbPanel, cbNumber,
                 cbState, isSelected):
        self.taskKey_ = taskKey
        self.zoneNum_ = zoneNum
        self.cbPanel_ = cbPanel
        self.cbNumber_ = cbNumber
        self.cbState_ = cbState
        self.isSelected_ = isSelected
        
#############################################################################

class CircuitBreakersDialogImpl(CircuitBreakersDialog):
    def __init__(self, parent, sernaDoc, circuitBreakers):
        CircuitBreakersDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        for data in circuitBreakers:
            list_item = QListViewItem(self.listView_, data.taskKey_,
                                      data.zoneNum_, data.cbPanel_,
                                      data.cbNumber_, data.cbState_)
            self.listView_.setSelected(list_item, data.isSelected_, True)

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
               cur.text(1) == item.text(1) and cur.text(2) == item.text(2) and \
               cur.text(3) == item.text(3) and cur.text(4) == item.text(4):
                deselectitems.append(item) 
            item = item.nextSibling(item, self.listView_.invisibleRootItem())

        self.processSignal_ = False
        for item in deselectitems:
            self.listView_.setSelected(item, False, True)
        self.processSignal_ = True
        
    
    def getCircuitBreakers(self):
        circuit_breakers = []
        checked_tools = []
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item):
                if (item.text(1),item.text(2),item.text(3),item.text(4)) in checked_tools:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated reference will be skiped:\n source-key:" + 
                     str(item.text(0)) + "\n zn-num:" +  str(item.text(1)) +
                     "\n cbpnl-num:" + str(item.text(2)) + 
                     "\n cb-num:" + str(item.text(3)) + 
                     "\n cd-state:" + str(item.text(4)))
                    item = item.nextSibling(item, self.listView_.invisibleRootItem())
                    continue;
                circuit_breakers.append(("circuit-breaker",
                                         [("source-key", str(item.text(0))),
                                          ("zn-num", str(item.text(1))),
                                          ("cbpnl-num", str(item.text(2))),
                                          ("cb-num", str(item.text(3))),
                                          ("cb-state", str(item.text(4)))]))
                checked_tools.append((item.text(1),item.text(2),item.text(3),item.text(4)))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())
        
        return circuit_breakers

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#cir-dialog")
