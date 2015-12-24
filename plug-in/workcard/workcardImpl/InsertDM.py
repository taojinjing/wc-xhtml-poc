from qt import *
from .dialog.RefdmDialogBase import RefdmDialogBase
from .TreeViewWidget import *
from .ExecutorBase import *
from .InsertDMRef import *
from string import *
from PyQt4.QtGui import QDialog, QMessageBox
from PyQt4.QtCore import QDir, QFile, QFileInfo
from .ListItem import *

class InsertDM(ExecutorBase):
    def execute(self):
        current_document = QFile(str(self.structEditor_.sourceGrove().topSysid()))
        cur_document_info = QFileInfo(current_document)
        QDir.setCurrent(cur_document_info.dirPath(True))
        if self.isReadOnly():
            return
        self.useTarget = (None != get_node("ancestor-or-self::hotspot", 
                              self.getCurrentNode()))
        self.dialog = ReuseDMDialogImpl(self.qtWidget_, self, None, None, False)
        self.dialog.init()
        if QDialog.Accepted == self.dialog.exec_loop():
            self.insertReference(self.dialog.getReference())
        

    def insertReference(self, refData):
        #(refId, refUri) = refData.#refItemxxx_todo_changeme
        #refId = refData.id_
        #refUri = refData.uri_
        if not refData or self.isReadOnly():
            return
        if None == refData.id_:
            return
        parents = ["expstatement", "refs", "captext",
                   "actref", "brexref", "hotspot", "reqcondm", "entry",
                   "para", "item", "def", "mainfunc"]
        context_node = self.getContext(parents,"//para|//refs")
        if not(context_node):
            QMessageBox.critical(self.dialog, "Warning",
                     "No place to insert <b>refdm</b> element found.")
            return
        url = self.composeDavPath(refData.id_ + '.xml')
        if self.sessionId_ == "":
            url = refData.uri_
        grove = Grove.buildGroveFromFile(url)
        avee = get_node("//idstatus/dmaddres/dmc/avee|//identAndStatusSection/dmAddress/dmIdent/dmCode", grove.document())
        if not avee:
            QMessageBox.critical(self.dialog, "Warning", 
                 "Can't insert reference properly:")
            return

        dialog = InsertDMRefImpl(self, self.qtWidget_, self.structEditor_, refData.id_, self.dialog.getDMC())
        dialog.exec_loop()
        return

    def getContext(self, possibleParentList, forcedContextExpr = None, axis = "self"):
        """
            getContext(parentsList, forcedContext = None)
                    returns context with specified parents, or
                    if they don't exist, force evaluated XPath expression
                    will be returned.
                @parentsList    -- ["p1", "p2", ...]
                @forcedContext  -- "//expr1 | //expr2 ..." 
        """

        context = None
        query = ""

        for allowed in possibleParentList:
           if query == "":
               query = axis + "::" + allowed 
               continue
           query = query + " or " + axis + "::" + allowed
        node = self.getCurrentNode()
        if node.asGroveText():
            node = node.parent()
        if get_node(query, node):
            return self.structEditor_.getSrcPos().node()

        while node:
           context = get_node(query, node)
           if context:
               break
           node = node.parent()
        if not context:
            context = get_node(forcedContextExpr, self.srcDoc_)
        return context
    
    def composeDavPath(self, filename):
        return self.serverDomain_ + "/dav/ses=" + self.sessionId_ + "/" + filename                  
               
    def composeUrl(self, action, parameters):
        """
            composeUrl(action, parameters)
                    Composes and returns certain docato server request
                @action     -- server action (e.g., ``GetDocument'')
                @parameters -- parameters for request
        """
        if ".do" != action[-3:]:
            action += ".dox"
        url = self.serverDomain_ + action + "?sessionid=" + self.sessionId_
        for param in list(parameters.keys()):
            url += "&" + str(param) + "=" + str(parameters[param])
        return url
        
    def searchRefs(self, searchCriteria):
        url = self.composeUrl("lookupDataModules", searchCriteria)
        grove = Grove.buildGroveFromFile(url)
        resources = get_nodes("//resources/resource", grove.document())
        total = get_first_text_data_from_expr("//resources/count", grove.document())
        refs_list = []
        for resource in resources:
            refs_list.append(
                RefData(get_first_text_data_from_expr("id", resource),
                          get_first_text_data_from_expr("uri", resource),
                          get_first_text_data_from_expr("title", resource),
                          get_first_text_data_from_expr("type", resource),
                        url
                        ))
        return (total, refs_list)


