import sys, random
from PyQt4.QtCore import QDir as QDir4
from PyQt4.QtCore import QFileInfo as QFileInfo4
from PyQt4.QtGui  import QToolTip as QToolTip4
from PyQt4.QtGui  import QMatrix, QApplication, QStackedWidget, QGroupBox, QTreeWidget, QTreeWidgetItem, QGraphicsScene, QGraphicsView, QGraphicsRectItem, QGraphicsLineItem, QGraphicsPolygonItem, QMenu, QTextEdit, QTextCursor, QImage, QPixmap, QButtonGroup, QIcon, QAction, QListView, QHeaderView, QAbstractItemView, QSortFilterProxyModel
from PyQt4.QtCore import *

###############################Class###########################
class QDir(QDir4):
    
    def __init__(self, path=None, nameFilter=None, sortSpect=0, filterSpect=0):
        if filterSpect:
            super(QDir4, self).__init__(path, nameFilter, sortSpect, filterSpect)
        elif path:
            super(QDir4, self).__init__(path)
        else:
            super(QDir4, self).__init__(".")
           
    @staticmethod
    def homeDirPath():
        dir = QDir()
        return dir.homePath()

    def setNameFilter(self, filterItem):
        return self.setNameFilters(filterItem)
    
    def setMatchAllDirs(self, ifall):
        if ifall:
            return self.setFilter(QDir4.AllDirs)

class QFileInfo(QFileInfo4):

    def __init__(self, dir = None, file = None):
        if dir is None and file is None :
            super(QFileInfo4, self).__init__(self)
        elif file is not None:
            super(QFileInfo4, self).__init__(dir ,file)
        else:
            super(QFileInfo4, self).__init__(dir)

    def dirPath(self, abspath=False):
        if abspath:
            return self.absolutePath()
        else:
            return self.path()

    def absFilePath(self):
        return self.absoluteFilePath()
    

class QToolTip(QToolTip4):

    def __init__(self, tooltip):
        super(QToolTip4, self).__init__(tooltip)

    @staticmethod
    def setGloballyEnabled(enable):
        print("QTWRAP NOTE: This method has been removed.") 
        return
    
    def add(self, showTipItem, showTipText):
        showTipItem.setToolTip(showTipText)

class QIconSet(QIcon):

    def __init__(self, arg):
        if arg is None:
            QIcon.__init__(self)
        else:
            QIcon.__init__(self, arg)


class QWMatrix(QMatrix):
    def __init__(self, m11=None, m12 = None, m21 = None, m22 = None, dx = None, dy = None):
        if m11 is not None:
            QMatrix.__init__(self, m11, m12, m21, m22, dx, dy)
        else:
            QMatrix.__init__(self)

