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
import vector
from vector import *

# ================ GLOBAL VARIABLES
global doc
doc = DocumentManager.Instance.CurrentDBDocument
cab_tray.doc = doc
el_sys.doc = doc
graph.doc = doc

reload = IN[1]
elem_id = IN[2]
outlist = list()

# Create electrical system objects
# TODO #2
# Get all systems in project
# Filter out electrical systems with empty path
el_system = ElSys(elem_id)

# find all connected cable-tray nets in project.
# for each net create TrayNet object.
all_trays = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
	WhereElementIsNotElementType().\
	ToElements()
tray_names = set([
	x.LookupParameter("""MC Object Variable 1""").AsString()
	for x in all_trays
	if x.LookupParameter("""MC Object Variable 1""").AsString()])
list_of_nets = [TrayNet(x) for x in tray_names]
el_sys.list_of_nets = list_of_nets
el_system.find_trays_run()
el_system.create_new_path()


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

el_system.rvt_sys.SetCircuitPath(el_system.path)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


# OUT = [x.name for x in el_system.run_along_trays]
OUT = [vector.toPoint(x) for x in el_system.path]
#OUT = el_system.run_along_trays
