
"""Cable tray fuctions."""

__author__ = "IvaSerge"
__email__ = "ivaserge@ukr.net"
__status__ = "Development"

# ================ system imports
import clr


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory

# ================ Python imports
import collections
from collections import deque


def param_by_cat(_bic, _name):
	"""Get parametr by category and parameter Name

	args:
		_bic (BuiltiInCategory.OST_xxx): category
		_name (str): parameter name
	return:
		Autodesk.Revit.DB.Parameter: parameter
	"""
	# check Type parameter
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# check instance parameter
	# ATTENTION! instance is first in!
	# Be sure that all instances has the parameter.
	elem = FilteredElementCollector(doc).\
		OfCategory(_bic).\
		WhereElementIsNotElementType().\
		FirstElement()
	param = elem.LookupParameter(_name)
	if param:
		return param

	# Not found
	return None


def get_first_tray(_name):
	# tray system name is in "MC Object Variable 1" parameter
	param = param_by_cat(
		Autodesk.Revit.DB.BuiltInCategory.OST_CableTray,
		"MC Object Variable 1")

	fnrvStr = FilterStringEquals()
	pvp = ParameterValueProvider(param.Id)
	frule = FilterStringRule(pvp, fnrvStr, _name, False)
	filter = ElementParameterFilter(frule)

	elem = FilteredElementCollector(doc).\
		OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
		WhereElementIsNotElementType().\
		WherePasses(filter).\
		FirstElement()

	return elem


def get_tray_relations(inst_first):

	elems_to_ceck = deque
	elems_to_ceck.append("1", "2")
	outlist = list()

	# for elem in elems_to_ceck:
	# 	reference_list = list()
	# 	elem_cat_id = elem.BuiltiInCategory.Id
	# 	# elem_current = elems_to_ceck.pop()

	# 	# for cable tray
	# 	if elem_cat_id == BuiltInCategory.OST_CableTray.Id:
	# 		elem_con_manager = elem_mep_model.ConnectorManager

	# 	# for cable tray fitting
	# 	if elem_cat_id == BuiltInCategory.OST_CableTrayFitting.Id:
	# 		elem_mep_model = elem.MEPModel
	# 		elem_con_manager = elem_mep_model.ConnectorManager

	# 	elem_cons = elem_con_manager.Connectors
	# 	for connector in elem_cons:
	# 		elem_ref = connector.AllRefs
	# 		if elem_ref:
	# 			reference_list.append(elem_ref.Owner)
	# 	outlist.append(reference_list)

	return outlist


global doc