class QListViewItem(QTreeWidgetItem):

    def __init__(self, parent, s0=None, s1 = None, s2 = None, s3 = None, s4 = None, s5 = None, s6 = None, s7 = None, s8 = None, after = None):
        args = []
        if s8 is not None and isinstance(s8, str):
            args.insert(0, s8)
        if s7 is not None and isinstance(s7, str):
            args.insert(0, s7)
        if s6 is not None and isinstance(s6, str):
            args.insert(0, s6)
        if s5 is not None and isinstance(s5, str):
            args.insert(0, s5)
        if s4 is not None and isinstance(s4, str):
            args.insert(0, s4)
        if s3 is not None and isinstance(s3, str):
            args.insert(0, s3)
        if s2 is not None and isinstance(s2, str):
            args.insert(0, s2)
        if s1 is not None and isinstance(s1, str):
            args.insert(0, s1)
        if s0 is not None and isinstance(s0, str):
            args.insert(0, s0) 
        
        if parent:
            if isinstance(parent, QTreeWidgetWrap):
                parent = parent.getActualObj()
        if len(args) <= 0:
            if parent is None and after is None:
                QTreeWidgetItem.__init__(self)
            else:
                if after is None:
                    QTreeWidgetItem.__init__(self, parent)
                else:
                    QTreeWidgetItem.__init__(self, parent, after)
                    self.setText(0, '')
                    currentIdex = parent.indexOfChild(after)
                    parent.insertChild(currentIdex,self)
        else:
            if parent is None and after is None:
                QTreeWidgetItem.__init__(self, args)
            else:
                if isinstance(parent, QTreeWidget):
                    parent = parent.invisibleRootItem()
                QTreeWidgetItem.__init__(self, parent, args)
                if len(args)>0:
                    self.setText(0,args[0])
                if len(args)>1:
                    self.setText(1,args[1])
                if len(args)>2:
                    self.setText(2,args[2])
                parent.addChild(self)
                

        self.randseed_ = random.randint(-10000, 10000)

    def setOpen(self, ifExpanded):
        return self.setExpanded(ifExpanded)
    
    def setPixmap(self, setColumn, folderIcon):
        return self.setIcon(setColumn, QIcon(QPixmap(folderIcon)))
    
    def firstChild(self): 
        return self.child(0)

    def nextSibling(self, currentItem=None, parnet=None):
        parentNode = None
        if parnet:
            parentNode = parnet
        elif not currentItem:
            parentNode = self.parent()
        else:
            parentNode = currentItem.parent()
        if parentNode is None:
            parentNode = self
        if isinstance(parentNode,QTreeWidgetWrap):
            parentNode = parentNode.getActualObj()
        if parentNode is not None:
            if isinstance(parentNode, QTreeWidget):
                return self.itemBelow(currentItem, parnet)
            else:
                index = parentNode.indexOfChild(self)
                return parentNode.child(index+1)
        else:
            return None
        
    def aboveSibling(self):
        parentNode = self.parent()
        if parentNode is not None:
            if isinstance(parentNode, QTreeWidget):
                return self.itemAbove(self)
            else:
                index = parentNode.indexOfChild(self)
                return parentNode.child(index-1)
        else:
            return None
    
    def __hash__(self):
        #key = random.randint(-10000, 10000)
        key = self.randseed_
        key = (key << 21) - key - 1;
        key ^= key >> 24
        key * 265
        key ^= key >> 14
        key * 21
        key ^= key >> 28
        key += key << 31
        return key

    def setRenameEnabled(self, column, editable):
        if editable:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
        else:
            self.setFlags(self.flags() & ~Qt.ItemIsEditable)

    def listView(self):
        return self.treeWidget()

    def startRename(self, column):
        self.data(column, Qt.EditRole)

    def okRename(self, column):
        self.data(column, Qt.DisplayRole)

    def itemBelow(self, currentItem=None, parnet=None):
        if self.childCount() > 0:
            return self.child(0)
        else:
            it = self
            below = it.nextSibling()
            while below is None and it is not None:
                it = it.parent()
                if it is None:
                    break
                below = it.nextSibling()
            return below
        
    def itemAbove(self):
        if self.childCount() > 0:
            return self.child(0)
        else:
            it = self
            above = it.aboveSibling()
            while above is None and it is not None:
                it = it.parent()
                if it is None:
                    break
                above = it.aboveSibling()
            return above
        
    def takeItem(self, item):
        # The item must be the top-level item.
        index = self.indexOfChild(item)
        if -1 == index:
            return None
        self.takeChild(index)

class QCanvas(QGraphicsScene):

    def __init__(self, parent = None, pixmap = None, name = None, w = 0, h = 0, v = 0, tilewidth = 0, tileheight = 0):
        rectF = QRectF(0, 0, w, h)
        QGraphicsScene.__init__(self, rectF, parent)
        
        if pixmap is not None:
            self.addPixmap(pixmap)
        if name is not None:
            self.setObjectName(name)

    def collisions(self, point):
        return self.items(point)
        
    
class QCanvasView(QGraphicsView):

    def __init__(self, canvas = None, parent = None, pixmap = None, flag = 0):
        if canvas is None:
            QGraphicsView.__init__(self, parent, flag)
        else:
            QGraphicsView.__init__(self, canvas, parent, flag)
        
        if pixmap is not None and canvas is None:
            inCanvas = QGraphicsScene(parent, pixmap)
            setScene(inCanvas)

    def inverseWorldMatrix(self):
        return self.matrix()

    def viewportToContents(self, point):
        return self.mapToScene(point)      

    def canvas(self):
        return self.scene()

class QCanvasLine(QGraphicsLineItem):

    def __init__(self, canvas):
        QGraphicsLineItem.__init__(self, None, canvas)
        
class QCanvasRectangle(QGraphicsRectItem):

    def __init__(self, canvas):
        QGraphicsRectItem.__init__(self, canvas)

class QCanvasPolygon(QGraphicsPolygonItem):
    
    def __init__(self, canvas):
        QGraphicsPolygonItem.__init__(self, None, canvas)

    def areaPoints(self):
        allPoints = self.polygon()
        return allPoints.toPolygon()
        
