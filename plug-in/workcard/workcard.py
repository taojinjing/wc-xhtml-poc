from SernaApi import *
from PyQt4.QtGui import  QMessageBox, QApplication, QDialog
from PyQt4.QtCore import QTimer, SIGNAL
from PyQt4.Qt import QObject
from workcardImpl import *
import urllib.parse
import re
import os
import http.client
from workcardImpl.LoginCMSDialog  import *
from workcardImpl.InsertDMNewSteps import *
from qt import *

gprjname=""
gusername=""

class WorkCard(DocumentPlugin):
    def __init__(self, sernaDoc, properties): 
        DocumentPlugin.__init__(self, sernaDoc, properties)
        self.buildPluginExecutors(True)
        self.isAutoSave_ = False
        schema_pn = self.sernaDoc().getDsi().getProperty("resolved-xml-schema")
        schema_pn.setString(str(self.pluginProperties().getProperty(
                  "resolved-path").getString()) + "/schema/workcardSchema.xsd")
        lock_pn = SernaConfig.root().getProperty("dav/protocols/http/lock-type")
        lock_pn.setString("lock")
        self.supportFigures_ = False
        self.sessionTimer_ = None
        self.autosaveTimer_ = None
        self.is_auto_gen_workcard_ = False


    #########################################################################
    # Plugin lifetime
    #########################################################################

    def beforeTransform(self):
        self.registerXsltFunctions()
        self.buildUpSrcStructure()

    def buildUpSrcStructure(self):
        allSources = get_nodes("descendant-or-self::source", self.srcDoc_)
        childrenCount = len(allSources)
        for source in allSources:
            children = source.children()
            isNoteExist = False
            note = get_node("note", source)
            if not note:
                note = build_element("note", None)
                lastChild = source.lastChild()
                lastChild.insertAfter(note)
        return
                              
    
    def registerXsltFunctions(self):
        self.structEditor_ = self.sernaDoc().structEditor()
        self.srcDoc_ = self.structEditor_.sourceGrove().document()
        self.sernaDoc_ = self.sernaDoc()
        self.docItemProps_ = self.sernaDoc().itemProps()

        url_tuple = urllib.parse.urlparse(str(self.structEditor_.sourceGrove().topSysid()))
        path = url_tuple[2]
        self.serverDomain_ = url_tuple[0] + "://" + url_tuple[1] + \
                             "/docato-composer/"
        self.serverIp_ = url_tuple[1]
        if self.serverIp_.find(':') > 0:
            pos = self.serverIp_.find(':')
            self.serverPort_ = self.serverIp_[pos+1:]
            self.serverIp_ = self.serverIp_[:pos]
        self.sessionId_ = re.search("ses=([0-9A-Fa-f]+)", path)
        if self.sessionId_ != None:
            self.sessionId_ = self.sessionId_.group(1)
        else:
            self.sessionId_ = ""
        self.docatoId_ = re.search("/([^/]+).xml", path)
        if self.docatoId_ != None:
            self.docatoId_ = self.docatoId_.group(1)
        else:
            self.docatoId_ = ""
        self.__stylePath = os.path.normpath(str(self.pluginProperties().getProperty(
                        "resolved-path").getString() + "/stylesheet"))       
        ex_uri = "http://www.syntext.com/Extensions/Functions"
        self.__serverFunc = StringFunction("server", ex_uri, \
                                           self.serverDomain_[:-1])
        self.sernaDoc().structEditor().xsltEngine().registerExternalFunction(
            self.__serverFunc)
        self.__sessionIdFunc = StringFunction("session-id", ex_uri, \
                                               self.sessionId_)
        self.sernaDoc().structEditor().xsltEngine().registerExternalFunction(
            self.__sessionIdFunc)
        self.__stylePathFunc = StringFunction("style-path", ex_uri, \
                                               self.__stylePath)
        self.sernaDoc().structEditor().xsltEngine().registerExternalFunction(
            self.__stylePathFunc)

        self.__documentFunc = StringFunction("document", ex_uri,"document")
        self.sernaDoc().structEditor().xsltEngine().registerExternalFunction(
            self.__documentFunc)

    def postInit(self):
        context = get_node("/workcard/mainfunc", self.srcDoc_)
        if context:
            if get_attribute(context, "autoadd"):
                self.is_auto_gen_workcard_ = (get_attribute(get_node("/workcard/mainfunc", self.srcDoc_), "autoadd").lower() in ("yes", "true", "t", "1"))

        item = self.sernaDoc().findItemByName("docContextLabel")
        if item:
            item.action().set("inscription", "Prepare workcard plugin") 
        # Following is for cursor change tracking
        self.__posWatcher = CursorPosWatcher(self)
        self.structEditor_.setElementPositionWatcher(self.__posWatcher)

        self.__clkWatcher = DblClickWatcher(self)
        self.structEditor_.setDoubleClickWatcher(self.__clkWatcher)

        self.prelreqNode_ = get_node("//prelreq", self.srcDoc_)
        self.updateInscription()
        if context:
            self.supportFigures_ = self.structEditor_.canInsertElement("figure","",GrovePos(context))
            if self.supportFigures_:
                SmallCommands(self).convertGraphics()

        LockPrelreq(self.prelreqNode_)
        toolbars = ["redlineToolbar", "zoomToolbar", "insertToolbar",\
                    "ahPublishButton", "splitElementButton", \
                    "joinElementsButton"]
        for item_name in toolbars:
            item = self.sernaDoc().findItemByName(item_name)
            if item:
               item.remove()
        signs = get_nodes("//sign/block", self.srcDoc_)
        for sign in signs: 
            sign.setReadOnly(True)  
        panels = get_nodes("//panel-table", self.srcDoc_)
        for p in panels: 
            p.setReadOnly(True)  
        self.updateLinks()
        nodes = get_nodes("//*[@dmidreftype='link' or @dmidreftype='linkStepContinue']", self.srcDoc_);
        for node in nodes:
            node.setReadOnly(True)  
        #AutoSave
        prop_vars = SernaConfig().root().getSafeProperty("app")
        prop_autosave = prop_vars.getProperty("autosave")
        if prop_autosave:
            if prop_autosave.getSafeProperty("enabled").getString() == 'true':
                prop_delay = prop_autosave.getProperty("delay")
                if prop_delay:                    
                    self.autosaveTimer_ = QTimer(ui_item_widget(self.sernaDoc()))
                    QObject.connect(self.autosaveTimer_, SIGNAL("timeout()"), self.saveDoc)
                    self.autosaveTimer_.start(prop_delay.getInt()*60*1000)
        if self.docatoId_ != "": #if there is a connection to CMS, monitor it
            self.sessionTimer_ = QTimer(ui_item_widget(self.sernaDoc()))
            QObject.connect(self.sessionTimer_, SIGNAL("timeout()"),self.testDocato)
            self.sessionTimer_.start(10*1000) # every 10 sec test connection with CMS


    def saveDoc(self):
        self.isAutoSave_ = True
        self.executeCommandEvent("SaveStructDocument",PropertyNode())
        self.isAutoSave_ = False

    def updateInscription(self):
        context = get_node("wc-num", self.prelreqNode_)
        if self.docItemProps_ and context and context.getChild(0):
            text = context.getChild(0).asGroveText().data()
            model = get_node("model", self.prelreqNode_)
            dash = get_node("dash", self.prelreqNode_)
            if model and dash and model.getChild(0) and dash.getChild(0):
               mtext = model.getChild(0).asGroveText().data()
               dtext = dash.getChild(0).asGroveText().data()
               text =  mtext + '-' + dtext + ' ' + text
            """if text.length() > 25 :
                text = text.left(25) + "..."
                """
            self.docItemProps_.makeDescendant("inscription").setString(text)
            self.sernaDoc().getDsi().makeDescendant(
                "inscription").setString(text)
        window = qApp.activeWindow()
        caption = window.caption().__str__()
        window.setCaption(caption.replace("\n"," "))

    def update_new_links_from_amm_task(self, refdm_set, message):
        is_message_popped = False
        for refdm_id in refdm_set:
            url = self.composeDavPath(refdm_id + '.xml')
            grove = Grove.buildGroveFromFile(url)
            avee = get_node("//idstatus/dmaddres/dmc/avee|//identAndStatusSection/dmAddress/dmIdent/dmCode", grove.document())
            dmc_code = get_dmc_from_avee(avee)
            dialog = InsertDMRefNewStepImpl(self, ui_item_widget(self.sernaDoc()), self.structEditor_,
                                            refdm_id, dmc_code)
            if dialog.has_unchecked_step_:
                if not is_message_popped:
                    QMessageBox.information(None, "Information", "%s" % message)
                    is_message_popped = True
                dialog.exec_loop()
        return is_message_popped

    def updateLinks(self):
        if self.sessionId_ == "":
            return
        carrier_code = get_node("//prelreq/carrier-code/text()", self.srcDoc_).asGroveText().data();
        mfg = get_node("//prelreq/mfg/text()", self.srcDoc_).asGroveText().data();
        model = get_node("//prelreq/model/text()", self.srcDoc_).asGroveText().data();
        dash = get_node("//prelreq/dash/text()", self.srcDoc_).asGroveText().data();
        linked_nodes = get_nodes("//*[@dmidreftype='link' or @dmidreftype='linkStepContinue']", self.srcDoc_);
        adapted_nodes = get_nodes("//*[@dmidreftype='adapt' or @dmidreftype='adaptStepContinue']", self.srcDoc_);
        mainfunc = get_node("//mainfunc", self.srcDoc_)
        batch = GroveBatchCommand()
        apply_changes = False
        has_linked_nodes = True if len(linked_nodes) > 0 else False;
        has_adapted_nodes = True if len(adapted_nodes) > 0 else False;
        refdm_set = set()
        def __add2Refdm(target0):
            pos = target0.find(".xml")
            if -1 != pos:
                refdm_set.add(target0[0 : pos])
            else:
                #refdm_set.add(target0)
                pass
            return
        for node in adapted_nodes:
            target = get_datum_from_expr("@target", node)
            if node.localName().startswith("step"):
                __add2Refdm(target)
        for node in linked_nodes:
            target = get_datum_from_expr("@target", node)
            if node.localName().startswith("step"):
                __add2Refdm(target)
            linkType = get_datum_from_expr("@dmidreftype", node)
            elementName = node.nodeName();
            if elementName == "frontmatter":
                dmUri = target[0 : target.find('#') ]
                target = dmUri+'%23autoGenerateWorkcardFrontmatter'
            elif target.find('#'):
                target = target.replace('#', '%23')
            url = self.composeUrl("lookupWorkcardFragment",{'type':linkType,'target':target,'crossReference':'true','showRevdate':'true', 'carrierCode':carrier_code, 'mfg':mfg, 'model':model, 'dash':dash})
            grove = Grove.buildGroveFromFile(url)
            root = grove.document().documentElement()
            if not(root):
                # If the 'root' is none, it means that the content of url is invalid. So 
                # we remove this node from current opened document.
                batch.executeAndAdd(self.structEditor_.groveEditor().removeNode(node))
                apply_changes = True
                continue
            # Try to paste the content from the fetched URL 
            # to current node's position.
            self.structEditor_.stripInfo().strip(root)
            fragment = GroveDocumentFragment()
            fragment.appendChild(root.cloneNode(True))
            pos = GrovePos(node.parent(), node)
            """figure cross reference, move figure/graphic out of xref to end of mainfunc"""
            ext_graphics = get_nodes("//xref[child::figure|graphic]", fragment)
            ext_graphics_id_map = {}
            ext_graphics_list = []
            for xref_node in ext_graphics:
                xref = xref_node.asGroveElement()
                ext_graphic = get_node("figure|graphic", xref);
                id = get_attribute(ext_graphic, "id")
                if not(get_node("//*[@id='"+id+"']", self.srcDoc_)) and not(id in ext_graphics_id_map):
                    ext_graphics_id_map[id] = ext_graphic
                    ext_graphics_list.append(ext_graphic)
                xref.removeAllChildren()
            ge = self.structEditor_.groveEditor()
            batch.executeAndAdd(ge.paste(fragment, pos))
            for ext_graphic in ext_graphics_list:
                graphic_fragment = GroveDocumentFragment()
                graphic_fragment.appendChild(ext_graphic.cloneNode(True))
                batch.executeAndAdd(ge.paste(graphic_fragment, GrovePos(mainfunc)))
            batch.executeAndAdd(ge.removeNode(node))
            apply_changes = True
        if apply_changes:
            #Stuido 6.1 workcard around
            self.setValidationMode("on")
            if self.structEditor_.executeAndUpdate(batch):
                if not (self.is_auto_gen_workcard_
                        and self.update_new_links_from_amm_task(refdm_set, "Update existing links successfully. Check un-referenced targets in AMM task...")):
                    self.sernaDoc().showMessageBox(SernaDoc.MB_INFO, "Information", "Update links successfully.", "OK") 
            else:
                self.sernaDoc().showMessageBox(SernaDoc.MB_WARNING, "Warning", 
                                               "Failed to update links caused by conflict, please re-edit links by delete and insert again.", "OK") 
        if not has_linked_nodes and has_adapted_nodes and self.is_auto_gen_workcard_:
            self.update_new_links_from_amm_task(refdm_set, "Check un-referenced targets in AMM task...")
        return 

    def setValidationMode(self, actionName):        
        action = self.sernaDoc().actionSet().findAction("validationMode")
        mode = 0
        for actionProp in action.properties().children():
            if("action" == actionProp.name()):
                if(actionName == actionProp.getSafeProperty("name").getString()):
                    break
                mode = mode + 1
        if(mode != action.getInt("current-action")):
            action.setInt("current-action", mode)
            self.sernaDoc().executeCommandEvent("SwitchValidation")

    def aboutToSave(self):
        if self.isAutoSave_:
            return;
        if self.supportFigures_:
            old_graphics = get_nodes("//graphic[not(ancestor-or-self::figure)]", self.srcDoc_)
            if len(old_graphics)>0:
                res = QMessageBox.warning(self.sernaDoc().widget(), "Warning",
                "Document contains stand alone 'graphic' elements.\n"
                "In order to keep consistency within this document\n"
                "and ability to support graphic sheets we recommend you to\n"
                "convert them into 'figures'", "Convert", "Cancel")
                if res == 0:
                    if SmallCommands(self).convertGraphics():
                        self.sernaDoc().showMessageBox(SernaDoc.MB_INFO, "Information", 
                                                       "Graphics successfully converted into figures.", "OK")
                        #QMessageBox.information(None, "Information", successfully converted into figures.")
        self.updateInscription()
        return

    def executeUiEvent(self, evName, uiAction):
        try:
            module=sys.modules["workcardImpl." + evName]
            if hasattr(module, evName):
                getattr(module, evName)(self).execute()
            else:
                self.sernaDoc().showMessageBox(SernaDoc.MB_WARNING, "Warning",
                                               "Command '" + evName + "' is not implemented yet.", "OK")
        except KeyError:                  
            ex_name = "SmallCommands"
            module=sys.modules["workcardImpl." + ex_name]
            if hasattr(module, ex_name):
                executor = getattr(module, ex_name)(self)
                name = (evName[0]).lower() + evName[1:]
                if hasattr(executor, name):
                    getattr(executor, name)()
                else:
                    self.sernaDoc().showMessageBox(SernaDoc.MB_WARNING, "Warning",
                                               "Command '" + evName + "' is not implemented yet.", "OK")
        return

    def reloadDoc(self):
        self.executeCommandEvent("ReloadStructDocument")

    def composeUrl(self, action, parameters):
        if action[-3:] != ".do":
            action = action + ".dox"
        url = self.serverDomain_ + action + "?sessionid=" + self.sessionId_
        url = url + "&prgrss=true"
        for param in list(parameters.keys()):
            url += "&" + str(param) + "=" + str(parameters[param])
        return url;

    def loginDialog(self,prjname,username):
        urls = self.composeUrl("listProjects.do", {})
        dialog = LoginCMSDialog(self,urls,prjname,username)
        if QDialog.Accepted != dialog.exec_loop():
            return self.executeCommandEvent("CloseDocument",PropertyNode())
        cms=dialog.getCMS()
        v_username = str(cms[0])
        v_password = str(cms[1])
        v_projectname = str(cms[2])
        v_projectindex = str(cms[3])
        
        if v_projectname=="-- Please select one --":
            QMessageBox.warning(self.sernaDoc().widget(),
            "Warning", "Please select one project.", "&OK")
            return self.loginDialog(v_projectname,v_username)

        url_tuple = urllib.parse.urlparse(str(self.structEditor_.sourceGrove().topSysid()))
        if url_tuple[0] == "https":
            path = '"'+os.path.normpath(str(self.pluginProperties().getProperty(
                "resolved-path").getString() + "\\workcardImpl\\tools\\get_ssl_session.exe")).replace("\\","\\\\") + '"'
            cmd = path +" -s %s -t %s -i %s -u %s -p %s"%(self.serverIp_,str(self.serverPort_),v_projectname,v_username,v_password)
            session = os.popen(cmd).read().strip()
        else:
            conn = http.client.HTTPConnection(self.serverIp_, self.serverPort_)
            conn.request("GET", "/docato-composer/login.do?project="+v_projectname+"&username="+v_username+"&password="+v_password)
            response = conn.getresponse()
            data = response.read()
            url_link =  response.getheaders()[4][1][29:]
            pos = url_link.find("jsess")
            session = url_link[pos + 11:]
            conn.close()            
        if session=="":
            QMessageBox.warning( ui_item_widget(self.sernaDoc()),
            "Warning", "User name or password is incorrect.", "&OK")
            return self.loginDialog(v_projectname,v_username)
        else:
            new_path = str(self.structEditor_.sourceGrove().topSysid()).replace(self.sessionId_,session)      
            old_path = str(self.structEditor_.sourceGrove().topSysid())
            if len(new_path)>len(old_path):
                QMessageBox.warning( ui_item_widget(self.sernaDoc()),
                "Warning", "User name or password is incorrect.", "&OK")
                return self.loginDialog(v_projectname,v_username)
            self.sessionId_ = session
            if url_tuple[0] == "https":                
                QMessageBox.warning( ui_item_widget(self.sernaDoc()),"Warning",
                   "The document is saved to CMS.\nIf you get 'Authentification required...' dialog at the next step, please cancel it.\nTo avoid changes lost, please save document to local file system by click 'Save As' button.")
                self.structEditor_.sourceGrove().saveAsXmlFile(Grove.GS_DEF_FILEFLAGS,GroveStripInfo(),new_path)
            else:
                self.structEditor_.sourceGrove().saveAsXmlFile(Grove.GS_DEF_FILEFLAGS,GroveStripInfo(),new_path)                       
                QMessageBox.warning( ui_item_widget(self.sernaDoc()),"Warning",
                   "The document is saved to CMS.\nIf you get 'Authentification required...' dialog at the next step, please cancel it.\nTo avoid changes lost, please save document to local file system by click 'Save As' button.")
