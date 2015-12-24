from .ExecutorBase import *
from .dialog.ChecksDialog import ChecksDialog
from .dialog.CheckTypeTailsDialog import CheckTypeTailsDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog
from PyQt4.QtCore import Qt, SIGNAL
##########################################################################
# Check Type
##########################################################################
class EditChecks(ExecutorBase):
    def execute(self):
        checks = []
        check_tail_map = {}
        for check_node in get_nodes("//prelreq/checks/check", self.srcDoc_):
            check_type = get_datum_from_expr("check-type", check_node)
            tails = get_data_from_expr("tails/airplane-tail|effgrp", check_node)
            check_tail_map[check_type] = tails
            checks.append(check_type)
        dialog = ChecksDialogImpl(self.qtWidget_,self.sernaDoc_, checks,
                                  self.getCheckDefinitions(),
                                  self.getCurrentChecks(),
                                  self.getTailsDescriptions(),
                                  self.getEffectivityTailsMap())
        if QDialog.Accepted == dialog.exec_loop():
            self.replaceOrInsert("checks", dialog.getChecks(),
                                 "crew-type maintflow-num",
                                 "//prelreq", None, True)

    # Returns currently inserted checks and their tails
    def getCurrentChecks(self):
        check_tail_map = {}
        for check_node in get_nodes("//prelreq/checks/check", self.srcDoc_):
            check_type = get_datum_from_expr("check-type", check_node)
            tails = get_data_from_expr("tails/airplane-tail|effgrp", check_node)
            check_tail_map[check_type] = tails
        return check_tail_map
        
    # Retrieving definitions for all chectypes
    def getCheckDefinitions(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        url = self.composeUrl("definitionList", [("param1", "check-def")])
        definitions_grove = Grove.buildGroveFromFile(url)
        check_desc_map = {}
        for gridrow in get_nodes("//dul:gridrow",
                                 definitions_grove.document()):
            check_type = get_datum_from_expr("dul:gridcell[1]", gridrow)
            check_desc = get_datum_from_expr("dul:gridcell[2]", gridrow)
            check_desc_map[check_type] = check_desc
        qApp.restoreOverrideCursor()
        return check_desc_map
        
    # Retrieve effectivity-group/tail combinations
    def getEffectivityTailsMap(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        effectivity_tails_map = {}

        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        data = self.getMfgModelDash()
        parameters = [("carrier", carrier_code), ("mfg", data.manufacturer_),
                      ("model", data.model_), ("dash", data.dash_)]
        effectivity_grove = Grove.buildGroveFromFile(
            self.composeUrl("tailByEffectivityGroup", parameters))

        eff_group_expr = XpathExpr("string(effgrp)")
        tails_expr = XpathExpr("string(tails)")
        for node in get_nodes("//result", effectivity_grove.document()):
            eff_group = str(eff_group_expr.eval(node).getString())
            tails = str(tails_expr.eval(node).getString())
            if tails[-1] == ",":
                tails = tails[:-1]
            tail_list = []
            for tail in tails.split(","):
                tail_list.append(tail.strip())
            effectivity_tails_map[eff_group] = tail_list
        qApp.restoreOverrideCursor()
        return effectivity_tails_map
        
    # Returns map from tailnumbers to their descriptions
    def getTailsDescriptions(self):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        carrier_code = get_datum_from_expr("//prelreq/carrier-code",
                                           self.srcDoc_)
        data = self.getMfgModelDash()
        parameters = [("param1", "airplane-def"), ("param3", carrier_code),
                      ("param4", data.manufacturer_), ("param5", data.model_),
                      ("param6", data.dash_)]
        defs_grove = Grove.buildGroveFromFile(
            self.composeUrl("definitionList", parameters))

        tails_desc_map = {}
        for gridrow in get_nodes("//dul:gridrow", defs_grove.document()):
            airplane_tail = get_datum_from_expr("dul:gridcell[1]", gridrow)
            mfg_serial = get_datum_from_expr("dul:gridcell[2]", gridrow)
            customer_serial = get_datum_from_expr("dul:gridcell[3]", gridrow)
            tails_desc_map[airplane_tail] = TailData(mfg_serial,
                                                     customer_serial)
        qApp.restoreOverrideCursor()
        return tails_desc_map

#############################################################################

class TailData:
    def __init__(self, mfgSerNum, customerSerNum):
        self.mfgSerNum = mfgSerNum
        self.customerSerNum = customerSerNum
    
##############################################################################

class ChecksDialogImpl(ChecksDialog):

    def __init__(self, parent, sernaDoc, checks, checkDescMap, checkTailMap,
                 tailsDescMap, effectivityTailsMap):
        ChecksDialog.__init__(self, parent)
        self.connect(self.checksListView_.getActualObj(), SIGNAL("itemSelectionChanged()"),self.itemSelected)
        self.sernaDoc_      = sernaDoc
        self.__checkDescMap = checkDescMap
        self.__checkTailMap = checkTailMap
        self.__tailsDescMap = tailsDescMap
        self.__effectivityTailsMap = effectivityTailsMap

        self.updateRemainingChecks()
        for check_type in checks: 
            tails = self.__checkTailMap[check_type]
            description = ""
            try:
                description = self.__checkDescMap[check_type]
            except KeyError:
                description = ""
            listitem = QListViewItem(self.checksListView_, check_type,
                                     description, self.makeTailsString(tails))

        self.checksListView_.setSorting(0)        
        self.editButton_.setEnabled(False)
        self.removeButton_.setEnabled(False)

    def makeTailsString(self, tails):
        tails_str = str()
        for tail in tails:
            if len(tails_str) != 0:
                tails_str = tails_str + ","
            tails_str = tails_str + tail
        return tails_str

    def getChecks(self):
        checks = []
        item = self.checksListView_.firstChild()
        while item:
            airplane_tails = []
            check_type = str(item.text(0))
            for tail in self.__checkTailMap[check_type]:
                airplane_tails.append(("airplane-tail", str(tail)))
            if len(airplane_tails) == 0: 
                checks.append(("check", [("check-type", check_type)]))
            elif len(airplane_tails) == 1 and len(airplane_tails[0][1]) > 4: 
                checks.append(("check", [("check-type", check_type),
                                        ("effgrp", airplane_tails[0][1])
                                        ]
                             ))
            else:
                checks.append(("check", [("check-type", check_type),
                                         ("tails", airplane_tails)
                                        ]
                             ))
            item = item.nextSibling(item, self.checksListView_.invisibleRootItem())
            
        return checks

    # Makes list of checktypes that are not listed. Only theese checks can
    # be added using "addChecks()" method. If all checktypes are already
    # inserted the "Add" button is disabled.
    
    def updateRemainingChecks(self):
        self.__remainingChecks = []
        for check_type in list(self.__checkDescMap.keys()):
            if not check_type in self.__checkTailMap:
                self.__remainingChecks.append(check_type)
        self.addButton_.setEnabled(len(self.__remainingChecks) > 0)
        
    # Adds user selected checktypes and corresponding tailnumbers. Checktypes
    # that are already in the list cannot be added again using this method.
    # Use "editChecks()" to change the checktype`s tailnumbers.

    def addChecks(self):
        checks = []
        dialog = CheckTypeTailsDialogImpl(self, self.__tailsDescMap,
                                          self.__remainingChecks, [], 
                                          self.__effectivityTailsMap)
        dialog.setCaption("Add Airplane Tails")
        if QDialog.Accepted == dialog.exec_loop():
            tails = dialog.getAirplaneTails()
            tails_str = self.makeTailsString(tails)
            check_type = dialog.getCheckType()
            self.__checkTailMap[check_type] = tails
            self.updateRemainingChecks()
            listitem = QListViewItem(self.checksListView_, check_type,
                                     self.__checkDescMap[check_type],
                                     tails_str)
            self.checksListView_.setSelected(listitem, True)

    # Changes tailnumbers corresponding to selected checktype
    def editChecks(self):
        curr_item = self.checksListView_.currentItem()
        if curr_item == None:
            return;
        check_type = str(curr_item.text(0))
        dialog = CheckTypeTailsDialogImpl(self, self.__tailsDescMap,
                                          [check_type],
                                          self.__checkTailMap[check_type],
                                          self.__effectivityTailsMap)
        dialog.setCaption("Change Airplane Tails")
        if QDialog.Accepted == dialog.exec_loop():
            tails = dialog.getAirplaneTails()
            self.__checkTailMap[check_type] = tails
            curr_item.setText(2, self.makeTailsString(tails))

    def removeChecks(self):
        curr_item = self.checksListView_.currentItem()
        if curr_item:
            del self.__checkTailMap[str(curr_item.text(0))]
            self.updateRemainingChecks()
            self.checksListView_.takeItem(curr_item)

    def itemSelected(self):
        is_selected = self.checksListView_.selectedItem() != None
        self.editButton_.setEnabled(is_selected)
        self.removeButton_.setEnabled(is_selected)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#che-dialog")

##########################################################################
   
class CheckTypeTailsDialogImpl(CheckTypeTailsDialog):
    def __init__(self, parent, tailsDescMap, checks,
                 selectedTails, effectivityTailsMap):

        CheckTypeTailsDialog.__init__(self, parent)
        self.connect(self.effGroupCheckBox_,SIGNAL("toggled(bool)"),self.effGroupComboBox_.setEnabled)
        self.connect(self.effGroupCheckBox_,SIGNAL("toggled(bool)"),self.selectByEffGroup)
        self.connect(self.effGroupComboBox_.getActualObj(),SIGNAL("activated(const QString&)"),self.changeEffGroup)
        self.connect(self.checkComboBox_.getActualObj(),SIGNAL("activated(int)"),self.enableOk)
        self.__tailsDescMap = tailsDescMap
        self.__selectedTails = selectedTails
        self.__effectivityTailsMap = effectivityTailsMap

        # Filling Effectivity Groups combo-box
        if self.__effectivityTailsMap != None:
            for group in list(self.__effectivityTailsMap.keys()):
                self.effGroupComboBox_.insertItem(group)
        else:
            self.effGroupCheckBox_.setEnabled(False)
        if len(checks) < 2:
            self.checkComboBox_.setEnabled(False)
            self.okButton_.setEnabled(True)
        else:
            self.checkComboBox_.insertItem("-please select-", -1)    
            self.okButton_.setEnabled(False)
        # Filling Checks combo-box
        for check in checks:
            self.checkComboBox_.insertItem(str(check))
        self.checkComboBox_.sort()
        self.fillTailsList(list(tailsDescMap.keys()))

    def fillTailsList(self, tails, selectAll = False):
        self.airplaneTailsListView_.clear()
        for tail in tails:
            if not tail in self.__tailsDescMap:
                listitem = QListViewItem(self.airplaneTailsListView_, tail)
                continue
            tail_desc = self.__tailsDescMap[tail]
            listitem = QListViewItem(self.airplaneTailsListView_, tail,
                                     tail_desc.mfgSerNum,
                                     tail_desc.customerSerNum)
            if selectAll or (tail in self.__selectedTails):
                self.airplaneTailsListView_.setSelected(listitem, True, True)
                
    # Toggles selection mode between "all tails" and
    # "select by effectivity group"
    def selectByEffGroup(self, isSelect):
        if isSelect:
            effectivity_group = str(self.effGroupComboBox_.currentText())
            if(effectivity_group!=''):
                self.fillTailsList(self.__effectivityTailsMap[effectivity_group], True)
            else:
                return    
        else:
            self.fillTailsList(list(self.__tailsDescMap.keys()))
                
    # Lists airplane tails corresponding to selected effectivity group.
    # Previous user selection is discarded and tails passed as selected
    # (in constructor) became selected as well.
    def changeEffGroup(self, effGroup):
        self.fillTailsList(self.__effectivityTailsMap[str(effGroup)], True)
        
    # Returns selected airplane tails
    def getAirplaneTails(self):
        selected_all = True
        airplane_tails = []
        item = self.airplaneTailsListView_.firstChild()
        itemIndex = 0
        while item:
            if self.airplaneTailsListView_.isSelected(item):
                airplane_tails.append(str(item.text(0)))
            else:
                selected_all = False
            item = self.airplaneTailsListView_.getActualObj().invisibleRootItem().child(itemIndex+1)
            itemIndex += 1   

        if selected_all and self.effGroupCheckBox_.isChecked():
            effectivity_group = str(self.effGroupComboBox_.currentText())
            return [effectivity_group]
        
        return airplane_tails

    # Returns assigned checktype
    def getCheckType(self):
        return str(self.checkComboBox_.currentText())

    def enableOk(self):
        self.okButton_.setEnabled(self.checkComboBox_.currentItem()!=0)
        