class QPopupMenu(QMenu):

    def __init__(self, parent = None, name = None):
        if name is not None:
            QMenu.__init__(self, name, parent)
        else:
            QMenu.__init__(self, parent)

        self.actionMap_ = {}
        self.slotMap_ = {}
        self.id_ = 0

    def insertItem(self, icon, text = None, receiver = None, shortcut = 0):
        if icon is not None:
            newAction = self.addAction(icon, text, receiver)
        else:
            if text is None:
                newAction = self.addAction("", receiver)
            else:
                newAction = self.addAction(text, receiver)

        if shortcut != 0:
            newAction.setShortcut(shortcut)

        self.id_ = self.id_ + 1
        self.actionMap_[self.id_] = newAction
        return self.id_
    
    def connectItem(self, id, receiver):
        action = self.actionMap_[id]
        if action is None:
            return False
        self.slotMap_[id] = receiver
        
        return True

    def disconnectItem(self, id, receiver):
        action = self.actionMap_[id]
        if action is None:
            return False
        QObject.disconnect(SIGNAL("triggered"), SLOT(receiver))     
        self.actionMap_.pop(id)
        self.slotMap_.pop(id)
    
    def setItemParameter(self, id, param):
        if id in self.slotMap_ and id in self.actionMap_:
        #if id in self.actionMap_:
            receiver = self.slotMap_[id]
            action = self.actionMap_[id]
            self.connect(action, SIGNAL("triggered()"), SLOT(receiver(param)))
            return True
        else:
            return False
     

class QPaintDeviceMetrics:

    def __init__(self, paintDevice):
        if isinstance(paintDevice, QImage):
            self.paintDevice_ = QPixmap(paintDevice)
        else:
            self.paintDevice_ = paintDevice
    
    def depth(self):
        return self.paintDevice_.depth()

    def height(self):
        return self.paintDevice_.height()

    def heightMM(self):
        return self.paintDevice_.heightMM()

    def logicalDpiX(self):
        return self.paintDevice_.logicalDpiX()

    def logicalDpiY(self):
        return self.paintDevice_.logicalDpiY()

    def numColors(self):
        return self.paintDevice_.colorCount()

    def width(self):
        return self.paintDevice_.width()

    def widthMM(self):
        return self.paintDevice_.widthMM()
    
    

    
##################Wrap classes############################3

class QApplicationWrap:

    def __init__(self, instance):
        self.instance_ = instance
        return

    @staticmethod
    def instance():
        return QApplicationWrap(QApplication.instance())
        #return QApplicationWrap(QApp)

    def activeWindow(self):
        window = QStackedWidgetWrap(self.instance_.activeWindow())
        return window

    def mainWidget(self):
        if len(self.instance_.topLevelWidgets()) > 0:
            return self.instance_.topLevelWidgets[0]
        else:
            return self.instance_.activeWindow()

    def desktop(self):
        return QApplication.desktop()
        #return self.instance_.desktop()
        
    def setOverrideCursor(self, overrideObject, ifOverride=None):
        return QApplication.setOverrideCursor(overrideObject)
    
    def restoreOverrideCursor(self):
        return QApplication.restoreOverrideCursor()
        
        

class QStackedWidgetWrap:

    def __init__(self, stackedWidget):
        self.qStackedWidget_ = stackedWidget
        return

    def caption(self):
        if self.qStackedWidget_ is None:
            return ""
        return self.qStackedWidget_.windowTitle()

    def setCaption(self, caption):
        if self.qStackedWidget_ is None:
            return 
        self.qStackedWidget_.setWindowTitle(caption)
        return


class QTextEditWrap:

    def __init__(self, textEdit):
        self.textEdit_ = textEdit

    def text(self):
        if self.textEdit_ is None:
            return ""
        else:
            return self.textEdit_.toPlainText()

    def setText(self, text):
        if self.textEdit_ is None:
            return ""
        else:
            return self.textEdit_.setPlainText(text)

    def paragraphs(self):
        if self.textEdit_ is None:
            return 0
        else:
            return self.textEdit_.document().blockCount()
        
    def moveCursor(self, moveOperation, cursorOperation):
        self.textEdit_.moveCursor(moveOperation, cursorOperation)
        self.textEdit_.setFocus()
    
    def getActualObj(self):
        return self.textEdit_

    def setCursorPosition(self, npara, len):
        if self.textEdit_ is None:
            return 0

        para_id = 0
        pos = 0
        while para_id < npara:
            block = self.textEdit_.document().findBlockByNumber(para_id)
            pos = pos + block.position()
        
        block = self.textEdit_.document().findBlockByNumber(npara)
        if block.isValid():
            pos = pos + len
            cursor = QTextCursor(block)
            cursor.setPosition(pos)
            self.textEdit_.setTextCursor(cursor)
        self.textEdit_.setFocus()
        
    def blockSignals(self, ifblock):
        return self.textEdit_.blockSignals(ifblock)
    
    def setFocus(self):
        return self.textEdit_.setFocus()

