import re
from weakref import ref
from SernaApi import *
from PyQt4.QtGui import QTableWidget, QTableWidgetItem, QToolTip, QPalette
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.Qt import *
from .dialog.DMReferencesDialog import DMReferencesDialog
from .utils import *
from urllib import *
from PyQt4.QtGui import QMessageBox
from qt import *
############################################################################
class RefData:
    def __init__(self, id, title, schema, changeType, attachAction = None, checkPi = True):
        self.id_ = id
        self.title_ = title
        self.type_ = schema
        self.changeType_ = changeType
        # This field stores the API which handles this structure.
        self.attachAction_ = attachAction
        self.checkPi_ = checkPi
    
class ReusedDM:
    def __init__(self, refData, element, parentIdMap, childIdMap, linkType):
        self.refData_ = refData
        self.id_ = refData.id_
        self.element_ = element
        self.parentIdMap_ = parentIdMap
        self.childIdMap_ = childIdMap
        self.refCount_ = 0
        self.linkType_ = linkType
        self.enabled_ = True
        self.continueStepList_ = []
        self.flattened_xref_ = ""
        if self.refData_.checkPi_:
            """check if there is flattened xref/internalRef"""
            flattened_pi = get_node("//processing-instruction('flattened-xref')", element)
            if flattened_pi:
                self.flattened_xref_ = "xref"
            #else:
            #    self.flattened_xref_ = ""
    
    
    def changeRefCount(self, add):
        if add:
            self.refCount_ = self.refCount_ + 1
        else:
            self.refCount_ = self.refCount_ - 1
    
    def hasRef(self):
        return self.refCount_ > 0
    
    def isAdded(self):
        return self.linkType_ and self.linkType_ != ""
    
    def setEnabled(self, enabled):
        self.enabled_ = enabled
        
    def isEnabled(self):
        return self.enabled_
    
    def addContinueStep(self, CSReusedDM):
        self.continueStepList_.append(CSReusedDM)
        
    def getContinueSteps(self):
        return self.continueStepList_
    
class ExtGraphic:
    def __init__(self, id, linkType, targetDM):
        self.id_ = id
        self.linkType_ = linkType
        self.targetDM_ = targetDM

class ColoredTableItem(QTableWidgetItem):
    def __init__(self, txt):
        QTableWidgetItem.__init__(self,txt)
        self.setEditable(False)

    def paint(self, p, colorGroup, rect, selected):
        newcolor = QPalette(colorGroup)
        if not(self.isEnabled()):
            newcolor.setColor(QPalette.Base, Qt.lightGray) 
        QTableWidgetItem.paint(self, p, newcolor, rect, selected)

    def setEditable(self, editable):
        flags = self.flags()
        if editable:
           flags = flags | Qt.ItemIsEditable
        else:
           flags = flags & (~Qt.ItemIsEditable)
        self.setFlags(flags);

    def setEnabled(self, enabled):
        flags = self.flags()
        if enabled:
           flags = flags | Qt.ItemIsEnabled
        else:
           flags = flags & (~Qt.ItemIsEnabled)
        self.setFlags(flags);

    def isEnabled(self):
        flags = self.flags()
        enabled = Qt.ItemIsEnabled & flags
        return enabled != Qt.NoItemFlags

class ColoredCheckTableItem(QTableWidgetItem):
    def __init__(self,table,txt):
        QTableWidgetItem.__init__(self,txt)
        self.setEditable(False)
        self.setCheckState(Qt.Unchecked)
        self.hasWarning_ = False

    def paint(self, p, colorGroup, rect, selected):
        newcolor = QPalette(colorGroup)
        if not(self.isEnabled()):
            newcolor.setColor(QPalette.Base, Qt.lightGray) 
        elif self.hasWarning_:
            newcolor.setColor(QPalette.Text, Qt.red)
            newcolor.setColor(QPalette.HighlightedText, Qt.red)
        QTableWidgetItem.paint(self, p, newcolor, rect, selected)

    def setEditable(self, editable):
        flags = self.flags()
        if editable:
           flags = flags | Qt.ItemIsEditable
        else:
           flags = flags & (~Qt.ItemIsEditable)
        self.setFlags(flags);

    def setEnabled(self, enabled):
        flags = self.flags()
        if enabled:
           flags = flags | Qt.ItemIsEnabled
        else:
           flags = flags & (~Qt.ItemIsEnabled)
        self.setFlags(flags);

    def isEnabled(self):
        flags = self.flags()
        enabled = Qt.ItemIsEnabled & flags
        return enabled != Qt.NoItemFlags

    def isChecked(self):
        return self.checkState() == Qt.Checked

    def setChecked(self, checked):
        if checked:
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

