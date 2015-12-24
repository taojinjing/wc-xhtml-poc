from SernaApi import *
from weakref import *
from .utils import *
from PyQt4.QtGui import QMessageBox
import re

class DblClickWatcher(SimpleWatcher):   
    def __init__(self, plugin): 
        SimpleWatcher.__init__(self)
        self.__plugin = ref(plugin)
        self.__map = {"major-zone":     "EditMajorZone", 
                      "maintflow-num":  "EditMaintenanceFlowNumber",
                      "model":          "EditManufacturerModelDash",
                      "dash":           "EditManufacturerModelDash",
                      "references":     "EditReferences",
                      "zones-panels":   "EditZonesPanels",
                      "configurations": "EditConfigurations",
                      "drawings":       "EditDrawings",
                      "checks":         "EditChecks",
                      "part-qty":       "EditPartQty",
                      "part-state":     "EditPartState",
                      "parts":          "EditParts",
                      "tool-qty":       "EditToolQty",
                      "tool-state":     "EditToolState",
                      "tools":          "EditTools",
                      "cb-state":       "EditCircuitBreakerState",
                      "circuit-breakers":"EditCircuitBreakers",
                      "crew-type":      "EditCrewType",
                      "wctype":         "EditWorkcardType",
                      "eff":            "EditEffectivityGroup",
                      "sign":           "EditSignBlocks",
                      "wc-title":       "EditTitle",
                      "wc-num":         "EditCard",
                      "source-docs":    "EditTasks",
                      "forecasts":      "EditForecasts",
                      "head-flags":     "InsertHeadFlags",
                      "panel-table":    "InsertPanelTable",
                      "graphic":        "EditGraphicSize",
                      "estimations":    "EditEstimations",}

    def goLocal(self, node, id):
        if not id:
            return 1
        elem = get_node("//*[@id='" + id + "'][1]", node)
        if not elem:
            return 1
        se = self.__plugin().sernaDoc().structEditor()
        se.setCursorBySrcPos(GrovePos(elem, elem.firstChild()),
            se.getFoPos().node())
        return 0

    def notifyChanged(self):
        pos = self.__plugin().sernaDoc().structEditor().getSrcPos()
        if pos.isNull():
            return True
        pos_fo = self.__plugin().sernaDoc().structEditor().getFoPos()
        node = pos_fo.node()
        if node.nodeName() == "fo:external-graphic":
            
            #graphic_id = str(get_attribute(pos.node(), "href"))
            #url = self.__plugin().composeUrl(
            #    "getRepositoryView.do", [("id", graphic_id)])
            #webbrowser.open_new(url)
            
            src = str(get_attribute(node, "src"))
            src_res = re.search("(\w+\-?\w+).jpg", src)
            if src_res:
                src = src_res.group(1)
            try:
                func = self.__map[src]
                prelreq = get_node("ancestor-or-self::prelreq", pos.node())
                self.__plugin().executeUiEvent(func, None)
                return False
            except KeyError:
                a = 1; #do nothing
        node = pos.node()
        while node:
            try:
                func = self.__map[str(node.nodeName())]
                prelreq = get_node("ancestor-or-self::prelreq", pos.node())
                self.__plugin().executeUiEvent(func, None)
                return False
            except KeyError:
                a = 1; #do nothing
            node = node.parent()
        node = pos.node()
        if node:
            if GrovePos.TEXT_POS == pos.type():
                node = node.parent() 
            if node.nodeName() == "xref":
                attr = node.asGroveElement().attrs().getAttribute("xrefid")
                if attr.isNull() or not attr.value():
                    return True
                return self.goLocal(node, attr.value().__str__())
        return True

class CursorPosWatcher(SimpleWatcher):   
    def __init__(self, plugin): 
        SimpleWatcher.__init__(self)
        self.__plugin = ref(plugin)
        #self.__warningsMenu = self.__plugin().sernaDoc().findItemByName(
        #    "editCautionsWarnings");

    def notifyChanged(self):
        # Get current position in the source XML tree (grove)
        se = self.__plugin().sernaDoc().structEditor()
        pos = se.getSrcPos()  
        if pos.isNull():
            return True # no valid position - do nothing               
        node = pos.node()
        if node.nodeName()=="sign" and not pos.before():
            se.setCursorBySrcPos(GrovePos(node.parent(), node.nextSibling()),\
                                     se.getFoPos().node(), True)
            return False
        return True
        # Check current position. If it is a text node, take its parent.
        #node = pos.node()
        #if GrovePos.TEXT_POS == pos.type():
        #    node = node.parent()   
        # For link element
        #name = node.nodeName()
        #if self.__warningsMenu:
        #    self.__warningsMenu.action().setEnabled(
        #        name == "warning" or name == "caution" or
        #        name == "note" or name == "text")
        #return False
