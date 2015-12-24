from .ExecutorBase import *
from .dialog.GraphicSizeDialog import GraphicSizeDialog
from PyQt4.QtGui import QSpinBox
from qt import *
from urllib import *
from PyQt4.QtGui import QDialog
##########################################################################
# Adjust Graphic Size Dialog
##########################################################################
class UnitsConverter:
    unitsMap = {"mm":1, "in":25.4, "cm":10, "m":1000, "pt":0.35} 

    def __init__(self, value, format = "in"):
        self.unitsMap_ = UnitsConverter.unitsMap
        try:
            self.mm_ = self.unitsMap_[format] * value
        except StandardError:
            self.mm_ = value

    def convert(self, format="mm"):
        if format == "mm":
            return float(self.mm_)
        return float(self.mm_) / float(self.unitsMap_[format])

def filterDigits(inStr):
    digits_str = ''
    units_str = ''
    for c in inStr:
        if c == '.' or c in string.digits:
            digits_str += c
        elif c in string.ascii_letters:        
            units_str += c
    return (digits_str, units_str)


class EditGraphicSize(ExecutorBase):
    def getAttrValues(self, name):
        attr = self.graphic_.attrs().getAttribute(name)
        result = None
        format = None
        if not attr:
            return (result, format)
        try:
            val = filterDigits(attr.value().__str__())
            if val[1] != '':
                result = UnitsConverter(float(val[0]), val[1]).convert()
                format = val[1]
            else:
                result = int(attr.value().__str__())
        except Exception:
            pass
        return (result, format)

    def removeAttr(self, name):
        attr = self.graphic_.asGroveElement().attrs().getAttribute(name)
        if attr:
           cmd = self.groveEditor_.removeAttribute(attr)
           if cmd:
               self.batchCmd_.executeAndAdd(cmd)
               return True
        return False

    def addAttr(self, name, val):
        cmd = self.groveEditor_.addAttribute(self.graphic_, PropertyNode(name, val))
        if cmd:
            self.batchCmd_.executeAndAdd(cmd)
            return True
        return False

    def execute(self):
        if self.isReadOnly():
            return
        current_node = self.getCurrentNode()
        graphic = get_node("ancestor-or-self::graphic", current_node)
        if not graphic:
            return
        self.graphic_ = graphic.asGroveElement()
        href = get_attribute(self.graphic_, "href")
        pixmap = QPixmap(self.getImage(href))
        #pdm = QPaintDeviceMetrics(pixmap)
        #dpi = float(pdm.heightMM()) / float(pixmap.height())
        #orig_size = (pdm.heightMM(), pdm.widthMM())
        dpi = float(UnitsConverter(1).convert() / pixmap.logicalDpiY())
        orig_size = (float(pixmap.height()) * dpi, float(pixmap.width()) * dpi)
        format ="in"
        scale = 100
        res=self.getAttrValues("reproscl")
        if res[0]:
            scale = res[0]
        size = orig_size
        res=self.getAttrValues("reprohgt")
        if res[0]:
            size = (res[0], size[1])
            format = res[1].strip()
        res=self.getAttrValues("reprowid")
        if res[0]:
            size = (size[0], res[0])
            format = res[1].strip()
        if format == '':
            format ="in"

        xslt_params = PropertyNode("root")
        self.plugin_().executeCommandEvent("GetXsltParams", PropertyNode(), xslt_params)
        max_width_str = xslt_params.getProperty("page.max.width/value").getString().__str__()
        max_width = "210"
        try:
            val = filterDigits(max_width_str)
            if val[1] != '':
                max_width = UnitsConverter(float(val[0]), val[1]).convert()
            else:
                result = int(max_width_str)
        except Exception:
            pass

        dialog = GraphicSizeDialogImpl(self.qtWidget_, self.sernaDoc_,\
                             orig_size, scale, size, max_width, dpi, format)
        if QDialog.Accepted == dialog.exec_():
            res = dialog.getGraphicSize()
            height = res[1]
            width = res[2]
            units = res[3]
            scale = res[0]
            if units == "px":
                units = ""
            self.groveEditor_ = self.structEditor_.groveEditor()
            self.batchCmd_ = GroveBatchCommand()
            executed = False
            #batch_cmd.setFlags(GroveBatchCommand.CF_NOVISUAL)
            executed = self.removeAttr("reproscl") or executed
            executed = self.removeAttr("reprohgt") or executed
            executed = self.removeAttr("reprowid") or executed
            #if scale:
            #    if scale != 100:
            #        executed = self.addAttr("reproscl", str(scale)) or executed
            #else:
            if width != size[1]:
                executed = self.addAttr("reprowid", width.strip() + units) or executed
            if height != size[0]:
                executed = self.addAttr("reprohgt", height.strip() + units) or executed
            if executed:
                self.batchCmd_.setSuggestedPos(GrovePos(self.graphic_))
                self.structEditor_.executeAndUpdate(self.batchCmd_)

    def getImage(self, id):
        return self.retrieveFile(id)

