from .ExecutorBase import *

############################################################################
class InsertAddMarkDialog(ExecutorBase):
    def execute(self):
        """
             execute(plugin)
                    performs the goal of the class object.
                    function is called from corresponded ui action,
                    e.g. pressing appropriate button
        """
        self.changeAttr("changeType", "add")
        self.changeAttr("changeMark", "1")
        
    def changeAttr(self, name, val):
        pos = self.structEditor_.getCheckedPos()
        node = pos.node()
        while node and 1 != node.nodeType(): #TEXT node
            node = node.parent()
        if not node:
            return
        ge = self.structEditor_.groveEditor()
        node = node.asGroveElement()
        attr = node.attrs().getAttribute(name)
        if attr:
            command = ge.setAttribute(attr, val)
        else:
            command = ge.addAttribute(node,PropertyNode(name, val))
        self.structEditor_.executeAndUpdate(command)