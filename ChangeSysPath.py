# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
import operator
from operator import itemgetter, attrgetter
import itertools

# ================ local imports
import el_sys
from el_sys import ElSys
import cab_tray
from cab_tray import *
import graph
from graph import *

global doc
doc = DocumentManager.Instance.CurrentDBDocument
cab_tray.doc = doc
el_sys.doc = doc
graph.doc = doc

reload = IN[1]
elem_id = IN[2]
tray_name = IN[3]
outlist = list()

# el_system = ElSys(doc, elem_id)
tray_net = TrayNet("test")

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# sys_electrical.SetCircuitPath(short_path)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = tray_net.instances