class TableToolTip(QToolTip):
    def __init__(self, table):
        QToolTip.__init__(self, table)
        self.table_ = table 
        self.cellMap_ = {}
    
    def addCell(self, row, col):
        self.cellMap_[(row,col)] = True

    def removeCell(self, row, col):
        del self.cellMap_[(row,col)]
        
    def maybeTip(self, point):
        y1 = point.y() - self.table_.leftMargin() + self.table_.contentsY()
        x1 = point.x() - self.table_.leftMargin() + self.table_.contentsX()
        row = self.table_.rowAt(y1)
        col = self.table_.columnAt(x1)
        #print("%d %d, %d %d" %(row, col, point.y(), point.x()))
        if (row,col) in self.cellMap_:
            rect = self.table_.cellGeometry(row, col)
            rect.moveTopLeft(QPoint(point.x()-20, point.y()-20))
            #print("%d %d %d %d" %(rect.top(),rect.left(),rect.bottom(),rect.right()))
            tipstr = "This selection has one or more references to targets in the Data Module that are" \
                +"\nnot selected for reuse in the workcard. These will result in reference text that will" \
                +"\nprobably not make sense in the workcard. Linking does not allow changing that text." \
                +"\nYou may want to Adapt this selection instead of Link to correct that text."
            self.tip(rect,tipstr)

############################################################################

