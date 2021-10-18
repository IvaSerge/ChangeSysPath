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
import calc_cab_tray
from calc_cab_tray import *
import cable_catalogue
from cable_catalogue import *

# ================ GLOBAL VARIABLES
global doc
doc = DocumentManager.Instance.CurrentDBDocument
cab_tray.doc = doc
el_sys.doc = doc
graph.doc = doc
calc_cab_tray.doc = doc

reload = IN[1]
outlist = list()

# Create electrical system objects
# Get all systems in project
not_filtered_systems = FilteredElementCollector(doc).\
	OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
	WhereElementIsNotElementType().\
	ToElements()
# filter out not connected systems
all_systems = [sys for sys in not_filtered_systems if sys.BaseEquipment]

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

for system in all_systems:
	sys_obj = ElSys(system.Id)
	list_of_systems.append(sys_obj)
	sys_obj.find_trays_run()
	sys_obj.create_new_path()

# 	systems_in_tray = [
# 		x for x in list_of_systems
# 		if x.run_along_trays]


# cable tray size calculation
# Cable.create_catalogue()
# tray_sys_link = get_tray_sys_link(systems_in_tray)
# tray_filling = [calc_tray_filling(link) for link in tray_sys_link]
# tray_filling = [x for x in tray_filling if x]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for sys_obj in list_of_systems:
	el_system = sys_obj.rvt_sys
	path = sys_obj.path
	try:
		el_system.SetCircuitPath(path)
	except:
		pass

# for tray_fill in tray_filling:
# 	set_tray_size(tray_fill)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# # OUT = [x.rvt_sys.CircuitNumber for x in list_of_systems if x.rvt_members == "Error"]
# # try:
# # 	OUT = el_sys.process_list(
# # 		lambda x: vector.toPoint(x), test_sys.path)
# # except:
# # 	OUT = test_sys.path
# # Cable.create_catalogue()
# OUT = list_of_nets
OUT = [x.run_along_trays for x in list_of_systems]
