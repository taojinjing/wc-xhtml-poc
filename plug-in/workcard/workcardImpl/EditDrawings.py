from .ExecutorBase import *
from .dialog.DrawingsDialog import DrawingsDialog
from .dialog.DrawParamsDialog import DrawParamsDialog
from qt import *
from PyQt4.QtGui import QDialog, QMessageBox
##########################################################################
# Drawings
##########################################################################
class EditDrawings(ExecutorBase):
    def execute(self):
        drawings = self.getCurrentDrawings()
        dialog = DrawingsDialogImpl(self.qtWidget_, self.sernaDoc_, drawings)
        if QDialog.Accepted == dialog.exec_loop():
            drawings = dialog.getDrawings()
            self.replaceOrInsert("drawings", drawings, 
            "zones-panels forecasts "
            "configurations checks maintflow-num crew-type")
        
    def getCurrentDrawings(self):
        drawings = []
        drawing_nodes = get_nodes("//prelreq/drawings/drawing", self.srcDoc_)
        for drawing_node in drawing_nodes:
            vendor_code = get_datum_from_expr("draw-vendor-code", drawing_node)
            drawing_num = get_datum_from_expr("draw-num", drawing_node)
            drawing_type = get_datum_from_expr("draw-type", drawing_node)
            drawing_rev = get_datum_from_expr("draw-rev", drawing_node)
            drawing_comment = get_datum_from_expr("draw-comment", drawing_node)
            drawing = vendor_code, drawing_num, \
                      drawing_type, drawing_rev, drawing_comment
            drawings.append(drawing)           
        return drawings

##########################################################################

class DrawingsDialogImpl(DrawingsDialog):
    def __init__(self, parent, sernaDoc, drawings):
        DrawingsDialog.__init__(self, parent)        
        self.sernaDoc_ = sernaDoc
        for d in drawings:
            param1 = ""
            if d[0] and  d[0] != "":
                param1 = d[0]
            param2 = ""
            if d[1] and  d[1] != "":
                param2 = d[1]
            param3 = ""
            if d[2] and  d[2] != "":
                param3 = d[2]
            param4 = ""
            if d[3] and  d[3] != "":
                param4 = d[3]
            param5 = ""
            if d[4] and  d[4] != "":
                param5 = d[4]
            listitem = QListViewItem(self.listView_, \
                       param1, param2, param3, param4, param5)
        self.selectionChanged()
        self.listView_.setSelected(self.listView_.firstChild(), True)

    def getDrawings(self):
        drawings = []
        item = self.listView_.firstChild()
        while item:
            params = []
            if item.text(0) and item.text(0) != "":
                params.append(("draw-vendor-code", str(item.text(0))))
            if item.text(1) and item.text(1) != "":
                params.append(("draw-num", str(item.text(1))))
            if item.text(2) and item.text(2) != "":
                params.append(("draw-type", str(item.text(2))))
            if item.text(3) and item.text(3) != "":
                params.append(("draw-rev", str(item.text(3))))
            if item.text(4) and item.text(4) != "":
                params.append(("draw-comment", str(item.text(4))))
            drawings.append(("drawing", params))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())   
        return drawings

    def add(self):
        param1 = ""
        param2 = ""
        param3 = ""
        param4 = ""
        param5 = ""
        while True:
            dialog = DrawParamsDialogImpl(self, param1, param2, param3, param4, param5)
            if QDialog.Accepted == dialog.exec_loop():
                data = dialog.getData()
                if self.hasDup(data[0], data[1]):
                    QMessageBox.warning(self, "Warning","Record with such fields already exists.")
                    param1 = data[0]
                    param2 = data[1]
                    param3 = data[2]
                    param4 = data[3]
                    param5 = data[4]
                else:
                    QListViewItem(self.listView_, data[0], \
                              data[1], data[2], data[3], data[4])
                    break
            else:
                break

    def edit(self):
        item = self.listView_.selectedItem()
        if not item:
            return
        param1 = item.text(0)
        param2 = item.text(1)
        param3 = item.text(2)
        param4 = item.text(3)
        param5 = item.text(4)
        while True:
            dialog = DrawParamsDialogImpl(self, param1, param2, param3, param4, param5)
            if QDialog.Accepted == dialog.exec_loop():
                data = dialog.getData()
                if self.hasDup(data[0], data[1], self.listView_.selectedItem()):
                    QMessageBox.warning(self, "Warning","Record with such fields already exists.")
                    param1 = data[0]
                    param2 = data[1]
                    param3 = data[2]
                    param4 = data[3]
                    param5 = data[4]
                else:
                    item.setText(0, data[0])
                    item.setText(1, data[1])
                    item.setText(2, data[2])
                    item.setText(3, data[3])
                    item.setText(4, data[4])
                    break
            else:
                break

    def remove(self):
        item = self.listView_.selectedItem()
        next = item.itemBelow()
        if not next:
            next = item.itemAbove()
        if item:
            self.listView_.takeItem(item)
        if next:
            self.listView_.setSelected(next, True)
        else:
            self.selectionChanged()

    def hasDup(self, text):
        item = self.listView_.firstChild()
        while item:
            if text == item.text(0).__str__():
                return True
            item = item.nextSibling(item, self.listView_.invisibleRootItem())
        return False

    def hasDup(self, field1, field2, cur = None):
        item = self.listView_.firstChild()
        while item:
            if item != cur and field1 == item.text(0).__str__() and \
               field2 == item.text(1).__str__():
                return True
            item = item.nextSibling(item, self.listView_.invisibleRootItem())  
        return False

    def selectionChanged(self):
        item = self.listView_.selectedItem()
        self.editButton_.setEnabled(item != None)
        self.removeButton_.setEnabled(item != None)

    def help(self):
        self.sernaDoc_.showHelp("workcard-doc.html#too-dialog")

##########################################################################
      
class DrawParamsDialogImpl(DrawParamsDialog):
    def __init__(self, parent, vendor="", num="", \
                 type="", rev="", comment=""):
        DrawParamsDialog.__init__(self, parent)
        self.vendorEdit_.setText(vendor)
        self.numEdit_.setText(num)
        if type != "":
            self.typeEdit_.setCurrentText(type)
        self.revEdit_.setText(rev)
        self.commentEdit_.setText(comment)
        self.vendorEdit_.setFocus()

    def accept(self):
        if not self.vendorEdit_.text() or not self.numEdit_.text():
            QMessageBox.warning(self, "Warning",
                "'Vendor Code' and 'Num' fields are required !")
            return;
        DrawParamsDialog.accept(self)

    def getData(self):
        return (self.vendorEdit_.text().__str__(),
                self.numEdit_.text().__str__(),
                self.typeEdit_.currentText().__str__(),
                self.revEdit_.text().__str__(),
                self.commentEdit_.text().__str__())
