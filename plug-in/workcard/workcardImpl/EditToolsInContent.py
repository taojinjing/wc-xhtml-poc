from .ExecutorBase import *
from .dialog.ToolsDialog import ToolsDialog
from qt import *
import time
from PyQt4.QtGui import QDialog
##########################################################################
# Tooling
##########################################################################
class EditToolsInContent(ExecutorBase):
    def execute(self):
        tools = self.getCurrentTools()
        if len(tools) < 1:
            return [];
        dialog = ToolsInContentDialogImpl(self.qtWidget_, self.sernaDoc_, tools)
        if QDialog.Accepted == dialog.exec_loop():
            return dialog.getTools()

    def getCurrentTools(self):
        tools = []
        tool_nodes = get_nodes("//prelreq/tools/tool", self.srcDoc_)
        for tool_node in tool_nodes:
            tooln = tool_node.asGroveElement()
            attrs = tooln.attrs()
            id_val = self.structEditor_.generateId("%t")
            idattr = get_attribute(tooln, "id")
            if not idattr:
                attrs.setAttribute(GroveAttr("id",id_val))
                time.sleep(0.05)
            else:
                id_val = idattr
            task_key = get_datum_from_expr("source-key", tool_node)
            vendor_code = get_datum_from_expr("vendor-code", tool_node)
            if not vendor_code:
                vendor_code = ""
            tool_num = get_datum_from_expr("tool-num", tool_node)
            tool_desc = get_datum_from_expr("tool-desc", tool_node)
            tool_qty = get_datum_from_expr("tool-qty", tool_node)
            tool_state = get_datum_from_expr("tool-state", tool_node)
            tool = id_val, task_key,vendor_code, tool_num, tool_qty, tool_desc, tool_state
            tools.append(tool)
        return tools

##########################################################################

class ToolsInContentDialogImpl(ToolsDialog):
    def __init__(self, parent, sernaDoc, tools_selection_list):
        ToolsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        self.id_map = {}
        for tool in tools_selection_list:
            selected = False
            vendor_code = ""
            tool_num = ""
            task_key = ""
            stk_num = ""
            tool_desc = ""
            tool_qty = ""
            tool_state = ""
            old_qty = ""
            id_val = tool[0]
            if tool[1]:
                task_key = tool[1]
            if tool[2]:
                vendor_code = tool[2]
            if tool[3]:
                tool_num = tool[3]
            if tool[4]:
                tool_qty = tool[4]
                old_qty = tool_qty
            if tool[5]:
                tool_desc = tool[5]
            if tool[6]:
                tool_state = tool[6]
            listitem = QListViewItem(self.toolsListView_, task_key,
                                     vendor_code, tool_num, stk_num, 
                                     tool_desc, old_qty, tool_state)
            self.id_map[listitem] = id_val
            #self.toolsListView_.setSelected(listitem, selected)

    def selectionChanged(self):
        if not self.processSignal_:
            return
        cur = self.toolsListView_.currentItem()
        if not self.toolsListView_.isSelected(cur):
            return
        deselectitems = []
        item = self.toolsListView_.firstChild()
        while item:
            if self.toolsListView_.isSelected(item) and  cur != item and \
               cur.text(1) == item.text(1) and cur.text(2) == item.text(2) and \
               cur.text(3) == item.text(3) and cur.text(4) == item.text(4): 
                deselectitems.append(item) 
            item = item.nextSibling(item, self.toolsListView_.invisibleRootItem())
        self.processSignal_ = False
        for item in deselectitems:
            self.toolsListView_.setSelected(item, False, True)
        self.processSignal_ = True

    def getTools(self):
        tools = []
        item = self.toolsListView_.firstChild()
        while item:
            if self.toolsListView_.isSelected(item):
                tools.append(self.id_map[item].__str__())
            item = item.nextSibling(item, self.toolsListView_.invisibleRootItem())      
        return tools

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#too-dialog")
