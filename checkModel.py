# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ local imports
import element_provider
from element_provider import ElementProvider

import cab_tray
from cab_tray import param_by_cat


def get_first_tray(doc, name):
	param = param_by_cat(
		Autodesk.Revit.DB.BuiltInCategory.OST_CableTray,
		"Cable Tray ID")
	fnrvStr = FilterStringEquals()
	pvp = ParameterValueProvider(param.Id)
	frule = FilterStringRule(pvp, fnrvStr, name, False)
	filter = ElementParameterFilter(frule)
	elem = FilteredElementCollector(doc).\
		OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
		WhereElementIsNotElementType().\
		WherePasses(filter).\
		FirstElement()
	return elem


def checkTrayId(doc, dir_path, el_systems):
	file_out = dir_path + r"\result.csv"
	outlist = list()
	for el_system in el_systems:
		# search for cable tray IDs in systems
		tray_names = ElementProvider.get_tray_names_by_system(el_system)
		if tray_names:
			for tray_name in tray_names:
				# try to find the first element with the ID
				first_tray = get_first_tray(doc, tray_name)
				# if ID not found
				if not(first_tray):
					outlist.append(tray_name)
	if outlist:
		# if it is not it the system Id - write to result.csv info
		outlist = set(outlist)
		with open(file_out, "w") as f_out:
			for element in outlist:
				f_out.write(element + "\n")
		raise ValueError("Errors found.\nCheck result.csv")

	else:
		with open(file_out, "w") as f_out:
			f_out.write("Ok")
		raise ValueError("Errors not found.")
	return None
