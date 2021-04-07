"""Electrical systems fuctions."""

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
import operator
from operator import itemgetter, attrgetter
import re

# ================ local imports


class ElSys():
	def __init__(self, el_sys_id):
		"""
		Extended electrical system class
		"""
		self.rvt_sys = doc.GetElement(ElementId(el_sys_id))
		self.rvt_board = self.rvt_sys.BaseEquipment
		if not(self.rvt_sys.Elements.IsEmpty):
			unsorted_members = [x for x in self.rvt_sys.Elements]
			self.rvt_members = self.sort_by_distance(unsorted_members)
		else:
			self.rvt_members = None
		self.routed_along_trays = self._get_rout_names()

	def sort_by_distance(self, unsorted):
		"""Sort families by nearest distance
		# 	args:
		# 		el_system - current electrical system
		# 		board_inst - electrical board instance
		# 		instances - list of instances
		# 	return:
		# 		sort_list - sorted list of instances
		# 	"""
		board_inst = self.rvt_board
		list_inst = unsorted
		sorted_list = list()
		sorted_list.append(board_inst)
		unsorted_list = list()
		map(lambda x: unsorted_list.append(x), list_inst)

		while unsorted_list:
			if len(unsorted_list) == 1:
				sorted_list.append(unsorted_list.pop(0))
			else:
				start_inst = sorted_list[-1]
				distances = [self._get_distance(
					start_inst,
					check_inst)
					for check_inst in unsorted_list]
				temp_list = zip(unsorted_list, distances)
				temp_list.sort(key=operator.itemgetter(1))
				next_pnt = temp_list[0][0]
				pop_index = unsorted_list.index(next_pnt)
				unsorted_list.pop(pop_index)
				sorted_list.append(next_pnt)
		return sorted_list

	def _get_distance(self, inst_start, inst_to_check):
		start_pnt = self._find_connector_origin(inst_start)
		next_pnt = self._find_connector_origin(inst_to_check)
		distance = start_pnt.DistanceTo(next_pnt)
		return distance

	def _find_connector_origin(self, inst):
		el_system = self.rvt_sys
		con_set = inst.MEPModel.ConnectorManager.Connectors
		for connector in con_set:
			con_type = connector.ConnectorType
			type_is_logic = con_type == ConnectorType.Logical
			if not(connector.AllRefs.IsEmpty):
				con_allRefs = [x for x in connector.AllRefs]
				el_system_owner = con_allRefs[0].Owner
				check_sys = el_system_owner.Id == el_system.Id
				if check_sys and not(type_is_logic):
					return connector.Origin
				if check_sys and type_is_logic:
					# connector is found
					# but logic connector have no Origin
					# so FamilyInstance coordinate would be taken
					# may lead to mistakes while path creation!!!
					return connector.Owner.Location.Point
		return None

	def _get_rout_names(self):
		"""Get name list of cable trays through which cables run
		"""
		# the list should be in correct ORDER at this point!
		# TO DO. Automatical ordering to be done later

		el_sys = self.rvt_sys
		tray_net_str = el_sys.LookupParameter("MC Object Variable 1")
		tray_net_str = tray_net_str.AsString()

		# tray-net names shoud be separated by koma and white space
		# Example: aaaa, bbbb
		if tray_net_str:
			return tray_net_str.split(", ")
		else:
			return None


global doc

# def create_new_path(inst_list, el_system):
# 	"""Creates list of XYZ that runs through instancees in list.

# 	args:
# 		inst_list - list of RVT instances
# 	return:
# 		xyz_list - list of points that make path
# 	"""
# 	pairs_list = list()
# 	for i, inst in enumerate(inst_list):
# 		if i < inst_list.Count - 1:
# 			pairs_list.append([inst, inst_list[i + 1]])
# 		else:
# 			pass
# 	xyz_list = [
# 		get_intermadiate_points(x, el_system)
# 		for x in pairs_list]
# 	last_pnt = find_connector_origin(inst_list[-1], el_system)
# 	xyz_list.append(last_pnt)

# 	return flatten_list(xyz_list)


# def get_intermadiate_points(inst_list, el_system):
# 	start_pnt = find_connector_origin(inst_list[0], el_system)
# 	end_pnt = find_connector_origin(inst_list[1], el_system)
# 	# check if Z is equal with the tolerance
# 	start_check_pnt = XYZ(0, 0, start_pnt.Z)
# 	end_check_pnt = XYZ(0, 0, end_pnt.Z)

# 	vert_point = XYZ(
# 		start_pnt.X,
# 		start_pnt.Y,
# 		end_pnt.Z)

# 	if any([
# 		start_check_pnt.IsAlmostEqualTo(end_check_pnt),
# 		vert_point.IsAlmostEqualTo(end_check_pnt)
# 	]):
# 		# points are on the same level or above each other
# 		# no additional vertical point requiered
# 		return start_pnt
# 	else:
# 		# points are not on the same level
# 		# additional vertical point requiered
# 		return [start_pnt, vert_point]


# def flatten_list(data):
# 	# iterating over the data
# 	list_in_progress = data
# 	list_found = True

# 	while list_found:
# 		flat_list = list()
# 		list_found = False
# 		for i in list_in_progress:
# 			if isinstance(i, list):
# 				list_found = True
# 				map(lambda x: flat_list.append(x), i)
# 			else:
# 				flat_list.append(i)
# 		list_in_progress = [x for x in flat_list]

# 	return list_in_progress


# global doc

# doc = ChangeSysPath.doc

# start_tray = getByCatAndStrParam(
# 	_bic,
# 	_bip,
# 	tray_name,
# 	False)

# sys_sorted_elements = sort_by_distance(
# 	sys_electrical,
# 	sys_board,
# 	sys_elements)

# short_path = create_new_path(
# 	sys_sorted_elements,
# 	sys_electrical)

# standard_path = elem.GetCircuitPath()
# short_path = List[XYZ]([
# 	standard_path[0],
# 	standard_path[standard_path.Count - 1]])