#            for i in range(100):  #undo all the changes to prevent "SaveAs dialog" from the system
#                self.executeCommandEvent("StructUndo",PropertyNode())
#            self.executeCommandEvent("CloseDocument",PropertyNode())
        
    def testDocato(self):        
        url = self.composeUrl("searchConditions", {})
        grove = Grove.buildGroveFromFile(url)
        conds = get_nodes("//conditionlist", grove.document())
        global gprjname
        global gusername
        if len(conds)<1:
            if self.sessionTimer_:
                self.sessionTimer_.stop();
            if self.autosaveTimer_:
                self.autosaveTimer_.stop();
            res = QMessageBox.warning( ui_item_widget(self.sernaDoc()),
            "Warning", "Connection with CMS server '" + str(self.serverIp_) + "' <b>is lost</b>.\nDocument <b>will be closed</b>. Do you want to save your changes?", "Yes", "No")
            if res == 0:
                self.loginDialog(gprjname,gusername)                
            else:
                QMessageBox.warning( ui_item_widget(self.sernaDoc()),"Warning",
                   "To avoid changes lost, please save document to local file system by click 'Save As' button...\nIf you get 'Authentification required...' dialog at the next step, please cancel it.")
#                for i in range(100):  #undo all the changes to prevent "SaveAs dialog" from the system
#                   self.executeCommandEvent("StructUndo",PropertyNode())
#                self.executeCommandEvent("CloseDocument",PropertyNode())

    def composeDavPath(self, filename):
        return self.serverDomain_ + "/dav/ses=" + self.sessionId_ + "/" + filename
