from .EditAirplaneTails import *
from .dialog.EffectivityGroupDialog import EffectivityGroupDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog, QTreeWidget, QAbstractItemView, QMessageBox
from PyQt4.QtCore import Qt
##########################################################################
# Effectivity Group
##########################################################################
class EditEffectivityGroup(EditAirplaneTails):
    def execute(self):
        current_node = self.getCurrentNode()
        if get_node("ancestor-or-self::prelreq", current_node) and \
           self.isReadOnly(True):
            return

        if get_node("ancestor-or-self::*[@dmidreftype='link' or @dmidreftype='linkStepContinue']", current_node):
            self.isReadOnly() # gives warning
            return # read-only linked content

        parent = get_node("ancestor-or-self::reference or\
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
        if not parent:
            QMessageBox.warning(self.qtWidget_, "Warning", "According to schema,"
                " 'Effectivity Group' cannot be inserted here.\n"
                "You can insert this element in the following parent element:\n"
                "'accfg', 'tool', 'part', 'circuit-breaker', 'zone-panel','drawing',\n"
                "'table', 'graphic', 'sign', 'warning', 'caution', 'note',\n"
                "'text', 'req-access', 'step1', 'step2', 'step3', 'step4', 'step5', 'step6'.")
            return None
        eff = get_node("eff", parent)
        if eff:
            eff.setReadOnly(False)  
        effectivity_group_list = self.getEffectivityGroup(eff)
        dialog = EffectivityGroupDialogImpl(self.qtWidget_, self.sernaDoc_,
                 effectivity_group_list, self.getAirplaneTails())
        if QDialog.Accepted == dialog.exec_loop():
            if dialog.isEffMode():
                self.insertEffectivityGroup(parent, eff, 
                                            dialog.getEffectivityGroup())
            else:
                self.insertAirplaneTails(dialog.getAirplaneTails())
    
    def getEffectivityGroup(self, eff):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        effectivity_group_list = []
        data = self.getMfgModelDash()        
        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        url = self.composeUrl(
            "definitionList", [("param1", "effgrp-fleet-def"),
                               ("param2", "Effectivity Groups"),
                               ("param3", carrier_code),
                               ("param4", data.manufacturer_),
                               ("param5", data.model_),
                               ("param6", data.dash_)])
        grove = Grove.buildGroveFromFile(url)

        gridrows = get_nodes("//dul:gridrow", grove.document())
        current_effectivity_group = None
        if eff:
            current_effectivity_group = get_datum_from_expr("effgrp", eff)        
        for gridrow in gridrows:
            effectivity_group = get_datum_from_expr("dul:gridcell[1]",gridrow)
            selected = effectivity_group == current_effectivity_group
            effectivity_group_list.append((effectivity_group, selected))
        qApp.restoreOverrideCursor()
        return effectivity_group_list

    def insertEffectivityGroup(self, parent, effNode, eff):
        batch_cmd = GroveBatchCommand()
        if eff == None:
            if effNode:
                self.structEditor_.executeAndUpdate(
                    self.removeElement("self::eff", effNode))
            return
        if not effNode:
            element = build_element("eff", None)
            batch_cmd.executeAndAdd(self.insertElement(\
                               "*[not(self::sources or self::location or contains(local-name(),'step'))]",
                                parent, element))
            effNode = get_node("eff", parent)
        elif get_node("effgrp", effNode):
            batch_cmd.executeAndAdd(self.removeElement("effgrp", effNode))
        elif get_node("tails", effNode):
            batch_cmd.executeAndAdd(self.removeElement("tails", effNode))
        element = build_element("effgrp", str(eff))
        batch_cmd.executeAndAdd(self.insertElement(\
                               "*", effNode, element))
        self.structEditor_.executeAndUpdate(batch_cmd)
        effNode.setReadOnly(True)  

##########################################################################

class EffectivityGroupDialogImpl(EffectivityGroupDialog):
    def __init__(self, parent, sernaDoc, effectivity_group_list,
                 airplane_tails):
        EffectivityGroupDialog.__init__(self, parent)
        self.effList_ = effectivity_group_list
        self.tailList_ = airplane_tails
        self.sernaDoc_ = sernaDoc
        self.prevSelItem_ = None
        self.okButton_.setEnabled(True)
        self.mode_ = "tail"
        self.switchMode()
    
    def isEffMode(self):
        if self.mode_ == "eff":
            return True
        return False

    def getEffectivityGroup(self):
        item = self.listView_.selectedItem()
        if item:
            return item.text(0)
        return None

    def getAirplaneTails(self):
        airplane_tails = []
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item):
                airplane_tail = str(item.text(0))
                airplane_tails.append(("airplane-tail", airplane_tail))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())    
        return airplane_tails

    def selectionChanged(self):
        item = self.listView_.selectedItem()
        if item and self.prevSelItem_ == item:
            self.prevSelItem_ = None
            self.listView_.setSelected(item, False)
            return;
        self.prevSelItem_ = item


    def switchMode(self):
        self.listView_.clear()
        if self.mode_ == "eff":
            self.switchButton_.setText("S&witch to Effectivity Groups View")
            #self.listView_.header().setLabel(0, "Airplane Tail Number")
            headList = []
            headList.append("Airplane Tail Number")
            headList.append("Airplane Mfg Serial Number")
            headList.append("Airplane Customer Serial Number")
            self.listView_.addColumn(headList)
            self.listView_.setColumnWidth(0, 110)
            self.listView_.setSelectionMode(QAbstractItemView.MultiSelection)
            #self.listView_.setAllColumnsShowFocus(1)
            #self.listView_.setResizeMode(QTreeWidget.AllColumns)
            self.mode_ = "tail"
            for at in self.tailList_:
                listitem = QListViewItem(self.listView_, at[0][0],
                                         at[0][1], at[0][2])
                self.listView_.setSelected(listitem, at[1], True)
        else:
            self.switchButton_.setText("S&witch to Airplane Tails View")
            if self.listView_.columns() > 1:
                self.listView_.removeColumn(1)
                self.listView_.removeColumn(1)
            #self.listView_.setResizeMode(QTreeWidget.AllColumns)
            #self.listView_.header().setLabel(0, "Effectivity Groups")
            self.listView_.header().model().setHeaderData(0,Qt.Horizontal,"Effectivity Groups",0)
            self.mode_ = "eff"
            for group in self.effList_:
                listitem = QListViewItem(self.listView_, group[0])
                self.listView_.setSelected(listitem, group[1])
        self.selectionChanged()


    def help(self):
        self.sernaDoc_.showHelp("index.html")
