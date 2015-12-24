from .ExecutorBase import *
import sys
from .dialog.GraphicsDialog import GraphicsDialog
from .EditGraphicSize import EditGraphicSize
from qt import *
from string import *
from .ListItem import *
from .icons import *
from urllib import *
from PyQt4.QtGui import QCursor, QDialog, QMessageBox
from PyQt4.QtCore import Qt
##########################################################################
# Graphics
##########################################################################
class EditGraphics(ExecutorBase):
    def execute(self):
        if self.isReadOnly():
            return
        navigateStr = get_datum_from_expr("ancestor-or-self::graphic/title",\
                                         self.getCurrentNode()).__str__()[7:]
        GraphicsDialogImpl(self, navigateStr)
        #if QDialog.Accepted == dialog.exec_loop():
        #    self.insertImage(dialog.getImage())
            #self.plugin_().executeUiEvent("EditGraphicSize", None)

    def searchCollections(self, searchReq = None):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor), True)
        if not searchReq:
            searchReq = ("getAllCollections", [("depth","5")])
        url = self.composeUrl(searchReq[0], searchReq[1])
        grove = Grove.buildGroveFromFile(url)
        folders = get_nodes("//collections/collection", grove.document())
        folder_list = []
        for folder in folders:
            folder_list.append(get_node_text(folder))
        qApp.restoreOverrideCursor()
        return folder_list

    def searchImages(self, searchCriteria, fromNum):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor), True)
        image_list = []
        criteria = searchCriteria
        criteria.insert(0, ("begin", str(fromNum).__str__()))
        url = self.composeUrl("imageSearch", criteria)
        #print url
        grove = Grove.buildGroveFromFile(url)
        images = get_nodes("//images/image", grove.document())
        total = get_datum_from_expr("//images/total", grove.document())
        for image in images:
            id = get_datum_from_expr("id", image)
            thumbnail_id = get_datum_from_expr("thumbnail-id", image)
            uri = get_datum_from_expr("uri", image)
            description = get_datum_from_expr("description", image)
            image_list.append((id, thumbnail_id, uri, description))      
        qApp.restoreOverrideCursor()
        return (total, image_list)
        
    def getImage(self, id):
        return self.retrieveFile(id)

    def insertImages(self, images):
        if not images:
            return
        node = self.getCurrentNode()
        while node:
           context = get_node("self::mainfunc or self::step1 or \
                               self::step2 or self::step3 or \
                               self::step4 or self::step5 or self::step6", node)
           if context:
               break
           node = node.parent()
        if not context:
            context = get_node("//mainfunc", self.srcDoc_)
            if not context:
                return
        batch = GroveBatchCommand()
        elements = []
        for image in images:
            id_str = str(image[0])
            plist = image[2].split("/")
            title = "Image: " + plist[len(plist) - 1]

            id_val = self.structEditor_.generateId("%t")
            element = build_element("graphic",[("title",title)],[("href", id_str), ("id", id_val)])
            pixmap = QPixmap(self.getImage(id_str))
            if not pixmap.isNull() : 
                pdm = QPaintDeviceMetrics(pixmap)
                orig_height = float(pixmap.height())/float(pdm.logicalDpiY())
                orig_width  = float(pixmap.width())/float(pdm.logicalDpiX())
                height = pixmap.height()
                if height > 600:
                    scale = float(600) / float(height)
                    orig_height = orig_height * scale
                    orig_width  = orig_width * scale
                    #scale = int((600 / float(height))*100)
                    #attr = GroveAttr("reproscl", str(scale*100))
                    #element.attrs().appendChild(attr)
                attr_h = GroveAttr("reprohgt", '%*.*f in'%(5,1,float(orig_height)))
                attr_w = GroveAttr("reprowid", '%*.*f in'%(5,1,float(orig_width)))
                element.attrs().appendChild(attr_h)
                element.attrs().appendChild(attr_w)
            elements.append(element)

        if self.structEditor_.canInsertElement("figure","",GrovePos(get_node("//mainfunc", self.srcDoc_))):
            parent_figure = get_node("ancestor-or-self::figure", self.getCurrentNode())
            fragment = GroveDocumentFragment()
            if not parent_figure:
                id_val = self.structEditor_.generateId("%t")
                fig_element = build_element("figure",None,[("id", id_val)])
                for element in elements:
                    fig_element.appendChild( element)
                batch.executeAndAdd(self.\
                    insertElement("figure|graphic|sign|req-access|text|note|caution|warning", context, fig_element))
            else:
                context = parent_figure
                for element in elements:
                    batch.executeAndAdd(self.\
                       insertElement("figure|graphic|sign|req-access|text|note|caution|warning", context, element))
            if get_node("figure", context):
                self.structEditor_.setCursorBySrcPos(GrovePos(get_node("figure", context)),\
                self.structEditor_.getFoPos().node(), True)
        else:
            for element in elements:
                batch.executeAndAdd(self.\
                    insertElement("graphic|sign|req-access|text|note|caution|warning", context, element))
                self.structEditor_.setCursorBySrcPos(GrovePos(get_node("graphic", context)),\
                           self.structEditor_.getFoPos().node(), True)
        self.structEditor_.executeAndUpdate(batch)

