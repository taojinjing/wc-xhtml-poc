import sys
from qt import *
from PyQt4.QtGui import QColor

class ListItem(QListViewItem):

    def __init__(self, list, s0, s1=None, s2 = None, s3 = None, s4 = None, s5 = None):
        if s5:
            QListViewItem.__init__(self, list, s0, s1, s2, s3, s4, s5)      
        elif s4:
            QListViewItem.__init__(self, list, s0, s1, s2, s3, s4)      
        elif s3:
            QListViewItem.__init__(self, list, s0, s1, s2, s3)
        elif s2:
            QListViewItem.__init__(self, list, s0, s1, s2)
        elif s1:
            QListViewItem.__init__(self, list, s0, s1)      
        else:
            QListViewItem.__init__(self, list, s0)      
        self.backColor1   = QColor(250, 248, 235)
        self.backColor2   = QColor(255, 255, 255)
        self.selectedBack = QColor(230, 230, 230)
        self.backColor_ = self.backColor1

    def paintCell(self, p, cg, column, width, alignment):
#        p.fillRect( 0, 0, width, self.height(), QBrush(self.backgroundColor()));
#        QListViewItem.paintCell(self, p, cg, column, width, alignment)
        group = cg
        if column == 0 and self.text(0).left(1) == '@':
            group.setColor(QColorGroup.Text, Qt.red)
        elif column != 0 or self.listView().columns() > 2:
            group.setColor(QColorGroup.Base, self.backgroundColor())
        QListViewItem.paintCell(self, p, group, column, width, alignment)
        p.save()
        p.setPen(QPen(cg.dark(), 1))
        wd = self.listView().columnWidth(column)
        if column == 0:
            p.translate(width - wd, 0)
        p.drawLine(0, self.height() - 1, wd, self.height() - 1)
        p.drawLine(wd - 1, 0, wd - 1, self.height())
        p.restore()
        group.setColor(QColorGroup.Base, Qt.white)
        group.setColor(QColorGroup.Text, Qt.black)

    def startRename(self, col):
        self.listView().viewport().repaint();
        QListViewItem.startRename(self, col)
        self.listView().viewport().repaint();

    def backgroundColor(self):
        if self.itemAbove() and self.listView().firstChild() != self :
            if self.itemAbove().backColor_ == self.backColor1:
                self.backColor_ = self.backColor2
            else :
                self.backColor_ = self.backColor1
        else:
            self.backColor_ = self.backColor1
        if self.listView().firstChild() == self :
            self.backColor_ = self.backColor1
        return self.backColor_


class ListToolTip(QToolTip):
    def __init__(self, lv):
        QToolTip.__init__(self, lv.viewport())
        self.view_ = lv;

    def maybeTip(pos):
        if not self.parentWidget() or not self.view_ or \
           not self.view_.showToolTips():
            return
        item = ListItem
        item = self.view_.itemAt(pos)
        contentsPos = self.view_.viewportToContents(pos)
        if not item or not self.view_.columns():
            return
        text = "To edit value, click on the right field";
        col = self.view_.header().sectionAt(contentsPos.x())
        rect = self.view_.itemRect(item)
        headerPos = self.view_.header().sectionPos(col)
        rect.setLeft(headerPos)
        rect.setRight(headerPos + view_.header().sectionSize(col))
        self.tip(rect, text);

