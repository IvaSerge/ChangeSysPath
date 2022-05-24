# ================ system imports
from os import linesep
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
file_in = dir_path + r"\database_points1.csv"
file_out = dir_path + r"\database_report.csv"
file_errors = dir_path + r"\database_errorlist.csv"
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
import re
from re import *
import collections

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


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

regexp = re.compile(r"(-*\d+\.*\d+e?\D?\d+),|(-*\d+\.*\d+e?\D?\d+)$")
outlist = list()
with open(file_in, "r") as f_in:
	next(f_in)
	for line in f_in:
		if len(line) == 0:
			continue

		list_total = collections.deque([i[0] if i[0] else i[1] for i in regexp.findall(line)])
		el_system_id = int(list_total.popleft())
		el_system = doc.GetElement(ElementId(el_system_id))

		path = list()
		while list_total:
			pnt_x = float(list_total.popleft())
			pnt_y = float(list_total.popleft())
			pnt_z = float(list_total.popleft())
			path.append(XYZ(pnt_x, pnt_y, pnt_z))

		elem_stat = Autodesk.Revit.DB.WorksharingUtils.GetCheckoutStatus(
			doc, el_system.Id)
		if elem_stat != Autodesk.Revit.DB.CheckoutStatus.OwnedByOtherUser:
				try:
					el_system.SetCircuitPath(path)
				except Exception as e:
					e_text = str(e)
					with open(file_errors, "a") as f_out:
						f_out.write("\nCheck electrical system: " + el_system.Id.ToString())

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

try:
	OUT = el_sys.process_list(lambda x: vector.toPoint(x), path)
except:
	OUT = None
