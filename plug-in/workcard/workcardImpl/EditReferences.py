from .ExecutorBase import *
from .dialog.ReferencesDialog import ReferencesDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# References
##########################################################################

class EditReferences(ExecutorBase):

    def execute(self):
        references_selection_list = self.getReferences()
        if not self.isValidWorkcardTaskList(references_selection_list,\
            "References"):
            return 
        dialog = ReferencesDialogImpl(self.qtWidget_, self.sernaDoc_,
                                      references_selection_list)
        if QDialog.Accepted == dialog.exec_loop():
            references = dialog.getReferences()
            self.replaceOrInsert("references", references,
                    "drawings zones-panels forecasts configurations checks maintflow-num crew-type")
    
    def getReferences(self):
        task_references = []
        tasks = self.getTasks("Info", "references")
        current_references = self.getCurrentReferences()
        
        for task in tasks: 
            task_key = get_attribute(task, "key")
            references = []
            reference_nodes = get_nodes(".//reference", task)
            for reference_node in reference_nodes:
                refid = get_attribute(reference_node, "refid")
                reforigin_type = get_datum_from_expr(
                    "reforigin-type", reference_node)
                ref_desc = get_datum_from_expr(
                    "ref-desc", reference_node)
                task_primary = get_datum_from_expr(
                    "task-primary", reference_node)
                wc_primary = get_datum_from_expr(
                    "wc-primary", reference_node)
                reference = refid, reforigin_type, ref_desc, \
                            task_primary, wc_primary
                selected = (task_key, refid) in current_references
                references.append((reference, selected))
            task_references.append((task_key, references))

        return task_references

    def getCurrentReferences(self):
        references = []
        reference_nodes = get_nodes("//prelreq/references/reference",
                                    self.srcDoc_)
        for reference_node in reference_nodes:
            task_key = get_datum_from_expr("source-key", reference_node)
            refid = get_datum_from_expr("refid", reference_node)
            references.append((task_key, refid))

        return references


class ReferencesDialogImpl(ReferencesDialog):
    def __init__(self, parent, sernaDoc, list):
        ReferencesDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        self.__resultMap = {}
        for item in list:
            task_key = item[0]
            references = item[1]
            for ref in references:
                reference = ref[0]
                selected = ref[1]
                listitem = QListViewItem(self.taskListView_)
                refid = reference[0]
                reforigin_type = reference[1]
                ref_desc = reference[2]
                task_primary = reference[3]
                wc_primary = reference[4]
                listitem.setText(0, task_key)
                listitem.setText(1, reforigin_type)
                listitem.setText(2, ref_desc)
                listitem.setText(3, task_primary)
                listitem.setText(4, wc_primary)
                self.taskListView_.setSelected(listitem, selected, True)
                self.__resultMap[listitem] = refid

    def selectionChanged(self):
        if not self.processSignal_:
            return
        cur = self.taskListView_.currentItem()
        if not self.taskListView_.isSelected(cur):
            return
        deselectitems = []
        item = self.taskListView_.firstChild()
        while item:
            if self.taskListView_.isSelected(item) and  cur != item and \
               cur.text(1) == item.text(1) and cur.text(2) == item.text(2): 
                deselectitems.append(item) 
            item = item.nextSibling(item, self.taskListView_.invisibleRootItem())
        self.processSignal_ = False
        for item in deselectitems:
            self.taskListView_.setSelected(item, False, True)
        self.processSignal_ = True
        
        
    def selectionChangedBack(self, item, itemIdex):
        ifslect = self.taskListView_.isSelected(item)
        self.taskListView_.setSelected(item, not ifslect, True)
                
    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#ref-dialog")
    
    def insertReferences(self):
        self.accept()
    
    def getReferences(self):
        checked_tools = []
        references = []
        item = self.taskListView_.firstChild()
        while item:
            if self.taskListView_.isSelected(item):
                if (item.text(1),item.text(1)) in checked_tools:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated reference will be skiped:\n source-key:" + 
                     str(item.text(0)) + "\n origin:" +  str(item.text(1)) +
                     "\n description:" + str(item.text(2)) + 
                     "\n task primary:" + str(item.text(3)) + 
                     "\n wc primary:" + str(item.text(4)))
                    item = item.nextSibling(item, self.taskListView_.invisibleRootItem())
                    continue;

                task_key = str(item.text(0))
                try:
                    refid = self.__resultMap[item]
                    references.append(("reference", [("source-key", task_key), ("refid", refid)]))
                    checked_tools.append((item.text(1),item.text(2)))
                except KeyError:
                    a = 1
            item = item.nextSibling(item, self.taskListView_.invisibleRootItem())
        
        return references