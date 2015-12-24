from .ExecutorBase import *
from .dialog.HeadFlagsDialog import HeadFlagsDialog
from qt import *
from PyQt4.QtGui import QDialog
##########################################################################
# Head Flags
##########################################################################
class InsertHeadFlags(ExecutorBase):
    def execute(self):
        if self.isReadOnly():
            return
        config_file = self.composeUrl("definitionList", [("param1", "hflag-def")])
        grove = Grove.buildGroveFromFile(config_file)
        root  = grove.document().documentElement()
        current_node = self.getCurrentNode()
        hflagslist = get_nodes("//mainfunc/head-flags/head-flag", self.srcDoc_)
        cur_flags = []
        for hf in hflagslist:
            attr_type = get_datum_from_expr("@type", hf)
            if attr_type:                      
                cur_flags.append(int(attr_type[2:4]))
        hflagslist = get_nodes("//gridrow", root)
        defined_flags = {}
        
        for hf in hflagslist:
            description = get_datum_from_expr("gridcell[2]", hf).__str__() 
            value = get_datum_from_expr("gridcell[1]", hf).__str__() 
            defined_flags[int(value.__str__()[2:4])] = description
        dialog = HeadFlagsDialogImpl(self.qtWidget_, self.sernaDoc_,
                                     defined_flags,  cur_flags)
        if QDialog.Accepted == dialog.exec_loop():
            flags = dialog.getHeadFlags(len(defined_flags))
            self.replaceOrInsert("head-flags", flags, "no_elem_stab",\
                                 "//mainfunc", None, True)
            
                

##########################################################################

class HeadFlagsDialogImpl(HeadFlagsDialog):
    def __init__(self, parent, sernaDoc, definedFlags, flags):
        HeadFlagsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.setTabOrder(self.headFlagList.getActualObj(),self.okButton_)
        self.setTabOrder(self.okButton_,self.cancelButton_)
        for i in definedFlags.keys():
            value = None
            if i< 10 :
                value = "hf0"+str(i)
            else:
                value = "hf"+str(i)    
            description = definedFlags[i]
            item = QListViewItem(self.headFlagList)
            item.setText(0,value)
            item.setText(1,description)
            if i in flags:
                self.headFlagList.setSelected(item,True,True) 
       
    def getHeadFlags(self,length):
        flags = []        
        item = self.headFlagList.firstChild()
        while item:
            if self.headFlagList.isSelected(item):
                flags.append(("head-flag", None, [("type",str(item.text(0)))])) 
            item = item.nextSibling(item, self.headFlagList.invisibleRootItem())     
        return flags    

    def help(self):
        self.sernaDoc_.showHelp("index.html")
