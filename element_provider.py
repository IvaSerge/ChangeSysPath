
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
	def inst_by_cat_strparamvalue(_bic, _bip, _val, _isType):
		"""Get all family instances by category and parameter value

			args:
			_bic: BuiltInCategory.OST_xxx
			_bip: BuiltInParameter
			_val: Parameter value
			_isType: is Type or Instance

			return:
			list()[Autodesk.Revit.DB.FamilySymbol]
		"""
		if _isType:
			fnrvStr = FilterStringEquals()
			pvp = ParameterValueProvider(ElementId(int(_bip)))
			frule = FilterStringRule(pvp, fnrvStr, _val)
			filter = ElementParameterFilter(frule)
			elem = FilteredElementCollector(doc).\
				OfCategory(_bic).\
				WhereElementIsElementType().\
				WherePasses(filter).\
				ToElements()
		else:
			fnrvStr = FilterStringEquals()
			pvp = ParameterValueProvider(ElementId(int(_bip)))
			frule = FilterStringRule(pvp, fnrvStr, _val)
			filter = ElementParameterFilter(frule)
			elem = FilteredElementCollector(doc).\
				OfCategory(_bic).\
				WhereElementIsNotElementType().\
				WherePasses(filter).\
				ToElements()
		return elem

	@staticmethod
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
			param = elem.get_Parameter(ElementProvider.get_bip(name))

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

	@staticmethod
	def get_bip(paramName):
		builtInParams = System.Enum.GetValues(BuiltInParameter)
		param = []
		for i in builtInParams:
			if i.ToString() == paramName:
				param.append(i)
				return i

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

		# filter out systems with empty "Cable tray Id" and path not Custom
		systems_with_Id = [sys for sys in all_systems
			if sys.LookupParameter("Cable Tray ID").HasValue and
			sys.LookupParameter("Cable Tray ID").AsString() != "NA"]

		# path_mode = Autodesk.Revit.DB.Electrical.ElectricalCircuitPathMode.Custom
		# systems_without_Id = [sys for sys in all_systems if
		# 	not(sys.LookupParameter("Cable Tray ID").HasValue) and sys.CircuitPathMode != path_mode]

		# return systems_without_Id + systems_with_Id
		return systems_with_Id

	@staticmethod
	def elsys_by_brd(_brd):
		# type: (FamilyInstance) -> list
		"""Get all systems of electrical board.

			args:
			_brd - electrical board FamilyInstance

			return list(0, 1) where:
			0 - main electrical circuit
			1 - list of connectet low circuits
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
			# TODO: Check sorting of circuits
			# lowsys.sort(key=lambda x: float(
			# 	ElementProvider.get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER")))
			return mainboardsys, lowsys
		else:
			return [i for i in allsys][0], None

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
			sys_el = sel_obj.MEPModel.GetElectricalSystems()
			sys_all = [x.Id for x in sel_obj.MEPModel.GetAssignedElectricalSystems()]
			el_sys_list = [x for x in sys_el if x.Id not in sys_all]
			# filter out electrical circuit only
			el_sys_list = [
				x for x in el_sys_list
				if x.SystemType == Electrical.ElectricalSystemType.PowerCircuit]

		else:
			el_sys_list = [x for x in sel_obj.MEPModel.GetElectricalSystems()]

		# filter NA circuit
		el_sys_list = [
			x for x in el_sys_list
			if x.LookupParameter("Cable Tray ID").AsString() != "NA"]

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

		# tray_names = [name for name in tray_names if "IT" in name]
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

	@staticmethod
	def get_trays_by_id(_cabletray_ID):
		"""
		Get trays in model by "Cable Tray ID" parameter
		"""
		# get "Cable Tray ID" parameter ID
		first_tray = FilteredElementCollector(doc).\
			OfCategory(BuiltInCategory.OST_CableTray).\
			WhereElementIsNotElementType().\
			FirstElement()

		param_id = first_tray.LookupParameter("Cable Tray ID").Id

		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(param_id)
		frule = FilterStringRule(pvp, fnrvStr, _cabletray_ID)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(BuiltInCategory.OST_CableTray).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()

		return elem


global doc
global uidoc
