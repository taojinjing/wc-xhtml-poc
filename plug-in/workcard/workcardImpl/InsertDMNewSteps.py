from SernaApi import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *
from urllib import *
from .InsertDMRef import *;


class InsertDMRefNewStepImpl(InsertDMRefImpl):
    def __init__(self, plugin, parent, structEditor, dmID, dmCode):
        self.has_unchecked_step_ = False
        InsertDMRefImpl.__init__(self, plugin, parent, structEditor, dmID, dmCode)


    def buildTable(self, rowNum, data):
        InsertDMRefImpl.buildTable(self, rowNum, data)
        linkedCB = self.tableView_.item(rowNum, 0)
        adaptedCB = self.tableView_.item(rowNum, 1)
        if (not self.has_unchecked_step_) and (linkedCB.isEnabled() or adaptedCB.isEnabled()):
            self.has_unchecked_step_ = True

    def place_to_insert(self, new_step_node):
        se = self.structEditor_
        current_document = self.structEditor_.sourceGrove().document()

        new_step_name= new_step_node.nodeName()
        new_step_id = get_node("/" + new_step_name + "/@id", new_step_node).value()
        pre_fragment_node = None
        post_fragment_node = None
        is_pre_current_node = True
        for step_node in self.result_:
            if step_node.id_==new_step_id:
                is_pre_current_node = False
                continue
            node = get_node("//*[@id='"+step_node.id_+"']", current_document)
            if node:
                if is_pre_current_node:
                    pre_fragment_node = node
                else:
                    post_fragment_node = node
                    break
        pos = None
        if pre_fragment_node:
            temp_pos = GrovePos(pre_fragment_node.parent(), pre_fragment_node.nextSibling())
            if self.structEditor_.canInsertElement(new_step_name,"",temp_pos):
                pos = temp_pos
        if not pos and post_fragment_node:
            temp_pos = GrovePos(post_fragment_node.parent(), post_fragment_node)
            if self.structEditor_.canInsertElement(new_step_name,"",temp_pos):
                pos = temp_pos
        if pos:
            se.setCursorBySrcPos(pos, se.getFoPos().node(), True)
            return pos
        return None