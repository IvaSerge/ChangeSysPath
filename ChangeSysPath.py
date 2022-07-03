# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
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
param_reverse = IN[3]  # type: ignore

outlist = list()
error_list = list()

all_systems = ElementProvider.get_sys_by_selection()
el_system = all_systems[0]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# Create electrical system objects
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
			raise ValueError("Tray with ID do not exists\n" + name)

else:
	# system runs not in cable tray
	list_of_nets = None

sys_obj.list_of_nets = list_of_nets
try:
	sys_obj.find_trays_run()
except Exception as e:
	error_text = "\n" + str(e)
	raise ValueError(error_text)

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
		error_text = ("Check electrical system: " + el_system.Id.ToString())
		raise ValueError(error_text)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

try:
	OUT = el_sys.process_list(lambda x: vector.toPoint(x), path)
except:
	OUT = all_systems