##########################################################################

class SpinBox(QSpinBox):
    def __init__(self, parent):
        QSpinBox.__init__(self, parent)

    def textFromValue(self, value):
        if value == -1:
            return str( "Auto" );
        return str("{0}.{1}").format(int(value/10),int(value%10))

    def valueFromText(self, text):
        if text == "Auto":
            return -1
        num = self.value()
        try:
            num = float(str(text).split(" ")[0])
        except:
            return num
        return int(10*num)


class GraphicSizeDialogImpl(GraphicSizeDialog):
    def __init__(self, parent, sernaDoc, origSize, scale, size, maxWidth, dpi, units = "in"):
        GraphicSizeDialog.__init__(self, parent)
        QDialog.__init__(self)
        self.setupUi(self)

        sizebox_layout = self.sizeBox_.layout()
        self.__createSpinBoxes(sizebox_layout)
        self.fitWarningLabel_.setPixmap(IconProvider.getPixmap("warning"))
        self.fitWarningLabel_.hide()
        self.fitWarningLabel_.setToolTip("Image won't fit to page width");
        self.unitsMap_ = UnitsConverter.unitsMap
        self.unitsMap_["px"] = dpi
        self.origHeight_ = origSize[0]
        self.origWidth_ =  origSize[1]
        self.maxWidth_ =  maxWidth
        self.radioList_ = (None, self.scale_, self.sizeBox_)
        self.sernaDoc_ = sernaDoc
        self.proportion_ = float(origSize[0]) / float(origSize[1])
        #self.scale_.blockSignals(True)
        self.height_.blockSignals(True)
        self.width_.blockSignals(True)
        #self.scale_.setValue(scale)
        self.height_.setValue(size[0]*10)
        self.width_.setValue(size[1]*10)
        #self.scale_.blockSignals(False)
        self.height_.blockSignals(False)
        self.width_.blockSignals(False)
        self.curUnit_ = "mm"
        self.units_.setCurrentIndex(self.units_.findText(units))
        self.height_.blockSignals(True)
        self.width_.blockSignals(True)
        self.refreshUnits()
        self.height_.blockSignals(False)
        self.width_.blockSignals(False)
        #if scale != 100:
        #    self.scaleButton_.setChecked(True)
        #    self.modeChanged(1)
        #else:
        self.connect(self.sizeButton_, SIGNAL("released()"), self.modeChanged)
        self.connect(self.scaleButton_, SIGNAL("released()"), self.modeChanged)
        self.sizeButton_.setChecked(True)
        self.modeChanged()
        self.heightChanged()

    def __createSpinBoxes(self, layout):
        """
             __createSpinBoxes(layout)
                    local function for creating custom spinboxes
                   @layout  -- parent container for spinboxes
        """
        self.height_ = SpinBox(self.sizeBox_)
        self.height_.setMaximum(999999)
        layout.addWidget(self.height_, 0, 1, 1, 1)
        self.width_ = SpinBox(self.sizeBox_)
        self.width_.setMaximum(999999)
        layout.addWidget(self.width_, 1, 1, 1, 1)
        self.connect(self.height_, SIGNAL("valueChanged(int)"),\
                     self.heightChanged)
        self.connect(self.width_, SIGNAL("valueChanged(int)"),\
                     self.widthChanged)

    def convertUnits(self, value):
        return float(value) / float(self.unitsMap_[self.curUnit_])


    def getGraphicSize(self):
        return (self.scale_.value(), '%*.*f'%(5,1,float(self.height_.value())/10), \
                   '%*.*f'%(5,1,float(self.width_.value())/10), self.curUnit_)              

    def modeChanged(self):
        show_size = self.sizeButton_.isChecked()
        self.sizeBox_.setEnabled(show_size)
        self.scale_.setEnabled(not show_size)

    def proportionsChanged(self):
        self.heightChanged()

    def scaleChanged(self):
        vscale = float(self.scale_.value()) / 10
        max_width = UnitsConverter(float(self.maxWidth_),"mm").convert(self.curUnit_)
        scale = ((vscale * max_width) / self.convertUnits(self.origWidth_))
        self.height_.blockSignals(True)
        self.height_.setValue(self.convertUnits(self.origHeight_) * scale)
        self.height_.blockSignals(False)
        self.width_.blockSignals(True)
        self.width_.setValue(self.convertUnits(self.origWidth_) * scale)
        self.width_.blockSignals(False)
        self.checkFitWidth()


    def heightChanged(self):
        newValue = float(self.height_.value())
        self.fixScale(newValue / self.convertUnits(self.origHeight_))
        if self.constrainedProportions_.isChecked():
            self.width_.blockSignals(True)
            self.width_.setValue(float(newValue) / self.proportion_)
            self.width_.blockSignals(False)
        self.checkFitWidth()

    def widthChanged(self):
        newValue = float(self.width_.value())
        self.fixScale(newValue / self.convertUnits(self.origWidth_))
        if self.constrainedProportions_.isChecked():
            newValue = self.width_.value()
            self.height_.blockSignals(True)
            self.height_.setValue(self.proportion_ * float(newValue))
            self.height_.blockSignals(False)
        self.checkFitWidth()

    def fixScale(self, value):
        max_width = UnitsConverter(float(self.maxWidth_),"mm").convert(self.curUnit_)
        scale = (value * self.convertUnits(self.origWidth_))/ max_width
        self.scale_.blockSignals(True)
        self.scale_.setValue(scale * 10)
        self.scale_.blockSignals(False)

    def refreshUnits(self):
        heightMM = self.height_.value() * float(self.unitsMap_[self.curUnit_])
        widthMM = self.width_.value() * float(self.unitsMap_[self.curUnit_])
        self.curUnit_ = self.units_.currentText().__str__()
        self.hLabel_.setText('%*.*f'%(5,1,self.convertUnits(self.origHeight_)) + " " + self.curUnit_)
        self.wLabel_.setText('%*.*f'%(5,1,self.convertUnits(self.origWidth_)) + " " + self.curUnit_)
        self.height_.setValue(round(self.convertUnits(heightMM)))
        self.width_.setValue(round(self.convertUnits(widthMM)))
        self.height_.setSuffix(" " +self.curUnit_)
        self.width_.setSuffix(" " +self.curUnit_)
        self.checkFitWidth()

    def checkFitWidth(self):
        max_width = UnitsConverter(float(self.maxWidth_),"mm").convert(self.curUnit_)
        to_show = ((float(self.width_.value())/10) >= max_width)
        self.fitWarningLabel_.setShown(to_show)
        #self.fitWarningLabel_.setShown(to_show)

    def help(self):
        self.sernaDoc_.showHelp("index.html")
