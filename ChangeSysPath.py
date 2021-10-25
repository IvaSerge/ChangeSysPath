# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

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
import element_provider
from element_provider import *
import tray_catalogue
from tray_catalogue import *

# ================ GLOBAL VARIABLES
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
app = uiapp.Application

global doc  # type: ignore
doc = DocumentManager.Instance.CurrentDBDocument
cab_tray.doc = doc
el_sys.doc = doc
graph.doc = doc
calc_cab_tray.doc = doc
element_provider.doc = doc
element_provider.uidoc = uidoc

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore
param_reverse = IN[3]  # type: ignore

outlist = list()
error_list = list()

fnrvStr = FilterStringEquals()
# "Cable Tray ID" - id of parameter is 8961921
pvp = ParameterValueProvider(ElementId(8961921))
frule = FilterStringRule(pvp, fnrvStr, "", False)
filter = ElementParameterFilter(frule)
empty_trays = FilteredElementCollector(doc).\
	OfCategory(BuiltInCategory.OST_CableTray).\
	WhereElementIsNotElementType().\
	WherePasses(filter).\
	ToElements()

if calc_all:
	all_systems = ElementProvider.get_all_systems()
	tray_names = ElementProvider.get_all_tray_names()
else:
	all_systems = ElementProvider.get_sys_by_selection()
	tray_names = ElementProvider.get_tray_names_by_system(all_systems[0])


list_of_nets = [TrayNet(x) for x in tray_names]
el_sys.list_of_nets = list_of_nets

# Create electrical system objects
list_of_systems = list()
for system in all_systems:
	sys_obj = ElSys(system.Id, param_reverse)
	list_of_systems.append(sys_obj)
	sys_obj.find_trays_run()

	try:
		sys_obj.create_new_path()
	except:
		# create error list
		tray_net_str = sys_obj.rvt_sys.LookupParameter("Cable Tray ID")
		tray_net_str = tray_net_str.AsString()
		error_list.append(tray_net_str)

systems_in_tray = [
	x for x in list_of_systems
	if x.run_along_trays]

# cable tray size calculation
Cable.create_catalogue()
tray_sys_link = get_tray_sys_link(systems_in_tray)
tray_filling = [calc_tray_filling(link) for link in tray_sys_link]
tray_weight = [calc_tray_weight(link) for link in tray_sys_link]
tray_tags = [get_tags(link) for link in tray_sys_link]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# for sys_obj in list_of_systems:
	# el_system = sys_obj.rvt_sys
	# path = sys_obj.path
	# try:
	# 	el_system.SetCircuitPath(path)
	# except:
	# 	pass

	# if param_reverse:
	# 	tray_net_param = el_system .LookupParameter("Cable Tray ID")
	# 	tray_net_str = tray_net_param.AsString()
	# 	not_reversed = tray_net_str.split("-")
	# 	reversed = not_reversed[::-1]
	# 	new_value = "-".join(reversed)
	# 	tray_net_param.Set(new_value)


for tray_fill in tray_filling:
	set_tray_size(tray_fill)

for tw in tray_weight:
	set_tray_weight(tw)

for tag in tray_tags:
	set_tag(tag)

# !!!CLEAN INFO IN EMPTY TRAYS
clean_tray_parameters(empty_trays)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = [x.rvt_sys.CircuitNumber for x in list_of_systems if x.rvt_members == "Error"]
# try:
# OUT = el_sys.process_list(lambda x: vector.toPoint(x), list_of_systems[0].path)
# except:
# 	OUT = test_sys.path
# Cable.create_catalogue()
# OUT = [x.run_along_trays for x in list_of_systems]
# OUT = tray_names
# OUT = list_of_systems[0].run_along_trays
# OUT = el_sys.process_list(lambda x: vector.toPoint(x), list_of_systems[0].run_along_trays)

OUT = tray_tags
