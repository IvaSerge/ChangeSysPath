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
import vector
from vector import *


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
		self.rvt_sys = doc.GetElement(el_sys_id)
		self.rvt_board = self.rvt_sys.BaseEquipment
		unsorted_members = [x for x in self.rvt_sys.Elements]
		unsorted_members.insert(0, self.rvt_board)
		self.rvt_members = self.sort_by_distance(unsorted_members)
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
		el_sys_nets = list()
		rout_names = self._get_rout_names()
		for rout in rout_names:
			for net in list_of_nets:
				if net.name == rout:
					el_sys_nets.append(net)

		# with cycle check all nets
		i = 0
		net_start = el_start
		outlist = list()
		while i <= len(el_sys_nets) - 1:
			outlist.append([])

			# if it is not the last net - find nearest elem to next net
			# in real life there is only one nearest point
			# but unpredectable crazy situations are possible HERE!!!

			net = el_sys_nets[i]
			if i != len(el_sys_nets) - 1:
				net_end = TrayNet.find_nearest_pnt(
					net, el_sys_nets[i + 1])
			else:
				net_end = el_end

			start_end = self.get_in_out(net, net_start, net_end)
			start, end = start_end[0].Id, start_end[1].Id

			if start == end:
				# it is only one object in net
				outlist[i].append(start)
			else:
				# path need to be calculated using graph
				path = net.graph.dijsktra(start, end)
				map(lambda x: outlist[i].append(x), path)
			net_start = net_end
			i += 1

		outlist = flatten_list(outlist)
		self.run_along_trays = process_list(lambda x: doc.GetElement(x), outlist)

	@staticmethod
	def _tray_path(pnt_list):
		"""From list of points create ordered path"""
		sorted_points = list()

		for points in pnt_list:
			# if it is only one point - nothing to sort.
			if len(points) == 1:
				sorted_points.append(points[0])
			# it is cable tray. Points need to be sorted
			elif len(points) == 2:
				# check if it is an entrance to the cable tray
				# if it is an entrance - we do not need 2 points, but only 1
				# as the projection of the height on the base of the triangle
				point_A = points[0]
				point_B = points[1]
				point_C = sorted_points[-1]
				triangle_vector = Vec(point_A, point_B)
				point_X = triangle_vector.altitude_foot(point_C)
				if point_X:
					sorted_points.append(point_X)
				else:
					points_by_distance = sort_list_by_point(point_C, points)
					map(lambda x: sorted_points.append(x), points_by_distance)
			else:
				# not possible situation
				raise ValueError("More than 3 poins in list")
		clean_path = ElSys.clear_near_points(sorted_points)
		return clean_path

	@staticmethod
	def clear_near_points(points):
		list_to_check = points
		clean_list = list()
		clean_list.append(list_to_check.pop(0))

		while list_to_check:
			current_point = clean_list[-1]
			next_point = list_to_check.pop(0)
			if current_point.IsAlmostEqualTo(next_point):
				pass
			else:
				clean_list.append(next_point)
		return clean_list

	@staticmethod
	def get_exit_point(line_points, check_pnt):
		vec = Vec(line_points[0], line_points[1])
		return vec.altitude_foot(check_pnt)

	def create_new_path(self):
		# next - cable tray sorted by tray-nets.
		# check if trays in parameter exist
		self._get_rout_names
		net_names_in_param = self._get_rout_names()
		net_names = [x.name for x in list_of_nets]

		for name in net_names_in_param:
			if name not in net_names:
				raise ValueError(
					"Tray not found \n check system name \"%s\""
					% self.rvt_sys.LookupParameter(
						"MC Object Variable 1").AsString())

		path_instances = list()

		# first instance - is electrical board
		brd_inst = self.rvt_members[0]
		#brd_point = TrayNet.get_connector_points(brd_inst)[0]
		path_instances.append(brd_inst)

		# trays
		map(lambda x: path_instances.append(x), self.run_along_trays)

		# get path on the tray
		points_list = process_list(lambda x: TrayNet.get_connector_points(x), path_instances)
		tray_path = self._tray_path(points_list)
		# sys_inst = self.rvt_members[1:]
		# path_instances.append([])
		# map(lambda x: path_instances[-1].append(x), sys_inst)

		# flattened_path = flatten_list(path_instances)
		# path_with_Z = self.add_z_points(flattened_path)
		# self.path = self.clear_near_points(path_with_Z)
		self.path = tray_path

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
