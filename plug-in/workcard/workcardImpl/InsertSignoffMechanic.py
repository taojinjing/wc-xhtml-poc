from .ExecutorBase import *
from .EditSignBlocks import EditSignBlocks

##########################################################################
# Sign off Mechanic
##########################################################################
class InsertSignoffMechanic(EditSignBlocks):
    def execute(self):
        EditSignBlocks.editSB(self, True)
