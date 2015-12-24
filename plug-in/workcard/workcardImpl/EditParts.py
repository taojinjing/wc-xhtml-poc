from .ExecutorBase import *
from .dialog.PartsDialog import PartsDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Parts
##########################################################################
class EditParts(ExecutorBase):
    def execute(self):
        parts = self.getParts()
        if not self.isValidWorkcardTaskList(parts, "Parts"):
            return 
        dialog = PartsDialogImpl(self.qtWidget_, self.sernaDoc_, parts)
        if QDialog.Accepted == dialog.exec_loop():
            parts = dialog.getParts()
            self.replaceOrInsert("parts", parts, 
                "tools references drawings zones-panels forecasts "
                "configurations checks maintflow-num crew-type")
            
    def getParts(self):
        task_parts = []
        tasks = self.getTasks("Info", "parts")
        current_parts = self.getCurrentParts()
        
        for task in tasks:
            parts = []
            task_key = get_attribute(task, "key")
            part_nodes = get_nodes(".//part", task)
            for part_node in part_nodes:
                vendor_code = get_datum_from_expr("vendor-code", part_node)
                if not vendor_code:
                    vendor_code = ""
                part_num = get_datum_from_expr("part-num", part_node)
                url = self.composeUrl("getPartInfo", [("vendorCode", vendor_code),
                                 ("partNumber",part_num)])
                grove = Grove.buildGroveFromFile(url)
                part_desc = get_datum_from_expr("//partDescription",grove.document())

                if not part_desc or len(part_desc) < 1 :
                    part_desc = get_datum_from_expr("part-desc", part_node)
                stk_num = get_datum_from_expr("stk-num", part_node)
                part_qty = get_datum_from_expr("part-qty", part_node)
                uom_code = get_datum_from_expr("uom-code", part_node)
                partType_code = get_datum_from_expr("part_type-code", part_node)
                part_state = get_datum_from_expr("part-state", part_node)
                part = [vendor_code, part_num, stk_num, part_desc, part_qty, uom_code, partType_code,part_state]
                selected = False
                for ct in current_parts:
                  if part_num == ct[1]:
                      if vendor_code=="" or vendor_code == ct[0]:
                        selected = True;
                        if part_qty != ct[2]:
                            part.append(ct[2])
                        break
                if part_state != "C":
                    parts.append((part, selected))
            task_parts.append((task_key, parts))
            
        return task_parts
        
    def getCurrentParts(self):
        parts = []
        part_nodes = get_nodes("//prelreq/parts/part", self.srcDoc_)
        for part_node in part_nodes:
            vendor_code = get_datum_from_expr("vendor-code", part_node)
            if not vendor_code:
                vendor_code = ""
            part_num = get_datum_from_expr("part-num", part_node)
            task_key = get_datum_from_expr("source-key", part_node)
            part_desc = get_datum_from_expr("part-desc", part_node)
            part_qty = get_datum_from_expr("part-qty", part_node)
            uom_code = get_datum_from_expr("uom-code", part_node)
            partType_code = get_datum_from_expr("part_type-code", part_node)
            part_state = get_datum_from_expr("part-state", part_node)
            part = task_key, vendor_code, part_num, part_desc, part_qty, uom_code, partType_code, part_state
            part = vendor_code, part_num, part_qty, uom_code, partType_code, part_desc, part_state
            parts.append(part)           
        return parts

##########################################################################

class PartsDialogImpl(PartsDialog):
    def __init__(self, parent, sernaDoc, parts_selection_list):
        PartsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        for part_selection in parts_selection_list:
            task_key = part_selection[0]
            parts = part_selection[1]
            for prt in parts:
                part = prt[0]
                selected = prt[1]
                vendor_code = ""
                old_qty = ""
                if part[0]:
                    vendor_code = part[0]
                part_num = ""
                if part[1]:
                    part_num = part[1]
                stk_num = ""
                if part[2]:
                    stk_num = part[2]
                part_desc = ""
                if part[3]:
                    part_desc = part[3]
                if part[4]:
                    part_qty = part[4]
                    old_qty = part_qty
                uom_code = ""
                if part[5]:
                    uom_code = part[5]
                partType_code = ""
                if part[6]:
                    partType_code = part[6]
                if part[7]:
                    part_state = part[7]
                if len(part)>8 and part[8]:
                    old_qty = part[8]
                listitem = QListViewItem(self.partsListView_, task_key,
                                         vendor_code, part_num, stk_num, 
                                         part_desc, old_qty, uom_code, partType_code)
                listitem.setText(8, part_state)
                self.partsListView_.setSelected(listitem, selected, True)

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
            self.partsListView_.setSelected(item, False)
        self.processSignal_ = True

    def getParts(self):
        checked_parts = []
        parts = []
        item = self.partsListView_.firstChild()
        while item:
            if self.partsListView_.isSelected(item):
                if (item.text(1), item.text(2), item.text(3), item.text(4)) in checked_parts:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated part will be skiped:\n source-key:" + 
                     str(item.text(0)) + "\n vendor code:" +  str(item.text(1)) +
                     "\n part number:" + str(item.text(2)))
                    item = item.nextSibling(item, self.partsListView_.invisibleRootItem())
                    continue;
                task_key = str(item.text(0))
                vendor_code = str(item.text(1))
                part_num = str(item.text(2))
                stk_num = str(item.text(3))
                part_desc = str(item.text(4))
                part_qty = str(item.text(5))
                uom_code = str(item.text(6))
                partType_code = str(item.text(7))
                part_state = str(item.text(8))
                children = [("source-key", task_key)]
                if vendor_code and vendor_code != "":
                    children.append(("vendor-code", vendor_code))
                if part_num and part_num != "":
                    children.append(("part-num", part_num))
                if stk_num and stk_num != "":
                    children.append(("stk-num", stk_num))
                if part_desc and part_desc != "":
                    children.append(("part-desc", part_desc))
                children.append(("part-qty", part_qty))
                if uom_code and uom_code != "":
                    children.append(("uom-code", uom_code))
                if partType_code and partType_code != "":
                    children.append(("part_type-code", partType_code))
                children.append(("part-state", part_state))
                parts.append(("part", children))
                checked_parts.append((item.text(1),item.text(2),item.text(3),item.text(4)))
            item = item.nextSibling(item, self.partsListView_.invisibleRootItem())       
        return parts

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#par-dialog")
