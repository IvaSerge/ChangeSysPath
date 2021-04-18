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
outlist = list()

# Create electrical system objects
# Get all systems in project
all_systems = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	ToElements()

filtered_el_sys = list()
for system in all_systems:
	param = system.LookupParameter("MC Object Variable 1")
	if param.HasValue:
		filtered_el_sys.append(system)

# find all connected cable-tray nets in project.
# for each net create TrayNet object.
all_trays = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
	WhereElementIsNotElementType().\
	ToElements()
tray_names = set([
	x.LookupParameter("MC Object Variable 1").AsString()
	for x in all_trays
	if x.LookupParameter("MC Object Variable 1").AsString()])
list_of_nets = [TrayNet(x) for x in tray_names]
el_sys.list_of_nets = list_of_nets


# create path for all systems in project
list_of_systems = list()
for system in filtered_el_sys:
	sys_obj = ElSys(system.Id)
	list_of_systems.append(sys_obj)
	sys_obj.find_trays_run()
	sys_obj.create_new_path()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# set path to all circuits
for sys_obj in list_of_systems:
	el_system = sys_obj.rvt_sys
	path = sys_obj.path
	el_system.SetCircuitPath(path)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

try:
	OUT = el_sys.process_list(
		lambda x: vector.toPoint(x), list_of_systems[1].path)
except:
	OUT = list_of_systems[0].path
