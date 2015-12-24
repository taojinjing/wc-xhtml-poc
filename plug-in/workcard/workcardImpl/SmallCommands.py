from .ExecutorBase import *
from .EditTasks import *
from .EditToolsInContent import *
from .EditPartsInContent import *
import time
from PyQt4.QtGui import QCursor, QDialog, QMessageBox, QComboBox, QLineEdit, QSpacerItem, QGridLayout, QWidgetItem
from PyQt4.QtCore import Qt

##########################################################################
# Executor for small generic commands
##########################################################################
class SmallCommands(ExecutorBase):
    def exploreImage(self):
        if self.isReadOnly():
            return
        pos = self.structEditor_.getSrcPos()
        if pos.node().nodeName() == "graphic":
            graphic_id = str(get_attribute(pos.node(), "href"))
            pos = graphic_id.find(".")
            if pos > 0:
                graphic_id = graphic_id[0:pos]
            url = self.composeUrl(
                "getRepositoryViewAbstractResource.do", [("id", graphic_id)])
            webbrowser.open_new(url)


    def editTitle(self):
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Title", 
                 get_datum_from_expr("//prelreq/wc-title", self.srcDoc_))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(
            "//prelreq/wc-title", self.srcDoc_, (dialog.getText()).upper()))

    def editCard(self):
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Card", 
                 get_datum_from_expr("//prelreq/wc-num", self.srcDoc_))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(
            "//prelreq/wc-num", self.srcDoc_, (dialog.getText()).upper()))


    def promoteStep(self):
        if self.isReadOnly():
            return
        current_node = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", current_node)
        if not step or step.nodeName() == "step1":
            return
        action = 2 # after parent by default
        if not step.prevSibling():
            action = 0 # before parent
        elif step.nextSibling():
            action = 1# dialog.buttonGroup1.selectedId()
        batch_cmd = GroveBatchCommand()
        ge = self.structEditor_.groveEditor()
        parent = step.parent()
        if action == 1:
            batch_cmd.executeAndAdd(ge.splitElement(GrovePos(parent, step)))
            step = get_node("*[substring(local-name(),1,4)='step'][1]", step.parent())
            parent = step.parent()
            paste_pos = GrovePos(parent, step.nextSibling())
            step_name = step.nodeName()
            self.renameSubTreeNodes(step, batch_cmd, step_name, paste_pos)  
            step = get_node("*[substring(local-name(),1,4)='step'][1]", parent)
            batch_cmd.executeAndAdd(ge.untag(GrovePos(step)))
        else:
            step_name = parent.nodeName()
            self.renameSubTreeNodes(step, batch_cmd, step_name) 
        self.structEditor_.executeAndUpdate(batch_cmd)

    def splitStep(self):
        if self.isReadOnly():
            return
        current_node = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring"
                        "(local-name(),1,4)='step'][1]", current_node)
        if not step or step.nodeName() == "step1":
            return
        batch_cmd = GroveBatchCommand()
        ge = self.structEditor_.groveEditor()
        parent = step.parent()
        id_val = self.structEditor_.generateId("%t")
        batch_cmd.executeAndAdd(ge.splitElement(GrovePos(parent, step)))
        parent = parent.nextSibling()
        step = get_node("*[substring(local-name(),1,4)='step'][1]", parent)
        fragment = GroveDocumentFragment()                     
        fragment.appendChild(build_element("text", [("para", None)]))
        batch_cmd.executeAndAdd(ge.paste(fragment,GrovePos(parent, step)))
        self.structEditor_.executeAndUpdate(batch_cmd)

    def __renameStepsInTree(self, parent, level = -1):
        for child in parent.children():
            if str(child.nodeName())[0:4] == "step":
                step_name = "step" + str(int(child.nodeName().__str__()[4]) + level)
                if step_name != "step7":
                    self.__renameStepsInTree(child, level)
                    child.asGroveElement().setName(step_name)

    def renameSubTreeNodes(self, rootRenameNode, batchCmd,\
                           newName = None, posToPaste = None, level = -1):
            ge = self.structEditor_.groveEditor()
            step = rootRenameNode
            parent = step.parent()
            grand = parent.parent()
            fragment = GroveDocumentFragment()
            ge.copy(GrovePos(parent, step), 
                    GrovePos(parent, step.nextSibling()), fragment)
            root = fragment.firstChild()
            self.__renameStepsInTree(root, level)
            if newName:
                root.asGroveElement().setName(newName)
            if not posToPaste:
                posToPaste = GrovePos(grand, parent.nextSibling())
            batchCmd.executeAndAdd(ge.cut(GrovePos(parent, step),\
                    GrovePos(parent, step.nextSibling())))
            batchCmd.executeAndAdd(ge.paste(fragment, posToPaste))

    def demoteStep(self):
        if self.isReadOnly():
            return
        current_node = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", current_node)
        if not step:
            return
        step_name = step.nodeName()
        if step_name == "step6":
            return;
        paste_pos = None
        base_step = get_node("preceding-sibling::*[substring(local-name(),1,4)='step'][1]", step)
        if not base_step:
            base_step = get_node("following-sibling::*[substring(\
                                 local-name(),1,4)='step'][1]", step)
            if base_step:
                child = get_node("*[substring(local-name(),1,4)='step'][1]",\
                        base_step)
                if child:
                    paste_pos = GrovePos(base_step, child)
                else:
                    paste_pos = GrovePos(base_step)
        else:
            child = get_node("*[substring(local-name(),1,4)='step'][last()]",\
                        base_step)
            if child and child.nextSibling():
                paste_pos = GrovePos(base_step, child.nextSibling())
            else:
                paste_pos = GrovePos(base_step)
        batch_cmd = GroveBatchCommand()
        ge = self.structEditor_.groveEditor()
        if not base_step:
            parent = step.parent()
            from_pos = GrovePos(parent, step)
            to_pos =   GrovePos(parent, step.nextSibling())
            batch_cmd.executeAndAdd(ge.tagRegion(from_pos, to_pos, step_name))
            id_val = self.structEditor_.generateId("%t")
            batch_cmd.executeAndAdd(ge.addAttribute(step.parent().asGroveElement(), \
                                    PropertyNode("id", id_val)))
            paste_pos = GrovePos(step.parent())
            step = get_node(str(step_name), step.parent())
        step_name = "step" + str(int(step_name.__str__()[4]) + 1)
        self.renameSubTreeNodes(step, batch_cmd, step_name, paste_pos, 1) 
        self.structEditor_.executeAndUpdate(batch_cmd)

    def insertNbsp(self):
        if self.isReadOnly():
            return
        pos = self.structEditor_.getSrcPos()
        if pos.type() != GrovePos.TEXT_POS:
            return
        ge = self.structEditor_.groveEditor()
        from_pos = GrovePos()
        to_pos = GrovePos()
        if self.structEditor_.getSelection(from_pos, to_pos, True):
            if from_pos.type() == GrovePos.TEXT_POS and \
               to_pos.text().data() == from_pos.text().data(): 
                all_text = str(to_pos.text().data().__str__())
                count = to_pos.idx() - from_pos.idx()
                text = all_text.mid(from_pos.idx(), count)
                text.replace(" ", "\xA0")
                self.structEditor_.executeAndUpdate(\
                     ge.replaceText(from_pos, count, text.__str__()))
        else:
            self.structEditor_.executeAndUpdate(ge.insertText(pos, "\xA0"))

    #########################################################################
        
    def editPartQty(self):
        cur = self.getCurrentNode()
        if not get_node("ancestor-or-self::part-qty", cur):
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Part Qty", 
                 get_datum_from_expr("ancestor-or-self::part-qty", cur))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(
            "ancestor-or-self::part-qty", cur, dialog.getText()))

    def editPartState(self):
        cur = self.getCurrentNode()
        if not get_node("ancestor-or-self::part-state", cur):
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Part State", 
                 get_datum_from_expr("ancestor-or-self::part-state", cur))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(\
            "ancestor-or-self::part-state", cur, dialog.getText()))

    def editToolQty(self):
        cur = self.getCurrentNode()
        if not get_node("ancestor-or-self::tool-qty", cur):
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Tool Qty", 
                 get_datum_from_expr("ancestor-or-self::tool-qty", cur))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(
            "ancestor-or-self::tool-qty", cur, dialog.getText()))

    def editToolState(self):
        cur = self.getCurrentNode()
        if not get_node("ancestor-or-self::tool-state", cur):
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Tool State", 
                 get_datum_from_expr("ancestor-or-self::tool-state", cur))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            self.structEditor_.executeAndUpdate(self.replaceText(\
            "ancestor-or-self::tool-state", cur, dialog.getText()))

    def editCircuitBreakerState(self):
        cur = self.getCurrentNode()
        if not get_node("ancestor-or-self::cb-state", cur):
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Edit Tool State", 
                 get_datum_from_expr("ancestor-or-self::cb-state", cur))
        dialog.lineEditComBox_.hide()
        if QDialog.Accepted == dialog.exec_loop():
            cbnum = get_datum_from_expr("ancestor-or-self::cb/cb-num", cur)
            if cbnum == None:
                return
            node = get_node("//prelreq/circuit-breakers/circuit-breaker"
                            "[cb-num='" + cbnum + "']//cb-state", self.srcDoc_)
            if not node:
                return
            LockPrelreq(self.prelreqNode_)
            ge = self.structEditor_.groveEditor()
            command = None
            if node.getChild(0).asGroveText():
                text_node = node.getChild(0).asGroveText()
                command = ge.replaceText(GrovePos(text_node), 
                          len(text_node.data()), dialog.getText())
            else:
                command = ge.insertText(GrovePos(node),dialog.getText())
            self.structEditor_.executeAndUpdate(command)

    def insertPrelreqData(self):
        if self.isReadOnly():
            return
        cur = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
        if not step:
            step = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
        if not step:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "No 'step' elements to insert 'prelreq-data'")
            return
        dialog = LineEditDialogImpl(self.qtWidget_, "Insert Prelreq Data")
        dialog.lineEdit_.hide()
        dialog.lineEditComBox_.insertItem(0,"Configurations")
        dialog.lineEditComBox_.insertItem(1,"Forecasts")
        dialog.lineEditComBox_.insertItem(2,"Zones/Panels")
        dialog.lineEditComBox_.insertItem(3,"Drawings")
        dialog.lineEditComBox_.insertItem(4,"References")
        dialog.lineEditComBox_.insertItem(5,"Tools")
        dialog.lineEditComBox_.insertItem(6,"Parts")
        dialog.lineEditComBox_.insertItem(7,"Circuit Breakers")
        if QDialog.Accepted == dialog.exec_loop():
            cpos = dialog.lineEditComBox_.currentIndex() + 1
            num = "pd0" + str(cpos)
            if cpos == 6:
                tools_dialog = EditToolsInContent(self.plugin_())
                res = tools_dialog.execute()
                elem = build_element("prelreq-data", None, [("type", num), ("idlist",','.join(res))])
            if cpos == 7:
                parts_dialog = EditPartsInContent(self.plugin_())
                res = parts_dialog.execute()
                elem = build_element("prelreq-data", None, [("type", num), ("idlist",','.join(res))])
            else:
                elem = build_element("prelreq-data", None, [("type", num)])
            batch_cmd = GroveBatchCommand()
            batch_cmd.executeAndAdd(self.insertElement("text "
                "or sign or graphic or table", step, elem, True))
            self.structEditor_.executeAndUpdate(batch_cmd)

    def insertProcedTemplate(self, content, st):
        if self.isReadOnly():
            return
        batch_cmd = GroveBatchCommand()
        cur = self.getCurrentNode()
        context = None
        inbetween_step = False  #if to insert before first step
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
        if not step:
            mf = get_node("/workcard/mainfunc", self.srcDoc_)
            if not mf:
                QMessageBox.warning(self.qtWidget_, "Warning",
                        "No 'mainfunc' element.")
                return
            cur_pos = self.structEditor_.getSrcPos()
            if cur_pos.node().nodeName() == "mainfunc":
                step = cur_pos.node()
                context = cur_pos.before()
                if context and (not context.prevSibling() or
                   context.nodeName() == "step1"): 
                    inbetween_step = True
            else:
                step = get_node("/workcard/mainfunc", self.srcDoc_)
                context = get_node("ancestor-or-self::*[parent::mainfunc]", cur)
        para = GroveElement("para")
        fragment = GroveDocumentFragment()
        randlist = build_element("randlist", [("item", "Project Engineer: ")],
                                [("prefix", "pf03")])
        if content:
            para.appendChild(randlist)
        pos = GrovePos(step)
        if inbetween_step:
            pos = GrovePos(step, context)
        elif not context: 
            context = get_node("ancestor-or-self::text", cur)
            if not context: 
                context = get_node("text[last()]", step)
            if not context: 
                pos = GrovePos(step)
            else:
                pos = GrovePos(step, context.nextSibling())
        text = GroveElement("text")
        text.appendChild(para)
        fragment.appendChild(text)          
        if content:
            fragment.appendChild(build_element("sign", [("block", [("sign-skill", "Mechanic")])]))
        ge = self.structEditor_.groveEditor()
        batch_cmd.executeAndAdd(ge.paste(fragment, pos))

        search_criteria = [("typeMappingId", "ref1"),\
                       ("ftsQuery", "a*"),\
                       ("schemaMappingId", "standardText"),\
                       ("elementName", "*")]
        url = self.composeUrl("getCrossReferenceTargets", search_criteria)
        grove = Grove.buildGroveFromFile(url)
        results = get_nodes("//result", grove.document())
        if not results:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "Can't find file 'std-text-def'.")
            return
        doc_id = get_datum_from_expr("document-id", results[1])
        if not doc_id:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "Can't find file 'std-text-def'.")
            return
        doc_id = doc_id.__str__() + ".xml"


        props = PropertyNode("xinclude")
        props.makeDescendant("parse").setString("xml")
        props.makeDescendant("href").setString(doc_id)
        props.makeDescendant("xpointer").setString(st)

       
        para = get_node("text[last()]/para[last()]", pos.node())
        pnode = pos.before()
        while pnode and pnode.nodeName() != "text":
            pnode = pnode.prevSibling()
        if pnode:
            para = get_node("para", pnode)
        pos = GrovePos(para.parent(), para)
        cmd = self.insertXinclude(pos, props)
        if cmd:
            batch_cmd.executeAndAdd(self.structEditor_.groveEditor().mapXmlNs(\
                get_node("/workcard", self.srcDoc_).asGroveElement(),
                "xi", "http://www.w3.org/2001/XInclude"))
            batch_cmd.executeAndAdd(cmd)
        else:
            QMessageBox.warning(self.qtWidget_, "Warning",
                "Operation can not be completed.\n"
                "Invalid xi:include value: 281.xml:" + st + ".")
            return
        self.structEditor_.executeAndUpdate(batch_cmd)

    def insertMockProced(self):
        if self.isReadOnly():
            return
        qApp.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.insertProcedTemplate("Notify Project Engineer that mockup "
                                  "is complete (leave voice mail if "
                                  "necessary).", "st28")
        qApp.restoreOverrideCursor()

    def insertFirstProced(self):
        if self.isReadOnly():
            return
        qApp.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.insertProcedTemplate("Notify Project Engineer that first time "
                                  "accomplishment is complete (leave voice "
                                  "mail if necessary).", "st29")
        qApp.restoreOverrideCursor()

    def insertRckEntry(self):
        if self.isReadOnly():
            return
        qApp.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.insertProcedTemplate(None, "st30")
        qApp.restoreOverrideCursor()

    def editTablePos(self):
        cur = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
        if not step:
            step = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
        if not step:
            step = get_node("/workcard/mainfunc", self.srcDoc_)
        if not step:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "No place to insert 'table'")
            return
        context = get_node("prelreq-data|panel-table|*[substring(local-name(),1,4)='pnl-']|eff|location|sources|*[substring(local-name(),1,4)='step'][1]", step)
        pos = GrovePos(step)
        if context:
            pos = GrovePos(step, context)
        se = self.structEditor_
        se.setCursorBySrcPos(pos, se.getFoPos().node(), True)

    def editGraphicPos(self):
        cur = self.getCurrentNode()
        step = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
        if not step:
            step = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
        if not step:
            step = get_node("/workcard/mainfunc", self.srcDoc_)
        if not step:
            QMessageBox.warning(self.qtWidget_, "Warning",
                    "No place to insert 'graphic' or 'figure'")
            return
        context = get_node("table|prelreq-data|panel-table|*[substring(local-name(),1,4)='pnl-']|eff|location|sources|*[substring(local-name(),1,4)='step'][1]", step)
        pos = GrovePos(step)
        if context:
            pos = GrovePos(step, context)
        se = self.structEditor_
        se.setCursorBySrcPos(pos, se.getFoPos().node(), True)

    def convertGraphics(self):
        cur = self.getCurrentNode()
        old_graphics = get_nodes("//graphic[not(ancestor-or-self::figure)]", cur)
        if len(old_graphics) == 0:
            return False
        batch_cmd = GroveBatchCommand()
        ge = self.structEditor_.groveEditor()
        for graphic in old_graphics:
            parent = graphic.parent()
            from_pos = GrovePos(parent, graphic)
            to_pos =   GrovePos(parent, graphic.nextSibling())
            batch_cmd.executeAndAdd(ge.tagRegion(from_pos, to_pos, 'figure'))
            id_val = self.structEditor_.generateId("%t")
            batch_cmd.executeAndAdd(ge.addAttribute(graphic.parent().asGroveElement(), \
                                    PropertyNode("id", id_val)))
            time.sleep(0.1)
        self.structEditor_.executeAndUpdate(batch_cmd)
        return True


    def insertSource(self):
        def checkNoteElement(source):
            count = source.countChildren()
            while count >= 0:
                 isNoteExist = source.getChild(count-1).nodeName() == "note"
                 if True == isNoteExist:
                    break
                 count = count - 1
            if isNoteExist == False:
               note_batch_cmd = GroveBatchCommand()
               note_batch_cmd.executeAndAdd(self.insertElement("*", source, build_element("note", None)))
               self.structEditor_.executeAndUpdate(note_batch_cmd)   

        if self.isReadOnly():
            return
        cur = self.getCurrentNode()
        batch_cmd = GroveBatchCommand()
        sources = get_node("ancestor-or-self::sources", cur)
        if sources:
            batch_cmd.executeAndAdd(self.insertElement("*", sources, build_element("source", None)))
            self.structEditor_.executeAndUpdate(batch_cmd)
            sources = get_node("ancestor-or-self::sources", cur)
            source = sources.lastChild()
            checkNoteElement(source)
            return
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
        if not context:
            context = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
            if not context:
                context = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
            if not context:
                QMessageBox.warning(self.qtWidget_, "Warning",
                        "No place to insert 'source'")
                return
            child_step = get_node("*[substring(local-name(),1,4)='step'][1]", context)
            if child_step:
                pos = GrovePos(context, child_step)
            else:
                pos = GrovePos(context)
        sources = get_node("sources", context)
        if sources:
            sources = get_node("sources", context)
            source = sources.lastChild()
            checkNoteElement(source)
            batch_cmd.executeAndAdd(self.insertElement("*", sources, build_element("source", None)))
            self.structEditor_.executeAndUpdate(batch_cmd)
            return
        sources = build_element("sources", [("source", None)])
        fragment = GroveDocumentFragment()
        fragment.appendChild(sources)
        batch_cmd.executeAndAdd(self.structEditor_.groveEditor().paste(fragment, pos))
        self.structEditor_.executeAndUpdate(batch_cmd)
        
        sources = get_node("sources", context)
        source = sources.lastChild()
        checkNoteElement(source)

    def insertLocation(self):
        if self.isReadOnly():
            return
        cur = self.getCurrentNode()
        batch_cmd = GroveBatchCommand()
        sources = get_node("ancestor-or-self::location", cur)
        if sources:
            return
        context = get_node("ancestor-or-self::table or \
                        ancestor-or-self::graphic or \
                        ancestor-or-self::sign or \
                        ancestor-or-self::warning or \
                        ancestor-or-self::caution or \
                        ancestor-or-self::note or \
                        ancestor-or-self::text or \
                        ancestor-or-self::req-access", cur)
        pos = None
        if context:
            pos = GrovePos(context)
            srcs = get_node("sources", context)
            if srcs:
                pos = GrovePos(context, srcs)
        else:
            context = get_node("ancestor-or-self::*[substring(local-name(),1,4)='step'][1]", cur)
            if not context:
                context = get_node("/workcard/mainfunc/step1[1]", self.srcDoc_)
            if not context:
                QMessageBox.warning(self.qtWidget_, "Warning",
                        "No place to insert 'location'")
                return
            pos = GrovePos(context)
            next_level_step = get_node("sources|*[substring(local-name(),1,4)='step'][1]", context)
            if next_level_step:
                pos = GrovePos(context, next_level_step)

        conditions = get_node("location", context)
        if conditions:
            return
        conditions = build_element("location", [("environment"," "),("company"," ")])
        fragment = GroveDocumentFragment()
        fragment.appendChild(conditions)
        batch_cmd.executeAndAdd(self.structEditor_.groveEditor().paste(fragment, pos))
        self.structEditor_.executeAndUpdate(batch_cmd)

    def callWorkcardHelp(self):
        self.sernaDoc_.showHelp("index.html")
