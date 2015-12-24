from .ExecutorBase import *
from .dialog.ConfigurationsDialog import ConfigurationsDialog
from qt import *
import string
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Configurations
##########################################################################
class EditConfigurations(ExecutorBase):
    def execute(self):
        configurations = self.getConfigurations()
        if not self.isValidWorkcardTaskList(configurations, "Configuration"):
            return 
        dialog = ConfigurationsDialogImpl(self.qtWidget_, self.sernaDoc_,
                                          configurations)
        if QDialog.Accepted == dialog.exec_loop():
            configurations = dialog.getConfigurations()
            self.replaceOrInsert("configurations", configurations,
                    "checks maintflow-num crew-type")
            
    def getConfigurations(self):
        task_configurations = []
        tasks = self.getTasks("Configurations")
        current_configurations = self.getCurrentConfigurations()      
        for task in tasks:
            configurations = []
            task_key = get_attribute(task, "key")
            configuration_nodes = get_nodes(".//accfg", task)
            for configuration_node in configuration_nodes:
                accfg_type = get_datum_from_expr("accfg-type",
                                                 configuration_node)
                accfg_desc = get_datum_from_expr("accfg-desc",
                                                 configuration_node)
                accfg_status = get_datum_from_expr("accfg-state",
                                                configuration_node)
                configuration = accfg_type, accfg_desc, accfg_status
                selected = (task_key, accfg_type) in current_configurations
                configurations.append((configuration, selected))
            task_configurations.append((task_key, configurations))            
        return task_configurations
        
    def getCurrentConfigurations(self):
        configurations = []
        configuration_nodes = get_nodes("//prelreq/configurations/accfg",
                                        self.srcDoc_)
        for configuration_node in configuration_nodes:
            task_key = get_datum_from_expr("source-key", configuration_node)
            accfg_type = get_datum_from_expr("accfg-type", configuration_node)
            configuration = task_key, accfg_type
            configurations.append(configuration)
            
        return configurations
        
##########################################################################

class ConfigurationsDialogImpl(ConfigurationsDialog):
    def __init__(self, parent, sernaDoc, configurations_selection_list):
        ConfigurationsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.parent_ = parent
        self.processSignal_ = True
        iffristChild = False
        for configuration_selection in configurations_selection_list:
            task_key = configuration_selection[0]
            configurations = configuration_selection[1]
            for cfg in configurations:
                configuration = cfg[0]
                selected = cfg[1]
                listitem = QListViewItem(self.configurationsListView_)
                accfg_type = ""
                if configuration[0]:
                    accfg_type = configuration[0]
                accfg_desc = ""
                if configuration[1]:
                    accfg_desc = configuration[1]
                accfg_state = ""
                if configuration[2]:
                    accfg_state = configuration[2]
                listitem.setText(0, task_key)
                listitem.setText(1, accfg_type)
                listitem.setText(2, accfg_desc)
                listitem.setText(3, accfg_state)
                self.configurationsListView_.setSelected(listitem, selected, True)
                if listitem == self.configurationsListView_.firstChild() and selected:
                    iffristChild = True
        if iffristChild:
            self.configurationsListView_.firstChild().setSelected(True)
            iffristChild = False
        else:
            self.configurationsListView_.firstChild().setSelected(False)

    def selectionChanged(self):
        if not self.processSignal_:
            return
        cur = self.configurationsListView_.currentItem()
        if not self.configurationsListView_.isSelected(cur):
            return
        deselectitems = []
        item = self.configurationsListView_.firstChild()
        while item:
            if self.configurationsListView_.isSelected(item) and  cur != item and \
               cur.text(1) == item.text(1):
                deselectitems.append(item) 
            item = item.nextSibling(item, self.configurationsListView_.invisibleRootItem())
        self.processSignal_ = False
        for item in deselectitems:
            self.configurationsListView_.setSelected(item, False, True)
        self.processSignal_ = True

    def getConfigurations(self):
        checked_confs = []
        configurations = []
        item = self.configurationsListView_.firstChild()
        while item:
            if self.configurationsListView_.isSelected(item):
                if item.text(1) in checked_confs:
                    QMessageBox.warning(self.parent_, "Warning",
                    "Duplicated configuration will be skiped:\n task-key:" + 
                     str(item.text(0)) + "\n type:" +  str(item.text(1)) +
                     "\n state:" + str(item.text(3)))
                    item = item.nextSibling(item, self.configurationsListView_.invisibleRootItem())
                    continue;
                task_key = (str(item.text(0))).strip()
                accfg_type = (str(item.text(1))).strip()
                accfg_state = (str(item.text(3))).strip()
                configurations.append(("accfg", [("source-key", task_key),
                    ("accfg-type", accfg_type), ("accfg-state", accfg_state)]))
                checked_confs.append(item.text(1))
            item = item.nextSibling(item, self.configurationsListView_.invisibleRootItem())
        
        return configurations

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#con-dialog")
