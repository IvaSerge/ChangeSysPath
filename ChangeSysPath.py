# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
file_out = dir_path + r"\result.csv"
file_database = dir_path + r"\database.csv"
sys.path.append(dir_path)

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
import checkModel
from checkModel import *

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

reload = IN[1]  # type: ignore[reportUndefinedVariable]
calc_all = IN[2]  # type: ignore
param_reverse = IN[3]  # type: ignore
check_id = IN[3]  # type: ignore

outlist = list()
error_list = list()

# clean files
with open(file_out, "w") as f_out:
	f_out.write("")

with open(file_database, "w") as f_db:
	f_db.write("")

if calc_all:
	all_systems = ElementProvider.get_all_systems()

else:
	all_systems = ElementProvider.get_sys_by_selection()

# before start script - check Id
if check_id:
	checkTrayId(doc, dir_path, all_systems)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# Create electrical system objects
for el_system in all_systems:
	sys_obj = ElSys(el_system.Id, param_reverse)
	tray_names = ElementProvider.get_tray_names_by_system(el_system)

	if tray_names:
		list_of_nets = list()
		# system runs along cable tray
		for name in tray_names:
			try:
				list_of_nets.append(TrayNet(name))
			except:
				error_text = "\nTray with ID do not exists: " + name
				# write errors to file
				with open(file_out, "a") as f_out:
					f_out.write(error_text)
				# raise ValueError("Tray with ID do not exists\n" + name)

	else:
		# system runs not in cable tray
		list_of_nets = None

	el_sys.list_of_nets = list_of_nets
	try:
		sys_obj.find_trays_run()
	except Exception as e:
		error_text = e
		# write errors to file
		try:
			with open(file_out, "a") as f_out:
				f_out.write(error_text)
		except:
			error_text = "\nCant write to file. ERROR in system: " + sys_obj.Id.ToString()
			with open(file_out, "a") as f_out:
				f_out.write(error_text)

	try:
		sys_obj.create_new_path()
	except:
		# create error list
		tray_net_str = sys_obj.rvt_sys.LookupParameter("Cable Tray ID")
		tray_net_str = tray_net_str.AsString()
		error_list.append(tray_net_str)

	path = sys_obj.path
	elem_stat = Autodesk.Revit.DB.WorksharingUtils.GetCheckoutStatus(
		doc, el_system.Id)
	if elem_stat != Autodesk.Revit.DB.CheckoutStatus.OwnedByOtherUser:
		try:
			el_system.SetCircuitPath(path)
		except Exception as e:
			e_text = str(e)
			with open(file_out, "a") as f_out:
				f_out.write("\nCheck electrical system: " + el_system.Id.ToString())

	if calc_all:
		# write result to data baise
		write_tray_sys_link(file_database, sys_obj)

if calc_all:
	# clean parameters of all cable trays
	with SubTransaction(doc) as sub_tr:
		sub_tr.Start()
		all_trays = FilteredElementCollector(doc).\
			OfCategory(BuiltInCategory.OST_CableTray).\
			WhereElementIsNotElementType()
		clean_tray_parameters(all_trays)
		sub_tr.Commit()

	# open file
	with open(file_database, "r") as f_db:
		while True:
			line = f_db.readline()
			if not line:
				break

			link = get_tray_sys_link(doc, line)
			if not link:
				continue

			# chxeck if tray is editable
			tray_id = link[0].Id
			elem_status = WorksharingUtils.GetCheckoutStatus(doc, tray_id)

			# calculate parameters
			try:
				tray_weight = calc_tray_weight(link)
			except:
				with open(file_out, "a") as f_out:
					tray_weight = 0
					f_out.write("\nWeight not found. Check tray size: " + tray_id.ToString())

			if elem_status == CheckoutStatus.OwnedByOtherUser:
				with open(file_out, "a") as f_out:
					f_out.write("\nTray not editable: " + tray_id.ToString())
				continue

			else:
				tray_fill = calc_tray_filling(link)
				tray_tag = get_tags(link)

				# write parameters to tray
				set_tray_size(tray_fill)
				set_tray_weight(tray_weight)
				set_tag(tray_tag)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

try:
	OUT = el_sys.process_list(lambda x: vector.toPoint(x), path)
except:
	OUT = all_systems
