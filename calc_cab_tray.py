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
from collections import defaultdict


def GetParVal(elem, name):
	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		param = elem.get_Parameter(GetBuiltInParam(name))

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


def GetBuiltInParam(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def SetupParVal(elem, name, pValue):
	global doc
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(GetBuiltInParam(name)).Set(pValue)
		except:
			pass
	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def dict_get_value(dict, key_name):
	try:
		value = dict[key_name]
	except KeyError:
		value = None
	return value


def tray_find_systems(list_of_systems):
	outlist = list()
	tray_dict = dict()
	for sys in list_of_systems:
		sys_id = sys.rvt_sys.Id
		used_trays = sys.run_along_trays
		for tray in used_trays:
			tray_id = tray.Id
			dict_value = dict_get_value(tray_dict, tray_id)
			if dict_value:
				dict_value.append(sys_id)
			else:
				dict_update = {tray_id: [sys_id]}
				tray_dict.update(dict_update)

	tray_id_list = tray_dict.items()
	for tray_id in tray_id_list:
		tray = doc.GetElement(tray_id[0])
		# sys_str = ",".join(tray_id[1])
		if len(tray_id[1]) == 1:
			outlist.append([tray, tray_id[1][0]])
		else:
			elem_str = [str(x) for x in tray_id[1]]
			sys_str = ", ".join(elem_str)
			outlist.append([tray, sys_str])

	return outlist


global doc
