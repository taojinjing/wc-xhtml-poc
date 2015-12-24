import sys
from SernaApi import *
from qt import *
from .icons import *
from .dialog.InsertReferenceDialog import InsertReferenceDialog
from .utils import *
from PyQt4.QtGui import QCursor
from PyQt4.QtCore import Qt
from pywrap import *

############################################################################
class LinkTargetData:
    def __init__(self, id, element, title, uri):
        self.id_ = id
        self.element_ = element
        self.title_ = title
        self.uri_ = uri
        
############################################################################

class InsertDMReferenceDialogImpl(InsertReferenceDialog):
    def __init__(self, plugin, parent, srcGrove, refSrcGrove, structEditor, dmID,\
                  name, isLocal = False):
        InsertReferenceDialog.__init__(self, parent, None, False, Qt.WDestructiveClose)
       
        self.setCaption("Insert DM Reference")
        self.insertButton_.hide()
        layout_widget = self.child("layout3")
        layout_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,1,0,layout_widget.sizePolicy().hasHeightForWidth()))
        layout_widget = self.child("layout6")
        layout_widget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,2,0,layout_widget.sizePolicy().hasHeightForWidth()))

        self.listView_.setColumnWidthMode(0, QListView.Maximum)
        self.listView_.setColumnWidthMode(0, QListView.Manual)
        self.listView_.setColumnWidth(1, 50)
        self.filter_ = [ ["figure"],["table"],["multimedia"],["supply"],["supequip"],\
            ["spares"],["para"],["step"],["graphic"],["multimediaobject"],["hotspot"],\
            ["param"],["other"]]
        self.isReject_ = False
        self.plugin_ = plugin
        self.structEditor_=structEditor
        self.dmID_ = dmID
        self.name_ = name
        self.isLocal_ = isLocal
        self.treeView_.setSorting(-1)
        self.listView_.setSorting(-1)
        self.treeView_.header().hide()
        self.srcFile_ = QFileInfo(refSrcGrove.topSysid().__str__())
        self.curDir_ = QDir(self.srcFile_.dirPath(True))
        self.curDir_.setMatchAllDirs(True)
        self.helpButton_.hide() #TODO enable when help is ready
        if isLocal:
            self.treeView_.hide()
            self.extComboBox_.hide()
            self.filterComboBox_.hide()
            self.addressLabel_.hide()
            self.addressEdit_.hide()
            self.browseButton_.hide()
            self.filePath_ = self.srcFile_.fileName()
            self.parseGrove(refSrcGrove)
            self.adjustSize()
        else:
            self.extensionChanged()

    def fillTreeView(self, dir):
        if not dir.isReadable():
            return;
        self.treeView_.clear()
        self.treeView_.setUpdatesEnabled(False)
        files = dir.entryInfoList(QDir.DefaultFilter, QDir.DirsFirst or QDir.Name)
        if not(len(dir.path())==3 and str(dir.path().mid(1,1))==":") and \
           len(files) > 0:
            files.pop(0)   
        files.reverse()
        for it in files:
            item = QListViewItem(self.treeView_, it.fileName())
            if it.isDir():
                if it.fileName() == "..":
                    item.setPixmap(0, QPixmap(pix_folder_open))
                else:
                    item.setPixmap(0, QPixmap(pix_folder))
            else:
                if it.extension() == "xml":
                    item.setPixmap(0, QPixmap(pix_file_xml))
                else:
                    item.setPixmap(0, QPixmap(pix_file))
        self.treeView_.clearSelection()
        self.treeView_.setUpdatesEnabled(True)

    def reject(self):
        self.isReject_ = True
        InsertReferenceDialog.reject(self)
            
    def fileOrFolderChanged(self):
        item = self.treeView_.selectedItem()
        if not item:
            return
        if self.curDir_.cd(item.text(0), False):
            self.fillTreeView(self.curDir_)
        else:
            self.parseGrove()

    def extensionChanged(self):
        self.curDir_.setNameFilter(self.extComboBox_.currentText())
        self.fillTreeView(self.curDir_)


    def prepareFilePath(self, path):
        parentItem = self.listView_
        self.listView_.clear()
        files = self.curDir_.entryInfoList(QDir.Files, QDir.Name)
        it = None
        is_found = False
        for it in files:
            if it.fileName() == path:
                is_found = True
                break
        if is_found and self.srcFile_.absFilePath() != it.absFilePath():
            self.filePath_ = it.absFilePath()
            src_path = self.srcFile_.dir().absPath()
            cut_start = len(src_path) + 1
            if cut_start == 4 and src_path.mid(1) == str(":/"):
                cut_start = cut_start  - 1 # for windows root paths
            if self.filePath_.contains(src_path):
                self.filePath_ = self.filePath_.mid(cut_start)
        if self.filterComboBox_.currentItem() == 0:
            parentItem = QListViewItem(self.listView_, self.filePath_)
            parentItem.setOpen(True)
        self.addressEdit_.setText(self.filePath_.__str__())
        return parentItem

    def parseGrove(self, grove = None, url = None):
        parentItem = self.listView_
        is_local = True
        self.grove_ = grove
        if url: #webdav
            is_local = False
            self.curDir_.setCurrent(QFileInfo(url).dirPath(True))
            self.filePath_ = url
            parentItem = self.prepareFilePath(QFileInfo(url).fileName())
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.grove_ = Grove.buildGroveFromFile(url)
            qApp.restoreOverrideCursor()
        elif not grove:
            is_local = False
            item = self.treeView_.selectedItem()
            if not item:
                return         
            self.filePath_ = self.srcFile_.fileName()
            parentItem = self.prepareFilePath(item.text(0))
            fi = QFileInfo(self.filePath_)
            full_path = fi.absFilePath()
            if fi.isRelative():
                full_path = QFileInfo(self.curDir_, fi.fileName()).absFilePath()
            qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.grove_ = Grove.buildGroveFromFile(full_path.__str__())
            qApp.restoreOverrideCursor()
        filters = []
        if self.filterComboBox_.currentItem() > 0:
            filters = self.filter_[self.filterComboBox_.currentItem() - 1]
        self.fillRefsView(self.grove_.document().documentElement(),
                          parentItem, filters, is_local)

    def fillRefsView(self, node, parentItem, filters, isLocal = False):
        elem = node.asGroveElement()
        if not elem:
            return
        id_attr = elem.attrs().getAttribute("id")
        success = (len(filters) == 0)
        for f in filters:
            if f == elem.nodeName():
                success = True
        if id_attr and success:
            content = XpathExpr(".").eval(elem).getString().__str__()
            if not content:
                content = ""
            content = simplifyWhiteSpace(content[0:36])
            if len(content) > 34: # longer string, for bug 5051
                content = content + "..."
            field = content# no more element id, for bug 5051
            selfItem = QListViewItem(parentItem, field, 
                           elem.nodeName().__str__())
            selfItem.setOpen(True)
        else:
            selfItem = parentItem
        lst = elem.children()
        lst.reverse()
        for child in lst:
            self.fillRefsView(child, selfItem, filters, isLocal)    
        if self.listView_.firstChild():
            self.listView_.setSelected(self.listView_.firstChild(), True)

    def filterChanged(self):
        self.parseGrove()

    def insertLink(self):
        sel_item = self.listView_.selectedItem()
        if not sel_item:
            return
        elem_name = sel_item.text(1).__str__()
        id_str = sel_item.text(0).__str__()
        id_str = id_str[id_str.find('[')+1:-1]
        result_col = ""
        if self.name_ == "conref":
            item = sel_item.parent()
            while item and item.text(0) != self.filePath_:
                id_txt = item.text(0).__str__()
                result_col = id_txt[id_txt.find('[')+1:-1] + "/" + result_col
                item = item.parent()
        if sel_item.text(0) != self.filePath_:
            result_col = "#" + result_col + id_str
        if not self.isLocal_ and  self.srcFile_.fileName() != self.filePath_:
            result_col = self.filePath_.__str__() + result_col
        if self.name_ == "link" and not get_node("//*[@id='"+ id_str + "']/title",\
           self.grove_.document().documentElement()):
            elem_name = ""
        self.insertReference(self.name_, result_col, elem_name)

    def insertLinkAndClose(self):
        self.insertLink()
        self.done(1)#accept()
        
    def selectionChanged(self):
        self.insertButton_.setEnabled(self.listView_.selectedItem() != None)
        self.insertAndCloseButton_.setEnabled(self.listView_.selectedItem() != None)

    def browse(self):
        pn = PropertyNode("")
        if not self.plugin_.executeCommandEvent("OpenUrlDialog",pn, pn):
            return;
        url = pn.getSafeProperty("doc-src").getString()
        if not url:
            return
        self.parseGrove(None, url.__str__())
        
    def insertReference(self, name, value, extraInfo = ""):
        name = "refdm"
        se = self.structEditor_
        pos = se.getCheckedPos()
        if not pos.node() or not get_node("ancestor-or-self::mainfunc", pos.node()):
            return       
        sep = value.index('#')
        attr_set = PropertyNode("")
        attr_set.appendChild(PropertyNode("dmreftype", "reference"))
        attr_set.appendChild(PropertyNode("target", self.dmID_ + ".xml" + "#" + value[sep + 1:]))
        se.executeAndUpdate(se.groveEditor().insertElement(
                            pos, name, attr_set));
        se.grabFocus() # set input focus back into the document 