class ReuseDMDialogImpl(RefdmDialogBase):

    def __init__(self, parent, executor, selected=None, alternate_widget=None, useTarget=False):
        RefdmDialogBase.__init__(self, parent)
        self.setCaption("Data Module Re-use")
        self.useTarget = useTarget
        self.sessionId_ = executor.sessionId_
        self.executor_ = executor
        if self.sessionId_ == "":
            self.treeWidget_ = LocalTreeViewWidget(self.collectionsListView_,
                    self.folderLabel_, executor.composeUrl, 'drives')
        else:
            self.treeWidget_ = TreeViewWidget(self.collectionsListView_,
                    self.folderLabel_, executor.composeUrl, 'data-module')
        self.__refsMap = {}
        self.imageView_.hide()
        if self.sessionId_ == "":
            self.listView_.removeColumn(0)
        self.treeWidget_.refresh()
        if selected:
            self.search()

    def search(self):
        self.setCursor(Qt.WaitCursor)
        path = str(self.folderLabel_.text())
        modelic = str(self.modelic_.text())
        sdc = str(self.sdc_.text())
        chapnum = str(self.chapnum_.text())
        sect = str(self.sect_.text()) 
        subject = str(self.subject_.text())
        dcs = str(self.discode_.text())
        ics = str(self.incode_.text())
        itemloc = str(self.itemloc_.text()) 
        search_criteria = { "modelic" : modelic, "sdc" : sdc,\
            "chapnum" : chapnum, "section" : sect[:1],\
            "subsect" : sect[2:],"subject" : subject,\
            "discode" : dcs[:2], "discodev": dcs[3:],\
            "incode"  : ics[:3], "incodev" : ics[4:],\
            "itemloc" : itemloc, "uri" : path }
        results = []
        if self.sessionId_ == "":
            curdir = QDir.current()
            label_text = curdir.absPath().__str__()
            if len(label_text) > 40:
                label_text = '..' + label_text[-38:]
            self.folderLabel_.setText(label_text)
            files = curdir.entryInfoList("*.xml")
            refs_list = []
            for it in files:
                if not it.isFile(): 
                    continue;
                grove = Grove.buildGroveFromFile(it.absFilePath())
                avee = get_node("//idstatus/dmaddres/dmc/avee", grove.document())
                if not avee:
                    continue
                matched = True
                for field in list(search_criteria.keys()):
                    value = search_criteria[field]
                    if field == "uri" or value == "":
                        continue
                    if value != get_first_text_data_from_expr(field, avee):
                        matched = False
                if matched:
                    path = it.absFilePath().__str__()
                    refs_list.append(RefData(path, path,\
                                     it.fileName().__str__(), "descript"))
            results = [len(refs_list), refs_list]
        else:
            results = self.executor_.searchRefs(search_criteria)        
        refs  = results[1]
        count = 0
        try:
            count = int(results[0])
        except:
            count = 0
        self.listView_.clear()
        self.__refsMap.clear()
        for i in range(count):
            ref = refs[i]
            uri = ref.uri_.__str__()
            title = ref.title_
            if len(title) > 90:
                title = ".." + title[-90:]
            if ref.type_.find("descript")>-1 or ref.type_.find("proced")>-1:
                item = ListItem(self.listView_,
                            str(uri[uri.rfind('/')+1:]), title.__str__())
                self.__refsMap[item] = ref
        self.listView_.setSelected(self.listView_.firstChild(), True)
        self.currentRefChanged()
        self.okButton_.setEnabled(None != self.listView_.firstChild())      
        self.setCursor(Qt.ArrowCursor)

    def currentRefChanged(self):
        selected_item = self.listView_.selectedItem()
        if not selected_item:
            self.okButton_.setEnabled(False)
            return           
        self.okButton_.setEnabled(True)
        self.listView_.setSelectedItemsFlase()
        selected_item.setSelected(True)
        if not self.useTarget:
            return
        #fill image list
        self.imageView_.clear()
        filename = self.getReference().__str__()
        url = filename
        if self.sessionId_ != "":
            filename = filename + ".xml"
            url = self.composeDavPath(filename)
        grove = Grove.buildGroveFromFile(url)
        images = get_nodes("//graphic/@boardno", grove.document())
        for node in images: 
            attr = node.asGroveAttr()
            ListItem(self.imageView_, attr.value().__str__())
        if self.imageView_.childCount():
            self.imageView_.show()
        else:
            self.imageView_.hide()

    def focusNext(self):
        self.focusNextPrevChild(True)

    def init(self):
        if self.listView_.firstChild():
            self.listView_.setCurrentItem(
                self.listView_.firstChild())
        self.search()

    def clearFields(self):
        self.modelic_.setText("")
        self.sdc_.setText("")
        self.chapnum_.setText("")
        self.sect_.setText("") 
        self.subject_.setText("")
        self.discode_.setText("")
        self.incode_.setText("")
        self.itemloc_.setText("") 
        self.listView_.clear()
        self.__refsMap.clear()
        self.okButton_.setEnabled(False)

    def exec_loop(self):
        return RefdmDialogBase.exec_loop(self)

    def getReference(self):
        selected_item = self.listView_.selectedItem()
        if selected_item:
            ref = self.__refsMap[selected_item]
            return ref
        return None
    
    def getDMC(self):
        selected_item = self.listView_.selectedItem()
        if selected_item:
            return selected_item.text(0).__str__()
        return None

    def getTarget(self):
        selected_item = self.imageView_.selectedItem()
        if selected_item:
            return selected_item.text(0)
        return None

    def help(self):
        self.sernaDoc_.showHelp("doc/index.html")    

    def refresh(self):
        self.treeWidget_.refresh()

    def collectionExpanded(self, listItem):
        self.treeWidget_.collectionExpanded(listItem)

    def collectionCollapsed(self, listItem):
        self.treeWidget_.collectionCollapsed(listItem)

    def currentCollectionChanged(self):
        self.treeWidget_.currentCollectionChanged()
        self.clearFields()
        details = self.folderLabel_.text().__str__().split('/')
        if self.sessionId_ == "":
            return
        dsize = len(details)
        if 2 < dsize:
            self.modelic_.setText(details[2])
        if 3 < dsize:
            self.sdc_.setText(details[3])
        if 4 < dsize:
            self.chapnum_.setText(details[4])
        if 5 < dsize:
            self.sect_.setText(details[5]) 
        if 6 < dsize:  
            self.subject_.setText(details[6])
    
    def getRefdm(self):
        refdm_tuple = self.insertReference(self.getReference())
        return refdm_tuple
    
class RefData:
    def __init__(self, id, uri, title, schema, fullUri = ""):
        self.id_ = id
        self.uri_ = uri
        self.title_ = title
        self.type_ = schema
        self.fullUri_ = fullUri
