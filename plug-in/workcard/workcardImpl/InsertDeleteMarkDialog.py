from .InsertAddMarkDialog import *

############################################################################
class InsertDeleteMarkDialog(InsertAddMarkDialog):
    def execute(self):
        """
             execute(plugin)
                    performs the goal of the class object.
                    function is called from corresponded ui action,
                    e.g. pressing appropriate button
        """
        self.changeAttr("changeType", "delete")
        self.changeAttr("changeMark", "1")