class QButtonGroupWrap:
    
    def __init__(self, buttonGroup):
        self.buttonGroup_ = buttonGroup

    def setTitle(self, title):
        # Nothing to do. Just let plug-in run.
        return

    def selectedId(self):
        return self.buttonGroup_.checkedId()
    
    def setButton(self, buttonIdex):
        if self.buttonGroup_.button(buttonIdex):
            return self.buttonGroup_.button(buttonIdex).setChecked(True)

class QTreeWidgetItemWrap:

    def __init__(self, treeWidgetItem):
        self.treeWidgetItem_ = treeWidgetItem
        self.randseed_ = random.randint(-10000, 10000)

    def selectedItem(self):
        if not self.treeWidgetItem_.currentItem():
            if self.treeWidgetItem_.selectedItems() and self.treeWidgetItem_.selectedItems().size()>0:
                return self.treeWidgetItem_.selectedItems()[0]
        return self.treeWidgetItem_.currentItem()

    def firstChild(self):
        if self.treeWidgetItem_.invisibleRootItem():
            return self.treeWidgetItem_.invisibleRootItem().child(0)
        return self.treeWidgetItem_.invisibleRootItem()

    def setSelected(self, item, selected):
        if item:
            item.setSelected(selected)
    
    def setSorting(self, ifEnabled):
        if not ifEnabled:
            return self.treeWidgetItem_.setSortingEnabled(False)
        return self.treeWidgetItem_.setSortingEnabled(True)
    
    def setColumnText(self, columnIdex, text):
        return self.treeWidgetItem_.invisibleRootItem().setText(columnIdex, text)
    
    def removeColumn(self, removeColumn):
        self.treeWidgetItem_.setColumnHidden(removeColumn,True)
    
    def childCount(self):
        return self.treeWidgetItem_.invisibleRootItem().childCount()

    def setPixmap(self, column, pixmap):
        self.treeWidgetItem_.setIcon(column, QIcon(pixmap))

    def __hash__(self):
        #key = random.randint(-10000, 10000)
        key = self.randseed_
        key = (key << 21) - key - 1;
        key ^= key >> 24
        key * 265
        key ^= key >> 14
        key * 21
        key ^= key >> 28
        key += key << 31
        return key
        
    def getActualObj(self):
        return self.treeWidgetItem_
    
    def setOpen(self, ifExpanded):
        return self.setExpanded(ifExpanded)

