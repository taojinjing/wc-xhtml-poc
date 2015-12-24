from .ExecutorBase import *
from .dialog.LineEdit2Dialog import LineEdit2Dialog
from .dialog.ForecastsDialog import ForecastsDialog
from .dialog.ForecastsSearchDialog import ForecastsSearchDialog
from qt import *
from PyQt4.QtGui import QCursor, QDialog, QMessageBox
from PyQt4.QtCore import Qt
##########################################################################
# Forecasts
##########################################################################
class EditForecasts(ExecutorBase):
    def execute(self):
        current_node = self.getCurrentNode()
        flist = get_nodes("//prelreq/forecasts/forecast", self.srcDoc_)
        forecasts = []
        for fc in flist:
            fcnum = get_datum_from_expr("fc-num", fc)
            nhapos = get_datum_from_expr("nha-pos", fc)
            forecasts.append((fcnum, nhapos))
        dialog = ForecastsDialogImpl(self.qtWidget_, self.sernaDoc_, 
                                     forecasts, self.validateForecasts)
        if QDialog.Accepted == dialog.exec_loop():
            forecasts = dialog.getForecasts()
            self.replaceOrInsert("forecasts", forecasts, 
            "configurations checks maintflow-num crew-type")

    def validateForecasts(self, num):
        qApp.setOverrideCursor(QCursor(Qt.WaitCursor))
        url = self.composeUrl("forecastLookup", [("fcnum",num)])
        grove = Grove.buildGroveFromFile(url)
        nha_list = []
        fcs = get_nodes("//forecasts/forecast", grove.document())
        for fc in fcs:
            num = get_datum_from_expr("fc-num", fc)
            nha = get_datum_from_expr("nha-pos", fc)
            nha_list.append((num, nha))
        qApp.restoreOverrideCursor()
        return nha_list

##########################################################################

class ForecastsDialogImpl(ForecastsDialog):
    def __init__(self, parent, sernaDoc, forecasts, func):
        ForecastsDialog.__init__(self, parent)        
        self.sernaDoc_ = sernaDoc
        self.func_ = func
        for fc in forecasts:
            listitem = QListViewItem(self.listView_, fc[0], fc[1])
        self.selectionChanged()
        self.listView_.setSelected(self.listView_.firstChild(), True)

    def getForecasts(self):
        forecasts = []
        item = self.listView_.firstChild()
        while item:
            forecasts.append(("forecast", [("fc-num", str(item.text(0))),
            ("nha-pos", str(item.text(1)))]))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())       
        return forecasts


    def add(self):
        dialog = ForecastsSearchDialogImpl(self, self.func_)
        if QDialog.Accepted == dialog.exec_loop():
            nhalist = dialog.getList()
            for item in nhalist:
                if not self.hasDup(item[0], item[1]):
                    QListViewItem(self.listView_, item[0], item[1])

    def edit(self):
        item = self.listView_.selectedItem()
        if not item:
            return
        fcnum = item.text(0).__str__()
        nhapos = item.text(1).__str__()
        while True:
            dialog = LineEdit2DialogImpl(self, self.func_, "Edit Forecast", fcnum, nhapos)
            if QDialog.Accepted == dialog.exec_loop():
                fcnum = dialog.getText1()
                nhapos = dialog.getText2()
                if not nhapos or not fcnum or nhapos=="Please select one":
                        QMessageBox.warning(self, "Warning",
                        "'fc-num' and 'nha-pos' fields are required !")
                elif self.hasDup(fcnum, nhapos, self.listView_.selectedItem()):
                    QMessageBox.warning(self, "Warning","Such 'fc-num' already exists.")
                else:
                    item.setText(0, fcnum)
                    item.setText(1, nhapos)
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

    def hasDup(self, text, nha, cur = None):
        item = self.listView_.firstChild()
        while item:
            if item != cur and text == item.text(0).__str__() and \
               nha == item.text(1).__str__():
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
      
class LineEdit2DialogImpl(LineEdit2Dialog):
    def __init__(self, parent, func, caption, text1 = "", text2 = ""):
        LineEdit2Dialog.__init__(self, parent)
        self.func_ = func
        self.setCaption(caption)
        self.lineEdit1_.setText(text1)
        self.loadingvalidate()
        self.nhaBox_.setCurrentText(text2)
        self.lineEdit1_.setFocus()
           
    def getText1(self):
        return self.lineEdit1_.text().__str__()

    def getText2(self):
        return self.nhaBox_.currentText().__str__()

    def loadingvalidate(self):
        self.nhaBox_.clear()
        #self.nhaBox_.insertItem("")
        if not self.lineEdit1_.text():
            return
        lst = self.func_(self.getText1())
        for nha in lst:
            self.nhaBox_.insertItem(nha[1])
    
    def validate(self):        
        if not self.lineEdit1_.text():
            return
        lst = self.func_(self.getText1())
        self.nhaBox_.clear()
        self.nhaBox_.insertItem("Please select one")
        for nha in lst:
           self.nhaBox_.insertItem(nha[1])

##########################################################################

class ForecastsSearchDialogImpl(ForecastsSearchDialog):
    def __init__(self, parent, func):
        ForecastsSearchDialog.__init__(self, parent)
        self.func_ = func
        self.searchLineEdit_.setFocus()

    def getList(self):
        result = []
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item):
                result.append((item.text(0), item.text(1)))
            item = item.nextSibling(item, self.listView_.invisibleRootItem())      
        return result

    def search(self):
        if not self.searchLineEdit_.text():
            return
        self.listView_.clear()
        lst = self.func_(self.searchLineEdit_.text().__str__())
        for nha in lst:
            QListViewItem(self.listView_, nha[0], nha[1])

    def selectionChanged(self):
        has_selection = False
        item = self.listView_.firstChild()
        while item:
            if self.listView_.isSelected(item):
                has_selection = True
                break
            item = item.nextSibling(item, self.listView_.invisibleRootItem())
        self.okButton_.setEnabled(has_selection)