# temp_pos = GrovePos(node, before)
# if not before:
#     temp_pos = GrovePos(node.parent(), node.nextSibling())
# if structEditor.canInsertElement(name,"",temp_pos):


##########################################################################

class GraphicsDialogImpl(GraphicsDialog):
    def __init__(self, plugin, navigateStr):
        GraphicsDialog.__init__(self, plugin.qtWidget_)
        self.setModal(False)
        self.plugin_ = plugin
        self.sernaDoc_ = plugin.sernaDoc_
        self.__searchImages = plugin.searchImages
        self.__getImage = plugin.getImage
        self.__searchFolders = plugin.searchCollections
        currentDate_ = QDate.currentDate()
        thisDayLastYear_ = currentDate_.addYears(-5)
        self.fromDateEdit_.setDate(thisDayLastYear_)
        self.toDateEdit_.setDate(currentDate_)
        self.__imageMap = {}
        self.__tumbMap = {}
        self.uriLineEdit_.setText("")
        self.__fromNumber = 1
        self.__maxResults = 14
        self.resultsLabel_.setText(str("Results: 0"))
        self.listView_.removeColumn(1)
        self.folderUri_ = self.folderLabel_.text().__str__()
        self.preview_.setScaledContents(False)
        self.buildFolders()
        #if navigateStr: #to navigate existing image
        #    self.uriLineEdit_.setText(navigateStr)
        #    self.search()
        self.show()
        if self.listView_.firstChild():
            self.listView_.setCurrentItem(self.listView_.firstChild())
               
    def buildFolders(self, searchReq = None):
        folders = self.__searchFolders(searchReq)
        for folder in folders:
            parent = self.treeView_
            plist = folder.split("/")
            if plist[1] != 'graphics':
               continue;
            for j in range(1,len(plist)):
                found = False
                item = parent.firstChild()
                while item:
                    if item.text(0) == plist[j]:
                        found = True
                        break
                    item = item.nextSibling(item, parent)
                if found:
                    parent = item
                    continue;
                item = QListViewItem(parent, plist[j]) 
                item.setOpen(True)
                item.setPixmap(0, QPixmap(pix_folder_open))
                parent = item
            parent.setOpen(True)
            #self.__uriMap[folder] = parent
            #self.__root.makeDescendant(folder)
        #self.treeView_.repaint()           
        #self.treeView_.triggerUpdate() 

    def refresh(self):
        self.treeView_.clear()
        self.buildFolders()

    def search(self, isNewSearch = True):
        uri = str(self.folderUri_)
        name = str(self.uriLineEdit_.text())
        source = str(self.sourceLineEdit_.text())
        description = str(self.descriptionLineEdit_.text())
        fromDate = str(self.fromDateEdit_.date().toString("MM/dd/yyyy"))
        toDate = str(self.toDateEdit_.date().addDays(1).toString("MM/dd/yyyy"))
        author = str(self.authorLineEdit.text())
        search_criteria = [("uri", uri), ("source", source), 
                           ("description", description),
                           ("fromDate", fromDate), ("toDate", toDate),
                           ("author", author),("name", name), 
                           ("maxResults", str(self.__maxResults))]
        if isNewSearch or 0 > self.__fromNumber:
            self.__fromNumber = 1
        results = self.__searchImages(search_criteria, self.__fromNumber)
        images = results[1]
        total  = results[0]
        self.listView_.clear()
        self.__imageMap.clear()
        self.__tumbMap.clear()
        if images != None and len(images) > 0:
            for i in range(len(images)):
                image = images[i]
                id = image[0]
                thumbnail_id = image[1]
                uri = image[2]
                description = image[3]
                if len(uri) > 90:
                    uri = ".." + uri[-90:]
                description = image[3]
                item = ListItem(self.listView_, uri)#, str(description))
                self.__imageMap[item] = image
            self.prevButton_.setEnabled(self.__fromNumber > self.__maxResults)
            self.nextButton_.setEnabled((self.__fromNumber+len(images)-1) < int(total))
            self.resultsLabel_.setText(str("Results:") + \
                str(self.__fromNumber) + str("-") +\
                str(self.__fromNumber + len(images) - 1) +\
                str(" of ") + str(total))

        elif self.__fromNumber > 1:
            self.nextButton_.setEnabled(False)
            self.__fromNumber = self.__fromNumber - self.__maxResults
        else:
            self.resultsLabel_.setText(str("Results: 0"))
            QMessageBox.warning(self, "Warning", "The search items were not found.\n"
            "Please define more search criteria\n"
            "use a combination of dates and other fields")


        self.listView_.setCurrentItem(self.listView_.firstChild())
        self.listView_.setSelected(self.listView_.firstChild(), True)
        #self.okButton_.setEnabled(self.listView_.selectedItem() != None)
        if isNewSearch or 0 > self.__fromNumber:
            self.itemSelected()
        
    def prev(self):
        self.__fromNumber = self.__fromNumber - self.__maxResults
        self.search(False)

    def next(self):
        self.__fromNumber = self.__fromNumber + self.__maxResults
        self.search(False)

    def scale(self, pixmap):
        border = 4
        if self.preview_.width() != pixmap.width():
            width = self.preview_.width() - border
            height = self.preview_.height() - border
            if pixmap.width() > pixmap.height() * 2:
                if pixmap.height() * width / pixmap.width() < height:
                    height = pixmap.height() * width / pixmap.width()
            if pixmap.height() > pixmap.width() * 2:
                koef = height / pixmap.height()
                if pixmap.width() * koef < width:
                    width = pixmap.width() * koef
            #image = pixmap.convertToImage()
            #image = image.smoothScale(width, height, QImage.ScaleMin)
            pixmap = pixmap.scaled(width, height,1,1)
            #pixmap = QPixmap(image)
        return pixmap

    def generateThumbnail(self, imageData):
        thumbnail_id =  imageData[1]
        id_ =  imageData[1]

        THUMBNAIL_BORDER = 4
        width = self.preview_.width()  - THUMBNAIL_BORDER

        pixmap = QPixmap(self.__getImage(thumbnail_id))
        #If pixmap is smaller then preview widget, take real image
        if not pixmap or pixmap.width() < width:
            pixmap = QPixmap(self.__getImage(id_))
        if not pixmap:
            return self.image0 # built-in image (see .ui) "Preview"

        if width == pixmap.width():
            return pixmap
        pixmap = pixmap.scaled(width, self.preview_.height() - THUMBNAIL_BORDER,1,1)
        return pixmap


    def itemSelected(self):
        #cur_item = self.listView_.currentItem()
        cur_item = self.listView_.selectedItem()
        if cur_item:
            self.listView_.setSelected(cur_item, True)
        if not cur_item:
            self.insertButton_.setEnabled(False)
            self.insertAndCloseButton_.setEnabled(False)
            return
            
        self.insertButton_.setEnabled(True)
        self.insertAndCloseButton_.setEnabled(True)
        image_data = self.__imageMap[cur_item]
        uri = image_data[2]
        
        if uri in self.__tumbMap:
            pixmap = self.__tumbMap[uri]
        else:
            self.setCursor(Qt.WaitCursor)
            pixmap = self.generateThumbnail(image_data)
            self.__tumbMap[uri] = pixmap
            self.setCursor(Qt.ArrowCursor)            
        self.preview_.setPixmap(pixmap)

    def itemChanged(self):
        uri = ""
        short_uri = None
        cur = self.treeView_.currentItem()
        tmp_item = cur
        while tmp_item:
            if not short_uri and (len(uri) + len(tmp_item.text(0))) > 30:
                short_uri = "..." + uri
            uri = "/" + tmp_item.text(0).__str__() + uri
            tmp_item = tmp_item.parent()
        if not short_uri:
            short_uri = uri
        self.folderLabel_.setText(short_uri)
        self.folderUri_ = uri
        if cur and not cur.firstChild(): # and cur.text(0) != 'cards':
            searchReq = ("getCollectionsWithParent", [("parent", uri)])
            self.buildFolders(searchReq)
        

    def expanded(self,a0):
        a0.setPixmap(0, QPixmap(pix_folder_open))

    def collapsed(self,a0):
        a0.setPixmap(0, QPixmap(pix_folder))

    def help(self):
        self.sernaDoc_.showHelp("index.html")       

    def getImage(self):
        items = []
        it = self.listView_.firstChild()
        while it:
            if it.isSelected():
                image = self.__imageMap[it]
                items.append(image)
            it = it.nextSibling(it, self.listView_.invisibleRootItem())
        if len(items) == 0:
            return None
        return items

    def insert(self):
        """
             insert()
                    insert image tag into source xml
        """
        self.plugin_.insertImages(self.getImage())

    def insertAndClose(self):
        """
             insertAndClose()
                    insert image tag into source xml
                    close and exit from dialog
        """
        self.plugin_.insertImages(self.getImage())
        GraphicsDialog.accept(self)