class QTreeWidgetWrap:

    def __init__(self, treeWidget):
        self.treeWidget_ = treeWidget
        self.randseed_ = random.randint(-10000, 10000)
        self.treeWidget_.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget_.setSortingEnabled(True)
        self.treeWidget_.header().setSortIndicatorShown(False)

    def selectedItem(self):
        if not self.treeWidget_.currentItem():
            if self.treeWidget_.selectedItems() and len(self.treeWidget_.selectedItems())>0:
                return self.treeWidget_.selectedItems()[0]
        return self.treeWidget_.currentItem()

    def addChild(self, widgetItem):
        self.treeWidget_.addChild(self)

    def removeColumn(self, columnID):
        self.setColumnHidden(columnID, True)

    def addColumn(self, textList):
        self.treeWidget_.setHeaderLabels(textList)

    def firstChild(self):
        if self.treeWidget_.invisibleRootItem():
            return self.treeWidget_.invisibleRootItem().child(0)
            return self.treeWidget_.invisibleRootItem()

    def setCurrentItem(self, treeWidgetItem):
        self.treeWidget_.setCurrentItem(treeWidgetItem)

    def clear(self):
        self.treeWidget_.clear()
        
    def setSelected(self, widgetItem, selected, ifBouble=False):
        if not ifBouble:
            self.setSelectedItemsFlase()
        if widgetItem:
            widgetItem.setSelected(selected)
    
    def setSelectedItemsFlase(self):
        selected_items = self.treeWidget_.selectedItems()
        if selected_items:
            for selectItem in selected_items:
                selectItem.setSelected(False)
          
    def getActualObj(self):
        return self.treeWidget_

    def columns(self):
        return self.treeWidget_.columnCount()

    def invisibleRootItem(self):
        return self.treeWidget_.invisibleRootItem()

    def setColumnHidden(self, columnID, hidden):
        self.treeWidget_.setColumnHidden(columnID, hidden)

    def setColumnWidthMode(self, columnID, mode=None):
        logicID = self.treeWidget_.header().logicalIndex(columnID)
        self.treeWidget_.header().setResizeMode(logicID, QHeaderView.Interactive)

    def setColumnWidth(self, columnID, width):
        return self.treeWidget_.setColumnWidth(columnID, width)

    def columnText(self, columnID):
        headerItem = self.treeWidget_.headerItem()
        if headerItem is not None:
            return headerItem.text(columnID)
        else:
            return ""
    
    def setSorting(self, ifEnabled):
        if ifEnabled > 0:
            self.treeWidget_.header().setSortIndicatorShown(False)
            return self.treeWidget_.setSortingEnabled(True)
        return self.treeWidget_.setSortingEnabled(False)
    
    def installEventFilter(self, filter):
        self.treeWidget_.installEventFilter(filter)
    
    def show(self):
        return self.treeWidget_.show()
  
    def hide(self):
        return self.treeWidget_.hide()
  
    def header(self):
        return self.treeWidget_.header() 
  
    def setColumnText(self, columnIdex, text):
        return self.treeWidget_.invisibleRootItem().setText(columnIdex, text)
    
    def setHeaderLabel(self, text):
        return self.treeWidget_.setHeaderLabel(text)
   
    def setPixmap(self,column, pixmap):
        self.treeWidget_.setIcon(column, QIcon(pixmap))  
        
    def childCount(self):
        return self.treeWidget_.invisibleRootItem().childCount()
    
    def currentItem(self):
        curitem = self.treeWidget_.currentItem()
        if curitem is None:
            rootItem = self.treeWidget_.invisibleRootItem()
            if rootItem and rootItem.childCount() > 0:
                self.treeWidget_.setCurrentItem(rootItem.child(0)) 

        return self.treeWidget_.currentItem()
    
    def takeItem(self, item):
        # The item must be the top-level item.
        index = self.treeWidget_.indexOfTopLevelItem(item)
        if -1 == index:
            return None

        self.treeWidget_.takeTopLevelItem(index)

    def connect(self, signal, slot):
        QObject.connect(self.treeWidget_, signal, slot)

    def blockSignals(self, block):
        self.treeWidget_.blockSignals(block)
    
    def setFocus(self):
        return self.treeWidget_.setFocus()

    def isRenaming(self):
        cur_item = self.currentItem()
        if cur_item is not None:
            if Qt.ItemIsEditable == (cur_item.flags() & Qt.ItemIsEditable):
                return True
        return False
    
    def setSelectionMode(self, selectedMode):
        self.treeWidget_.setSelectionMode(selectedMode)
        
    def setResizeMode(self, selectedMode):
        self.treeWidget_.setResizeMode(selectedMode)
        
    def isSelected(self, item):
        return item.isSelected()
    
    def ensureItemVisible(self, item):
        self.treeWidget_.scrollToItem(item, QAbstractItemView.EnsureVisible) 
        
        
    def __hash__(self):
        key = self.randseed_
        key = (key << 21) - key - 1;
        key ^= key >> 24
        key * 265
        key ^= key >> 14
        key * 21
        key ^= key >> 28
        key += key << 31
        return key
         
         
class QComboxWrap:

    def __init__(self, instance):
        self.combox_ = instance

    def insertItem(self, text, id = None):
        if not id:
            id = self.combox_.count() 
        self.combox_.insertItem(id, text)

    def blockSignals(self, block):
        self.combox_.blockSignals(block)

    def setEnabled(self, enable):
        self.combox_.setEnabled(enable)

    def setDuplicatesEnabled(self, enable):
        self.combox_.setDuplicatesEnabled(enable)

    def setCurrentItem(self, id):
        self.combox_.setCurrentIndex(id)
        
    def setItemText(self, index, test):
        self.combox_.setItemText(index, test)

    def setCurrentText(self, text):
        curid = self.combox_.currentIndex()
        self.combox_.setCurrentIndex(curid)
        
    def insertStrList(self, strLst, index = 0):
        return  self.combox_.insertItems(index, strLst)
    
    def lineEdit(self):
        return self.combox_.lineEdit()
    
    def hide(self):
        return self.combox_.hide()
        
    def count(self):
        return self.combox_.count()

    def currentText(self):
        return self.combox_.currentText()

    def currentItem(self):
        return self.combox_.currentIndex()

    def clear(self):
        return self.combox_.clear()

    def connect(self, signal, slot):
        QObject.connect(self.combox_, signal, slot)
        
    def insertStringList(self, listString, index=0):
        return self.combox_.insertItems(index, listString)   
    
    def sort(self):
        proxy = QSortFilterProxyModel(self.combox_)
        proxy.setSourceModel(self.combox_.model())
        self.combox_.model().setParent(proxy)
        self.combox_.setModel(proxy)
        self.combox_.model().sort(0)
        
    def getActualObj(self):
        return self.combox_   

qApp = QApplicationWrap.instance()
