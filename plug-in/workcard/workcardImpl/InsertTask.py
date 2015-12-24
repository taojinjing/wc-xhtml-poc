from .ExecutorBase import *
from .dialog.TaskRefDialog import TaskRefDialog
from .dialog.LineEditDialog import LineEditDialog
from qt import *
from SernaApi import *
from PyQt4.QtGui import QMessageBox, QDialog
##########################################################################
# Tasks
##########################################################################
class InsertTask(ExecutorBase):
    def execute(self):
        if self.isReadOnly():
            return
        current_node = self.getCurrentNode()
        task_list = get_nodes("//prelreq/source-docs/tasks/task-key", self.srcDoc_)
        tasks = []
        for task in task_list:
            val = get_datum_from_expr("self::*", task)
            tasks.append(val)
        dialog = TaskRefDialogImpl(self.qtWidget_, self.sernaDoc_, tasks)
        if QDialog.Accepted == dialog.exec_loop():
            self.insertTask(dialog.getTarget())
            
    def insertTask(self, task):
        ge = self.structEditor_.groveEditor()
        se = self.structEditor_
        batch_cmd = GroveBatchCommand()
        cur = self.getCurrentNode()
        pos = None
        context = get_node("ancestor-or-self::table or \
                        ancestor-or-self::graphic or \
                        ancestor-or-self::sign or \
                        ancestor-or-self::warning or \
                        ancestor-or-self::caution or \
                        ancestor-or-self::note or \
                        ancestor-or-self::text or \
                        ancestor-or-self::req-access", cur)

        if context:
            pos = GrovePos(context)
        children = [("type", "Task"),("ref", str(task)),("note", "")]    
        source = build_element("source", children)
        sources = get_node("ancestor-or-self::sources", cur)
        if sources:
            batch_cmd.executeAndAdd(self.insertElement("*", sources, source))
        else:  
            sources = build_element("sources", [("source", children)])
            fragment = GroveDocumentFragment()
            fragment.appendChild(sources)
            batch_cmd.executeAndAdd(self.structEditor_.groveEditor().paste(fragment, pos))
        self.structEditor_.executeAndUpdate(batch_cmd)
        
        
class TaskRefDialogImpl(TaskRefDialog):
    def __init__(self, parent, sernaDoc, tasks_selection_list):
        TaskRefDialog.__init__(self, parent)
        self.setCaption("Add Tasks Reference")
        self.sernaDoc_ = sernaDoc
        for task_key in tasks_selection_list:
            listitem = QListViewItem(self.tasksListView_, task_key.__str__())
        self.selectionChanged()
        self.tasksListView_.setSelected(self.tasksListView_.firstChild(), True)

    def getTasks(self):
        tasks = []
        item = self.tasksListView_.firstChild()
        while item:
            tasks.append(item.text(0).__str__())
            item = item.nextSibling(item, self.tasksListView_.invisibleRootItem())       
        return tasks

    def add(self):
        dialog = LineEditDialogImpl(self, "Add Task","")
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            if not self.hasDup(dialog.getText()):
                QListViewItem(self.tasksListView_, dialog.getText())

    def edit(self):
        item = self.tasksListView_.selectedItem()
        if not item:
            return
        task = item.text(0).__str__()
        dialog = LineEditDialogImpl(self, "Edit Task", task)
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            if not self.hasDup(dialog.getText()):
                item.setText(0, dialog.getText())

    def remove(self):
        item = self.tasksListView_.selectedItem()
        next = item.itemBelow()
        if not next:
            next = item.itemAbove()
        if item:
            self.tasksListView_.takeItem(item)
        if next:
            self.tasksListView_.setSelected(next, True)
        else:
            self.selectionChanged()

    def hasDup(self, text):
        item = self.tasksListView_.firstChild()
        while item:
            if text == item.text(0).__str__():
                return True
            item = item.nextSibling(item, self.tasksListView_.invisibleRootItem())       
        return False

    def selectionChanged(self):
        item = self.tasksListView_.selectedItem()
        #self.okButton_.setEnabled(self.tasksListView_.firstChild() != None)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#too-dialog")
        
    def getTarget(self):
        selected_item = self.tasksListView_.selectedItem()
        if selected_item:
            return selected_item.text(0)
        return None

