from .ExecutorBase import *
from .dialog.MainfuncDialog import MainfuncDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog, QMessageBox
from PyQt4.QtCore import Qt
##########################################################################
# Mainfunc
##########################################################################
class EditMainfunc(ExecutorBase):
    def execute(self):
        context = get_node("//mainfunc", self.srcDoc_)
        batch_cmd = GroveBatchCommand()
        xinclude_node = get_node("/workcard/xi:include", self.srcDoc_)
        isXinclude = False
        mfid = get_datum_from_expr("//mainfunc/@mfid", self.srcDoc_)
        if xinclude_node:
            isXinclude = True
            context = xinclude_node
            mfid = get_datum_from_expr("@xpointer", context)
        #ers = context.prevSibling().asGroveErs()
        #ers = context.getErs()        
        #isXinclude = False
        #if ers:
        #    isXinclude = ers.entityDecl().declType() == GroveEntityDecl.xinclude

        key = get_datum_from_expr("/workcard/@key", self.srcDoc_)
        dialog = MainfuncDialogImpl(self.qtWidget_, isXinclude, mfid, key,
                 self.getXincludeWorkcard)
        if QDialog.Accepted == dialog.exec_loop():
            if not context:
                return
            se = self.structEditor_
            ge = se.groveEditor()
            if dialog.xincludeSelected():
                key = dialog.getText().__str__()
                document_id = self.getXincludeWorkcard(key)[0]
                if not document_id or document_id == "":
                    QMessageBox.warning(self.qtWidget_, "Warning",
                    "Not valid value for xi:include element.")
                    self.editMfid()
                    return
                parent = context.parent()
                props = PropertyNode("xinclude")
                props.makeDescendant("parse").setString("xml")
                props.makeDescendant("href").setString(document_id + ".xml")
                props.makeDescendant("xpointer").setString("W" + key)
                props.makeDescendant("encoding").setString("UTF-8")
                cmd = self.insertXinclude(GrovePos(parent), props)
                if cmd:
                    batch_cmd.executeAndAdd(self.structEditor_.groveEditor().mapXmlNs(\
                        get_node("/workcard", self.srcDoc_).asGroveElement(),
                        "xi", "http://www.w3.org/2001/XInclude"))
                    batch_cmd.executeAndAdd(cmd)
                else:
                    QMessageBox.warning(self.qtWidget_, "Warning",
                        "Can't make xi:include here.\n"
                        "Please check the value for xi:include element.")
                    self.editMfid()
                    return
                if isXinclude:
                    #batch_cmd.executeAndAdd(ge.cut(GrovePos(ers.parent(), ers),
                    #    GrovePos(ers.parent(), ers.asGroveErs().ere().nextSibling())))       
                    batch_cmd.executeAndAdd(ge.removeNode(xinclude_node))
                else:
                    batch_cmd.executeAndAdd(ge.removeNode(context))
                batch_cmd.setSuggestedPos(GrovePos(self.prelreqNode_.parent()))
                se.executeAndUpdate(batch_cmd)
            else:
                if isXinclude:
                    batch_cmd.executeAndAdd(ge.removeNode(xinclude_node))
                    #batch_cmd.executeAndAdd(ge.cut(GrovePos(ers.parent(), ers),
                    #    GrovePos(ers.parent(), ers.asGroveErs().ere().nextSibling())))       
                    elem = build_element("mainfunc", None, 
                           [("mfid", "W" + dialog.getText().__str__())])
                    fragment = GroveDocumentFragment()
                    fragment.appendChild(elem)
                    batch_cmd.executeAndAdd(ge.paste(fragment, 
                              GrovePos(self.prelreqNode_.parent())))
                    se.executeAndUpdate(batch_cmd)
                    return
                attr = context.asGroveElement().attrs().getAttribute("mfid")
                ge.setAttribute(attr, "W" + dialog.getText().__str__())
                se.setCursorBySrcPos(GrovePos(context, context.firstChild()),\
                                     se.getFoPos().node(), True)

    def getXincludeWorkcard(self, key):
        url = self.composeUrl("getDocatoIdByWorkcardKey", [("key", str(int(key)))])
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        grove = Grove.buildGroveFromFile(url)
        qApp.restoreOverrideCursor()
        return get_datum_from_expr("//docato-id", grove.document()),\
               get_datum_from_expr("//wc-num", grove.document()),\
               get_datum_from_expr("//wc-title", grove.document()),\
               get_datum_from_expr("//mfg", grove.document()),\
               get_datum_from_expr("//model", grove.document()),\
               get_datum_from_expr("//dash", grove.document())

##########################################################################


class MainfuncDialogImpl(MainfuncDialog):
    def __init__(self, parent, isXinclude, text, key, func):
        MainfuncDialog.__init__(self, parent)
        self.actionGroup_.setButton(int(isXinclude))
        self.checkButton_.setEnabled(isXinclude)
        self.isXinclude_ = isXinclude
        self.infoLabel_.setText("")
        self.noticed_ = False
        self.key_ = key
        self.func_ = func
        self.lineEdit_.setEnabled(isXinclude)
        if text == None:
            text = ""
        elif text[0] == "W":
            text = text[1:]
        #self.browseButton_.hide()
        self.lineEdit_.setText(text)
        self.lineEdit_.setFocus()
           
    def getText(self):
        return self.lineEdit_.text()

    def xincludeSelected(self):
        return self.actionGroup_.selectedId() == 1

    def actionChanged(self, buttonId):
        if not self.noticed_ and 1 == buttonId:
            res = QMessageBox.warning(self, "Warning",
                "Switching to XInclude mode will cause "
                "loss of current mainfunc content.\n Choose 'OK' "
                "to proceed or 'Cancel' to return to dialog.", "OK", "Cancel")
            if res == 1:
                buttonId = 0
            else:
                self.noticed_ = True

        if buttonId == 0:
            self.textLabel_.setText("Edit attribute 'mfid'")
            self.infoLabel_.setText("")
            #if self.isXinclude_:
            self.lineEdit_.setText(self.key_)
            self.lineEdit_.setEnabled(False)
        else:
            self.textLabel_.setText("Edit workcard key as xi:include reference")
            self.lineEdit_.setEnabled(True)
        self.actionGroup_.setButton(buttonId)
        self.checkButton_.setEnabled(buttonId)
        #self.actionGroup_.setFocus()

    def checkKey(self):
        key = str(self.lineEdit_.text())
        data = self.func_(key)
        info = str(data[3]) + " " + str(data[4]) + " " + str(data[5]) +\
               " " + str(data[1]) + "\n" + str(data[2])\
               
        if data[1] or data[2]:
            self.infoLabel_.setText(info)
        else:
            self.infoLabel_.setText("Key " + key + " not found")

