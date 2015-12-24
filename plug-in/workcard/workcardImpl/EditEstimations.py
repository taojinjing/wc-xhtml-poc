from .ExecutorBase import *
from .dialog.EstimationsDialog import EstimationsDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog, QIntValidator, QDoubleValidator
from PyQt4.QtCore import Qt, SIGNAL
##########################################################################
# Sign Blocks
##########################################################################
class EditEstimations(ExecutorBase):
    def execute(self):
        self.editEstimations()

    def editEstimations(self, auto = False):
        dialog = EstimationsDialogImpl(self.qtWidget_, self.sernaDoc_,self.getSignoffSkills(),self.getEstimations())
        if QDialog.Accepted == dialog.exec_loop():
            blocks = dialog.getBlocks()
            self.replaceOrInsert("estimations", blocks,
                "parts tools references drawings zones-panels forecasts "
                "configurations checks maintflow-num crew-type circuit-breakers")
    
    def getEstimations(self):
        blocks = []
        current_node = self.getCurrentNode()
        block_nodes = get_nodes("ancestor-or-self::estimations/estimation", current_node)
        for block_node in block_nodes:
            skill = get_datum_from_expr("skill", block_node)
            staff = get_datum_from_expr("staff", block_node)
            effort = get_datum_from_expr("effort", block_node)
            duration = get_datum_from_expr("duration", block_node)
            blocks.append((skill,staff,effort,duration))
        return blocks
       
    def getSignoffSkills(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        signoff_skills_list = []
        mfg_code = get_datum_from_expr("//prelreq/mfg", self.srcDoc_)
        grove = Grove.buildGroveFromFile(self.composeUrl(
            "definitionList", [("param1", "mfg-skill-def"), ("param3", mfg_code)]))
        gridrows = get_nodes("//dul:gridrow", grove.document())
        for gridrow in gridrows:
            sign_skill = get_datum_from_expr("dul:gridcell[1]", gridrow)
            signoff_skills_list.append(sign_skill)
        qApp.restoreOverrideCursor()
        return signoff_skills_list


##########################################################################

class WidgetGroup:
    def __init__(self, checkBox, skillsCombo, staffEdit, effortEdit, durationEdit):
        self.checkBox_ = checkBox
        self.skillsCombo_ = skillsCombo
        self.staffEdit_ = staffEdit
        self.effortEdit_ = effortEdit
        self.durationEdit_ = durationEdit

##########################################################################
        
class EstimationsDialogImpl(EstimationsDialog):
    def __init__(self, parent, sernaDoc, skills, blocks):
        EstimationsDialog.__init__(self, parent)
        self.sernaDoc_ = sernaDoc
        self.__widgetGroupList = [
            WidgetGroup(self.blockBox1, self.comboSkill1, self.staffEdit1, self.effortEdit1, self.durationEdit1),
            WidgetGroup(self.blockBox2, self.comboSkill2, self.staffEdit2, self.effortEdit2, self.durationEdit2),
            WidgetGroup(self.blockBox3, self.comboSkill3, self.staffEdit3, self.effortEdit3, self.durationEdit3),
            WidgetGroup(self.blockBox4, self.comboSkill4, self.staffEdit4, self.effortEdit4, self.durationEdit4),
            WidgetGroup(self.blockBox5, self.comboSkill5, self.staffEdit5, self.effortEdit5, self.durationEdit5),
            WidgetGroup(self.blockBox6, self.comboSkill6, self.staffEdit6, self.effortEdit6, self.durationEdit6) ]

        skills_list = []
        for skill in skills:
            skills_list.append(skill)

        for group in self.__widgetGroupList:
            group.checkBox_.setChecked(False)
            group.skillsCombo_.insertStringList(skills_list)
            group.skillsCombo_.setEnabled(False)
            group.staffEdit_.setEnabled(False)
            group.staffEdit_.setValidator(QIntValidator(group.staffEdit_));
            group.effortEdit_.setEnabled(False)
            group.effortEdit_.setValidator(QDoubleValidator( 0.0, 999.0, 2,group.effortEdit_));
            group.durationEdit_.setEnabled(False)
            group.durationEdit_.setValidator(QDoubleValidator( 0.0, 999.0, 2,group.durationEdit_));
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.skillsCombo_.setEnabled)
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.staffEdit_.setEnabled)
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.effortEdit_.setEnabled)
            self.connect(group.checkBox_, SIGNAL("toggled(bool)"),
                         group.durationEdit_.setEnabled)
           
        i = 0
        for signs in blocks:
            group = self.__widgetGroupList[i]
            if signs[0]:
                group.skillsCombo_.setCurrentText(signs[0])
            if signs[1]:
                group.staffEdit_.setText(signs[1])
            if signs[2]:
                group.effortEdit_.setText(signs[2])
            if signs[3]:
                group.durationEdit_.setText(signs[3])
            group.checkBox_.setChecked(True)
            i = i + 1
           
    def getBlocks(self):
        blocks = []
        for group in self.__widgetGroupList:
            if group.checkBox_.isChecked():
                blocks.append(("estimation",
                                         [("skill", str(group.skillsCombo_.currentText())),
                                          ("staff", str(group.staffEdit_.text())),
                                          ("effort", str(group.effortEdit_.text())),
                                          ("duration", str(group.durationEdit_.text()))]))
        return blocks

    def help(self):
        self.sernaDoc_.showHelp("index.html")
