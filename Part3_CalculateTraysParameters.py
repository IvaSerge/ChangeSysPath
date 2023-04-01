# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
dir_path = IN[0].DirectoryName  # type: ignore
file_out = dir_path + r"\database_errorlist.csv"
file_database = dir_path + r"\database_trays.csv"
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

outlist = list()
error_list = list()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# set tray parameters
# clean parameters of all cable trays
with SubTransaction(doc) as sub_tr:
	sub_tr.Start()
	all_trays = FilteredElementCollector(doc).\
		OfCategory(BuiltInCategory.OST_CableTray).\
		WhereElementIsNotElementType()
	all_trays = [i for i in all_trays if
		WorksharingUtils.GetCheckoutStatus(doc, i.Id) != CheckoutStatus.OwnedByOtherUser]

	calc_cab_tray.clean_tray_parameters(all_trays)
	sub_tr.Commit()

# open file
with open(file_database, "r") as f_db:
	for line in f_db:

		if len(line) <= 1:
			continue
		else:
			link = calc_cab_tray.get_tray_sys_link(doc, line)

		if not link:
			continue

		outlist.append(link)

		# check if tray is editable
		# if tray not exists - continue
		if link[0]:
			tray_id = link[0].Id
		else:
			continue

		elem_status = WorksharingUtils.GetCheckoutStatus(doc, tray_id)

		if elem_status == CheckoutStatus.OwnedByOtherUser:
			with open(file_out, "a") as f_out:
				f_out.write("\nTray not editable: " + tray_id.ToString())
			continue

		# calculate parameters
		try:
			tray_weight = calc_cab_tray.calc_tray_weight(link)
			calc_cab_tray.set_tray_weight(tray_weight)
		except:
			with open(file_out, "a") as f_out:
				tray_weight = 0
				f_out.write("\nWeight not found. Check tray size: " + tray_id.ToString())

		tray_fill = calc_cab_tray.calc_tray_filling(link)
		tray_tag = calc_cab_tray.get_tags(link)

		# # write parameters to tray
		calc_cab_tray.set_tray_size(tray_fill)
		calc_cab_tray.set_tag(tray_tag)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = outlist
