# pyright: reportUnusedVariables=false
"""Provide elements for script"""

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


class ElementProvider():

	@staticmethod
	def get_all_systems():
		"""
		Get all systems, that connected to electrical boards
		"""

		# Get all systems in project
		not_filtered_systems = FilteredElementCollector(doc).\
			OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_ElectricalCircuit).\
			WhereElementIsNotElementType().\
			ToElements()
		# filter out not connected systems
		all_systems = [sys for sys in not_filtered_systems if sys.BaseEquipment]
		# data_systems = [sys for sys in all_systems if sys.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.Data]
		return all_systems

	@staticmethod
	def get_sys_by_selection():
		"""
		Get system by selected object
		"""
		el_sys_list = list()
		# get system by selected object
		sel = uidoc.Selection.PickObject(  # type: ignore
			Autodesk.Revit.UI.Selection.ObjectType.Element, "")
		sel_obj = doc.GetElement(sel.ElementId)  # type: ignore
		# check if selection is electrical board
		# OST_ElectricalEquipment.Id == -2001040
		if sel_obj.Category.Id == ElementId(-2001040):
			sys_el = sel_obj.MEPModel.ElectricalSystems
			sys_all = [x.Id for x in sel_obj.MEPModel.AssignedElectricalSystems]
			el_sys_list = [x for x in sys_el if x.Id not in sys_all]
			# filter out electrical circuit only
			el_sys_list = [
				x for x in el_sys_list
				if x.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
		else:
			el_sys_list = [x for x in sel_obj.MEPModel.ElectricalSystems]
		return el_sys_list

	@staticmethod
	def get_all_tray_names():
		"""
		Get the list of all tray IDs in the project
		"""
		all_trays = FilteredElementCollector(doc).\
			OfCategory(Autodesk.Revit.DB.BuiltInCategory.OST_CableTray).\
			WhereElementIsNotElementType()

		tray_names = set([
			x.LookupParameter("Cable Tray ID").AsString()
			for x in all_trays
			if x.LookupParameter("Cable Tray ID").AsString()])
		
		tray_names = [name for name in tray_names if "IT" in name]
		return tray_names

	@staticmethod
	def get_tray_names_by_system(_sys):
		"""
		Get the list of trays in system by selection
		"""
		param_as_text = _sys.LookupParameter("Cable Tray ID").AsString()
		if param_as_text:
			return param_as_text.split("-")
		else:
			return None

	@staticmethod
	def get_obj_by_selection():
		"""
		Get any object by selection
		"""
		sel = uidoc.Selection.PickObject(  # type: ignore
			Autodesk.Revit.UI.Selection.ObjectType.Element, "")
		sel_obj = doc.GetElement(sel.ElementId)  # type: ignore
		# check if selection is electrical board
		# OST_ElectricalEquipment.Id == -2001040
		return sel_obj


global doc
global uidoc
