from .ExecutorBase import *
from .dialog.TasksDialog import TasksDialog
from .dialog.LineEditDialog import LineEditDialog
from qt import *
from PyQt4.QtGui import QDialog
##########################################################################
# Tasks
##########################################################################
class EditTasks(ExecutorBase):
    def execute(self):
        current_node = self.getCurrentNode()
        task_list = get_nodes("//prelreq/source-docs/tasks/task-key", self.srcDoc_)
        tasks = []
        for task in task_list:
            val = get_datum_from_expr("self::*", task)
            tasks.append(val)
        dialog = TasksDialogImpl(self.qtWidget_, self.sernaDoc_, tasks)
        if QDialog.Accepted == dialog.exec_loop():
            self.updateTasks(dialog.getTasks())
            
    def updateTasks(self, tasks):
        ge = self.structEditor_.groveEditor()
        tasks_node = get_node("//prelreq/source-docs/tasks", self.srcDoc_)
        batch_cmd = GroveBatchCommand()
        if not tasks_node:
            fragment = GroveDocumentFragment()
            fragment.appendChild(build_element( "source-docs", None))
            mzone = get_node("major-zone", self.prelreqNode_)
            batch_cmd.executeAndAdd(ge.paste(fragment, \
                GrovePos(self.prelreqNode_, mzone)))
        else:
            batch_cmd.executeAndAdd(ge.removeNode(tasks_node))
        parent = get_node("source-docs", self.prelreqNode_)
        if len(tasks) > 0:
            tasks_node = build_element( "tasks", None)
            for task in tasks:
                tasks_node.appendChild(build_element("task-key", task.__str__()))  
            fragment = GroveDocumentFragment()
            fragment.appendChild(tasks_node)
            batch_cmd.executeAndAdd(ge.paste(fragment, GrovePos(parent)))
        else:
            batch_cmd.executeAndAdd(ge.removeNode(parent))
        self.structEditor_.executeAndUpdate(batch_cmd)


##########################################################################

class TasksDialogImpl(TasksDialog):
    def __init__(self, parent, sernaDoc, tasks_selection_list):
        TasksDialog.__init__(self, parent)
        self.connect(self.tasksListView_.getActualObj(), SIGNAL("currentItemChanged(QTreeWidgetItem*,QTreeWidgetItem*)"),self.selectionChanged)
        self.sernaDoc_ = sernaDoc
        for task_key in tasks_selection_list:
            listitem = QListViewItem(self.tasksListView_, task_key.__str__())
        #self.selectionChanged()
        self.tasksListView_.setSelected(self.tasksListView_.firstChild(), True)

    def getTasks(self):
        tasks = []
        item = self.tasksListView_.firstChild()
        itemIndex = 0
        while item:
            tasks.append(item.text(0).__str__())
            item = self.tasksListView_.getActualObj().invisibleRootItem().child(itemIndex+1)
            itemIndex += 1   
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
        self.editButton_.setEnabled(item != None)
        self.removeButton_.setEnabled(item != None)
        self.tasksListView_.setSelectedItemsFlase()
        if item:
            self.tasksListView_.setSelected(item, True)
        #self.okButton_.setEnabled(self.tasksListView_.firstChild() != None)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#too-dialog")

##########################################################################
      
class LineEditDialogImpl(LineEditDialog):
    def __init__(self, parent, caption, text = None):
        LineEditDialog.__init__(self, parent)
        self.setCaption(caption)
        if text:
            self.lineEdit_.setText(text)
        self.lineEdit_.setFocus()
           
    def getText(self):
        return self.lineEdit_.text().__str__()
