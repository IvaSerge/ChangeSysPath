# ================ system imports
from tokenize import Double
from winsound import Beep
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
from System import Console

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
param_reverse = False  # type: ignore

# get all cable trays with not empty "Cable tray ID"
tray_net_ids = ElementProvider.get_all_tray_names()


# for every tray-net
# tray_id = [i for i in tray_net_ids][0]
# get net_instances
net_name = "T.LV1F.151"
tray_net = TrayNet(net_name)
inst_in_net = tray_net.instances
inst_in_net_IDs = [i.Id for i in inst_in_net]


# check if there dublicates of the systems
inst_in_model = ElementProvider.get_trays_by_id(net_name)
for inst in inst_in_model:
	if inst.Id not in inst_in_net_IDs:
		# if instance not in net_instance - report an Error.
		error_text = "\nDuplicate of net found: " + net_name
		with open(file_errors, "a") as f_out:
						f_out.write(error_text)
		break

# check if one net system contains elements with other tray IDs


OUT = inst_in_model
