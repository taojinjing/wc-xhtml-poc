from .ExecutorBase import *
import sys
from qt import *
from .dialog.CautionsWarningsDialog import CautionsWarningsDialog
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt
from pywrap import *
#from mock.MockWorkcard import MockWorkcard

##########################################################################
# Cautions and Warnings
##########################################################################
class EditCautionsWarnings(ExecutorBase):
    def execute(self):
        if self.isReadOnly():
            return
        node = get_node(
            "self::caution or self::warning or self::text or self::note",
            self.getCurrentNode())
        dialog = CautionsWarningsDialogImpl(self.qtWidget_, self.sernaDoc_,
                                            (node != None),
                                            self.findCautionsWarnings)
        dialog.linkButton_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            caution_warning = dialog.getCautionWarning()
            self.insertCautionWarning(caution_warning)
            
    def findCautionsWarnings(self, fulltext):
        qApp.setOverrideCursor( QCursor(Qt.WaitCursor) )
        cautions_warnings = []
        tags = [ "caution", "warning", "note", "text"]
        for i in range(len(tags)):
            search_criteria = [("typeMappingId", "ref1"),\
                           ("ftsQuery", fulltext.__str__()),\
                           ("schemaMappingId", "standardText"),\
                           ("elementName", tags[i] + "/para")]
            if not fulltext or fulltext == "*":
                search_criteria = [("typeMappingId", "ref1"),\
                               ("schemaMappingId", "standardText"),\
                               ("elementName", tags[i] + "/para")]
            url = self.composeUrl("getCrossReferenceTargets", search_criteria)
            grove = Grove.buildGroveFromFile(url)
            results = get_nodes("//result", grove.document())
            if results:
                cautions_warnings.append((tags[i], results))
        qApp.restoreOverrideCursor()
        return cautions_warnings
        
    def insertCautionWarning(self, caution_warning):
        if caution_warning == None:
            return
        result = caution_warning[1]
        document_id = get_datum_from_expr("document-id", result)
        target_id = get_attribute(get_node("target-id", result), "id")
        tag = caution_warning[2]
        wo_parent = caution_warning[3]
        cur_node = self.getCurrentNode()
        ancestor = get_node("ancestor-or-self::warning or \
                             ancestor-or-self::caution or \
                             ancestor-or-self::note", cur_node)
        if wo_parent:
            tag = None

        context = get_node("ancestor-or-self::mainfunc or \
                             ancestor-or-self::step1 or \
                             ancestor-or-self::step2 or \
                             ancestor-or-self::step3 or \
                             ancestor-or-self::step4 or \
                             ancestor-or-self::step5 or \
                             ancestor-or-self::step6", cur_node)
        if not context:
            context = get_node("//mainfunc", self.srcDoc_)
            if not context:
                return

        batch_cmd = GroveBatchCommand()
        #if ancestor:
        #    delete_cmd = self.structEditor_.groveEditor().removeNode(ancestor)
        #    if delete_cmd != None:
        #        batch_cmd.executeAndAdd(delete_cmd)
        #           
        grove_editor = self.structEditor_.groveEditor()
        parent = get_node("ancestor-or-self::text", cur_node)
        pos = self.structEditor_.getSrcPos()
        if parent and tag == "text":
            child = get_node("ancestor-or-self::*[parent::text]", cur_node)
            if pos.node().nodeName() == "text":
                pos = pos
            elif child:
                pos = GrovePos(parent, child.nextSibling())
            else:
                pos = GrovePos(parent)
        elif tag == "note":
            wc_node = get_node("ancestor-or-self::*[self::caution or self::warning or self::note]", cur_node)
            if wc_node or (cur_node.nodeName().__str__()[0:4] == "step" and \
               get_node("preceding-sibling::*", pos.before()) == None):
                if wc_node and wo_parent:
                    batch_cmd.executeAndAdd(grove_editor.insertElement(pos,tag))
                    pos = GrovePos(pos.before().prevSibling())
                elif not wc_node:
                    text_node = get_node("text", cur_node)
                    pos = GrovePos(cur_node, text_node)
                    batch_cmd.executeAndAdd(grove_editor.insertElement(pos,tag))
                    pos = GrovePos(text_node.prevSibling())
                else:
                    parent = wc_node.parent()
                    if wc_node.nodeName() == tag:
                        before = wc_node.nextSibling()
                    else:
                        before = get_node("*[self::warning or self::caution][last()]", parent).nextSibling()
                    if before:
                        batch_cmd.executeAndAdd(grove_editor.insertElement(GrovePos(parent, before),tag))
                        pos = GrovePos(before.prevSibling())
                    else:
                        batch_cmd.executeAndAdd(grove_editor.insertElement(GrovePos(parent),tag))
                        pos = GrovePos(get_node(tag + "[last()]", parent))
            elif get_node("ancestor-or-self::*[substring(local-name(.),1,4)='step']", cur_node):
                if cur_node.nodeName().__str__()[0:4] == "step":
                    batch_cmd.executeAndAdd(grove_editor.insertElement(pos,tag))
                    pos = GrovePos(pos.before().prevSibling())
                else:
                    step_child = get_node("ancestor-or-self::*[substring(local-name(..),1,4)='step']", cur_node)
                    pos = GrovePos(step_child.parent(), step_child.nextSibling())
                    batch_cmd.executeAndAdd(grove_editor.insertElement(pos,tag))
                    pos = GrovePos(step_child.nextSibling())
        elif tag:
            element = build_element(tag, None)
            wc_node = get_node("ancestor-or-self::*[self::caution or self::warning]", cur_node)
            if tag == "text" or (wc_node and wo_parent):
                batch_cmd.executeAndAdd(grove_editor.insertElement(pos,tag))
                if pos.before():
                    pos = GrovePos(pos.before().prevSibling())
                else:
                    pos = GrovePos(get_node(tag + "[last()]", pos.node()))
            else:
                batch_cmd.executeAndAdd(self.insertWarningsInOrder(context, tag, element))
                pos = GrovePos(get_node(tag + "[last()]", context))

        if caution_warning[0]: # if copy
            para = get_node("para", result).asGroveElement()
            para.attrs().removeAttribute("id")            
            link = build_element( "link", para,
                [("href", document_id + ".xml#" + target_id)])
            if not tag:
                pos = self.structEditor_.getSrcPos()
            fragment = GroveDocumentFragment()
            fragment.appendChild(link)
            batch_cmd.executeAndAdd(self.structEditor_.groveEditor().paste(fragment, pos))
        else:
            props = PropertyNode("xinclude")
            props.makeDescendant("parse").setString("xml")
            props.makeDescendant("href").setString(document_id + ".xml")
            props.makeDescendant("xpointer").setString(target_id)
            cmd = self.insertXinclude(pos, props)
            if cmd:
                batch_cmd.executeAndAdd(self.structEditor_.groveEditor().mapXmlNs(\
                    get_node("/workcard", self.srcDoc_).asGroveElement(),
                "xi", "http://www.w3.org/2001/XInclude"))
                batch_cmd.executeAndAdd(cmd)
        self.structEditor_.executeAndUpdate(batch_cmd)

    def insertWarningsInOrder(self, step, tag, element):
        warning = get_node("warning", step)
        caution = get_node("caution", step)
        note    = get_node("text/preceding-sibling::note"   , step)
        if tag=="note":
            if note:
                return self.insertElement("note[last()]",step,element, False)
            elif caution:
                return self.insertElement("caution[last()]",step,element)
            elif warning:
                return self.insertElement("warning[last()]",step,element)
            else:
                return self.insertElement("*[1]",step,element, False)
        elif tag=="caution":
            if note:
                return self.insertElement("note[1]",step,element, False)
            elif caution:
                return self.insertElement("caution[last()]",step,element)
            elif warning:
                return self.insertElement("warning[last()]",step,element)
            else:
                return self.insertElement("*[1]",step,element, False)
        elif tag=="warning":
            if warning:
                return self.insertElement("warning",step,element)
            elif caution:
                return self.insertElement("caution[1]",step,element, False)
            elif note:
                return self.insertElement("note[1]",step,element, False)
            else:
                return self.insertElement("*[1]",step,element, False)
        else:
            return self.insertElement("*[1]",step,element)

