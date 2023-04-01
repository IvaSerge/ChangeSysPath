# ================ system imports
from os import linesep
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
file_in = dir_path + r"\database_points.csv"
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
import importlib

# ================ local imports
import el_sys
importlib.reload(el_sys)
from el_sys import ElSys

import cab_tray
importlib.reload(cab_tray)

import graph
importlib.reload(graph)

import vector
importlib.reload(graph)

import calc_cab_tray
importlib.reload(calc_cab_tray)

import cable_catalogue
importlib.reload(cable_catalogue)

import element_provider
importlib.reload(element_provider)
from element_provider import ElementProvider

import tray_catalogue
importlib.reload(tray_catalogue)

import checkModel
importlib.reload(checkModel)

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

regexp = re.compile(r"-*\w+\.*\w+-?e?\w*")
outlist = list()

with open(file_in, "r") as f_in:
	next(f_in)

	for line in f_in:
		if len(line) == 0 or not line:
			continue

		search_result = regexp.findall(line)
		list_total = collections.deque([i for i in search_result])
		el_system_id = int(list_total.popleft())
		el_system = doc.GetElement(ElementId(el_system_id))

		# check if system exists in model
		if not el_system:
			continue

		path = list()

		while list_total:
			pnt_x = float(list_total.popleft())
			pnt_y = float(list_total.popleft())
			pnt_z = float(list_total.popleft())
			path.append(XYZ(pnt_x, pnt_y, pnt_z))

		disable_path_change = el_system.LookupParameter("Disable_change_ of_ path").AsInteger()
		elem_stat = Autodesk.Revit.DB.WorksharingUtils.GetCheckoutStatus(
			doc, el_system.Id)
		if elem_stat != Autodesk.Revit.DB.CheckoutStatus.OwnedByOtherUser and disable_path_change == 0:
				try:
					el_system.SetCircuitPath(path)
					outlist.append(el_system)
				except Exception as e:
					e_text = str(e)


# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# sort error file after execution
checkModel.sortData(file_errors)

OUT = outlist
