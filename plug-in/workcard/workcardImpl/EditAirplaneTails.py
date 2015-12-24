from .ExecutorBase import *
from .dialog.AirplaneTailsDialog import AirplaneTailsDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
##########################################################################
# Airplane Tails
##########################################################################
class EditAirplaneTails(ExecutorBase):
    def execute(self):
        current_node = self.getCurrentNode()
        if get_node("ancestor-or-self::prelreq", current_node) and \
           self.isReadOnly(True):
            return
        eff = get_node("ancestor-or-self::eff", current_node)
        check = get_node("ancestor-or-self::check", current_node)
        effgrp = get_node("effgrp", eff)
        ok_enabled = check != None or (eff != None and effgrp == None)
        airplane_tails_list = self.getAirplaneTails()
        dialog = AirplaneTailsDialogImpl(self.qtWidget_, self.sernaDoc_,
                                         airplane_tails_list, ok_enabled)
        if QDialog.Accepted == dialog.exec_loop():
            airplane_tails = dialog.getAirplaneTails()
            self.insertAirplaneTails(airplane_tails)
            
    def getAirplaneTails(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        airplane_tail_list = []
        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        data = self.getMfgModelDash()
        parameters = [("param1", "airplane-def"), ("param3", carrier_code),
                      ("param4", data.manufacturer_), ("param5", data.model_),
                      ("param6", data.dash_)]
        grove = Grove.buildGroveFromFile(self.composeUrl(
            "definitionList", parameters))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        current_airplane_tails = self.getCurrentAirplaneTails()
        
        for gridrow in gridrows:
            airplane_tail = get_datum_from_expr("dul:gridcell[1]", gridrow)
            airplane_msn = get_datum_from_expr("dul:gridcell[2]", gridrow)
            airplane_csn = get_datum_from_expr("dul:gridcell[3]", gridrow)
            selected = airplane_tail in current_airplane_tails
            airplane = airplane_tail, airplane_msn, airplane_csn
            airplane_tail_list.append((airplane, selected))
        qApp.restoreOverrideCursor()
        return airplane_tail_list

    def getCurrentAirplaneTails(self):
        ancestor = get_node("ancestor-or-self::eff or ancestor-or-self::check",
                            self.getCurrentNode())
        if not ancestor:
            return []
        return get_data_from_expr(".//airplane-tail", ancestor)

    def insertAirplaneTails(self, airplane_tails):
        current_node = self.getCurrentNode()
        eff = get_node("ancestor-or-self::eff", current_node)
        parent = get_node("ancestor-or-self::reference or \
        									 ancestor-or-self::accfg or \
                           ancestor-or-self::tool or \
                           ancestor-or-self::part or\
                           ancestor-or-self::circuit-breaker or\
                           ancestor-or-self::zone-panel or\
                           ancestor-or-self::drawing or\
                           ancestor-or-self::table or\
                           ancestor-or-self::graphic or\
                           ancestor-or-self::sign or\
                           ancestor-or-self::warning or\
                           ancestor-or-self::caution or\
                           ancestor-or-self::note or\
                           ancestor-or-self::text or\
                           ancestor-or-self::step6 or\
                           ancestor-or-self::step5 or\
                           ancestor-or-self::step4 or\
                           ancestor-or-self::step3 or\
                           ancestor-or-self::step2 or\
                           ancestor-or-self::step1 or\
                           ancestor-or-self::req-access", current_node)
        if not eff:
            eff = get_node("eff", parent)
        if eff:
            eff.setReadOnly(False)  
        check = get_node("ancestor-or-self::check", current_node)
        effgrp = get_node("effgrp", eff)
        ancestor = get_node("ancestor-or-self::eff or ancestor-or-self::check",
                            current_node)
        if eff and not ancestor:
            ancestor = eff
        batch_cmd = GroveBatchCommand()
        if not check and  not eff:
            element = build_element("eff", None)
            eff_cmd = self.insertElement("*[not(self::sources or self::location or "
                                         "contains(local-name(),'step'))]", parent, element)
            if not eff_cmd:
                return
            batch_cmd.executeAndAdd(eff_cmd)
            eff = get_node("eff", parent)
            ancestor = eff
        delete_tails_command = None
        if get_node("tails", ancestor):
            delete_tails_command = self.removeElement("tails", ancestor)
        elif effgrp:
            delete_tails_command = self.removeElement("effgrp", ancestor)
        empty_batch_cmd = True
        
        if delete_tails_command != None:
            batch_cmd.executeAndAdd(delete_tails_command)
            empty_batch_cmd = False

        if airplane_tails != None or len(airplane_tails > 0):
            element = build_element("tails", airplane_tails)
            insert_tails_command = self.insertElement("check-type or child::*",\
                                   ancestor, element)
            batch_cmd.executeAndAdd(insert_tails_command)
            empty_batch_cmd = False

        if empty_batch_cmd:
            return
            
        self.structEditor_.executeAndUpdate(batch_cmd)
        if eff:
            eff.setReadOnly(True)  

##########################################################################

class AirplaneTailsDialogImpl(AirplaneTailsDialog):
    def __init__(self, parent, sernaDoc, airplane_tails, ok_enabled):
        AirplaneTailsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.okButton_.setEnabled(ok_enabled)
        for at in airplane_tails:
            airplane = at[0]
            selected = at[1]
            listitem = QListViewItem(self.airplaneTailsListView_)
            airplane_tail = airplane[0]
            airplane_msn = airplane[1]
            airplane_csn = airplane[2]
            listitem.setText(0, airplane_tail)
            listitem.setText(1, airplane_msn)
            listitem.setText(2, airplane_csn)
            self.airplaneTailsListView_.setSelected(listitem, selected, True)

    def getAirplaneTails(self):
        airplane_tails = []
        item = self.airplaneTailsListView_.firstChild()
        while item:
            if self.airplaneTailsListView_.isSelected(item):
                airplane_tail = str(item.text(0))
                airplane_tails.append(("airplane-tail", airplane_tail))
            item = item.nextSibling(item, self.airplaneTailsListView_.invisibleRootItem())
        
        return airplane_tails

    def getCheckType(self):
        return self.checkComboBox_.currentText()

    def help(self):
        self.sernaDoc_.showHelp("index.html")
