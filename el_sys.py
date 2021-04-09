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

# ================ local imports
import cab_tray
from cab_tray import *
import graph
from graph import *


def process_list(_func, _list):
	return map(
		lambda x: process_list(_func, x)
		if type(x) == list else _func(x), _list)


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


def sort_list_by_point(start_point, point_list):
	list_len = len(point_list)
	start_pnt_list = [start_point] * list_len
	calc_dist = zip(point_list, start_pnt_list)
	sort_dist = [x[0].DistanceTo(x[1]) for x in calc_dist]
	sort_list = zip(point_list, sort_dist)
	return [x[0] for x in sorted(sort_list, key=itemgetter(1))]


class ElSys():
	def __init__(self, el_sys_id):
		"""
		Extended electrical system class
		"""
		self.rvt_sys = doc.GetElement(ElementId(el_sys_id))
		self.rvt_board = self.rvt_sys.BaseEquipment
		if not(self.rvt_sys.Elements.IsEmpty):
			unsorted_members = [x for x in self.rvt_sys.Elements]
			unsorted_members.insert(0, self.rvt_board)
			self.rvt_members = self.sort_by_distance(unsorted_members)
		else:
			self.rvt_members = None
		self.run_along_trays = None
		self.path = None

	def sort_by_distance(self, _unsorted):
		"""Sort families by nearest distance

		args:
			instances - list of instances
		return:
			sort_list - sorted list of instances
		"""

		unsorted_list = list()
		sorted_list = list()
		# New list need to be created! Not just memory link!
		map(lambda x: unsorted_list.append(x), _unsorted)
		sorted_list.append(unsorted_list.pop(0))

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

	def get_in_out(self, tray_net, start, end):
		"""
		For each graph it is necessery to find IN-OUT elements

		args:
			tray_net (TrayNet instance)
			start, end (XYZ) - end points

		return:
			start_tray, end_tray - IN, OUT instances
		"""

		tray_elems = tray_net.instances
		outlist = list()

		for check_point in [start, end]:
			min_distance = 1000000000
			for elem in tray_elems:
				pnts = TrayNet.get_connector_points(elem)
				for pnt in pnts:
					distance = check_point.DistanceTo(pnt)
					if distance < min_distance:
						min_distance = distance
						out_elem = elem
			outlist.append(out_elem)
		return outlist

	def find_trays_run(self):
		"""Find cable trays witin cable runs"""
		el_system_start = self.rvt_members[0]
		el_start = self._find_connector_origin(el_system_start)
		el_system_end = self.rvt_members[1]
		el_end = self._find_connector_origin(el_system_end)

		# find a net in net list
		nets_current = list()
		rout_names = self._get_rout_names()
		for rout in rout_names:
			for net in list_of_nets:
				if net.name == rout:
					nets_current.append(net)

		# if it is not the single net - find connection between nets

		# get start-end points of the current net
		net = nets_current[0]
		start_end = self.get_in_out(net, el_start, el_end)
		start, end = start_end[0].Id, start_end[1].Id
		path = net.graph.dijsktra(start, end)
		self.run_along_trays = [doc.GetElement(x) for x in path]

		# TODO #1
		# # if it is not the last net - find connection to other net

	def create_new_path(self):
		path_instances = [[], [], []]
		# first of all instances need to be sorted
		# Elements need to be sorted to calculate additional points
		# between parts of instances

		# first instance - is electrical board
		brd_inst = self.rvt_members[0]
		brd_point = TrayNet.get_connector_points(brd_inst)[0]
		path_instances[0].append(brd_point)

		# next - cable tray sorted by tray-nets.
		unsorted_points = [
			TrayNet.get_connector_points(x)
			for x in self.run_along_trays]

		# Points are need to be sorted because connectors are unsorted
		sorted_path_points = list()
		for i, pnt_list in enumerate(unsorted_points):
			if i == 0:
				# the last point of previous net
				check_pnt = path_instances[0][-1]
			if i > 0:
				check_pnt = sorted_path_points[-1]
			sorted_list = sort_list_by_point(check_pnt, pnt_list)
			map(lambda x: sorted_path_points.append(x), sorted_list)
		map(lambda x: path_instances[1].append(x), sorted_path_points)

		# last instancees - list of electrical equipment points
		sys_inst = self.rvt_members[1:]
		inst_points = flatten_list([
			TrayNet.get_connector_points(x)
			for x in sys_inst])
		map(lambda x: path_instances[2].append(x), inst_points)
		# flattened_path = flatten_list(path_instances)
		self.path = path_instances
		# self.path = self.add_z_points(flattened_path)

	@staticmethod
	def add_z_points(path_points):
		"""Add or remove additional points to path

		new horisontal points to be add when Z changes,
		remove points in reisers, remove dublicates
		"""
		updated_list = list()
		for i, point in enumerate(path_points):
			if i == len(path_points) - 1:
				updated_list.append(point)
				continue

			point_next = path_points[i + 1]
			# no changes in Z
			if point.Z == point_next.Z:
				updated_list.append(point)

			# Z is changed
			# add new point on the same level as current
			if point.Z != point_next.Z:
				point_new = XYZ(
					point_next.X,
					point_next.Y,
					point.Z)
				# check if new point is not the same point as next point
				if point_new.IsAlmostEqualTo(point_next):
					# there is no need to make dublicate of the point
					updated_list.append(point)
				else:
					# new point will be added to list
					updated_list.append(point)
					updated_list.append(point_new)
		return updated_list


global doc
global list_of_nets
