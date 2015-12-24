from .ExecutorBase import *
from .dialog.PanelTableDialog import PanelTableDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Panel Table
##########################################################################
class InsertPanelTable(ExecutorBase):
    def execute(self):
        pos = self.structEditor_.getSrcPos()
        if pos.isNull():
            return True
        cur = pos.node()
        if get_node("ancestor-or-self::*[@dmidreftype='link' or @dmidreftype='linkStepContinue']", cur):
            self.isReadOnly() # gives warning
            return # read-only linked content

        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
        if not step:
            step = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
        if not step:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "No 'step' elements to insert 'panel-table'")
            return
        pt = -1
        panel = get_node("ancestor-or-self::panel-table", cur)
        is_parent_mainfunc = False
        attr_type = None
        if panel: 
          if panel.parent().nodeName() == "mainfunc":
              is_parent_mainfunc = True
              pos = GrovePos(panel.parent(), panel.nextSibling())
          attr_type = get_datum_from_expr("@type", panel)
          if attr_type:
              pt = int(attr_type[2:])
        dialog = PanelTableDialogImpl(self.qtWidget_, self.sernaDoc_, pt)
        if QDialog.Accepted == dialog.exec_loop():
            batch_cmd = GroveBatchCommand()
            pt = dialog.getPanelTable()
            panel_table = build_element("panel-table", None, [("type", "pt" + str(pt))])
            if panel:
                ge = self.structEditor_.groveEditor()
                panel.setReadOnly(False)  
                batch_cmd.executeAndAdd(ge.removeNode(panel))
            if cur.nodeName() == "mainfunc" or is_parent_mainfunc or \
               cur.nodeName()[0:4] == "step":
                fragment = GroveDocumentFragment()
                fragment.appendChild(panel_table)
                batch_cmd.executeAndAdd(self.structEditor_.groveEditor().paste(fragment, pos))
            else:
                batch_cmd.executeAndAdd(self.insertElement("text|sign|graphic|table|prelreq-data", step, panel_table))
            self.structEditor_.executeAndUpdate(batch_cmd)
            panels = get_nodes("//panel-table", step)
            for p in panels: 
                p.setReadOnly(True)  

##########################################################################

class PanelTableDialogImpl(PanelTableDialog):
    def __init__(self, parent, sernaDoc, pt):
        PanelTableDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        if pt != -1:
            self.groupBox_.setButton(pt-1)
           
    def getPanelTable(self):
        return self.groupBox_.selectedId() + 1

    def help(self):
        self.sernaDoc_.showHelp("index.html")