class InsertDMRefImpl(DMReferencesDialog):
    def __init__(self, plugin, parent, structEditor, dmID, dmCode):
        DMReferencesDialog.__init__(self, parent)
        self.setCaption("Select Element for Reuse - " + dmCode)
        self.tableView_.setColumnWidth(0,50)
        self.tableView_.setColumnWidth(1,50)
        self.tableView_.setColumnWidth(2,100)
        self.tableView_.setColumnWidth(3,170)
        self.tableView_.setColumnWidth(4,155)
        self.tableView_.setSelectionMode(QTableWidget.NoSelection)
        self.connect(self.tableView_,SIGNAL("cellClicked(int,int)"), self.checkElement)

        self.dmc_ = dmCode
        self.plugin_ = ref(plugin)
        self.structEditor_= structEditor
        workcard = structEditor.sourceGrove().document()
        self.carrier_code = get_node("//prelreq/carrier-code/text()",workcard).asGroveText().data()
        self.mfg = get_node("//prelreq/mfg/text()",workcard).asGroveText().data()
        self.model = get_node("//prelreq/model/text()",workcard).asGroveText().data()
        self.dash = get_node("//prelreq/dash/text()",workcard).asGroveText().data()
        self.dmID_  = dmID        
        self.batch_ = GroveBatchCommand()
        self.result_ = self.searchRefs({"id": self.dmID_})
        frontmatter = self.__searchDM4Frontmatter(self.dmID_)
        if frontmatter:
            self.result_.insert(0, frontmatter)
        self.elementRows_ = {}
        self.elementMap_ = {}
        rowNum = 0
        for data in self.result_:
            if self.addElementRow(rowNum, data, self.elementRows_):
                rowNum = rowNum + 1
        self.tableView_.setRowCount(rowNum)
        rowNum = 0
        for data in self.result_:
            if data.id_.find("-EXT") == -1:
                self.buildTable(rowNum, data)
                rowNum = rowNum + 1

    def addElementRow(self, rowNum, refData, map):
        id = refData.id_
        add_row = False
        target = self.dmID_ + ".xml" + "%23" + id
        url = self.composeUrl("lookupWorkcardFragment",{'type':'preview','target':target,'crossReference':'true', 'carrierCode':self.carrier_code, 'mfg':self.mfg, 'model':self.model, 'dash':self.dash})
        grove = Grove.buildGroveFromFile(url)
        root = grove.document().documentElement()
        parentIdMap = {}
        linkType = ""
        cur = self.structEditor_.sourceGrove().document()
        if get_node("//*[@id='"+id+"' and ancestor-or-self::*/@dmidreftype='link']", cur):
            linkType = 'link'
        elif get_node("//*[@id='"+id+"' and ancestor-or-self::*/@dmidreftype='adapt']", cur):
            linkType = 'adapt'
        if get_node("//*[@id='"+id+"' and ancestor-or-self::*/@dmidreftype='linkStepContinue']", cur):
            linkType = 'link'
        elif get_node("//*[@id='"+id+"' and ancestor-or-self::*/@dmidreftype='adaptStepContinue']", cur):
            linkType = 'adapt'

        for addedRow in list(map.values()):
            if id in addedRow.childIdMap_:
                parentIdMap[addedRow.id_] = addedRow.element_
                """disable parent when child is added"""
                if linkType != "":
                    addedRow.setEnabled(False)
        childs = get_nodes(".//step1[@id]|.//step3[@id]|.//figure[@id]|.//graphic[@id]|.//table[@id]", root)
        childIdMap = {}
        for child in childs:
            childId = get_attribute(child, "id")
            childIdMap[childId] = child
        element = ReusedDM(refData, root, parentIdMap, childIdMap, linkType)

        if id.find("-EXT") != -1:
            """add continue steps to head step"""
            headStepId = id[:id.find("-EXT")]
            headStep = self.elementMap_.get(headStepId)
            headStep.addContinueStep(element)
            self.extendMap(headStep.childIdMap_, childIdMap)
        else:
            map[rowNum] = element
            add_row = True
        self.elementMap_[id] = element
        return add_row

    def extendMap(self, source, target):
        for key in list(target.keys()):
            source[key] = target[key]

    def formatStr_toShow(self, txt):
        newTxt = re.sub(r'\s+', " ", txt)
        newTxt = re.sub(r'\s*$', "", newTxt)
        if len(newTxt) > 100:
            newTxt = newTxt[0:100]+'...'
        return str(newTxt)

    def buildTable(self, rowNum, data):
        elementRow = self.elementRows_.get(rowNum)
        linkCB = ColoredCheckTableItem(self.tableView_, elementRow.flattened_xref_)
        if not(elementRow.flattened_xref_ == ""):
            linkCB.hasWarning_ = True
        adaptCB = ColoredCheckTableItem(self.tableView_, "")
        if not(elementRow.isEnabled()):
            linkCB.setEnabled(False)
            adaptCB.setEnabled(False)
        if elementRow.linkType_ == "link":
            linkCB.setEnabled(False)
            linkCB.setChecked(True)
            adaptCB.setEnabled(False)
        elif elementRow.linkType_ == "adapt":
            adaptCB.setEnabled(False)
            adaptCB.setChecked(True)
            linkCB.setEnabled(False)
        elementItem = ColoredTableItem(self.formatStr_toShow(data.type_))
        idItem = ColoredTableItem(self.formatStr_toShow(data.id_))
        titleItem = ColoredTableItem(self.formatStr_toShow(data.title_))
        elementItem.setEnabled(linkCB.isEnabled())
        idItem.setEnabled(linkCB.isEnabled())
        titleItem.setEnabled(linkCB.isEnabled())

        self.tableView_.setItem(rowNum, 0, linkCB)
        self.tableView_.setItem(rowNum, 1, adaptCB)
        self.tableView_.setItem(rowNum, 2, elementItem)
        self.tableView_.setItem(rowNum, 3, idItem)
        self.tableView_.setItem(rowNum, 4, titleItem)


    def checkElement(self, row, col):
        if (col > 1):
            return
        item = self.tableView_.item(row, col)
        if not(item.isEnabled()):
            return
        neighbour = self.tableView_.item(row, 1 - col)
        element = self.elementRows_.get(row)
        changeType = neighbour.isChecked()
        neighbour.setChecked(False)
        isChecked = item.isChecked()

        for key in list(self.elementRows_.keys()):
            elementRow = self.elementRows_[key]
            if element.id_ in elementRow.parentIdMap_ and not(elementRow.isAdded()):
                if not(changeType):
                    elementRow.changeRefCount(isChecked)
                isEnabled = not(isChecked or elementRow.hasRef())
                self.tableView_.item(key, col).setChecked(not(isEnabled))
                self.tableView_.item(key, 1 - col).setChecked(False)
                self.updateTableState(key, isEnabled)
            elif element.id_ in elementRow.childIdMap_ and not(elementRow.isAdded()):
                isEnabled = not(isChecked)
                self.tableView_.item(key, col).setChecked(False)
                self.tableView_.item(key, 1 - col).setChecked(False)
                self.updateTableState(key, isEnabled)

    def updateTableState(self, row, isEnabled):
        for col in range(0, self.tableView_.columnCount()):
            self.tableView_.item(row, col).setEnabled(isEnabled)

    def composeUrl(self, action, parameters):
        if ".do" != action[-3:]:
            action += ".dox"
        url = self.plugin_().serverDomain_ + action + "?sessionid=" + self.plugin_().sessionId_
        for param in list(parameters.keys()):
            url += "&" + str(param) + "=" + str(parameters[param])
        return url

    def __searchDM4Frontmatter(self, dmID):
        url = self.plugin_().composeDavPath(dmID + ".xml")
        grove = Grove.buildGroveFromFile(url)
        if not grove:
            return None
        dmNode = get_node("//dmodule", grove.document())
        if not dmNode:
            return None
        attr = dmNode.attrs().getAttribute("id")
        if attr and attr.value():
            # The instance of 'RefData' holds all necessary informations which 
            # creates the 'frontmatter' in workcard. 
            return RefData(attr.value(), "Descriptive Frontmatter", "frontmatter", "add", self.__addFrontmatter, False)
        else:
            return None

    def __addFrontmatter(self, refdata, link, batchCmd):
        target = self.dmID_ + ".xml%23autoGenerateWorkcardFrontmatter"
        url = self.composeUrl("lookupWorkcardFragment",{'type':link, 'target':target,'showRevdate':'true', 'carrierCode':self.carrier_code, 'mfg':self.mfg, 'model':self.model, 'dash':self.dash})
        grove = Grove.buildGroveFromFile(url)
        root = None
        if grove:
            root = grove.document().documentElement()
        if not root:
            QMessageBox.warning(self, "Error", "Cannot retrieve content '" + refData.id_ + "' from " + self.dmc_)
            return False
        node = get_node("//workcard/mainfunc/frontmatter", self.structEditor_.sourceGrove().document())
        if node:
            if node.isReadOnly():
                return False
            ask = QMessageBox.question(self, "Overwrite confirmation", "Do you want to overwrite existed 'frontmatter' information?", QMessageBox.Yes, QMessageBox.No)
            if ask != QMessageBox.Yes:
                return False
            cmd = self.structEditor_.groveEditor().removeNode(node)
            batchCmd.executeAndAdd(cmd)

        # Create one new frontmatter node.
        mainfuncNode = get_node("//workcard/mainfunc", self.structEditor_.sourceGrove().document())
        if not mainfuncNode:
            # There is no position to add 'frontmatter'
            return False
        else:
            insPos = self.__locateInspos('frontmatter', '', mainfuncNode, mainfuncNode.firstChild())
            
            fragment = GroveDocumentFragment()
            fragment.appendChild(root.cloneNode(True))
            cmd = self.structEditor_.groveEditor().paste(fragment, insPos)
            batchCmd.executeAndAdd(cmd)

        # Do we really to lock the new added node? 
        # frontNode = get_node("//workcard/mainfunc/frontmatter[1]", self.structEditor_.sourceGrove().document())
        #if link == 'link':
        #    frontNode.setReadOnly(True)
        return True

    def __locateInspos(self, eleName, ns, p, c):
        if not p:
            return None
        if not c:
            insPos = GrovePos(p)
        else:
            insPos = GrovePos(p, c)
        if self.structEditor_.canInsertElement(eleName, ns, insPos):
            return insPos
        
        if c:
            if c.countChildren() > 0:
                subc = c.firstChild()
                while subc:
                    insPos = self.__locateInspos(eleName, ns, c, subc)
                    if insPos:
                        return insPos
                    else:
                        subc = subc.nextSibling()
            else:
                insPos = self.__locateInspos(eleName, ns, c, None)
            if insPos:
                return insPos
            return self.__locateInspos(eleName, ns, p, c.nextSibling())
        else:
            return None
    
    def searchRefs(self, searchCriteria):
        url = self.composeUrl("lookupLinkTargets", searchCriteria)
        grove = Grove.buildGroveFromFile(url)
        resources = get_nodes("//linktargets/linktarget", grove.document())
        refs_list = []
        for resource in resources:
            refs_list.append(
                RefData(get_first_text_data_from_expr("id", resource),
                        get_first_text_data_from_expr("title", resource),
                        get_first_text_data_from_expr("type", resource),
                        get_first_text_data_from_expr("changeType", resource)))
        return refs_list

    def getImage(self, id):
        return self.plugin_().retrieveFile(id)

    def indexOfExtGraphicInList(self, graphic_id, list):
        i = 0
        for extGraphic in list:
            if extGraphic.id_ == graphic_id:
                return i
            i = i + 1
        return -1

    def insertRef(self):
        res_ids = []
        ext_graphic_list = []
        ext_refdm_list = []
        handledItemCount = 0
        for row in range(0, self.tableView_.rowCount()):
            linkItem = self.tableView_.item(row, 0)
            adaptItem = self.tableView_.item(row, 1)
            if linkItem.isChecked() and linkItem.isEnabled():
                linkType = "link"
            elif adaptItem.isChecked() and adaptItem.isEnabled():
                linkType = "adapt"
            else:
                # The item is disabled and we don't need it.
                continue
            # Insert/Update 'frontmatter'.
            reusedDM = self.elementMap_[self.elementRows_.get(row).id_]
            if reusedDM and reusedDM.refData_.attachAction_:
                opCode = reusedDM.refData_.attachAction_(reusedDM.refData_, linkType, self.batch_)
                if opCode:
                    handledItemCount = handledItemCount + 1
                continue
            
            # To keep the old processing logic.
            if linkItem.isChecked() and linkItem.isEnabled():
                link_id = self.insertRefItem('link', self.elementRows_.get(row).id_, ext_graphic_list, ext_refdm_list)
                if link_id == -1:
                    return ([], 0)
                res_ids.append(link_id)
                self.insertContinueSteps('linkStepContinue', self.elementRows_.get(row), ext_graphic_list, ext_refdm_list, res_ids)
                handledItemCount = handledItemCount + 1
            elif adaptItem.isChecked() and adaptItem.isEnabled():
                adapt_id = self.insertRefItem('adapt', self.elementRows_.get(row).id_, ext_graphic_list, ext_refdm_list)
                if adapt_id == -1:
                    return ([], 0)
                res_ids.append(adapt_id)
                handledItemCount = handledItemCount + 1
                self.insertContinueSteps('adaptStepContinue', self.elementRows_.get(row), ext_graphic_list, ext_refdm_list, res_ids)

        for ext_graphic in ext_graphic_list:
            ext_id = self.insertExtGraphic(ext_graphic.linkType_, ext_graphic.id_, ext_graphic.targetDM_)
            res_ids.append(ext_id)
        for ext_graphic in ext_refdm_list:
            ext_id = self.insertExtGraphic(ext_graphic.linkType_, ext_graphic.id_, ext_graphic.targetDM_)
            res_ids.append(ext_id)
        return (res_ids, handledItemCount)

    def insertContinueSteps(self, linkType ,reusedDM, ext_graphic_list, ext_refdm_list, result_id_list):
        for continueStep in reusedDM.getContinueSteps():
            contiueStepId = self.insertRefItem(linkType, continueStep.id_, ext_graphic_list, ext_refdm_list)
            result_id_list.append(contiueStepId)

    def insertRefItem(self, linkType, id, ext_graphic_list, ext_refdm_list):
        target = self.dmID_ + ".xml" + "%23" + id
        url = self.composeUrl("lookupWorkcardFragment",{'type':linkType,'target':target,'showRevdate':'true', 'carrierCode':self.carrier_code, 'mfg':self.mfg, 'model':self.model, 'dash':self.dash})
        grove = Grove.buildGroveFromFile(url)
        root = grove.document().documentElement()
        if not root:
            QMessageBox.warning(self, "Error", "Cannot retrieve content '" + id + "' from " + self.dmc_)
            return -1
        res_id = get_datum_from_expr("@id",root)
        pos = self.place_to_insert(root)
        if not pos:
            QMessageBox.warning(self, "Warning", "No place to insert '"+ \
                                root.nodeName().__str__()+"'")
            return -1
        """remove added ext graphic"""
        if root.nodeName().__str__() == "figure" or root.nodeName().__str__() == "graphic":
            index = self.indexOfExtGraphicInList(id, ext_graphic_list)
            if index != -1:
                ext_graphic_list.pop(index)
            childIdMap = self.elementMap_.get(id).childIdMap_
            for childId in list(childIdMap.keys()):
                childIndex = self.indexOfExtGraphicInList(childId, ext_graphic_list)
                if childIndex != -1:
                    ext_graphic_list.pop(childIndex)

        self.structEditor_.stripInfo().strip(root)
        fragment = GroveDocumentFragment()
        fragment.appendChild(root.cloneNode(True))
        graphics = get_nodes("//graphic[not(@reprowid) and not(@reprohgt)]", fragment)
        for node in graphics:
            self.adaptGraphicSize(node)
        """figure cross reference, move figure/graphic out of xref to end of mainfunc"""
        ext_graphics = get_nodes("//xref[not(@xrefid=//@id)]", fragment)
        for node in ext_graphics:
            ext_id = get_attribute(node, "xrefid")
            ref_target = get_attribute(node, "target")
            if ref_target and ref_target != '' and self.indexOfExtGraphicInList(ext_id, ext_refdm_list) == -1 \
                    and not(get_node("//*[@id='"+ext_id+"']", self.structEditor_.sourceGrove().document())):
                ext_refdm_list.append(ExtGraphic(ext_id, linkType, ref_target))
            elif self.indexOfExtGraphicInList(ext_id, ext_graphic_list) == -1 and self.indexOfExtGraphicInList(ext_id, ext_refdm_list) == -1 \
                    and not(get_node("//*[@id='"+ext_id+"']", self.structEditor_.sourceGrove().document())):
                ext_graphic_list.append(ExtGraphic(ext_id, linkType, self.dmID_ + ".xml"))

        ge = self.structEditor_.groveEditor()
        self.batch_.setSuggestedPos(pos)
        self.batch_.executeAndAdd(ge.paste(fragment, pos))
        return res_id

    def insertExtGraphic(self, linkType, id, targetDM):
        target = targetDM + "%23" + id
        url = self.composeUrl("lookupWorkcardFragment",{'type':linkType,'target':target,'showRevdate':'true', 'carrierCode':self.carrier_code, 'mfg':self.mfg, 'model':self.model, 'dash':self.dash})
        grove = Grove.buildGroveFromFile(url)
        root = grove.document().documentElement()
        if not root:
            QMessageBox.warning(self, "Error", "Cannot retrieve content '" + id + "' from " + targetDM)
            return -1;
        res_id = get_datum_from_expr("@id",root)
        mainfunc = get_node("//mainfunc", self.structEditor_.sourceGrove().document())
        pos = GrovePos(mainfunc)
        self.structEditor_.stripInfo().strip(root)
        fragment = GroveDocumentFragment()
        fragment.appendChild(root.cloneNode(True))
        graphics = get_nodes("//graphic[not(@reprowid) and not(@reprohgt)]", fragment)
        for node in graphics:
            self.adaptGraphicSize(node)
        ge = self.structEditor_.groveEditor()
        self.batch_.executeAndAdd(ge.paste(fragment, pos))
        return res_id

    def adaptGraphicSize(self, node):
        graphic = node.asGroveElement()
        attrs = graphic.attrs()
        href = get_attribute(graphic, "href")
        pixmap = QPixmap(self.getImage(href))
        pdm = QPaintDeviceMetrics(pixmap)
        hgt = '%*.*f'%(5,1,float(pixmap.height())/float(pdm.logicalDpiY()))
        wid = '%*.*f'%(5,1,float(pixmap.width())/float(pdm.logicalDpiY()))
        if float(wid) > 8:
            wid = "8";
        if float(hgt) > 11:
            hgt = "11";
        attrs.setAttribute(GroveAttr("reprohgt",hgt+"in"))
        attrs.setAttribute(GroveAttr("reprowid",wid+"in"))

    def reuse(self):
        self.batch_ = GroveBatchCommand()
        (res_list, handledItemCount) = self.insertRef()
        if not handledItemCount:
            return;
        if not self.addActref():
            return;
        cur = self.structEditor_.sourceGrove().document()
        self.structEditor_.executeAndUpdate(self.batch_)
        for res in res_list:
            node = get_node("//*[@id='"+res.__str__()+"' and (@dmidreftype='link' or @dmidreftype='linkStepContinue')]", cur);
            if node:
                node.setReadOnly(True)
                self.structEditor_.setCursorBySrcPos(GrovePos(node), \
                                                     self.structEditor_.getFoPos().node(), True)

        DMReferencesDialog.accept(self)

    def getActrefElement(self):
        target = self.dmID_ + ".xml"
        url = self.composeUrl("lookupWorkcardFragment",{'type':'preview','target':target, 'carrierCode':self.carrier_code, 'mfg':self.mfg, 'model':self.model, 'dash':self.dash})
        grove = Grove.buildGroveFromFile(url)
        root = grove.document().documentElement()
        return root

    def addActref(self):
        root = self.getActrefElement()
        if not root:
            return True
        fragment = GroveDocumentFragment()
        fragment.appendChild(root.cloneNode(True))
        refdm = get_node("//refdm", fragment);
        if not refdm:
            #QMessageBox.warning(self, "Error", "Error occurs when retrieving 'actref' from " + self.dmc_)
            return True
        current_actdm = get_node("//actref/refdm", self.structEditor_.sourceGrove().document())
        if current_actdm:
            current_dmc = self.getDMC(current_actdm)
            refact_dmc = self.getDMC(refdm)
            if  current_dmc != refact_dmc:
                QMessageBox.warning(self, "Error", "Cannot reuse data module, workcard 'actref' is " \
                                    + str(current_dmc) + " but DM 'actref' is " + str(refact_dmc))
                return False
        else:
            ge = self.structEditor_.groveEditor()
            mainfunc = get_node("//mainfunc", self.structEditor_.sourceGrove().document())
            pos = GrovePos(mainfunc, mainfunc.firstChild())
            self.batch_.executeAndAdd(ge.paste(fragment, pos))
        return True

    def getDMC(self, node):
        modelic = get_node("avee/modelic/text()", node).asGroveText().data()
        sdc = get_node("avee/sdc/text()", node).asGroveText().data()
        chapnum = get_node("avee/chapnum/text()", node).asGroveText().data()
        section = get_node("avee/section/text()", node).asGroveText().data()
        subsect = get_node("avee/subsect/text()", node).asGroveText().data()
        subject = get_node("avee/subject/text()", node).asGroveText().data()
        discode = get_node("avee/discode/text()", node).asGroveText().data()
        discodev = get_node("avee/discodev/text()", node).asGroveText().data()
        incode = get_node("avee/incode/text()", node).asGroveText().data()
        incodev = get_node("avee/incodev/text()", node).asGroveText().data()
        itemloc = get_node("avee/itemloc/text()", node).asGroveText().data()
        return modelic + "-" + sdc + "-" + chapnum + "-" + section + "-" \
               + subsect + "-" + subject + "-" + subject + "-" + discode + "-" \
               + discodev + "-" + incode + "-" + incodev + "-" + itemloc

    def selectionChanged(self):
        is_not_none_current_item = True if self.listView_.currentItem() else False
        self.linkButton_.setEnabled(is_not_none_current_item)
        self.adaptButton_.setEnabled(is_not_none_current_item)

    def categoryChanged(self, category):
        it = self.listView_.firstChild()
        while it:
            it.setSelected(False)
            if category == 'All' or category == it.text(0):
                it.setVisible(True)
            else:
                it.setVisible(False)
            it = it.nextSibling()

    def placeToInsert(self, typeName):
        se = self.structEditor_
        name= typeName
        pos = self.structEditor_.getCheckedPos()
        if self.structEditor_.canInsertElement(typeName, "", pos):
            se.setCursorBySrcPos(pos, se.getFoPos().node(), True)
            return pos
        node = pos.node()
        before = pos.before()
        if pos.type() == GrovePos.TEXT_POS:
            before = node.parent()
            node = before.parent()
            before = before.nextSibling()
        pos = None
        while node:
            while True:
                temp_pos = GrovePos(node, before)
                if not before:
                    temp_pos = GrovePos(node.parent(), node.nextSibling())
                if self.structEditor_.canInsertElement(typeName, "", temp_pos):
                    pos = temp_pos
                    break
                if not before:
                    break
                before = before.nextSibling()
            if pos:
                break
            if node.nextSibling():
                node = node.nextSibling()
                before = node.firstChild()
            else:
                before = node.nextSibling()
                node = node.parent()

        if pos:
            se.setCursorBySrcPos(pos, se.getFoPos().node(), True)
            return pos
        return None;

    def place_to_insert(self, root):
        return self.placeToInsert(root.nodeName())
