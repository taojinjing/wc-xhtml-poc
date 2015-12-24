from .ExecutorBase import *
from .dialog.PartsDialog import PartsDialog
from qt import *
import time
from PyQt4.QtGui import QDialog
##########################################################################
# Tooling
##########################################################################
class EditPartsInContent(ExecutorBase):
    def execute(self):
        parts = self.getCurrentParts()
        if len(parts) < 1:
            return [];
        dialog = PartsInContentDialogImpl(self.qtWidget_, self.sernaDoc_, parts)
        if QDialog.Accepted == dialog.exec_loop():
            return dialog.getParts()

    def getCurrentParts(self):
        parts = []
        part_nodes = get_nodes("//prelreq/parts/part", self.srcDoc_)
        for part_node in part_nodes:
            partn = part_node.asGroveElement()
            attrs = partn.attrs()
            id_val = self.structEditor_.generateId("%t")
            idattr = get_attribute(partn, "id")
            if not idattr:
                attrs.setAttribute(GroveAttr("id",id_val))
                time.sleep(0.05)
            else:
                id_val = idattr
            vendor_code = get_datum_from_expr("vendor-code", part_node)
            if not vendor_code:
                vendor_code = ""
            part_num = get_datum_from_expr("part-num", part_node)
            task_key = get_datum_from_expr("source-key", part_node)
            part_desc = get_datum_from_expr("part-desc", part_node)
            part_qty = get_datum_from_expr("part-qty", part_node)
            part_state = get_datum_from_expr("part-state", part_node)
            part = id_val,task_key,vendor_code, part_num, part_qty, part_desc, part_state
            parts.append(part)           
        return parts

##########################################################################

class PartsInContentDialogImpl(PartsDialog):

    def __init__(self, parent, sernaDoc, parts_selection_list):
        PartsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        self.id_map = {}
        for part in parts_selection_list:
            id_val = part[0]
            task_key = part[1]
            selected = False
            vendor_code = ""
            old_qty = ""
            if part[2]:
                vendor_code = part[2]
            part_num = ""
            if part[3]:
                part_num = part[3]
            stk_num = ""
            if part[4]:
                part_qty = part[4]
                old_qty = part_qty
            part_desc = ""
            if part[5]:
                part_desc = part[5]
            if part[6]:
                part_state = part[6]
            listitem = QListViewItem(self.partsListView_, task_key,
                                     vendor_code, part_num, stk_num, 
                                     part_desc, old_qty, part_state)
            self.id_map[listitem] = id_val

    def selectionChanged(self):
        if not self.processSignal_:
            return
        cur = self.partsListView_.currentItem()
        if not self.partsListView_.isSelected(cur):
            return
        deselectitems = []
        item = self.partsListView_.firstChild()
        while item:
            if self.partsListView_.isSelected(item) and  cur != item and \
               cur.text(1) == item.text(1) and cur.text(2) == item.text(2) and \
               cur.text(3) == item.text(3) and cur.text(4) == item.text(4): 
                deselectitems.append(item) 
            item = item.nextSibling(item, self.partsListView_.invisibleRootItem())
        self.processSignal_ = False
        for item in deselectitems:
            self.partsListView_.setSelected(item, False, True)
        self.processSignal_ = True

    def getParts(self):
        checked_parts = []
        parts = []
        item = self.partsListView_.firstChild()
        while item:
            if self.partsListView_.isSelected(item):
                parts.append(self.id_map[item].__str__())
            item = item.nextSibling(item, self.partsListView_.invisibleRootItem())      
        return parts

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#par-dialog")
