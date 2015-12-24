from .ExecutorBase import *

############################################################################
class InsertClearMarkDialog(ExecutorBase):
    def execute(self):
        """
             execute(plugin)
                    performs the goal of the class object.
                    function is called from corresponded ui action,
                    e.g. pressing appropriate button
        """
        self.removeAttr("changeType")
        self.removeAttr("changeMark")
        
    def removeAttr(self, name):
        pos = self.structEditor_.getCheckedPos()
        node = pos.node()
        while node and 1 != node.nodeType(): #TEXT node
            node = node.parent()
        if not node:
            return
        attr = node.asGroveElement().attrs().getAttribute(name)
        if attr:
            command = self.structEditor_.groveEditor().removeAttribute(attr)
            self.structEditor_.executeAndUpdate(command)

