# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
file_points = dir_path + r"\database_points.csv"
file_trays = dir_path + r"\database_trays.csv"
file_errors = dir_path + r"\database_errorlist.csv"
file_report = dir_path + r"\database_report.csv"


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
import time

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
calc_all = True  # type: ignore
param_reverse = IN[3]  # type: ignore
check_id = IN[3]  # type: ignore

outlist = list()
error_list = list()

continue_exec = False

all_systems = ElementProvider.get_all_systems()
SYSTEMS_TOTAL = len(all_systems)
report_text = "TOTAL systems: " + str(SYSTEMS_TOTAL + 1)
with open(file_report, "a") as f_out:
	f_out.write(report_text)

if not continue_exec:
	# clean files
	with open(file_errors, "w") as f_out:
		f_out.write("")

	with open(file_points, "w") as f_db:
		f_db.write("")

	with open(file_trays, "w") as f_db:
		f_db.write("")

	with open(file_report, "w") as f_db:
		f_db.write("")

	i_sys = 1.0

# TODO
if continue_exec:
	pass
	# do not clean files
	# filter out systems list
	# all_systems = [x if i x not in Done list]

	# calculate Done systems
	# i_sys = 1.0


# Create electrical system objects

for el_system in all_systems:
	time_start = time.time()
	report_text = "\n" + el_system.Id.ToString()
	with open(file_report, "a") as f_out:
		f_out.write(report_text)

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
				with open(file_errors, "a") as f_out:
					f_out.write(error_text)
				# raise ValueError("Tray with ID do not exists\n" + name)

	else:
		# system runs not in cable tray
		list_of_nets = None

	el_sys.list_of_nets = list_of_nets
	try:
		sys_obj.find_trays_run()
	except Exception as e:
		# check if the error is allerady in the file
		with open(file_errors, "r") as post_out:
			data = post_out.read()
			check_list = re.findall(str(e), data, flags=DOTALL)

		# if error not in the file - write to file
		if not(check_list):
			error_text = "\n" + str(e)
			# write errors to file
			with open(file_errors, "a") as f_out:
					f_out.write(error_text)

	try:
		sys_obj.create_new_path()
	except:
		# create error list
		tray_net_str = sys_obj.rvt_sys.LookupParameter("Cable Tray ID")
		tray_net_str = tray_net_str.AsString()
		error_list.append(tray_net_str)

	path = sys_obj.path

	# write result to data baise

	if path:
		write_tray_sys_link(file_trays, sys_obj)
		write_path(file_points, el_system.Id.ToString(), path)

	current_percentage = str(round(i_sys / SYSTEMS_TOTAL, 2) * 100)
	time_end = time.time()
	time_exec = str(time_end - time_start)
	report_text = ". Done: " + current_percentage + ", " + "Runtime: " + time_exec
	i_sys += 1
	with open(file_report, "a") as f_out:
		f_out.write(report_text)


OUT = path[0].X, path[0].Y, path[0].Z
