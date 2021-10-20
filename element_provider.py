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
		return all_systems

	@staticmethod
	def get_sys_by_selection():
		"""
		Get system by selected object
		"""
		# get system by selected object
		sel = uidoc.Selection.PickObject(
			Autodesk.Revit.UI.Selection.ObjectType.Element, "")
		sel_obj = doc.GetElement(sel.ElementId)
		return [x for x in sel_obj.MEPModel.ElectricalSystems]


global doc
global uidoc
