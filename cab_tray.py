
"""Cable tray fuctions."""

__author__ = "IvaSerge"
__email__ = "ivaserge@ukr.net"
__status__ = "Development"

# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory
from Autodesk.Revit.DB.Category import GetCategory

# ================ Python imports
import collections
from collections import deque


def _param_by_cat(_bic, _name):
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


def _category_by_bic_name(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return GetCategory(doc, bic)


def _get_all_reference(_inst):
	reference_list = list()
	elem = _inst
	category_elem = elem.Category.Id
	category_tray = _category_by_bic_name("OST_CableTray").Id
	category_fitting = _category_by_bic_name("OST_CableTrayFitting").Id

	# for cable tray
	if category_elem == category_tray:
		elem_con_manager = elem.ConnectorManager

	# for cable tray fitting
	if category_elem == category_fitting:
		elem_mep_model = elem.MEPModel
		elem_con_manager = elem_mep_model.ConnectorManager

	elem_cons = elem_con_manager.Connectors
	for connector in elem_cons:
		elem_ref = connector.AllRefs
		if elem_ref:
			for ref in elem_ref:
				reference_list.append(ref.Owner)

	return reference_list


def get_first_tray(_name):
	"""Get first-in cable tray instance.

	Cable tray will be selected by "MC Object Variable 1" parameter value

	args:
		_name (str): parameter value
	return:
		cable tray instance
	"""

	# tray system name is in "MC Object Variable 1" parameter
	param = _param_by_cat(
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
	"""Get relations between cable trays and fittings

	Relations are represented as pairs of neighbors.\n
	It is possible more than 1 neighbor.\n
	Example: A-B, A-C means that object A is connected to B and C

	args:
		inst_first: first instance of net
	return:
		relation_list: list of pairs
	"""

	elems_to_ceck = collections.deque([])
	elems_to_ceck.append(inst_first)
	outlist = list()

	elem_current = elems_to_ceck.pop()
	elem_refs = _get_all_reference(elem_current)
	# outlist.append(elem_refs)

	return elem_refs


global doc
