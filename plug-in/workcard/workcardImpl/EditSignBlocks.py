from .ExecutorBase import *
from .dialog.BlocksDialog import BlocksDialog
from qt import *
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog
##########################################################################
# Sign Blocks
##########################################################################
class EditSignBlocks(ExecutorBase):
    def execute(self):
        self.editSB()

    def editSB(self, auto = False):
        current_node = self.getCurrentNode()
        if get_node("ancestor-or-self::*[@dmidreftype='link' or @dmidreftype='linkStepContinue']", current_node):
            self.isReadOnly() # gives warning
            return # read-only linked content
        sign = get_node("ancestor-or-self::sign", current_node)
        parent = get_node(
            "ancestor-or-self::*[self::step1 or self::step2 or \
            self::step3 or self::step4 or self::step5 or \
            self::step6 or self::mainfunc][1]",
            current_node)
        if not (sign or parent):
            return

        blocks = []
        if sign:
            blocks = self.getSignBlocks()
   
        context = get_node("preceding-sibling::*[1]", sign)
        if not context:
            context = parent

        if auto:
            self.insertSignBlocks([(None, "Mechanic")], context)
            return

        dialog = BlocksDialogImpl(self.qtWidget_, self.sernaDoc_,
                                  self.getSignoffLabels(),
                                  self.getSignoffSkills(), blocks)
        if QDialog.Accepted == dialog.exec_loop():
            sign_blocks = dialog.getBlocks()
            self.insertSignBlocks(sign_blocks, context);
    
    def getSignBlocks(self):
        blocks = []
        current_node = self.getCurrentNode()
        block_nodes = get_nodes("ancestor-or-self::sign/block", current_node)
        for block_node in block_nodes:
            label = get_datum_from_expr("sign-label", block_node)
            skill = get_datum_from_expr("sign-skill", block_node)
            blocks.append((label, skill))
        return blocks
       
    def getSignoffLabels(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        signoff_labels_list = []
        grove = Grove.buildGroveFromFile(self.composeUrl(
            "definitionList", [("param1", "sign-label-def")]))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        for gridrow in gridrows:
            sign_label = get_datum_from_expr("dul:gridcell[1]", gridrow)
            signoff_labels_list.append(sign_label)
        qApp.restoreOverrideCursor()
        return signoff_labels_list

    def getSignoffSkills(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        signoff_skills_list = []
        grove = Grove.buildGroveFromFile(self.composeUrl(
            "definitionList", [("param1", "sign-skill-def")]))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        for gridrow in gridrows:
            sign_skill = get_datum_from_expr("dul:gridcell[1]", gridrow)
            signoff_skills_list.append(sign_skill)
        qApp.restoreOverrideCursor()
        return signoff_skills_list

    def insertSignBlocks(self, blocks, context):
        current_node = self.getCurrentNode()
        sign = get_node("ancestor-or-self::sign", current_node)
        eff = get_node("eff", sign)
        location = get_node("location", sign)
        batch_cmd = GroveBatchCommand()
        empty_batch_cmd = True
        to = None
        if sign != None:
            sign.setReadOnly(False)

        sign_elem = GroveElement("sign")
        for block in blocks:
            block_elem = GroveElement("block")
            label = block[0]
            if label != None and label != "":
                sign_label = build_element("sign-label", str(label))
                block_elem.appendChild(sign_label)
            skill = block[1]
            if skill != None and skill != "":
                sign_skill = build_element("sign-skill", str(skill))
                block_elem.appendChild(sign_skill)
            sign_elem.appendChild(block_elem)
        if eff:
            sign_elem.appendChild(eff)
        if location:
            sign_elem.appendChild(location)
        if get_node("*", sign_elem) != None:
            clipboard = GroveDocumentFragment()
            clipboard.appendChild(sign_elem)
            if sign == None:
                #if str(current_node.nodeName())[0:4] == "step":
                #    to = self.structEditor_.getSrcPos()  
                #elif str(current_node.nodeName()) == "mainfunc":
                #    to = self.structEditor_.getSrcPos()  
                #else:
                before = get_node("*[substring(local-name(),1,4)='step' or self::sources or self::location or self::eff][1]", context)
                if before:
                    to = GrovePos(context, before)
                else:
                    to = GrovePos(context)
            else:
                to = GrovePos(context.parent(), sign.nextSibling())
                context = context.parent()
                
            insert_sign_command = self.structEditor_.groveEditor().paste(
                clipboard, to)
            if insert_sign_command != None:
                batch_cmd.executeAndAdd(insert_sign_command)
                empty_batch_cmd = False
                
        if sign:
            delete_blocks_command = self.removeElement("self::sign", sign)
            if delete_blocks_command != None:
                batch_cmd.executeAndAdd(delete_blocks_command)
                empty_batch_cmd = False

        if not empty_batch_cmd:
            self.structEditor_.executeAndUpdate(batch_cmd)
#            signs = get_nodes("descendant-or-self::sign/block", context)
#            for sign in signs: 
#                sign.setReadOnly(True)  
##########################################################################

class WidgetGroup:
    def __init__(self, checkBox, labelCombo, skillsCombo):
        self.checkBox_ = checkBox
        self.labelCombo_ = labelCombo
        self.skillsCombo_ = skillsCombo

##########################################################################
        
class BlocksDialogImpl(BlocksDialog):
    def __init__(self, parent, sernaDoc, labels, skills, blocks):
        BlocksDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.__widgetGroupList = [
            WidgetGroup(self.blockBox1, self.comboLabel1, self.comboSkill1),
            WidgetGroup(self.blockBox2, self.comboLabel2, self.comboSkill2),
            WidgetGroup(self.blockBox3, self.comboLabel3, self.comboSkill3),
            WidgetGroup(self.blockBox4, self.comboLabel4, self.comboSkill4),
            WidgetGroup(self.blockBox5, self.comboLabel5, self.comboSkill5),
            WidgetGroup(self.blockBox6, self.comboLabel6, self.comboSkill6) ]

        label_list = []
        for label in labels:
            label_list.append(label)

        skills_list = []
        for skill in skills:
            skills_list.append(skill)

        for group in self.__widgetGroupList:
            group.checkBox_.setChecked(False)
            group.labelCombo_.insertStringList(label_list)
            group.labelCombo_.setEnabled(False)
            group.skillsCombo_.insertStringList(skills_list)
            group.skillsCombo_.setEnabled(False)
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.labelCombo_.setEnabled)
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.skillsCombo_.setEnabled)
           
        i = 0
        for signs in blocks:
            group = self.__widgetGroupList[i]
            if signs[0]:
                group.labelCombo_.setCurrentText(signs[0])
            if signs[1]:
                group.skillsCombo_.setCurrentText(signs[1])
            group.checkBox_.setChecked(True)
            i = i + 1
           
    def getBlocks(self):
        blocks = []
        for group in self.__widgetGroupList:
            if group.checkBox_.isChecked():
                blocks.append((group.labelCombo_.currentText(),
                               group.skillsCombo_.currentText()))
        return blocks

    def help(self):
        self.sernaDoc_.showHelp("index.html")
