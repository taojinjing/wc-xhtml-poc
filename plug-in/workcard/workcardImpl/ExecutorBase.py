#############################################################################
# Base class for exacutors                                                  #
#############################################################################
from SernaApi import *
from urllib.parse import *
from .utils import *
from weakref import *
from qt import *
from PyQt4.QtGui import *
import os
from sapiwrap import *
import string
import webbrowser
import tempfile
from functools import reduce
from PyQt4.QtGui import QCursor, QMessageBox
from PyQt4.QtCore import Qt

class ExecutorBase:
    def __init__(self, plugin):
        self.plugin_ = ref(plugin)
        self.sernaDoc_ = self.plugin_().sernaDoc()
        self.structEditor_ = self.sernaDoc_.structEditor()
        self.srcDoc_ = self.structEditor_.sourceGrove().document()
        self.docItemProps_ = self.sernaDoc_.itemProps()
        self.serverDomain_ = self.plugin_().serverDomain_
        self.sessionId_ = self.plugin_().sessionId_
        self.docatoId_ = self.plugin_().docatoId_
        self.prelreqNode_ = self.plugin_().prelreqNode_
        #self.__stylePath = self.plugin_().__stylePath
        self.qtWidget_ = ui_item_widget(self.plugin_().sernaDoc())

    #########################################################################
    # Commonly used methods
    #########################################################################
    def plugin_():
        return self.plugin_

    def insertXinclude(self, pos, props):       
        return self.structEditor_.groveEditor().insertElement(pos, "xi:include", props)

    # Checks that content is readonly
    def isReadOnly(self, checkOnlyErs = False):
        cur = self.getCurrentNode()
        if cur.grove().topSysid() != self.structEditor_.sourceGrove().topSysid():
            QMessageBox.warning(self.qtWidget_, "Warning",
                "Cannot modify content: source document is read-only or locked")
            return True
        node = cur
        if checkOnlyErs:
            is_readonly = False
        else:
            is_readonly = node.isReadOnly()
        while not(is_readonly) and node:
            if checkOnlyErs:
                is_readonly = False
            else:
                is_readonly = node.isReadOnly()
            ers = node.prevSibling().asGroveErs()
            if ers and ers.entityDecl().declType() == GroveEntityDecl.xinclude:
                is_readonly = ers.entityDecl().isReadOnly()
            node = node.parent()
        if is_readonly:
            QMessageBox.warning(self.qtWidget_, "Warning",
                "Cannot modify content: source document is read-only or locked")
        return is_readonly

    # Composes and returns certain docato server request
    def composeUrl(self, action, parameters):
        if action[-3:] != ".do":
            action = action + ".dox"
        url = self.serverDomain_ + action + "?sessionid=" + self.sessionId_
        url = url + "&prgrss=true"
        for param in parameters:
            if param[0] and param[1]:
                url = url + "&" + param[0] + "=" + param[1]
        return url;

    def getTaskKeyList(self):
        task_key_parameter_value = ""
        task_keys = get_data_from_expr(
            "//source-docs/tasks/task-key", self.srcDoc_)

        for task_key in task_keys:
            if task_key == task_keys[0]:
                task_key_parameter_value = (task_key).strip()
            else:
                task_key_parameter_value = task_key_parameter_value + \
                                           "," + (task_key).strip()
        return task_key_parameter_value

        
    def getTaskKeyParameter(self):
        param_list = []
        eng_proj_num = get_datum_from_expr(
            "//prelreq/source-docs/eng-proj-num", self.srcDoc_)
        if eng_proj_num:
            param_list.append(("epkey", (eng_proj_num).strip()))
            section_num = get_datum_from_expr(
                "//prelreq/source-docs/section-num", self.srcDoc_)
            if section_num:
                param_list.append(("section", (section_num).strip()))
            return param_list;
        task_keys = get_data_from_expr(
            "//source-docs/tasks/task-key", self.srcDoc_)
        for task_key in task_keys:        
            param_list.append(("taskkey", task_key))
        return param_list;

    def getTasks(self, action, infotype = None):
        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        data = self.getMfgModelDash()
        task_key_parameter_value = self.getTaskKeyParameter()
        parameters = [("carriercode", carrier_code),
                      ("mfg", data.manufacturer_),
                      ("model", data.model_),
                      ("dash", data.dash_)]
        if action == "Info":
            parameters.append(("infotype", infotype))
        req_num = len(task_key_parameter_value)
        pdialog = None
        nodes = []
        if req_num > 5:
            res = QMessageBox.information(self.qtWidget_, "Information",\
                  "There are too many requests to server need to be done.\n" + \
                  "Getting the information will take some time.\n" + \
                  "Do you wish to continue?",\
                  "Yes", "No")
            if res == 1:
                return nodes
            pdialog = QProgressDialog("Doing requests to server.", "Cancel", 0, req_num,\
                                  self.qtWidget_)

        for item in task_key_parameter_value:
            params = []
            params.extend(parameters)
            params.append(item)
            url = self.composeUrl("getTask" + action, params)
            if pdialog:
                pdialog.setValue(pdialog.value() + 1)
                if pdialog.wasCanceled():
                    return nodes
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            tasks_grove = Grove.buildGroveFromFile(url)
            qApp.restoreOverrideCursor()
            nodes.extend(get_nodes("//task", tasks_grove.document()))
        if pdialog:
            pdialog.setValue(req_num)
        return nodes
        
    def isValidWorkcardTaskList(self, tasks, name):
        if len(tasks) == 0:
            lst = self.getTaskKeyList()
            msg = "Check AMDS '"+ name +"' for tasks:\n" + lst
            if lst == "":
                proj = get_datum_from_expr(\
                    "//prelreq/source-docs/eng-proj-num", self.srcDoc_)
                if proj:
                    proj = proj.strip()
                    msg = "Check AMDS Engineering Project '" + proj + "' exists."
            QMessageBox.warning(self.qtWidget_, "Warning",
                "There is no data available for this command.\n" + msg)
            return False
        return True

    # Returns GroveCommand which inserts element in evaluated context
    def insertElement(self, expr, context, element, after = True):
        LockPrelreq(self.prelreqNode_)
        fragment = GroveDocumentFragment()
        fragment.appendChild(element)
        nodes = get_nodes(expr, context)
        ins_pos = GrovePos(context)
        
        if len(nodes) > 0:
            node = nodes[-1]
            parent = node.parent()
            if after:
                node = node.nextSibling()
            ins_pos = GrovePos(parent, node)
        result = None
        if not ins_pos.isNull():
            result = self.structEditor_.groveEditor().paste(fragment, ins_pos)
        return result

    # Returns GroveCommand which removes given element
    def removeElement(self, expr, context):
        node = get_node(expr, context)
        if not node:
            return None
        LockPrelreq(self.prelreqNode_)
        result = self.structEditor_.groveEditor().removeNode(node)
        return result
    
    def replaceText(self, expr, context, newText):
        LockPrelreq(self.prelreqNode_)
        node = get_node(expr, context)
        grove_text = node.getChild(0).asGroveText()
        command = self.structEditor_.groveEditor().replaceText(
            GrovePos(grove_text), len(grove_text.data()), newText)
        return command

    def compareNodes(self, node1, node2, skipNodes = []):
       if node2.asGroveText():
           if not node1.asGroveText():
               return False
           #print  node1.asGroveText().data(), node2.asGroveText().data()
           return node1.asGroveText().data()== \
                  node2.asGroveText().data()
       for name in skipNodes:
           if node1.nodeName() == name or \
               node2.nodeName() == name :
               return True
       if node1.nodeName() != node2.nodeName():
           return False
       for child1 in node1.children():
            found = False
            for child2 in node2.children():
                if self.compareNodes(child1, child2, skipNodes):

                    found = True
                    break
            if not found:
                return False
       return True

    # Inserts given element at certain position, or replaces
    # already inserted element with same name
    def replaceOrInsert(self, elementName, elementData, insertAfter,
                        parentExpr = "//prelreq", context = None, 
                        forceToReplace = False):
        if not context:
            context = self.srcDoc_
        LockPrelreq(self.prelreqNode_)
        fragment = GroveDocumentFragment()
        new_root = build_element(elementName, elementData)
        node_to_replace = get_node_set(
            parentExpr + "/" + elementName, context).firstNode()
        grove_editor = self.structEditor_.groveEditor()
        cmd_added = False
        if node_to_replace:
            batch_cmd = GroveBatchCommand()
            skipNodes= ["eff"]
            for old_child in node_to_replace.children():
                found = False
                if not forceToReplace:
                    for child in new_root.children():
                        if self.compareNodes(old_child, child, skipNodes):
                            child.remove()
                            found = True
                            break
                if not found:
                    cmd_added = True
                    batch_cmd.executeAndAdd(grove_editor.removeNode(old_child))
            for node in new_root.children():
                frag = node.copyAsFragment()
                batch_cmd.executeAndAdd(grove_editor.paste(frag, GrovePos(node_to_replace)))
                cmd_added = True
            if cmd_added:
                if not node_to_replace.firstChild():
                    batch_cmd.executeAndAdd(grove_editor.removeNode(node_to_replace))
                self.structEditor_.executeAndUpdate(batch_cmd)
        else:
            if len(elementData) > 0:
                fragment.appendChild(new_root)    
                insert_expr = parentExpr + "/*[self::" + \
                              reduce(lambda a, b: a + " or self::" + b,
                                     insertAfter.split()) + "]"
                node = get_node_set(insert_expr, context).lastNode()
                pos = None
                if node:
                    pos = GrovePos(node.parent(), node.nextSibling())
                else: 
                    node = get_node_set(parentExpr, context).firstNode()
                    pos = GrovePos(node, node.firstChild())
                self.structEditor_.executeAndUpdate(grove_editor.paste(
                    fragment, pos))
                
    def getCurrentNode(self):
        return self.structEditor_.getSrcPos().node()
                   
    def getMfgModelDash(self):
        return MfgModelDash(
            get_datum_from_expr("//prelreq/mfg", self.srcDoc_),
            get_datum_from_expr("//prelreq/model", self.srcDoc_),
            get_datum_from_expr("//prelreq/dash", self.srcDoc_))


    def retrieveFile(self, filename):
        """
            retrieveFile(filename)
                    download specified file in current WebDAV session
                @filename -- specified file
        """
        url_from = self.serverDomain_ + "/dav/ses=" +\
                   self.sessionId_ + "/" + filename        
        url_to = tempfile.gettempdir().__str__() + "/" + filename
        if '' != self.sessionId_:
            res = DavManager.instance().copy(Url(url_from), Url(url_to))
            if res != DavManager.DAV_RESULT_OK:
                QMessageBox.warning( ui_item_widget(self.sernaDoc_),
                "Warning",
                "Cannot retreive file " + str(filename) + " from WebDAV")
            return url_to
        return filename
    
#############################################################################

class MfgModelDash:
    def __init__(self, manufacturer, model, dash):
        self.manufacturer_ = manufacturer
        self.model_ = model
        self.dash_ = dash
        
    def __eq__(self, other):
        return (self.manufacturer_ == other.manufacturer_ and
                self.model_ == other.model_ and self.dash_ == other.dash_)
    
