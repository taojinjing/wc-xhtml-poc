import sys,os
curdir = os.path.split(os.path.realpath(__file__))[0]
def portabledir():
    i = 0
    curdir = __file__
    while i <= 2:
        i = i + 1
        curdir = os.path.split(curdir)[0]

    return curdir

#curdir = os.path.split(os.path.realpath(__file__))[0]
curdir = portabledir() 
#curdir = "G:/serna/s1000d-plugins5"
sys.path.append(curdir + '/portable/sapi')
sys.path.append(curdir + '/portable/pyqt')
sys.path.append(curdir + '/portable/python')

from .Watchers   import *
from .utils  import *
from .EditReferences import *
from .InsertLocalReference import *
from .EditManufacturerModelDash import *
from .EditZonesPanels import *
from .EditConfigurations import * 
from .EditParts import *
from .EditTools import *
from .EditToolsInContent import *
from .EditDrawings import *
from .EditCircuitBreakers import *
from .EditChecks import *
from .EditCrewType import *
from .EditWorkcardType import *
from .EditMajorZone import *
from .EditMaintenanceFlowNumber import *
from .EditEffectivityGroup import *
from .EditAirplaneTails import *
from .EditSignBlocks import *
from .EditCautionsWarnings import *
from .EditGraphics import *
from .EditGraphicSize import *
from .EditTasks import *
from .EditForecasts import *
from .InsertHeadFlags import *
from .EditMainfunc import *
from .InsertPanelTable import *
from .InsertSignoffMechanic import *
from .SmallCommands import *
from .InsertDM import *
from .InsertTask import *
from .AboutPlugin import *
from .EditEstimations import *
from .InsertAddMarkDialog import *
from .InsertDeleteMarkDialog import *
from .InsertModifyMarkDialog import *
from .InsertClearMarkDialog import *
from .LoginCMSDialog import *