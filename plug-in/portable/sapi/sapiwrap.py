import sys
from SernaApi import *
from PyQt4.QtGui import QGraphicsView, QGraphicsScene
import random

def ui_item_widget(sernaDoc):
    if sernaDoc is None:
        return None
    else:
        widget = sernaDoc.widget()
        if isinstance(widget, PyQt4.QtGui.QGraphicsView):
            return QGraphicsViewWrap(widget)
        else:
            return sernaDoc.widget()

class QGraphicsViewWrap():

    def __init__(self, graphicsView):
        self.graphicsView_ = graphicsView

    def inverseWorldMatrix(self):
        return self.graphicsView_.matrix()

    def viewportToContents(self, point):
        return self.graphicsView_.mapToScene(point)      

    def canvas(self):
        return QGraphicsSceneWrap(self.graphicsView_.scene()) 

    def viewport(self):
        return self.graphicsView_.viewport()

class QGraphicsSceneWrap():

    def __init__(self, scene):
        self.scene_ = scene

    def collisions(self, point):
        return self.scene_.items(point)

def nodeSet2List(nodeset):
    targetList = []

    for onenode in nodeset:
        targetList.append(onenode)

    return targetList

class GroveElementWrap:

    def __init__(self, groveEle):
        self.groveEle_ = groveEle
        self.randseed_ = random.randint(-100000, 100000)

    def getActualObj(self):
        return self.groveEle_

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
