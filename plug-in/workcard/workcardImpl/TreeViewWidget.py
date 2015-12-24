from SernaApi import *
from weakref import *
import sip
from pywrap import *
from qt import *
from .utils import *
from string import *
from .dialog.icons import *

##########################################################################
# Folders view for image dialog, references dialog and others
##########################################################################

class TreeViewWidget:

    def __init__(self, listView, label, composeFunc, rootFolderName = None):
        self.listView_ = listView
        self.label_ = label
        self.filter_ = rootFolderName
        self.composeUrl_ = composeFunc

    def fillCollectionsList(self, searchReq = None):
        collections = self.searchCollections(searchReq)
        fristTime = False
        for collection in collections:
            parent = self.listView_
            plist = collection.split("/")
            if self.filter_ and  plist[1].find(self.filter_) < 0:
                continue
            parent_name = plist[1]
            if len(parent_name.strip())<1:
                continue
            parent = None
            for i in range(self.listView_.topLevelItemCount()):
                if self.listView_.topLevelItem(i).text(0) == parent_name:
                    parent = self.listView_.topLevelItem(i)
            if not parent:
                itemAtt = QTreeWidgetItem()
                itemAtt.setText(0,parent_name)
                parent = self.listView_.invisibleRootItem()
                parent.addChild(itemAtt)
                itemAtt.setExpanded(True)
                parent.setIcon(0, QIcon(QPixmap(open_folder_icon)))
                fristTime = True
            startI = 0
            if fristTime:
                fristTime = False
                startI = 1
            else:
                startI = 2
            for counter in range(startI, len(plist)):
                if ':' in plist[counter]:
                    plist[counter] = plist[counter].upper()
                found = False
                item = None
                for i in range(parent.childCount()):
                    item = parent.child(i)
                    if item and item.text(0) == plist[counter]:
                        found = True
                        break
                if found:
                    parent = item
                    continue;
                item = QListViewItem(parent, plist[counter])
                item.setExpanded(True)
                item.setPixmap(0, QPixmap(open_folder_icon))
                parent = item
            parent.setExpanded(True)
#        self.listView_.repaint()

    def searchCollections(self, searchReq = None):
        if not searchReq:
            #searchReq = ("getAllCollections", {"depth" : 5})
            searchReq = ("getAllCollections", {})
        url = self.composeUrl_(searchReq[0], searchReq[1])
        grove = Grove.buildGroveFromFile(url)
        collections = get_nodes("//collections/collection", grove.document())
        collection_list = []
        for collection in collections:
            collection_list.append(get_node_text(collection))
        return collection_list

    def currentCollectionChanged(self):
        uri = ""
        cur = self.listView_.currentItem()
        tmp_item = cur
        while tmp_item:
            uri = "/" + tmp_item.text(0).__str__() + uri
            tmp_item = tmp_item.parent()
        self.label_.setText(uri)
        if cur and not cur.child(0) and cur.text(0) != 'cards':
            searchReq = ("getCollectionsWithParent",\
                         {"parent" : self.label_.text().__str__()})
            self.fillCollectionsList(searchReq)

    def collectionExpanded(self, listItem):
        """
             collectionExpanded(listItem)
                    draw opened folder icon when click on closed folder
                   @listItem - item
        """
        QTreeWidgetItemWrap(listItem).setPixmap(0, QPixmap(open_folder_icon))

    def collectionCollapsed(self, listItem):
        """
             collectionExpanded(listItem)
                    draw closed folder icon when click on opened folder
                   @listItem - item
        """
        QTreeWidgetItemWrap(listItem).setPixmap(0, QPixmap(folder_icon))

    def refresh(self):
        self.listView_.clear()
        self.fillCollectionsList()
        self.listView_.repaint()

def matchFolder(collection, folder):
    if folder is None or collection is None:
        return True
    if len(folder) == 0 or len(collection) < 2:
        return True
    if folder[0] != collection[1]:
        return False
    if len(folder) == 1 or len(collection) < 3:
        return True
    if folder[1] != collection[2]:
        return False
    if len(folder) == 2 or len(collection) < 4:
        return True
    if folder[2] != collection[3]:
        return False
    return True
#################################################################

class LocalTreeViewWidget(TreeViewWidget):
    def __init__(self, listView, label, composeFunc, rootFolderName = None):
        TreeViewWidget.__init__(self, listView, label, composeFunc, rootFolderName)
        self.__currentDir = QDir()
        self.__currentDir.setPath(QDir.current().path().__str__())

    def searchCollections(self, searchReq=None):
        collection_list = []
        drives = QDir.drives()
        for drive in drives:
            path = drive.filePath().__str__()[:-1]
            collection_list.append('/drives/' + path)
        dirs = self.__currentDir.entryInfoList(QDir.Dirs, QDir.Name)
        if 2 == len(dirs):
            path = '/drives/' + self.__currentDir.absPath().__str__()
            collection_list.append(path)
        for dir_ in dirs[2:]:
            path = '/drives/' + dir_.absFilePath().__str__()
            collection_list.append(path)
        return collection_list

    def currentCollectionChanged(self):
        uri = ""
        cur = self.listView_.currentItem()
        tmp_item = cur
        while tmp_item:
            uri = "/" + tmp_item.text(0).__str__() + uri
            tmp_item = tmp_item.parent()
        uri = uri.replace('/drives/', '')
        if len(uri) > 40:
            uri = '..' + uri[-38:]
        self.label_.setText(uri)
        self.__currentDir.setPath(self.label_.text().__str__())
        QDir.setCurrent(self.label_.text().__str__())
        TreeViewWidget.fillCollectionsList(self, None)