##########################################################################

class CautionsWarningsDialogImpl(CautionsWarningsDialog):
    def __init__(self, parent, sernaDoc, insert_enabled, searchFunc):
        CautionsWarningsDialog.__init__(self, parent)
        self.sernaDoc_    = sernaDoc
        self.isReject_    = False
        self.__searchFunc = searchFunc
        self.filterGroup_.setButton(1)
        self.filterChanged()
        self.searchLineEdit_.setFocus()
        self.listView_.setColumnWidth(0, 50)        

    def reject(self):
        self.isReject_ = True
        CautionsWarningsDialog.reject(self)
        
    def search(self):
        if self.isReject_:
            return
        self.__resultMap = {}
        self.listView_.clear()
        fulltext = self.searchLineEdit_.text()
        results = self.__searchFunc(fulltext)
        first = True        
        for result in results:
            for node in result[1]:
                listitem = QListViewItem(self.listView_)
                #content = get_datum_text_tree(get_node("para", node)).__str__()
                content = get_datum_from_node(get_node("para", node)).__str__()
                listitem.setText(0, result[0])
                if not content:
                    content = ""
                content = simplifyWhiteSpace(content[0:100])
                if len(content) > 100:
                    content = content + "..."

                listitem.setText(1, content)
                self.__resultMap[listitem] = node
                if first:
                    self.listView_.setSelected(listitem, True)
                    first = False              
    
    def getCautionWarning(self):
        cur = self.listView_.currentItem()
        if cur:
            try:
                result = self.__resultMap[cur]
                if self.checkBox_.isChecked():
                    return self.isLink_, result, cur.text(0).__str__(), True
                return self.isLink_, result, cur.text(0).__str__(), False
            except KeyError:
                return None;
        return None;
        
    def selectionChanged(self):
        sel_item= self.listView_.selectedItem()
        itemSelected = sel_item != None
        self.linkButton_.setEnabled(itemSelected)
        self.xincludeButton_.setEnabled(itemSelected)
        content = ""
        if itemSelected:
            try:
                node = self.__resultMap[sel_item]
                #content = get_datum_text_tree(get_node("para", node)).__str__()
                content = get_datum_from_node(get_node("para", node)).__str__()
            except KeyError:
                return
        self.textEdit_.setText(content)

    def filterChanged(self):
        names = ["all", "warning", "caution", "note", "text"]
        self.search()
        if self.filterGroup_.selectedId() <=1 :
            return
        item = self.listView_.firstChild()
        while item:
            next = item.nextSibling(item, self.listView_.invisibleRootItem())
            if item.text(0) != names[self.filterGroup_.selectedId()-1]:
                self.listView_.takeItem(item)
            item = next

    def insertLink(self):
        self.isLink_ = True
        self.accept()        

    def insertXInclude(self):
        self.isLink_ = False
        self.accept()
    
    def help(self):
        self.sernaDoc_.showHelp("index.html")
