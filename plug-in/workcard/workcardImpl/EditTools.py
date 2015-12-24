from .ExecutorBase import *
from .dialog.ToolsDialog import ToolsDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Tooling
##########################################################################
class EditTools(ExecutorBase):
    def execute(self):
        tools = self.getTools()
        if not self.isValidWorkcardTaskList(tools, "Tools"):
            return 
        dialog = ToolsDialogImpl(self.qtWidget_, self.sernaDoc_, tools)
        if QDialog.Accepted == dialog.exec_loop():
            tools = dialog.getTools()
            self.replaceOrInsert("tools", tools,
                "references drawings zones-panels forecasts "
                "configurations checks maintflow-num crew-type")

    def getTools(self):
        task_tools = []
        current_tools = self.getCurrentTools()
        
        for task in self.getTasks("Info", "tools"):
            tools = []
            task_key = get_attribute(task, "key")
            tool_nodes = get_nodes(".//tool", task)
            for tool_node in tool_nodes:
                vendor_code = get_datum_from_expr("vendor-code", tool_node)
                if not vendor_code:
                    vendor_code = ""
                tool_num = get_datum_from_expr("tool-num", tool_node)
                stk_num = get_datum_from_expr("stk-num", tool_node)
                tool_desc = get_datum_from_expr("tool-desc", tool_node)
                tool_qty = get_datum_from_expr("tool-qty", tool_node)
                uom_code = get_datum_from_expr("uom-code", tool_node)
                tool_state = get_datum_from_expr("tool-state", tool_node)
                tool = [vendor_code, tool_num, stk_num, tool_desc, tool_qty, uom_code, tool_state]
                selected = False
                for ct in current_tools:
                  if tool_num == ct[1]:
                      if vendor_code=="" or vendor_code == ct[0]:
                        selected = True;
                        if tool_qty != ct[2]:
                            tool.append(ct[2])
                        break
                if tool_state != "C":
                    tools.append((tool, selected))                                           
            task_tools.append((task_key, tools))
            
        return task_tools
        
    def getCurrentTools(self):
        tools = []
        tool_nodes = get_nodes("//prelreq/tools/tool", self.srcDoc_)
        for tool_node in tool_nodes:
            task_key = get_datum_from_expr("source-key", tool_node)
            vendor_code = get_datum_from_expr("vendor-code", tool_node)
            if not vendor_code:
                vendor_code = ""
            tool_num = get_datum_from_expr("tool-num", tool_node)
            tool_desc = get_datum_from_expr("tool-desc", tool_node)
            tool_qty = get_datum_from_expr("tool-qty", tool_node)
            uom_code = get_datum_from_expr("uom-code", tool_node)
            tool_state = get_datum_from_expr("tool-state", tool_node)
            tool = vendor_code, tool_num, tool_qty, uom_code, tool_desc, tool_state
            tools.append(tool)
            
        return tools

##########################################################################

class ToolsDialogImpl(ToolsDialog):
    def __init__(self, parent, sernaDoc, tools_selection_list):
        ToolsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        for tool_selection in tools_selection_list:
            task_key = tool_selection[0]
            tools = tool_selection[1]
            for prt in tools:
                tool = prt[0]
                selected = prt[1]
                vendor_code = ""
                tool_num = ""
                stk_num = ""
                tool_desc = ""
                tool_qty = ""
                uom_code = ""
                tool_state = ""
                old_qty = ""
                if tool[0]:
                    vendor_code = tool[0]
                if tool[1]:
                    tool_num = tool[1]
                if tool[2]:
                    stk_num = tool[2]
                if tool[3]:
                    tool_desc = tool[3]
                if tool[4]:
                    tool_qty = tool[4]
                    old_qty = tool_qty
                if tool[5]:
                    uom_code = tool[5]
                if tool[6]:
                    tool_state = tool[6]
                if len(tool)>7 and tool[7]:
                    old_qty = tool[7]
                listitem = QListViewItem(self.toolsListView_, task_key,
                                         vendor_code, tool_num, stk_num, 
                                         tool_desc, old_qty, uom_code, tool_state)
                self.toolsListView_.setSelected(listitem, selected, True)

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
            self.toolsListView_.setSelected(item, False)
        self.processSignal_ = True

    def getTools(self):
        checked_tools = []
        tools = []
        item = self.toolsListView_.firstChild()
        while item:
            if self.toolsListView_.isSelected(item):
                if (item.text(1), item.text(2), item.text(3), item.text(4)) in checked_tools:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated tool will be skiped:\n source-key:" + 
                     str(item.text(0)) + "\n vendor code:" +  str(item.text(1)) +
                     "\n tool number:" + str(item.text(2)))
                    item = item.nextSibling(item, self.toolsListView_.invisibleRootItem())
                    continue;

                children = []
                if item.text(0):
                    children.append(("source-key", str(item.text(0))))
                if item.text(1):
                    children.append(("vendor-code", str(item.text(1))))
                if item.text(2):
                    children.append(("tool-num", str(item.text(2))))
                if item.text(3):
                    children.append(("stk-num", str(item.text(3))))
                if item.text(4):
                    children.append(("tool-desc", str(item.text(4))))
                if item.text(5):
                    children.append(("tool-qty", str(item.text(5))))
                if item.text(6):
                    children.append(("uom-code", str(item.text(6))))
                if item.text(7):
                    children.append(("tool-state", str(item.text(7))))
                tools.append(("tool", children))
                checked_tools.append((item.text(1),item.text(2),item.text(3),item.text(4)))
            item = item.nextSibling(item, self.toolsListView_.invisibleRootItem())   
        return tools

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#too-dialog")
