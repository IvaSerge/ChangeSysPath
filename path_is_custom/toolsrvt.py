
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Dynamo imports
clr.AddReference('ProtoGeometry')
import Autodesk.DesignScript

from Autodesk.DesignScript.Geometry import *

clr.AddReference("RevitNodes")
import Revit
clr.ImportExtensions(Revit.Elements)
from Revit.Elements import *
clr.ImportExtensions(Revit.GeometryConversion)
clr.ImportExtensions(Revit.GeometryReferences)

# ================ Python imports
import os.path
import math
import string
import re
import operator
from operator import itemgetter, attrgetter
import itertools
from types import FunctionType


def process_list(_func, _list):
	# type: (FunctionType, list) -> any
	return map(
		lambda x: process_list(_func, x)
		if type(x) == list else _func(x), _list)


def unwrap(_item):
	if isinstance(_item, list):
		return process_list(unwrap, _item)
	else:
		return UnwrapElement(_item)  # type: ignore


def flatten_list(data):
	# iterating over the data
	list_in_progress = data
	list_found = True

	while list_found:
		flat_list = list()
		list_found = False
		for i in list_in_progress:
			if isinstance(i, list):
				list_found = True
				map(lambda x: flat_list.append(x), i)
			else:
				flat_list.append(i)
		list_in_progress = [x for x in flat_list]

	return list_in_progress


def get_parval(elem, name):
	# type: (FamilyInstance, str) -> any
	"""Get parametr value

	args:
		elem - family instance or type
		name - parameter name
	return:
		value - parameter value
	"""

	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not param:
		param = elem.get_Parameter(get_bip(name))

	# get paremeter Value if found
	try:
		storeType = param.StorageType
		# value = storeType
		if storeType == StorageType.String:
			value = param.AsString()
		elif storeType == StorageType.Integer:
			value = param.AsDouble()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def get_bip(paramName):
	builtInParams = [i for i in System.Enum.GetNames(BuiltInParameter)]
	param = None
	for i, i_name in enumerate(builtInParams):
		if i_name == paramName:
			param = System.Enum.GetValues(BuiltInParameter)[i]
			break
	return param


def setup_param_value(elem, name, pValue):

	# check element staus
	doc = elem.Document
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, elem.Id)
	if elem_status == CheckoutStatus.OwnedByOtherUser:
		return None

	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not param:
		param = elem.get_Parameter(get_bip(name))
	param.Set(pValue)
	return param


def category_by_bic_name(doc, _bicString):
	bic_value = System.Enum.Parse(BuiltInCategory, _bicString)
	return Autodesk.Revit.DB.Category.GetCategory(doc, bic_value)


# def param_by_cat(_bic, _name):
# 	# type: (Autodesk.Revit.DB.BuiltiInCategory, str) -> Autodesk.Revit.DB.Parameter
# 	"""Get parametr in

# 	args:
# 		_bic (BuiltiInCategory.OST_xxx): category
# 		_name (str): parameter name
# 	return:
# 		param (Autodesk.Revit.DB.Parameter) - parameter
# 	"""
# 	# check Type parameter
# 	elem = FilteredElementCollector(doc).\
# 		OfCategory(_bic).\
# 		WhereElementIsElementType().\
# 		FirstElement()
# 	param = elem.LookupParameter(_name)
# 	if param:
# 		return param

# 	# check instance parameter
# 	# ATTENTION! instance is first in!
# 	# Be sure that all instances has the parameter.
# 	elem = FilteredElementCollector(doc).\
# 		OfCategory(_bic).\
# 		WhereElementIsNotElementType().\
# 		FirstElement()
# 	param = elem.LookupParameter(_name)
# 	if param:
# 		return param

# 	# Not found
# 	return None


# 	if param:
# 		try:
# 			param.Set(pValue)
# 		except:
# 			pass
# 	return elem


def inst_by_cat_strparamvalue(_doc, _bic, _bip, _val, _isType):
	"""Get all family instances by category and parameter value

		args:
		_doc: Active document
		_bic: BuiltInCategory.OST_xxx
		_bip: BuiltInParameter
		_val: Parameter value
		_isType: is Type or Instance

		return:
		list()[Autodesk.Revit.DB.FamilySymbol]
	"""
	if _isType:
		fnrvStr = FilterStringContains()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(_doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringContains()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(_doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


def type_by_bic_fam_type(_doc, _bic, _fnam, _tnam):
	"""Get Type by family category, family name and type

		args:
		_doc: active document
		_bic: BuiltInCategory.OST_xxx
		_fnam (str): family name
		_tnam (str): type name

		return:
		Autodesk.Revit.DB.FamilySymbol
	"""

	fnrvStr = FilterStringEquals()

	pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
	pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

	fruleF = FilterStringRule(pvpFam, fnrvStr, _fnam)
	filterF = ElementParameterFilter(fruleF)

	fruleT = FilterStringRule(pvpType, fnrvStr, _tnam)
	filterT = ElementParameterFilter(fruleT)

	filter = LogicalAndFilter(filterT, filterF)

	elem = FilteredElementCollector(_doc).\
		OfCategory(_bic).\
		WhereElementIsElementType().\
		WherePasses(filter).\
		FirstElement()
	return elem


def mm_to_ft(mm):
	return 3.2808 * mm / 1000


# def ft_to_mm(ft):
# 	mm = Autodesk.Revit.DB.UnitUtils.ConvertFromInternalUnits(
# 		ft, Autodesk.Revit.DB.DisplayUnitType.DUT_MILLIMETERS)
# 	return mm


def elsys_by_brd(_brd):
	# type: (FamilyInstance) -> list
	"""Get all systems of electrical board.

		args:
		_brd - electrical board FamilyInstance

		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()

	# filter out non Power circuits
	allsys = [i for i in allsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	lowsys = [i for i in lowsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]

	if lowsys:
		lowsysId = [i.Id for i in lowsys]
		mainboardsysLst = [i for i in allsys if i.Id not in lowsysId]
		if len(mainboardsysLst) == 0:
			mainboardsys = None
		else:
			mainboardsys = mainboardsysLst[0]
		lowsys = [i for i in allsys if i.Id in lowsysId]
		lowsys.sort(key=lambda x: float(get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER")))
		return mainboardsys, lowsys
	else:
		return [i for i in allsys][0], None
